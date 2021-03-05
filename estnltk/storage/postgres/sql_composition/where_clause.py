from psycopg2.sql import Composed, SQL

from estnltk.storage.postgres.queries.query import Query


#logger.setLevel('DEBUG')


class WhereClause(Composed):
    """`WhereClause` class is a sequence of Composed SQL strings following the statement "WHERE" in an SQL query,
    indicating what is being queried from the database.

    The main usecase for the class is as a selection criterion for selecting data from a collection.

    """

    def __init__(self,
                 collection,
                 query: Query = None,
                 seq=None,
                 required_layers=None):
        self.collection = collection

        # WhereClause is specified by SQL fragment
        if seq is not None:
            assert query is None, "SQL sequence and query can not be set simultaneously"
            self._required_layers = sorted(set(required_layers or ()))
            super().__init__(seq)
            return

        # No restrictions are placed, empty WhereClause
        if query is None:
            self._required_layers = sorted(set(required_layers or ()))
            super().__init__([])
            return

        self._required_layers = query.required_layers

        super().__init__(self.where_clause(collection, query=query))

    def __bool__(self):
        return bool(self.seq)

    def _non_attached_required_layers(self):
        """Returns self._required_layers without attached layers."""
        return [layer for layer in self._required_layers if self.collection.structure[layer]['layer_type'] != 'attached']

    @property
    def required_layers(self):
        return self._non_attached_required_layers()

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
    def where_clause(collection, query: Query = None):
        """

        :param layer_ngram_query:
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

        if query is not None:
            # build constraint on the main text table
            q = query.eval( collection )
            sql_parts.append(q)
        if sql_parts:
            return SQL(" AND ").join(sql_parts)
        return []
