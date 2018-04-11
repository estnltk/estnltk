from estnltk.layer import AmbiguousAttributeTupleList


class AttributeList(AmbiguousAttributeTupleList):
    """Immutable lists for representing single attribute value of unambiguous layer."""
    def __init__(self, attr_list: list, attr_name):
        amb_attr_tuple_list = [[[v]] for v in attr_list]
        super().__init__(amb_attr_tuple_list, [attr_name])

    def __getitem__(self, item):
        return self.amb_attr_tuple_list[item][0][0]
