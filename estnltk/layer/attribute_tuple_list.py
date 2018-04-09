from estnltk.layer import AttributeList


class AttributeTupleList(AttributeList):
    def __init__(self, tuple_list: list):
        tuple_list = [tuple(t) for t in tuple_list]
        super().__init__(tuple_list)
