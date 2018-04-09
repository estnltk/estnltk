from estnltk.layer import AttributeList


class AmbiguousAttributeList(AttributeList):
    def __init__(self, amb_attr_list: list):
        amb_attr_list = [AttributeList(t) for t in amb_attr_list]
        super().__init__(amb_attr_list)
