import warnings

from psycopg2.sql import SQL, Literal

from estnltk import logger
from estnltk.storage import postgres as pg


class StorageCollections:
    '''
    `StorageCollections` wraps the table of collections of the storage.
    It provides read-only view to the entries of the table. 
    Index operator can be used to set and retrieve `PgCollection` objects
    by collection names. 

    Note: This class maintains collection names, versions and corresponding
    `PgCollection` objects, but does not create `PgCollection` objects.
    A lazy loading is used for `PgCollection` objects, meaning that objects
    are created by `PostgresStorage` only on user demand.
    `PostgresStorage` also handles creation of the table of collections, 
    insertion to the table and deletion from the table.
    '''
    def __init__(self, storage):
        self._storage = storage
        self._table_identifier = pg.table_identifier(self._storage, '__collections')
        self._collections = {}

    @property
    def collections(self):
        return self._collections

    @property
    def table_identifier(self):
        return self._table_identifier

    def __setitem__(self, collection_name: str, collection: pg.PgCollection):
        assert collection.name == collection_name
        self.load()
        if collection_name in self._collections and self._collections[collection_name]['collection_object'] is not None:
            raise NotImplementedError("a collection {!r} cannot be added twice to the storage".format(collection_name))
        self._collections[collection_name] = {'version': collection.version,
                                              'collection_object': collection}

    def __getitem__(self, collection_name: str):
        return self._collections[collection_name]['collection_object']

    def get(self, collection_name):
        error_msg = '(!) Method storage_collections.get(...) is deprecated. '+\
                    'Please use storage_collections[collection_name] instead.'
        raise Exception( error_msg )

    def __contains__(self, item: str):
        return item in self.collections

    def __iter__(self):
        yield from self._collections

    def load(self):
        collections = {}
        assert pg.table_exists(self._storage, '__collections')
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
        self._collections = collections
