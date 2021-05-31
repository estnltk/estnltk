import collections
from typing import Mapping, Set, Any

from psycopg2.sql import SQL, Identifier, Literal

from estnltk.storage.postgres import layer_table_identifier, layer_table_name
from estnltk.storage.postgres.queries.query import Query


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
    """Constructs database query to search `text` objects that have specific N-grams in specific layers.
       Note: this query only works on detached layers that have appropriate ngram_index.

       Example. Search ("üks","kaks" AND "kolm","neli") OR "viis","kuus":
       
       collection.select(query=LayerNgramQuery({
            "some_layer": {
                "some_field": [[("üks", "kaks"), ("kolm", "neli")], [("viis", "kuus")]],
       }}))
       
    """
    __slots__ = ['layer_ngram_query', 'kwargs']

    def __init__(self, layer_ngram_query: Mapping[str, Any] = None, ambiguous=True, **kwargs):
        self.layer_ngram_query = layer_ngram_query
        self.kwargs = kwargs

    @property
    def required_layers(self) -> Set[str]:
        return { *self.layer_ngram_query }


    def validate( self, collection: 'PgCollection' ):
        """ Validates that this collection has detached layer table with appropriate ngram columns.
        """
        assert collection is not None
        collection_name = collection.name
        storage = collection.storage
        
        def _fetch_table_column_names( storage, collection_name, layer_name ):
            # Fetches column names for given detached layer
            table_name = layer_table_name( collection_name, layer_name )
            with storage.conn.cursor() as c:
                c.execute(SQL('SELECT column_name, data_type from information_schema.columns '
                              'WHERE table_schema={} and table_name={} '
                              'ORDER BY ordinal_position'
                              ).format(Literal(storage.schema), Literal(table_name)))
                return collections.OrderedDict( c.fetchall() )
        
        for layer_name in self.layer_ngram_query:
            columns = [column for column, _ in self.layer_ngram_query[layer_name].items()]
            existing_columns_dict = _fetch_table_column_names( storage, collection_name, layer_name )
            for c in columns:
                if c not in existing_columns_dict.keys():
                    existing_columns = [k for k in existing_columns_dict.keys()]
                    raise ValueError('(!) The layer {!r} does not contain ngram index column {!r}. Available columns: {!r}'.format(layer_name, c, existing_columns))


    def eval(self, collection: 'PgCollection'):
        # Check that the collection has ngram_index columns
        self.validate( collection )
        # Construct the query
        collection_name = collection.name
        storage = collection.storage
        sql_parts = []

        for layer_name in self.layer_ngram_query:
            for column, q in self.layer_ngram_query[layer_name].items():
                col_query = build_column_ngram_query(storage, collection_name, q, column, layer_name)
                sql_parts.append(col_query)

        q = SQL(" AND ").join(sql_parts)

        return q
