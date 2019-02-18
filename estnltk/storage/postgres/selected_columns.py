from itertools import chain
from psycopg2.sql import Composed, Identifier, SQL

from estnltk.storage import postgres as pg


class SelectedColumns(Composed):
    def __init__(self,
                 storage,
                 collection_name,
                 layer_query: dict = None,
                 layer_ngram_query: dict = None,
                 layers: list = None,
                 collection_meta: list = None):

        select_and_join, where_and = self.select_and_join_clause(storage,
                                                                 collection_name,
                                                                 layer_query=layer_query,
                                                                 layer_ngram_query=layer_ngram_query,
                                                                 layers=layers,
                                                                 collection_meta=collection_meta)
        self.where_and = where_and

        super().__init__(select_and_join)

    def __add__(self, other):
        if isinstance(other, pg.WhereClause):
            if other:
                return SQL(' ').join([self, self.where_and, other])
            return self
        raise NotImplementedError()

    @staticmethod
    def select_and_join_clause(storage,
                               collection_name,
                               layer_query: dict = None,
                               layer_ngram_query: dict = None,
                               layers: list = None,
                               collection_meta: list = None):

        collection_identifier = pg.collection_table_identifier(storage, collection_name)

        # selected_columns(collection_meta, collection_identifier, layers)
        collection_meta = collection_meta or []

        selected_columns = [SQL('{}.{}').format(collection_identifier, column_id) for
                            column_id in map(Identifier, ['id', 'data', *collection_meta])]
        # col.id, col.data, col.meta_*

        # list columns of selected layers
        layers = layers or []
        for layer in chain(layers):
            selected_columns.append(SQL('{}."id"').format(pg.layer_table_identifier(storage, collection_name, layer)))
            selected_columns.append(SQL('{}."data"').format(pg.layer_table_identifier(storage, collection_name, layer)))
        # col__layer1__layer.id, col__layer1__layer.data, ...

        # no restrictions to the collection
        if not layers and layer_query is None and layer_ngram_query is None:
            # select only text table
            select = SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns), collection_identifier)
            where_and = SQL('WHERE')
            return select, where_and

        # we have restrictions and must join tables to meet them
        # need to join text and all layer tables
        # selected_layer_tables(...)
        layer_query = layer_query or {}
        layer_ngram_query = layer_ngram_query or {}

        # selected_tables(layers, layer_query, ngram_query)
        # find all layers needed for the where clause
        selected_layers = []
        for layer in sorted(set(chain(layers, layer_query.keys(), layer_ngram_query.keys()))):
            layer = SQL("{}").format(pg.layer_table_identifier(storage, collection_name, layer))
            selected_layers.append(layer)
        # col__layer1_layer, col_layer2_layer

        # join_clause(collection_identifier, selected_layers)
        join_condition = SQL(" AND ").join(SQL('{}."id" = {}."text_id"').format(
                collection_identifier, layer)
                                           for layer in selected_layers)

        # selected_tables_clause()
        selected_tables = [collection_identifier, *selected_layers]
        select = SQL('SELECT {columns} FROM {tables} WHERE {join_condition}').format(
                columns=SQL(', ').join(selected_columns),
                tables=SQL(", ").join(selected_tables),
                join_condition=join_condition)
        where_and = SQL('AND')

        return select, where_and
