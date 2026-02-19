from psycopg2.sql import SQL
from typing import Set

"""
The module provides tools to compose boolean queries.

Supports nested disjunctive ("|") and conjunction ("&") queries, e.g.

    q = ( SimpleQuery(city='Bristol') | SimpleQuery(city='London') ) & SimpleQuery(country='UK')

Client code is expected to subclass a base query class `Query` and implement `eval` method.
See `SimpleQuery` for example.
"""


class Node:
    """Base class for operations and leaf nodes"""

    def __and__(self, other):
        """And operation with "&" operator"""
        return And(self, other)

    def __or__(self, other):
        """Or operation with "|" operator"""
        return Or(self, other)

    def eval(self, collection: 'PgCollection'):
        """Operations and leaf nodes should implement it"""
        raise NotImplemented()


class BinaryOperation(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right


class And(BinaryOperation):
    def eval(self, collection: 'PgCollection'):
        return SQL("({} AND {})").format(self.left.eval(collection),
                                         self.right.eval(collection))
    @property
    def required_layers(self) -> Set[str]:
        return (self.left.required_layers).union( self.right.required_layers )

    @property
    def required_layer_ngram_indexes(self) -> Set[str]:
        return (self.left.required_layer_ngram_indexes).union( self.right.required_layer_ngram_indexes )

class Or(BinaryOperation):
    def eval(self, collection: 'PgCollection'):
        return SQL("({} OR {})").format(self.left.eval(collection),
                                        self.right.eval(collection))
    @property
    def required_layers(self) -> Set[str]:
        return (self.left.required_layers).union( self.right.required_layers )

    @property
    def required_layer_ngram_indexes(self) -> Set[str]:
        return (self.left.required_layer_ngram_indexes).union( self.right.required_layer_ngram_indexes )

class Query(Node):
    def eval(self, collection: 'PgCollection'):
        """Returns string representation of a (leaf) node"""
        raise NotImplemented()

    @property
    def required_layers(self) -> Set[str]:
        """Returns list of detached collection layers used in query"""
        raise NotImplemented()

    @property
    def required_layer_ngram_indexes(self) -> Set[str]:
        """Returns list of layers whose ngram indexes are used in query"""
        # TODO: find a way to merge required_layers & required_layer_ngram_indexes
        return set()


# TODO: test or remove
class SimpleQuery(Query):
    """Example implementation of `Query`.
        >>> SimpleQuery(city='London', country='UK').eval()
        >>> "city='London' AND country='UK'"
    """

    def _init__(self, **kwargs):
        self.kwargs = kwargs

    def eval(self, collection: 'PgCollection'):
        return SQL(' AND '.join("%s = '%s'" % (k, v) for k, v in self.kwargs.items()))