from psycopg2.sql import Composed, Literal, SQL

from estnltk.storage import postgres as pg
from estnltk.storage.postgres.queries.query import Query


class WhereClause(Composed):
    """`WhereClause` class is a sequence of Composed SQL strings following the statement "WHERE" in an SQL query,
    indicating what is being queried from the database.

    The main usecase for the class is as a selection criterion for selecting data from a collection.

    """
    def __init__(self,
                 collection,
                 query=None,
                 layer_query: dict = None,
                 # layer_ngram_query: dict = None,
                 # keys: list = None,
                 # missing_layer: str = None,
                 seq=None,
                 required_layers=None):
        self.collection = collection

        if seq is None:
            seq = self.where_clause(collection,
                                    query=query,
                                    layer_query=layer_query)
            # layer_ngram_query=layer_ngram_query
            # keys=keys,
            # missing_layer=missing_layer



        # We omit layers inside a Text object.
        if required_layers is None:
            self._required_layers = sorted(set(layer_query or ()))
        else:
            self._required_layers = required_layers

        # Initialization of composed object
        super().__init__(seq)

    def __bool__(self):
        return bool(self.seq)

    @property
    def required_layers(self):
        return self._required_layers

    def __and__(self, other):
        if not isinstance(other, WhereClause):
            raise TypeError('unsupported operand type for &: {!r}'.format(type(other)))
        if self.collection is not other.collection:
            raise ValueError("can't combine WhereClauses with different collections: {!r} and {!r}".format(
                self.collection.name, other.collection.name))

        if not other:
            return self
        if not self:
            return other

        seq = SQL(" AND ").join((self, other))
        required_layers = sorted(set(self.required_layers) | set(other.required_layers))
        return WhereClause(collection=self.collection, seq=seq, required_layers=required_layers)

    @staticmethod
    def where_clause(collection,
                     query: Query = None,
                     layer_query: dict = None
                     # layer_ngram_query: dict = None
                     # keys: list = None,
                     # missing_layer: str = None
                     ):
        """

        :param collection:
            instance of the EstNLTK PostgreSQL collection
        :param query:
            composed SQL query
        :param layer_query:
            composed SQL query to search 'layer' objects
        :return:
            composed SQL query following "WHERE" statement based on queries given as parameters, joined by AND operator
        """
        sql_parts = []
        collection_name = collection.name
        storage = collection.storage

        if query is not None:
            # build constraint on the main text table
            q = query.eval(storage, collection_name)
            sql_parts.append(q)
        if layer_query:
            # build constraint on related layer tables
            q = SQL(" AND ").join(query.eval(storage, collection_name) for query in layer_query)
            sql_parts.append(q)

        if sql_parts:
            return SQL(" AND ").join(sql_parts)
        return []
