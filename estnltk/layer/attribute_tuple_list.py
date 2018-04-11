from estnltk.layer import AmbiguousAttributeTupleList


class AttributeTupleList(AmbiguousAttributeTupleList):
    def __init__(self, tuple_list: list, attribute_names):
        amb_attr_tuple_list = [[values] for values in tuple_list]
        super().__init__(amb_attr_tuple_list, attribute_names)

    def __getitem__(self, item):
        return self.amb_attr_tuple_list[item][0]
