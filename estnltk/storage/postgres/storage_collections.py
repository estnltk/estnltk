from psycopg2.sql import SQL, Literal

from estnltk.logger import logger
from estnltk.storage import postgres as pg


class StorageCollections:
    def __init__(self, storage):
        self._storage = storage
        self._modified = True
        self._table_identifier = pg.table_identifier(self._storage, '__collections')
        self._collections = self.load()

    @property
    def collections(self):
        if self._modified:
            self._collections = self.load()
            self._modified = False
        return self._collections

    def create_table(self):
        temporary = SQL('TEMPORARY') if self._storage.temporary else SQL('')
        with self._storage.conn.cursor() as c:
            c.execute(SQL('CREATE {temporary} TABLE {table} ('
                          'collection text primary key, '
                          'structure_version text);').format(temporary=temporary,
                                                            table=self._table_identifier))
            logger.debug(c.query.decode())

    def __setitem__(self, collection_name: str, collection: pg.PgCollection):
        if collection_name not in self._collections:
            self._collections[collection_name] = {'structure_version': collection.structure_version,
                                                  'collection_object': collection}
            self.insert(collection_name, collection.structure_version)
        self._collections[collection_name]['collection_object'] = collection

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
        self._modified = True
        with self._storage.conn.cursor() as c:
            c.execute(SQL(
                    "INSERT INTO {} (collection, structure_version) "
                    "VALUES ({}, {});").format(
                    self._table_identifier,
                    Literal(collection),
                    Literal(version)
            )
            )

    def __delitem__(self, collection_name: str):
        self._modified = True
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
        if pg.table_exists(self._storage, '__collections'):
            with self._storage.conn.cursor() as c:
                c.execute(SQL("SELECT collection, structure_version FROM {};").
                          format(self._table_identifier))
                collections = {row[0]: {'structure_version': row[1],
                                        'collection_object': None} for row in c.fetchall()}
        else:
            tables = pg.get_all_tables(self._storage)
            collections = {table: {'structure_version': '0.0',
                                   'collection_object': None} for table in tables if table + '__structure' in tables}
            self.create_table()
            for collection, data in collections.items():
                self.insert(collection, data['structure_version'])

        return collections

    def drop_table(self):
        pg.drop_table(self._storage, '__collections')
