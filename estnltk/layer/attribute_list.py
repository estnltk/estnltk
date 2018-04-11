import pandas


class AttributeList:
    """Immutable lists for representing single attribute value of unambiguous layer."""
    def __init__(self, attr_list: list):
        self._list = attr_list

    def __getitem__(self, item):
        return self._list[item]

    def __repr__(self):
        return repr(self._list)

    def __str__(self):
        return str(self._list)

    def _repr_html_(self):
        df = pandas.DataFrame(self._list, columns=['attribute'])
        pandas.set_option('display.max_colwidth', -1)
        table = df.to_html(index=True, escape=False)
        return '\n'.join(('<h4>' + self.__class__.__name__ + '</h4>', table))
