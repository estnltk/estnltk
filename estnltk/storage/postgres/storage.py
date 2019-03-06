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
        return sorted(self._collections)

    def __getitem__(self, item):
        self._load()
        collection = self._collections.get(item)
        if collection is not None:
            return collection
        collection = PgCollection(item, self, version='1.0')
        self._collections[item] = collection
        return collection

    def __delitem__(self, collection_name: str):
        if collection_name not in self.collections:
            raise KeyError('collection not found: {!r}'.format(collection_name))

        for layer, v in self[collection_name].structure.structure.items():
            if v['layer_type'] == 'detached':
                drop_layer_table(self, collection_name, layer)
        pg.drop_structure_table(self, collection_name)
        pg.drop_collection_table(self, collection_name)

        del self._collections[collection_name]

    def __str__(self):
        return '{self.__class__.__name__}({self.conn.dsn} schema={self.schema} temporary={self.temporary})'.format(
                self=self)

    def _repr_html_(self):
        self._load()
        tables = pg.get_all_tables(self)

        structure = {}

        collection_tables = ''
        if tables is not None:
            for t, v in tables.items():
                t_split = t.split('__')
                if len(t_split) == 1 and t_split[0] + '__structure' in tables:
                    structure[(t_split[0], '')] = v
                elif len(t_split) == 3 and t_split[2] == 'layer' and t_split[0] in tables:
                    structure[(t_split[0], t_split[1])] = v

            if structure:
                df = pandas.DataFrame.from_dict(structure, orient='index', columns=['total_size', 'comment'])
                df.index.names = ('collection', 'layers')
                collection_tables = df.to_html()
            else:
                collection_tables = '<br/>This storage has no collections.'
        return ('<b>{self.__class__.__name__}</b><br/>\n{self.conn.dsn} schema={self.schema}<br/>'
                'temporary={self.temporary}\n'
                '{collections}').format(
                self=self, collections=collection_tables)
