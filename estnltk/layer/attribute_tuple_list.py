from estnltk.layer import AmbiguousAttributeTupleList


class AttributeTupleList(AmbiguousAttributeTupleList):
    def __init__(self, tuple_list: list, attribute_names):
        amb_attr_tuple_list = [[values] for values in tuple_list]
        super().__init__(amb_attr_tuple_list, attribute_names)

    def __eq__(self, other):
        if isinstance(other, AttributeTupleList):
            return super().__eq__(other)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AttributeTupleList([a[0] for a in self.amb_attr_tuple_list[item]], self.attribute_names)
        return self.amb_attr_tuple_list[item][0]
