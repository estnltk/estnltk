import pandas

from estnltk.layer import AttributeList


class AmbiguousAttributeList(AttributeList):
    def __init__(self, amb_attr_list: list, attribute_name='attribute'):
        amb_attr_list = [AttributeList(t) for t in amb_attr_list]
        super().__init__(amb_attr_list)
        self.attribute_name = attribute_name

    def _repr_html_(self):
        records = []
        for i, values in enumerate(self._list):
            first = True
            for value in values:
                record = {'index': i if first else '',
                          self.attribute_name: value}
                records.append(record)
                first = False
        df = pandas.DataFrame.from_records(records, columns=['index', self.attribute_name])
        pandas.set_option('display.max_colwidth', -1)
        table = df.to_html(index=False, escape=False)
        return '\n'.join(('<h4>' + self.__class__.__name__ + '</h4>', table))
