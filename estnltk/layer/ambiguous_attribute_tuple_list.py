from estnltk.layer import AttributeList
from estnltk.layer import AttributeTupleList


class AmbiguousAttributeTupleList(AttributeList):
    def __init__(self, amb_attr_tuple_list: list):
        amb_attr_tuple_list = [AttributeTupleList(t) for t in amb_attr_tuple_list]
        super().__init__(amb_attr_tuple_list)
