from psycopg2.sql import Composed, Literal, SQL

from estnltk.storage import postgres as pg


class WhereClause(Composed):
    def __init__(self,
                 collection,
                 query=None,
                 layer_query: dict = None,
                 layer_ngram_query: dict = None,
                 keys: list = None,
                 missing_layer: str = None):

        where = self.where_clause(collection,
                                  query=query,
                                  layer_query=layer_query,
                                  layer_ngram_query=layer_ngram_query,
                                  keys=keys,
                                  missing_layer=missing_layer)
        if where:
            super().__init__(where)
        else:
            super().__init__([])

    def __bool__(self):
        return bool(self.seq)

    # TODO
    @property
    def required_tables(self):
        return self.required_layer_tables

    # TODO
    @property
    def required_layer_tables(self):
        return

    @staticmethod
    def where_clause(collection,
                     query=None,
                     layer_query: dict = None,
                     layer_ngram_query: dict = None,
                     keys: list = None,
                     missing_layer: str = None):
        sql_parts = []
        collection_name = collection.name
        storage = collection.storage


        if query is not None:
            # build constraint on the main text table
            sql_parts.append(query.eval(storage, collection_name))
        if layer_query:
            # build constraint on related layer tables
            q = SQL(" AND ").join(query.eval(storage, collection_name) for layer, query in layer_query.items())
            sql_parts.append(q)
        if keys is not None:
            # build constraint on id-s
            sql_parts.append(SQL('{table}."id" = ANY({keys})').format(
                    table=pg.collection_table_identifier(storage, collection_name),
                    keys=Literal(list(keys))))
        if layer_ngram_query:
            # build constraint on related layer's ngram index
            sql_parts.append(pg.build_layer_ngram_query(storage, layer_ngram_query, collection_name))
        if missing_layer:
            # select collection objects for which there is no entry in the layer table
            q = SQL('"id" NOT IN (SELECT "text_id" FROM {})'
                    ).format(pg.layer_table_identifier(storage, collection_name, missing_layer))
            sql_parts.append(q)

        if sql_parts:
            return SQL(" AND ").join(sql_parts)
