import json
from psycopg2.sql import SQL, Identifier, Literal

from estnltk.storage.postgres import collection_table_identifier, layer_table_identifier
from estnltk.storage.postgres.queries.query import Query
from typing import Mapping, Set, Any


def build_column_ngram_query(storage, collection_name, query, column, layer_name):
    if not isinstance(query, list):
        query = list(query)
    if isinstance(query[0], list):
        # case: [[(a),(b)], [(c)]] -> a AND b OR c
        or_terms = [["-".join(e) for e in and_term] for and_term in query]
    elif isinstance(query[0], tuple):
        # case: [(a), (b)] -> a OR b
        or_terms = [["-".join(e)] for e in query]
    elif isinstance(query[0], str):
        # case: [a, b] -> "a-b"
        or_terms = [["-".join(query)]]
    else:
        raise ValueError("Invalid ngram query format: {}".format(query))

    table_identifier = layer_table_identifier(storage, collection_name, layer_name)
    or_parts = []
    for and_term in or_terms:
        arr = ",".join("'%s'" % v for v in and_term)
        p = SQL("{table}.{column} @> ARRAY[%s]" % arr).format(
            table=table_identifier,
            column=Identifier(column))
        or_parts.append(p)
    column_ngram_query = SQL("({})").format(SQL(" OR ").join(or_parts))
    return column_ngram_query


class LayerNgramQuery(Query):
    """Constructs database query to search `text` objects with provided key.

    """
    __slots__ = ['layer_ngram_query', 'kwargs']

    def __init__(self, layer_ngram_query: Mapping[str, Any] = None, ambiguous=True, **kwargs):
        self.layer_ngram_query = layer_ngram_query
        self.kwargs = kwargs

    @property
    def required_layers(self) -> Set[str]:
        return {*self.layer_ngram_query}

    def eval(self, storage, collection_name):
        sql_parts = []

        for layer_name in self.layer_ngram_query:
            for column, q in self.layer_ngram_query[layer_name].items():
                col_query = build_column_ngram_query(storage, collection_name, q, column, layer_name)
                sql_parts.append(col_query)

        q = SQL(" AND ").join(sql_parts)

        return q
