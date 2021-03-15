from estnltk.layer import AmbiguousAttributeTupleList
from estnltk.layer.immutable_list import ImmutableList


class AmbiguousAttributeList(AmbiguousAttributeTupleList):
    def __init__(self, amb_attr_list, attribute_name):
        amb_attr_tuple_list = [[[v] for v in value] for value in amb_attr_list]
        super().__init__(amb_attr_tuple_list, [attribute_name])

    def __eq__(self, other):
        if isinstance(other, AmbiguousAttributeList):
            return super().__eq__(other)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AmbiguousAttributeList([[v[0] for v in t] for t in self.amb_attr_tuple_list[item]],
                                          self.attribute_names)
        return ImmutableList([v[0] for v in self.amb_attr_tuple_list[item]])
