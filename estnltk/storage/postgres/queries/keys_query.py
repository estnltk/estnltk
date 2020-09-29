import json
from psycopg2.sql import SQL, Identifier, Literal
from typing import Set

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query


class KeysQuery(Query):
    """Constructs database query to search `text` objects with provided key.

    """
    __slots__ = ['keys', 'kwargs']

    def __init__(self, keys, ambiguous=True, **kwargs):
        self.keys = keys
        self.kwargs = kwargs

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, storage, collection_name):
        table = collection_table_identifier(storage, collection_name)
        pat = SQL('{table}."id" = ANY({keys})').format(
                    table=table,
                    keys=Literal(list(self.keys)),
                    condition=SQL(json.dumps(self.kwargs)))
        return pat
