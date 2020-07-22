import json
from psycopg2.sql import SQL, Identifier, Literal

from estnltk.storage.postgres import collection_table_identifier, build_layer_ngram_query
from estnltk.storage.postgres.queries.query import Query


class LayerNgramQuery(Query):
    """Constructs database query to search `text` objects with provided key.

    """
    __slots__ = ['layer_ngram_query', 'kwargs']

    def __init__(self, layer_ngram_query, ambiguous=True, **kwargs):
        self.layer_ngram_query = layer_ngram_query
        self.kwargs = kwargs

    def eval(self, storage, collection_name):
        q = build_layer_ngram_query(storage, collection_name, self.layer_ngram_query)

        return q
