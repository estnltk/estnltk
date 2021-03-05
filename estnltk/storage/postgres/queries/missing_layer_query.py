from typing import Set

from psycopg2.sql import SQL, Identifier

from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres.queries.query import Query


class MissingLayerQuery(Query):
    """Constructs database query to search `text` objects with provided key.

    """
    __slots__ = ['missing_layer']

    def __init__(self, missing_layer, ambiguous=True):
        self.missing_layer = missing_layer

    def eval(self, collection: 'PgCollection'):
        collection_name = collection.name
        storage = collection.storage
        table = layer_table_identifier(storage, collection_name, self.missing_layer)
        pat = SQL('{collection_name}."id" NOT IN (SELECT "text_id" FROM {table})').format(
            collection_name = Identifier(collection_name),
            table=table
            )
        return pat

    @property
    def required_layers(self) -> Set[str]:
        # No detached layers are joined with the collection
        return set()
