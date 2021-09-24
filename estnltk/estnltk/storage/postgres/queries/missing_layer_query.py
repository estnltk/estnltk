from typing import Set

from psycopg2.sql import SQL, Identifier

from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import collection_table_identifier
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
        collection_identifier = collection_table_identifier(collection.storage, collection.name)
        table = layer_table_identifier(storage, collection_name, self.missing_layer)
        # Note: the previous solution ( WHERE id NOT IN get_all_ids_from_missing_layer_table ) was terribly slow 
        #       on large tables. Credits for the optimization hint go to: https://stackoverflow.com/a/16996103 
        pat = SQL('NOT EXISTS (SELECT 1 FROM {table} WHERE {collection_identifier}."id" = {table}."text_id" LIMIT 1)').format(
            collection_identifier = collection_identifier,
            table=table
        )
        return pat

    @property
    def required_layers(self) -> Set[str]:
        # No detached layers are joined with the collection
        return set()
