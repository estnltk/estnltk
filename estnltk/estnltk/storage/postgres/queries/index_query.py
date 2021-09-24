from psycopg2.sql import SQL, Literal
from typing import Union, List, Set

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query


class IndexQuery(Query):
    """
    Selects text objects corresponding to the index list.
    """

    __slots__ = ['_keys']

    def __init__(self, keys: Union[int, List[int]]):
        self._keys = keys

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, collection: 'PgCollection'):
        collection_name = collection.name
        storage = collection.storage
        table = collection_table_identifier(storage, collection_name)
        if isinstance(self._keys, int):
            return SQL('{table}.id = {key}').format(table=table, key=Literal(self._keys))
        else:
            return SQL('{table}."id" = ANY({keys})').format(table=table, keys=Literal(list(self._keys)))
