import bisect
import time
import warnings

import pandas

import psycopg2
from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import parse_pgpass
from estnltk.storage.postgres import create_schema
from estnltk.storage.postgres import schema_exists
from estnltk.storage.postgres import drop_layer_table
from estnltk.storage import postgres as pg


class PgStorageException(Exception):
    pass


class PostgresStorage:
    """
    `PostgresStorage` instance wraps a database connection and
    exposes interface to conveniently search/save json data.
    """

    TABLED_LAYER_TYPES = {'detached', 'fragmented', 'multi'}

    ALL_LAYER_TYPES = ({'attached'}).union(TABLED_LAYER_TYPES)

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None,
                 pgpass_file=None, schema="public", role=None, temporary=False, 
                 create_schema_if_missing=False, **kwargs):
        """
        Connects to database either using connection parameters if specified, or ~/.pgpass file.

            ~/.pgpass file format: hostname:port:database:username:password

        Normally, expects that the schema has already been created in the database, 
        and raises a PgStorageException if the schema is missing. 
        Use flag `create_schema_if_missing=True` to create the schema automatically if 
        the user has sufficient privileges.
        """
        self.schema = schema
        self.temporary = temporary
        self.collections_table = pg.table_identifier(self, '__collections')
        conn_param = parse_pgpass(pgpass_file, host, port, dbname, user, password)

        if role is None:
            role = conn_param['user']

        self.user = conn_param['user']

        logger.info('connecting to host: '
                    '{host!r}, port: {port!r}, dbname: {dbname!r}, user: {user!r}'.format(**conn_param))
        try:
            self.conn = psycopg2.connect(**conn_param, **kwargs)
        except Exception as connection_error:
            conn_param_copy = dict(conn_param)
            conn_param_copy['connection_error'] = connection_error
            connection_error_msg = ('Failed to connect '+\
                'host: {host!r}, port: {port!r}, dbname: {dbname!r}, user: {user!r} '+\
                'due to an error: {connection_error}').format(**conn_param_copy)
            logger.error( connection_error_msg )
            raise PgStorageException( connection_error_msg ) from connection_error

        self.conn.autocommit = False
        with self.conn.cursor() as c:
            c.execute(SQL("SET ROLE {};").format(Identifier(role)))
        self.conn.commit()

        if not schema_exists(self):
            if create_schema_if_missing:
                create_schema(self)
                logger.info('new schema {!r} created'.format(self.schema))
            else:
                schema_error_msg = ('Schema {!r} does not exist in the database. '+\
                                    'Set flag create_schema_if_missing=True to create '+\
                                    'the schema if you have enough privileges.').format(schema)
                logger.error(schema_error_msg)
                raise PgStorageException(schema_error_msg)

        self._collections = pg.StorageCollections(self)
        # Create storage_collections table (if missing)
        if not pg.table_exists( self, '__collections' ):
            try:
                temporary = SQL('TEMPORARY') if temporary else SQL('')
                with self.conn.cursor() as c:
                    c.execute(SQL('CREATE {temporary} TABLE {table} ('
                                  'collection text primary key, '
                                  'version text);').format(temporary=temporary,
                                                           table=self.collections_table))
                    logger.debug(c.query.decode())
            except Exception as table_creation_error:
                table_creation_error_msg = ('Failed to create storage_collections '+\
                    'table due to an error: {}. Please make sure you have enough '+\
                    'privileges for creating the table.').format(table_creation_error)
                logger.error(table_creation_error_msg)
                raise PgStorageException(table_creation_error_msg) from table_creation_error
            self.conn.commit()
        # Load the collections table to get the latest status
        # (otherwise user needs to manually call refresh())
        self._collections.load()
        
        logger.info('schema: {!r}, temporary: {!r}, role: {!r}'.format(self.schema, self.temporary, role))

    def refresh(self, omit_commit: bool=False, omit_rollback: bool=False):
        """Reloads table of collections of this storage. 
        Motivation: if any new collections have been inserted to 
        the database by a separate user/thread/job, this updates 
        the information about collections.
        
        By default, reloading the table involves making a commit 
        after the query. If you need to discard the commit (e.g. 
        in order to preserve a lock), set omit_commit=True.
        
        By default, if the current transaction has been aborted due 
        to an error, this function also makes a rollback, and starts 
        a new transaction. If you need to discard that behaviour, 
        set omit_rollback=True.
        """
        self._collections.load(omit_commit=omit_commit, omit_rollback=omit_rollback)

    def close(self):
        """Closes database connection."""
        self.conn.commit()
        self.conn.close()

    def closed(self):
        return self.conn.closed

    def get_collection(self, name: str):
        """
        Gets an existing collection from this storage. 
        **Important**: this method is deprecated, please use 
        storage[name] instead.
        """
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('Method storage.get_collection(...) is deprecated, '+\
                      'please use storage[collection_name] instead.', 
                      DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        collection = self[name]
        return collection

    def add_collection(self, name: str, description: str = None, meta: dict = None):
        """
        Adds a new collection to this storage. 
        Inserts entry about the collection to the table of collections 
        and creates corresponding structure and collection tables.
        Raises PgStorageException if a collection with the given name 
        already exists.
        Returns an instance of the newly created PgCollection.
        
        Parameters
        -----------
        name: str
            Name of the new collection. Must be an unique name, 
            not existing in this storage.
        description: str
            Description of this collection. Optional, if missing, 
            then pattern 'created by {user} on {creation_time}' 
            is used. 
        meta: dict
            A mapping with names and types of metadata columns. 
            Keys are strings, and values must be types from set 
            {"int", "bigint", "float", "str", "datetime"}.
            Optional, if meta is not provided, then no metadata 
            columns will be added to the collection table.

        Returns
        --------
        PgCollection
            an instance of the created collection
        """
        # This is required to avoid psycopg2.errors.NoActiveSqlTransaction
        self.conn.commit()
        self.conn.autocommit = False
        collection = None
        # Add storage.collections entry (collection name + version)
        with self.conn.cursor() as c:
            try:
                # EXCLUSIVE locking -- this mode allows only reads from the table 
                # can proceed in parallel with a transaction holding this lock mode.
                # Prohibit all other modification operations such as delete, insert, 
                # update, create index.
                # (https://www.postgresql.org/docs/9.4/explicit-locking.html)
                c.execute(SQL('LOCK TABLE ONLY {} IN EXCLUSIVE MODE').format( \
                                    self.collections_table ) )
                # Check if collection has been recorded in collection's table
                self.refresh(omit_commit=True, omit_rollback=True)
                if name not in self._collections:
                    # Note: we need to make insertion before creating PgCollection, 
                    # because creating PgCollection involves db queries with commits, 
                    # which would release the lock
                    version = '4.0'
                    c.execute(SQL(
                            "INSERT INTO {} (collection, version) "
                            "VALUES ({}, {});").format(
                            self.collections_table,
                            Literal(name),
                            Literal(version)
                    ))
                    collection = PgCollection(name, self, version=version)
                else:
                    raise PgStorageException(('collection {!r} already exists.'+\
                                              '').format(name))
            except Exception as adding_error:
                self.conn.rollback()
                raise PgStorageException(('(!) Cannot add new collection {!r} '+\
                                          'due to an exception: {}').format( \
                                                name, adding_error)) from adding_error
            finally:
                if self.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    self.conn.commit()
        # At this point, either PgCollection object was successfully created and 
        # inserted into the collections table, or exception was encountered (due
        # to collection already existing or some other problem).
        # Update the storage_collections view
        self._collections[collection.name] = collection
        try:
            # Create structure table (contains information about collection's layers)
            collection.structure.create_layer_info_table()
            if description is None:
                description = 'created by {} on {}'.format(self.user, time.asctime())
            # Create collection table (stores Text objects with attached layers and metadata columns)
            collection.structure.create_collection_table(meta_columns=meta,
                                                         description=description)
            logger.info('new empty collection {!r} created'.format(name))
        except Exception as adding_error:
            raise PgStorageException(('(!) Cannot add new collection {!r} '+\
                                      'due to an exception: {}').format( \
                                            name, adding_error)) from adding_error
        self.conn.commit()
        return collection

    @property
    def collections(self):
        return sorted(self._collections)

    def __getitem__(self, name: str):
        """
        Returns an existing PgCollection from this storage.
        Raises KeyError if there is no such collection.
        
        Note: this method does not automatically update the list 
        of available collections. If the status of collections has 
        been changed (some collections added or deleted) by another 
        thread or process during this connection, then refresh() 
        method needs to be called before this method to update the 
        information about available collections.
        """
        if name in self._collections:
            collection = self._collections[name]
            if collection is None:
                # An unloaded collection. 
                # Load it now, because there is a demand for it.
                version = self._collections.collections[name]['version']
                collection = PgCollection(name, self, version=version)
                self._collections[name] = collection
            # Return a loaded collection
            return collection
        raise KeyError(('(!) Collection {!r} does not '+\
                        'exist in this storage. Use Storage.refresh() '+\
                        'if the collection is updated by another thread '+\
                        'or process.').format(name))

    def delete(self, collection_name: str, cascade=False):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('Method storage.delete(collection_name) is deprecated, '+\
                      'please use storage.delete_collection(collection_name) '+\
                      'instead.', DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        self.delete_collection(collection_name, cascade=cascade)

    def delete_collection(self, collection_name: str, cascade=False):
        '''
        Deletes the given collection from the database.
        If cascade=True is set, then removes layer and collection 
        tables along with the tables dependent on these (if any).
        '''
        # Delete storage.collections entry
        assert self.conn.autocommit == False
        with self.conn.cursor() as c:
            try:
                # EXCLUSIVE locking -- this mode allows only reads from the table 
                # can proceed in parallel with a transaction holding this lock mode.
                # Prohibit all other modification operations such as delete, insert, 
                # update, create index.
                # (https://www.postgresql.org/docs/9.4/explicit-locking.html)
                c.execute(SQL('LOCK TABLE ONLY {} IN EXCLUSIVE MODE').format( \
                    self.collections_table ))
                # Check if collection hasn't already been deleted from collections_table
                self.refresh(omit_commit=True, omit_rollback=True)
                if collection_name not in self.collections:
                    raise KeyError('collection not found: {!r}'.format(collection_name))
                # Delete collection from collections_table
                c.execute(SQL("DELETE FROM {} WHERE collection={};").format(
                    self.collections_table,
                    Literal(collection_name)
                ))
                logger.debug(c.query.decode())
            except KeyError:
                self.conn.rollback() # release lock
                raise
            except Exception as deletion_err:
                self.conn.rollback()
                raise PgStorageException(('(!) Failed to delete collection {!r} '+\
                                          'due to an exception: {}.').format( \
                                                collection_name, deletion_err)) from deletion_err
            finally:
                if self.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    self.conn.commit()
        # Remove collection table, layer tables, structure table
        try:
            for layer, v in self[collection_name].structure.structure.items():
                if v['layer_type'] in PostgresStorage.TABLED_LAYER_TYPES:
                    drop_layer_table(self, collection_name, layer, 
                                           cascade=cascade, layer_type=v['layer_type'])
            pg.drop_collection_table(self, collection_name, cascade=cascade)
            pg.drop_structure_table(self, collection_name)
        except Exception as deletion_err:
            self.conn.rollback()
            raise PgStorageException(('(!) Failed to delete collection {!r} '+\
                                      'due to an exception: {}.').format( \
                                            collection_name, deletion_err)) from deletion_err
        self.refresh()


    def __setitem__(self, name: str, collection: pg.PgCollection):
        error_msg = '(!) Cannot assign collection via index operator. '+\
                    'Use add_collection(collection_name) method for '+\
                    'adding a new collection.'
        raise PgStorageException( error_msg )

    def __delitem__(self, collection_name: str):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('Method del storage[collection_name] is deprecated, '+\
                      'please use storage.delete_collection(collection_name) '+\
                      'instead.', DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        self.delete_collection(collection_name)

    def __str__(self):
        return '{self.__class__.__name__}({self.conn.dsn} schema={self.schema} temporary={self.temporary})'.format(
                self=self)

    def _repr_html_(self):
        self.refresh()

        bisect_left = bisect.bisect_left

        tables = pg.get_all_tables(self)
        table_names = sorted(tables)
        structure = {}
        missing_collections = []
        for collection in self.collections:
            index = bisect_left(table_names, collection)

            if table_names[index] != collection:
                missing_collections.append(collection)

            version = self._collections.collections[collection]['version']
            for i in range(index, len(table_names)):
                table = table_names[i]
                table_name_parts = table.split('__')
                if table_name_parts[0] == collection:
                    structure[(collection, version, table[len(collection):].lstrip('_'))] = tables[table]
                else:
                    break

        if structure:
            df = pandas.DataFrame.from_dict(structure, orient='index', columns=['rows', 'total_size', 'comment'])
            df.index.names = ('collection', 'version', 'relations')
            collection_tables = df.to_html()
        else:
            collection_tables = '<br/>This storage has no collections.'

        missing = ''
        if missing_collections:
            missing = ('\n There are collections listed in the __collections table '
                       'without tables in the database: {}').format(missing_collections)
        return ('<b>{self.__class__.__name__}</b><br/>\n{self.conn.dsn} schema={self.schema}<br/>'
                'temporary={self.temporary}<br/>\n'
                'collection count: {count}\n'
                '{collections}'
                '{missing}').format(
                self=self,
                count=len([coll for coll, version, layer in structure if layer == '']),
                collections=collection_tables,
                missing=missing)
