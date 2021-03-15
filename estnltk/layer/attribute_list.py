from typing import Iterable
from estnltk.layer import AmbiguousAttributeTupleList


class AttributeList(AmbiguousAttributeTupleList):
    """Immutable lists for representing single attribute value of unambiguous layer."""
    def __init__(self, attr_list: Iterable, attr_name):
        amb_attr_tuple_list = [[[v]] for v in attr_list]
        super().__init__(amb_attr_tuple_list, [attr_name])

    def __eq__(self, other):
        if isinstance(other, AttributeList):
            return super().__eq__(other)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AttributeList([a[0][0] for a in self.amb_attr_tuple_list[item]], self.attribute_names[0])
        return self.amb_attr_tuple_list[item][0][0]
