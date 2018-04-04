# immutable lists for attribute value representation


class AttrList:
    def __init__(self, attr_list: list):
        self._list = attr_list

    def __getitem__(self, item):
        return self._list[item]

    def __repr__(self):
        return repr(self._list)

    def __str__(self):
        return str(self._list)


class AmbiguousAttrList(AttrList):
    def __init__(self, amb_attr_list: list):
        amb_attr_list = [AttrList(t) for t in amb_attr_list]
        super().__init__(amb_attr_list)


class AttrTupleList(AttrList):
    def __init__(self, tuple_list: list):
        tuple_list = [tuple(t) for t in tuple_list]
        super().__init__(tuple_list)


class AmbiguousAttrTupleList(AttrList):
    def __init__(self, amb_attr_tuple_list: list):
        amb_attr_tuple_list = [AttrTupleList(t) for t in amb_attr_tuple_list]
        super().__init__(amb_attr_tuple_list)


al = AttrList([1,2,3,4])
print(al)

aal = AmbiguousAttrList([[1,2], [3,4], [5]])
print(aal)

atl = AttrTupleList([[1,2,3], [4,5,6], [7,8,9]])
print(atl)

aatl = AmbiguousAttrTupleList([[[1,2], [3,4]], [[5,6], [7,8], [9,10]], [[11,12]]])
print(aatl, aatl[0][0][0])
