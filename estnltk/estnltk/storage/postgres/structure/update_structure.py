from warnings import warn

from collections import OrderedDict

from psycopg2.sql import SQL, Literal, Identifier
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.storage import postgres as pg

class PgCollectionUpdateException(Exception):
    pass

def _update_layer_info_table( storage: 'PostgresStorage', collection_name: str, new_version: str ):
    '''Updates collection's layer info table (the structure table) to the given collection version. 
       Currently only supports updating to '4.0'. 
    '''
    from datetime import datetime
    update_start = datetime.now()
    collection_version = storage._collections.collections[collection_name]['version']
    if collection_version not in {'2.0', '3.0'}:
        raise NotImplementedError(f'(!) Updating structure from {collection_version} to {new_version} is not implemented.')
    if new_version == '4.0':
        old_structure_table_id = pg.structure_table_identifier(storage, collection_name)
        old_structure_table_name = pg.structure_table_name(collection_name)
        # a) Create new temporary structure table
        new_structure_table_name = collection_name + '__structure' + '__new'
        if pg.table_exists(storage, new_structure_table_name):
            raise PgCollectionUpdateException(f'(!) Cannot update collection {collection_name!r}: '+\
                                              f'new structure table {new_structure_table_name!r} already exists. '+\
                                              'If the previous update was incomplete, then delete the table '+\
                                              f'{new_structure_table_name!r} to proceed with the update.')
        new_structure_table_id = pg.table_identifier(storage, new_structure_table_name)
        temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
        with storage.conn.cursor() as c:
            try:
                # Create structure for '4.0'
                c.execute(SQL('CREATE {temporary} TABLE {table} ('
                              'layer_name text primary key, '
                              'attributes text[] not null, '
                              'span_names text[], '
                              'ambiguous bool not null, '
                              'sparse bool not null, '
                              'parent text, '
                              'enveloping text, '
                              'meta text[], '
                              'layer_type text not null, '
                              'serialisation_module text, '
                              'layer_template jsonb);').format(temporary=temporary,
                                                        table=new_structure_table_id))
            except Exception:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
                    logger.debug(c.query.decode())
        # b) Carry over data from the old table to the new table
        # ( can be done on the server side )
        new_structure_columns = \
            ['layer_name', 'attributes', 'span_names', 'ambiguous', 'sparse', 'parent', 'enveloping', 
             'meta', 'layer_type', 'serialisation_module', 'layer_template']
        new_structure_columns_select = []
        for column in new_structure_columns:
            if column == 'sparse' and collection_version == '2.0':
                new_structure_columns_select.append( SQL('FALSE') )
            elif column == 'layer_template' and collection_version == '2.0':
                new_structure_columns_select.append( SQL('NULL') )
            elif column == 'span_names':
                new_structure_columns_select.append( SQL('NULL') )
            else:
                new_structure_columns_select.append( Identifier(column) )
        assert len(new_structure_columns) == len(new_structure_columns_select)
        with storage.conn.cursor() as c:
            try:
                # EXCLUSIVE locking -- allow read, but prohibit all modifications to table. 
                # (https://www.postgresql.org/docs/9.4/explicit-locking.html)
                c.execute(SQL('LOCK TABLE ONLY {} IN EXCLUSIVE MODE').format(old_structure_table_id))
                # Carry over data
                query = \
                    SQL("INSERT INTO {} ({}) SELECT {} FROM {}").format( 
                        new_structure_table_id, 
                        SQL(', ').join(map(Identifier, new_structure_columns)),
                        SQL(", ").join(new_structure_columns_select) ,
                        old_structure_table_id )
                c.execute( query )
                logger.debug(c.query.decode())
            except:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
        # c) Delete old structure table
        pg.drop_table( storage, old_structure_table_name )
        # d) Rename the new structure table to old
        sql = SQL('ALTER TABLE {} RENAME TO {}; ')
        with storage.conn.cursor() as c:
            try:
                c.execute(sql.format(new_structure_table_id, Identifier(old_structure_table_name)))
            except Exception:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
                    logger.debug(c.query.decode())
        time_elapsed = f'time elapsed: {datetime.now()-update_start}'
        logger.info(f'updated collection {collection_name!r} structure table to {new_version} ({time_elapsed})')
    else:
        raise NotImplementedError(f'(!) Updating structure from {collection_version} to {new_version} is not implemented.')


