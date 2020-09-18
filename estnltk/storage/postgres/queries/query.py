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

    def eval(self, storage, collection_name):
        """Operations and leaf nodes should implement it"""
        raise NotImplemented()


class BinaryOperation(Node):
    def __init__(self, left, right):
        self.left, self.right = left, right


class And(BinaryOperation):
    def eval(self, storage, collection_name):
        return SQL("({} AND {})").format(self.left.eval(storage, collection_name),
                                         self.right.eval(storage, collection_name))


class Or(BinaryOperation):
    def eval(self, storage, collection_name):
        return SQL("({} OR {})").format(self.left.eval(storage, collection_name),
                                        self.right.eval(storage, collection_name))


class Query(Node):
    def eval(self, storage, collection_name):
        """Returns string representation of a (leaf) node"""
        raise NotImplemented()

    @property
    def required_layers(self) -> Set[str]:
        """Returns list of detached collection layers used in query"""
        raise NotImplemented()


# TODO: test or remove
class SimpleQuery(Query):
    """Example implementation of `Query`.

        >>> SimpleQuery(city='London', country='UK').eval()
        >>> "city='London' AND country='UK'"

    """

    def _init__(self, **kwargs):
        self.kwargs = kwargs

    def eval(self, storage, collection_name):
        return SQL(' AND '.join("%s = '%s'" % (k, v) for k, v in self.kwargs.items()))
