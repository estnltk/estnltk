import pandas

from estnltk.layer.immutable_list import ImmutableList


class AmbiguousAttributeTupleList:
    def __init__(self, amb_attr_tuple_list, attribute_names):

        self.amb_attr_tuple_list = ImmutableList(ImmutableList(ImmutableList(v) for v in value_tuples)
                                                 for value_tuples in amb_attr_tuple_list)
        self.attribute_names = tuple(attribute_names)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AmbiguousAttributeTupleList(self.amb_attr_tuple_list[item], self.attribute_names)
        return self.amb_attr_tuple_list[item]

    def __len__(self):
        return len(self.amb_attr_tuple_list)

    def __eq__(self, other):
        if isinstance(other, AmbiguousAttributeTupleList):
            return self.attribute_names == other.attribute_names and \
                   self.amb_attr_tuple_list == other.amb_attr_tuple_list
        return False

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, list(self), self.attribute_names)

    def __str__(self):
        return str(list(self))

    def to_html(self, index=True):
        if index is True:
            columns = ['']
            columns.extend(self.attribute_names)
        else:
            columns = self.attribute_names
        records = []
        for i, value_tuples in enumerate(self.amb_attr_tuple_list):
            first = True
            for value_tuple in value_tuples:
                record = {k: str(v) for k, v in zip(self.attribute_names, value_tuple)}
                if index is True:
                    record[''] = i if first else ''
                elif isinstance(index, str) and not first:
                    record[index] = ''
                records.append(record)
                first = False
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records(records, columns=columns)
        return df.to_html(index=False, escape=False)

    def _repr_html_(self):
        return '\n'.join(('<h4>' + self.__class__.__name__ + '</h4>',
                          self.to_html()))
