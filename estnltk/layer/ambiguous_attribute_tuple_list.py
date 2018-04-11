import pandas

from .immutable_list import ImmutableList


class AmbiguousAttributeTupleList:
    def __init__(self, amb_attr_tuple_list: list, attribute_names):

        self._list = amb_attr_tuple_list

        self.amb_attr_tuple_list = ImmutableList(ImmutableList(ImmutableList(v) for v in value_tuples)
                                                 for value_tuples in amb_attr_tuple_list)
        self.attribute_names = attribute_names

    def __getitem__(self, item):
        return self.amb_attr_tuple_list[item]

    def _repr_html_(self):
        records = []
        for i, value_tuples in enumerate(self.amb_attr_tuple_list):
            first = True
            for value_tuple in value_tuples:
                record = {'index': i if first else '',
                          **{k:v for k,v in zip(self.attribute_names, value_tuple)}}
                records.append(record)
                first = False
        df = pandas.DataFrame.from_records(records, columns=['index', *self.attribute_names])
        pandas.set_option('display.max_colwidth', -1)
        table = df.to_html(index=False, escape=False)
        return '\n'.join(('<h4>' + self.__class__.__name__ + '</h4>', table))
