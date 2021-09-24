import pandas
import html
import regex as re

from estnltk.layer.immutable_list import ImmutableList


def to_str(value, escape_html=False):
    if isinstance(value, str):
        value_str = value
    elif callable(value) and hasattr(value, '__name__') and hasattr(value, '__module__'):
        value_str = '<function {}.{}>'.format(value.__module__, value.__name__)
    elif isinstance(value, re.regex.Pattern):
        value_str = '<Regex {}>'.format(value.pattern)
    elif isinstance(value, tuple):
        value_str = str(tuple(to_str(v) for v in value))
    else:
        value_str = str(value)

    if len(value_str) >= 100:
        value_str = value_str[:80] + ' ..., type: ' + str(type(value))
        if hasattr(value, '__len__'):
            value_str += ', length: ' + str(len(value))

    if escape_html:
        value_str = html.escape(value_str)
    return value_str


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
                record = {k: to_str(v) for k, v in zip(self.attribute_names, value_tuple)}
                if index is True:
                    record[''] = i if first else ''
                elif isinstance(index, str) and not first:
                    record[index] = ''
                records.append(record)
                first = False
        df = pandas.DataFrame.from_records(records, columns=columns)
        return df.to_html(index=False, escape=True)

    def _repr_html_(self):
        return '\n'.join(('<h4>' + self.__class__.__name__ + '</h4>',
                          self.to_html()))
