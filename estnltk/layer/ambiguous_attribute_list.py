from estnltk.layer import AmbiguousAttributeTupleList
from estnltk.layer.immutable_list import ImmutableList


class AmbiguousAttributeList(AmbiguousAttributeTupleList):
    def __init__(self, amb_attr_list: list, attribute_name):
        amb_attr_tuple_list = [[[v] for v in value] for value in amb_attr_list]
        super().__init__(amb_attr_tuple_list, [attribute_name])

    def __getitem__(self, item):
        return ImmutableList([v[0] for v in self.amb_attr_tuple_list[item]])