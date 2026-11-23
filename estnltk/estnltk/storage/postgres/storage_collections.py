import warnings

from psycopg2.sql import SQL, Literal

from estnltk import logger
from estnltk.storage import postgres as pg

from estnltk.storage.postgres.pg_operations import TABLE_RELKINDS
from estnltk.storage.postgres.pg_operations import VIEW_RELKINDS

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
    
    TODO: logic of this class can be moved into `PostgresStorage`.
    this class is subject to removal in the next version
    '''
    def __init__(self, storage):
        self._storage = storage
        self.collections = {}

    def __setitem__(self, collection_name: str, collection: pg.PgCollection):
        assert collection.name == collection_name
        self.load()
        if collection_name in self.collections and self.collections[collection_name]['collection_object'] is not None:
            raise NotImplementedError("a collection {!r} cannot be added twice to the storage".format(collection_name))
        self.collections[collection_name] = {'version': collection.version,
                                             'collection_object': collection}

    def __getitem__(self, collection_name: str):
        return self.collections[collection_name]['collection_object']

    def get(self, collection_name):
        error_msg = '(!) Method storage_collections.get(...) is deprecated. '+\
                    'Please use storage_collections[collection_name] instead.'
        raise Exception( error_msg )

    def __contains__(self, item: str):
        return item in self.collections

    def __iter__(self):
        yield from self.collections

    def load(self, omit_commit: bool=False, omit_rollback: bool=False):
        new_collections = {}
        # Check for the existence of the storage_collections table
        # It can be a table or a view
        any_kind = TABLE_RELKINDS + VIEW_RELKINDS
        if not pg.table_exists(self._storage, '__collections', \
                               omit_commit=omit_commit, \
                               omit_rollback=omit_rollback, \
                               relkinds=any_kind):
            raise Exception("(!) Collections table {!r} does not exist!".format(str(self._storage.collections_table)))
        with self._storage.conn.cursor() as c:
            c.execute(SQL("SELECT collection, version FROM {};").
                      format(self._storage.collections_table))
            for collection, version in c.fetchall():
                if collection in self.collections:
                    # Collection has been loaded already, check the version.
                    assert self.collections[collection]['version'] == version
                    new_collections[collection] = self.collections[collection]
                else:
                    # Initialize an unloaded collection. It will be loaded
                    # if user calls storage[collection]
                    new_collections[collection] = {'version': version,
                                                   'collection_object': None}
        if not omit_commit:
            # make a commit to avoid 'idle in transaction' status
            self._storage.conn.commit()
        self.collections = new_collections