def _update_collection_table( storage: 'PostgresStorage', collection_name: str, new_version: str, create_index=False ):
    '''Updates collection table to the given collection version. 
       Currently only supports updating to '4.0'. 
    '''
    import time
    from datetime import datetime
    update_start = datetime.now()
    collection_version = storage._collections.collections[collection_name]['version']
    if collection_version not in {'2.0', '3.0'}:
        raise NotImplementedError(f'(!) Updating collection from {collection_version} to {new_version} is not implemented.')
    if new_version == '4.0':
        # a) Get all columns of the collection table, along with the corresponding data types
        collection_table_columns = OrderedDict()
        with storage.conn.cursor() as c:
            c.execute(SQL('SELECT column_name, data_type from information_schema.columns '
                          'WHERE table_schema={} and table_name={} '
                          'ORDER BY ordinal_position'
                          ).format(Literal(storage.schema), 
                                   Literal(collection_name)))
            collection_table_columns = OrderedDict(c.fetchall())
        if len(collection_table_columns.keys()) == 0:
            raise PgCollectionUpdateException(f'(!) Cannot update collection {collection_name!r} table: '+\
                                              f'collection table does not exist. ')
        # Get metadata columns
        collection_meta_columns = OrderedDict()
        for (name, col_type) in collection_table_columns.items():
            if name not in ['id', 'data', 'hidden']:
                collection_meta_columns[name] = col_type
            elif name == 'hidden':
                raise PgCollectionUpdateException(f'(!) Cannot update collection {collection_name!r} table: '+\
                                                  f'the table already has column named "hidden". ')
        # a) Create new temporary collection table
        new_collection_table_name = collection_name + '__new'
        if pg.table_exists(storage, new_collection_table_name):
            raise PgCollectionUpdateException(f'(!) Cannot update collection {collection_name!r}: '+\
                                              f'new collection table {new_collection_table_name!r} already exists. '+\
                                              'If the previous update was incomplete, then delete the table '+\
                                              f'{new_collection_table_name!r} to proceed with the update.')
        new_collection_table_id = pg.table_identifier(storage, new_collection_table_name)
        columns = [SQL('id BIGSERIAL PRIMARY KEY'),
                   SQL('data jsonb')]
        new_column_names = ['id', 'data']
        columns.append( SQL('hidden BOOLEAN DEFAULT FALSE') )
        new_column_names.append( 'hidden' )
        if len( collection_meta_columns.keys() ) > 0:
            for col_name, col_type in collection_meta_columns.items():
                columns.append(SQL('{} {}').format(Identifier(col_name), SQL(col_type)))
                new_column_names.append( col_name )
        temp = SQL('TEMPORARY') if storage.temporary else SQL('')
        with storage.conn.cursor() as c:
            try:
                c.execute(SQL("CREATE {} TABLE {} ({});").format(
                    temp, new_collection_table_id, SQL(', ').join(columns)))
                logger.debug(c.query.decode())
                if create_index:
                    c.execute(
                        SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops);").format(
                            index=Identifier( get_index_name_hash('%s_layer_data' % table_name) ), table=new_collection_table_id))
                    c.execute(
                        SQL("CREATE INDEX {index} ON {table} USING gin ((data->'relation_layers') jsonb_path_ops);").format(
                            index=Identifier( get_index_name_hash('%s_relation_layer_data' % table_name) ), table=new_collection_table_id) )
                    logger.debug(c.query.decode())
                description = 'updated by {} on {}'.format(storage.user, time.asctime())
                c.execute(SQL("COMMENT ON TABLE {} IS {}").format(new_collection_table_id, Literal(description)))
                logger.debug(c.query.decode())
            except:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
        old_collection_table_id = pg.collection_table_identifier(storage, pg.collection_table_name(collection_name))
        old_collection_table_name = pg.collection_table_name(collection_name)
        # b) Carry over data from the old table to the new table
        # ( can be done on the server side )
        new_column_names_select = \
            [Identifier(name) if name != 'hidden' else SQL('FALSE') for name in new_column_names]
        assert len(new_column_names) == len(new_column_names_select)
        with storage.conn.cursor() as c:
            try:
                # EXCLUSIVE locking -- allow read, but prohibit all modifications to table. 
                # (https://www.postgresql.org/docs/9.4/explicit-locking.html)
                c.execute(SQL('LOCK TABLE ONLY {} IN EXCLUSIVE MODE').format(old_collection_table_id))
                # Carry over data
                query = \
                    SQL("INSERT INTO {} ({}) SELECT {} FROM {}").format( 
                        new_collection_table_id, 
                        SQL(', ').join(map(Identifier, new_column_names)),
                        SQL(", ").join(new_column_names_select) ,
                        old_collection_table_id )
                c.execute( query )
                logger.debug(c.query.decode())
            except:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
        # c) Delete old collection table
        pg.drop_table(storage, old_collection_table_name)
        # d) Rename the new structure table to old
        sql = SQL('ALTER TABLE {} RENAME TO {}; ')
        with storage.conn.cursor() as c:
            try:
                c.execute(sql.format(new_collection_table_id, Identifier(old_collection_table_name)))
            except Exception:
                storage.conn.rollback()
                raise
            finally:
                if storage.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    storage.conn.commit()
                    logger.debug(c.query.decode())
        time_elapsed = f'time elapsed: {datetime.now()-update_start}'
        logger.info(f'updated collection {collection_name!r} table to {new_version} ({time_elapsed})')
    else:
        raise NotImplementedError(f'(!) Updating collection from {collection_version} to {new_version} is not implemented.')


