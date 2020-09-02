import json
from psycopg2.sql import SQL, Identifier, Literal

from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres.queries.query import Query


class MissingLayerQuery(Query):
    """Constructs database query to search `text` objects with provided key.

    """
    __slots__ = ['missing_layer']

    def __init__(self, missing_layer, ambiguous=True):
        self.missing_layer = missing_layer

    def eval(self, storage, collection_name):
        table = layer_table_identifier(storage, collection_name, self.missing_layer)
        pat = SQL('"id" NOT IN (SELECT "text_id" FROM {table})').format(
            table=table
            )
        return pat
