from psycopg2.sql import SQL, Literal

from estnltk import logger
from estnltk.storage import postgres as pg


class StorageCollections:
    '''
    `StorageCollections` wraps the table of collections of the storage.
    It allows creating the table, inserting new entries to the table, 
    removing entries from the table and deleting the table.
    Index operator can be used to set and retrieve `PgCollection` objects
    by collection names.

    Note: This class maintains collection names, versions and corresponding
    `PgCollection` objects, but does not create `PgCollection` objects.
    A lazy loading is used for `PgCollection` objects, meaning that objects
    are created by `PostgresStorage` only on user demand.
    '''
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
        self._storage.conn.commit()

    def __setitem__(self, collection_name: str, collection: pg.PgCollection):
        assert collection.name == collection_name
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

    def insert(self, collection: pg.PgCollection):
        with self._storage.conn.cursor() as c:
            c.execute(SQL(
                    "INSERT INTO {} (collection, version) "
                    "VALUES ({}, {});").format(
                    self._table_identifier,
                    Literal(collection.name),
                    Literal(collection.version)
            )
            )
        self._storage.conn.commit()
        # Update entries
        self.load()

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
                        # Collection has been loaded already, check the version.
                        assert self._collections[collection]['version'] == version
                        collections[collection] = self._collections[collection]
                    else:
                        # Initialize an unloaded collection. It will be loaded
                        # if user calls storage[collection]
                        collections[collection] = {'version': version,
                                                   'collection_object': None}
        else:
            self.create_table()
        self._collections = collections

    def drop_table(self):
        pg.drop_table(self._storage, '__collections')