def _update_collection_version( storage: 'PostgresStorage', collection_name: str, new_version: str ):
    '''Updates collection's version in the table '__collections'. 
       Note that this should be a final step, after the steps _update_layer_info_table(...) and 
       _update_collection_table(...) have been completed.
    '''
    if not pg.table_exists(storage, '__collections'):
        raise Exception("(!) Collections table {!r} does not exist!".format(str(storage.collections_table)))
    if collection_name not in storage.collections:
        raise pg.PgCollectionException(f'(!) Cannot update collection {collection_name!r}: no such collection.')
    # Update version in the database
    with storage.conn.cursor() as c:
        try:
            # EXCLUSIVE locking -- allow read, but prohibit all modifications to table. 
            # (https://www.postgresql.org/docs/9.4/explicit-locking.html)
            c.execute(SQL('LOCK TABLE ONLY {} IN EXCLUSIVE MODE').format(storage.collections_table))
            # Update version number in the table
            sql = SQL('UPDATE {} SET version = {} WHERE collection = {}')
            c.execute(sql.format(storage.collections_table, Literal(new_version), Literal(collection_name)))
        except Exception as updating_error:
            storage.conn.rollback()
            raise pg.PgStorageException(('(!) Cannot update version of the collection {!r} '+\
                                         'due to an exception: {}').format( \
                                            collection_name, updating_error)) from updating_error
        finally:
            if storage.conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                storage.conn.commit()
                logger.debug(c.query.decode())
                logger.info(f'updated collection {collection_name!r} version to {new_version} (finalized update)')


def update_structure( storage: 'PostgresStorage', collection_name: str, new_version: str ):
    '''Updates structure of the given collection to the new version in the database. 
       Note: if the given collection has been loaded in the PostgresStorage, you should 
       close the PostgresStorage after the update and create a new PostgresStorage and 
       load the collection again for the update to take effect. 
       Otherwise, calling storage.refresh() ( StorageCollections.load() ) will raise 
       AssertionError.
    '''
    assert isinstance(new_version, str)
    assert isinstance(collection_name, str)
    if collection_name not in storage.collections:
        raise pg.PgCollectionException(f'(!) Cannot update collection {collection_name!r}: no such collection.')
    collection_version = storage._collections.collections[collection_name]['version']
    if collection_version == new_version:
        warn(f'(!) collection {collection_name!r} already has version {new_version}, nothing to update.')
    elif collection_version > new_version:
        warn(f'(!) collection {collection_name!r} has version {collection_version}, cannot downgrade to {new_version}.')
    else:
        if collection_version == '2.0' and new_version == '4.0':
            # Rewrite structure table: add columns 'span_names', 'sparse', 'layer_template'
            _update_layer_info_table(storage, collection_name, new_version)
            # Rewrite collection table: add column 'hidden'
            _update_collection_table(storage, collection_name, new_version)
            # Finally, update collection's version in the __collections table
            _update_collection_version(storage, collection_name, new_version)
        elif collection_version == '3.0' and new_version == '4.0':
            # Rewrite structure table: add column 'span_names'
            _update_layer_info_table(storage, collection_name, new_version)
            # Rewrite collection table: add column 'hidden'
            _update_collection_table(storage, collection_name, new_version)
            # Finally, update collection's version in the __collections table
            _update_collection_version(storage, collection_name, new_version)
        else:
            raise NotImplementedError(f'(!) Updating structure from {collection_version} to {new_version} is not implemented.')

