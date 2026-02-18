from psycopg2.sql import Composed, SQL

from estnltk.storage.postgres import fragment_table_name
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import layer_ngrams_table_name

from estnltk.storage.postgres.queries.query import Query

#logger.setLevel('DEBUG')


class WhereClause(Composed):
    """`WhereClause` class is a sequence of Composed SQL strings following the statement "WHERE" in 
    an SQL query, indicating what is being queried from the database.

    The main usecase for the class is as a selection criterion for selecting data from a collection.

    Note: `required_tables` should only cover names of the auxiliary tables (e.g. detached layer 
    tables) that need to be joined inside the query, excluding collection table name. 
    """

    def __init__(self,
                 collection,
                 query: Query = None,
                 seq=None,
                 required_tables=None):
        self.collection = collection

        # WhereClause is specified by SQL fragment
        if seq is not None:
            assert query is None, "SQL sequence and query can not be set simultaneously"
            self._required_tables = sorted(set(required_tables or ()))
            super().__init__(seq)
            return

        # No restrictions are placed, empty WhereClause
        if query is None:
            self._required_tables = sorted(set(required_tables or ()))
            super().__init__([])
            return

        self._required_tables = \
            WhereClause.get_required_tables_from_query(collection, query)

        super().__init__(self.where_clause(collection, query=query))

    @staticmethod
    def get_required_tables_from_query(collection, query: Query):
        required_tables = []
        if query is not None:
            for layer_name in sorted(set( query.required_layers )):
                layer_type = collection.structure[layer_name]['layer_type']
                if layer_type == 'fragmented': 
                    required_tables.append( fragment_table_name(collection.name, layer_name) )
                elif layer_type == 'detached': 
                    required_tables.append( layer_table_name(collection.name, layer_name) )
            for layer_name in sorted(set( query.required_layer_ngram_indexes )):
                required_tables.append( layer_ngrams_table_name(collection.name, layer_name) )
        return required_tables

    def __bool__(self):
        return bool(self.seq)

    @property
    def required_tables(self):
        return self._required_tables

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
        required_tables = sorted(set(self.required_tables) | set(other.required_tables))
        return WhereClause(collection=self.collection, seq=seq, 
                           required_tables=required_tables)

    @staticmethod
    def where_clause(collection, query: Query = None):
        """
        :param collection:
            instance of the EstNLTK's PostgreSQL collection
        :param query:
            composed SQL query
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
