import psycopg2
from psycopg2.sql import SQL, Literal

from estnltk import logger
from estnltk.storage import postgres as pg


class StorageCollections:
    def __init__(self, storage):
        self._storage = storage
        self._table_identifier = pg.table_identifier(self._storage, '__collections')
        self._collections = {}
        self.load()

    @property
    def collections(self):
        return self._collections

    def create_table(self):
        temporary = SQL('TEMPORARY') if self._storage.temporary else SQL('')
        with self._storage.conn.cursor() as c:
            c.execute(SQL('CREATE {temporary} TABLE {table} ('
                          'collection text primary key, '
                          'version text);').format(temporary=temporary,
                                                            table=self._table_identifier))
            logger.debug(c.query.decode())

    def __setitem__(self, collection_name: str, collection: pg.PgCollection):
        assert collection.name == collection_name
        self.load()
        if not collection_name in self._collections:
            try:
                self.insert(collection_name, collection.version)
            except psycopg2.IntegrityError:
                self.load()
        if collection_name in self._collections and self._collections[collection_name]['collection_object'] is not None:
            raise NotImplementedError('re-adding a collection not implemented: ' + collection_name)
        self._collections[collection_name] = {'version': collection.version,
                                              'collection_object': collection}

    def __getitem__(self, collection_name: str):
        return self._collections[collection_name]['collection_object']

    def get(self, collection_name):
        if collection_name in self._collections:
            return self._collections[collection_name]['collection_object']

    def __contains__(self, item: str):
        return item in self.collections

    def __iter__(self):
        yield from self._collections

    def insert(self, collection: str, version: str):
        with self._storage.conn.cursor() as c:
            c.execute(SQL(
                    "INSERT INTO {} (collection, version) "
                    "VALUES ({}, {});").format(
                    self._table_identifier,
                    Literal(collection),
                    Literal(version)
            )
            )
        self._storage.conn.commit()

    def __delitem__(self, collection_name: str):
        with self._storage.conn.cursor() as c:
            c.execute(SQL("DELETE FROM {} WHERE collection={};").format(
                self._table_identifier,
                Literal(collection_name)
            )
            )
            logger.debug(c.query.decode())
        self._storage.conn.commit()

        del self._collections[collection_name]

    def load(self):
        collections = {}
        if pg.table_exists(self._storage, '__collections'):
            with self._storage.conn.cursor() as c:
                c.execute(SQL("SELECT collection, version FROM {};").
                          format(self._table_identifier))
                for collection, version in c.fetchall():
                    if collection in self._collections:
                        assert self._collections[collection]['version'] == version
                        collections[collection] = self._collections[collection]
                    else:
                        collections[collection] = {'version': version,
                                                   'collection_object': None}
        else:
            self.create_table()

        tables = pg.get_all_tables(self._storage)
        for table in tables:
            if table not in collections and table + '__structure' in tables:
                collections[table] = {'version': 'unknown',
                                      'collection_object': None}
                self.insert(table, 'unknown')

        self._collections = collections

    def drop_table(self):
        pg.drop_table(self._storage, '__collections')
