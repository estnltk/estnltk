import bisect
import pandas

import psycopg2
from psycopg2.sql import SQL, Identifier

from estnltk import logger
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import parse_pgpass
from estnltk.storage.postgres import drop_layer_table
from estnltk.storage import postgres as pg


class PgStorageException(Exception):
    pass


class PostgresStorage:
    """`PostgresStorage` instance wraps a database connection and
    exposes interface to conveniently search/save json data.
    """

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None,
                 pgpass_file=None, schema="public", role=None, temporary=False, **kwargs):
        """
        Connects to database either using connection parameters if specified, or ~/.pgpass file.

            ~/.pgpass file format: hostname:port:database:username:password

        """
        self.schema = schema
        self.temporary = temporary

        conn_param = parse_pgpass(pgpass_file, host, port, dbname, user, password)

        if role is None:
            role = conn_param['user']

        self.user = conn_param['user']

        logger.info('connecting to host: '
                    '{host!r}, port: {port!r}, dbname: {dbname!r}, user: {user!r}'.format(**conn_param))

        try:
            self.conn = psycopg2.connect(**conn_param, **kwargs)
        except Exception:
            logger.error('Failed to connect '
                         'host: {host!r}, port: {port!r}, dbname: {dbname!r}, user: {user!r}.'.format(**conn_param))
            raise

        with self.conn.cursor() as c:
            c.execute(SQL("SET ROLE {};").format(Identifier(role)))
        self.conn.commit()

        self._collections = None
        self._loaded = False

        logger.info('schema: {!r}, temporary: {!r}, role: {!r}'.format(self.schema, self.temporary, role))

    def _load(self):
        if not self._loaded:
            self._collections = pg.StorageCollections(self)
            self._loaded = True

    def close(self):
        """Closes database connection"""
        self.conn.commit()
        self.conn.close()

    def closed(self):
        return self.conn.closed

    def get_collection(self, table_name: str, meta_fields: dict = None):
        """Returns a new instance of `PgCollection` without physically creating it."""
        collection = self[table_name]
        if meta_fields is not None:
            collection.meta = meta_fields
        return collection

    @property
    def collections(self):
        self._load()
        return sorted(self._collections)

    def __getitem__(self, name: str):
        self._load()
        if name in self._collections:
            collection = self._collections[name]
            if collection is None:
                version = self._collections.collections[name]['version']
                collection = PgCollection(name, self, version=version)
                self._collections[name] = collection
                return collection
            return collection

        collection = PgCollection(name, self, version='3.0')
        self._collections[name] = collection
        return collection

    def delete(self, collection_name: str, cascade=False):
        if collection_name not in self.collections:
            raise KeyError('collection not found: {!r}'.format(collection_name))

        for layer, v in self[collection_name].structure.structure.items():
            if v['layer_type'] == 'detached':
                drop_layer_table(self, collection_name, layer, cascade=cascade)
                # TODO: delete layer from structure immediately
        pg.drop_collection_table(self, collection_name, cascade=cascade)
        pg.drop_structure_table(self, collection_name)

        del self._collections[collection_name]

    def __delitem__(self, collection_name: str):
        if collection_name not in self.collections:
            raise KeyError('collection not found: {!r}'.format(collection_name))

        for layer, v in self[collection_name].structure.structure.items():
            if v['layer_type'] in {'detached', 'fragmented'}:
                drop_layer_table(self, collection_name, layer)
                # TODO: delete layer from structure immediately
        pg.drop_collection_table(self, collection_name)
        pg.drop_structure_table(self, collection_name)

        del self._collections[collection_name]

    def __str__(self):
        return '{self.__class__.__name__}({self.conn.dsn} schema={self.schema} temporary={self.temporary})'.format(
                self=self)

    def _repr_html_(self):
        self._load()
        self._collections.load()

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
