import regex as re
from collections import defaultdict
from pandas import read_csv, DataFrame, set_option
from typing import Hashable, Iterable, Union


class Vocabulary:
    def __init__(self,
                 vocabulary: Union[str, DataFrame, list, dict],
                 key: Hashable,
                 default_rec: dict = None,
                 string_attributes=(),
                 regex_attributes=(),
                 callable_attributes=()
                 ):
        """
        Input data object for SpanTagger, PhraseTagger, RegexTagger.

        :param vocabulary:
            Name of the input csv file, a DataFrame, records or a dict in the vocabulary format.
        :param key:
            Name of the index attribute. In csv file, DataFrame or records points to the values that the tagger searches
            from the Text object.
        :param default_rec:
            Default vocabulary record to fill in missing columns in the input vocabulary.
            example:
                default_rec = {'_validator_': lambda t, s: True,
                               '_group_': 'default_group',
                               '_priority_': 0}
            The default values are overwritten if present in the input.
        :param string_attributes:
            Names of attributes that should have string value. Used if the input is in form of records.
        :param regex_attributes:
            Names of the attributes that are to be compiled as regular expressions. Used if the input is in form of
            records.
        :param callable_attributes:
            Names of the attributes that are to be evaluated using eval function. Used if the input is in form of
            records.

        csv file structure

        First row: header (attribute names)
        Second row: value type ('string', 'regex' or 'callable')
        Other rows: data
        Rows with value type
            'string' are interpreted as strings;
            'regex' are compiled as regular expressions;
            'callable' are evaluated with eval function.
        Example:
            pattern, validator, comment
            regex, callable, string
            \d+, lambda s, t: True, number
        """
        assert not isinstance(vocabulary, DataFrame) or not vocabulary.empty, 'empty vocabulary DataFrame'
        assert isinstance(vocabulary, DataFrame) or vocabulary, 'empty vocabulary: ' + str(vocabulary)
        self.key = key
        self.attributes = ()
        if default_rec is None:
            default_rec = {}

        if isinstance(vocabulary, str):
            self.vocabulary = self._csv_to_vocabulary(vocabulary_file=vocabulary,
                                                      default_rec=default_rec)
        elif isinstance(vocabulary, DataFrame):
            self.vocabulary = self._df_to_vocabulary(df=vocabulary,
                                                     default_rec=default_rec,
                                                     string_attributes=string_attributes,
                                                     regex_attributes=regex_attributes,
                                                     callable_attributes=callable_attributes
                                                     )
        elif isinstance(vocabulary, list):
            self.vocabulary = self._records_to_vocabulary(records=vocabulary,
                                                          default_rec=default_rec,
                                                          string_attributes=string_attributes,
                                                          regex_attributes=regex_attributes,
                                                          callable_attributes=callable_attributes)
        elif isinstance(vocabulary, dict):
            self.vocabulary = vocabulary
        else:
            raise TypeError('unkonown vocabulary type: ' + str(type(vocabulary)))

        self.string_attributes = string_attributes
        self.regex_attributes = regex_attributes
        self.callable_attributes = callable_attributes

        self.attributes = tuple(tuple(self.vocabulary.values())[0][0])

    def items(self):
        return self.vocabulary.items()

    def values(self):
        return self.vocabulary.values()

    def __getitem__(self, item):
        return self.vocabulary[item]

    def __contains__(self, item):
        return item in self.vocabulary

    def __iter__(self):
        return iter(self.vocabulary)

    def _csv_to_records(self, vocabulary_file: str) -> list:
        df = read_csv(vocabulary_file,
                      na_filter=False,
                      index_col=False,
                      dtype=str
                      )
        lines = df.to_dict('records')

        lines = iter(lines)
        attribute_types = next(lines)
        string_attributes = []
        regex_attributes = []
        callable_attributes = []
        for k, v in attribute_types.items():
            if v == 'string':
                string_attributes.append(k)
            elif v == 'callable':
                callable_attributes.append(k)
            elif v == 'regex':
                regex_attributes.append(k)
            else:
                raise ValueError('unexpected format type: ' + k)

        records = []
        for record in lines:
            rec = {}
            for k in string_attributes:
                rec[k] = record[k]
            for k in callable_attributes:
                rec[k] = eval(record[k])
            for k in regex_attributes:
                rec[k] = re.compile(record[k])
            records.append(rec)

        return records

    def _records_to_vocabulary(self,
                               records: Iterable[dict],
                               default_rec: dict = None,
                               string_attributes=(),
                               regex_attributes=(),
                               callable_attributes=()
                              ) -> dict:

        vocabulary = defaultdict(list)
        for record in records:
            rec = default_rec.copy()
            rec.update(record)
            for attr in callable_attributes:
                rec[attr] = eval(rec[attr])
            for attr in regex_attributes:
                rec[attr] = re.compile(rec[attr])
            for attr in string_attributes:
                rec[attr] = str(rec[attr])
            # TODO: remove next 3 lines
            for k, v in rec.items():
                if isinstance(v, str) and v.startswith('lambda m'):
                    rec[k] = eval(v)
            value = rec[self.key]
            del rec[self.key]
            vocabulary[value].append(rec)
        return dict(vocabulary)

    def _csv_to_vocabulary(self,
                           vocabulary_file: str,
                           default_rec: dict
                           ):
        """
        Reads a csv file and returns a dict that is used by several taggers as an input vocabulary.

        :return: dict
            Map key value to a list of dicts.

        """
        records = self._csv_to_records(vocabulary_file=vocabulary_file)

        return self._records_to_vocabulary(records=records,
                                           default_rec=default_rec,
                                           )

    def _df_to_vocabulary(self, df: DataFrame,
                          default_rec: dict,
                          string_attributes,
                          regex_attributes,
                          callable_attributes):
        records = df.to_dict('records')
        return self._records_to_vocabulary(records=records,
                                           default_rec=default_rec,
                                           string_attributes=string_attributes,
                                           regex_attributes=regex_attributes,
                                           callable_attributes=callable_attributes)

    def to_dict(self):
        return self.vocabulary

    def to_records(self):
        records = []
        try:
            key_value_list = sorted(self.vocabulary)
        except TypeError:
            key_value_list = list(self.vocabulary)
        for key_value in key_value_list:
            for record in self.vocabulary[key_value]:
                record[self.key] = key_value
                records.append(record)
        return records

    def _records_to_df(self, records):
        return DataFrame(data=records, columns=(self.key,)+tuple(self.attributes))

    def to_df(self):
        return self._records_to_df(self.to_records())

    def __str__(self):
        return 'Vocabulary(key: {}, len={})'.format(self.key, len(self.vocabulary))

    def _repr_html_(self):
        res = []
        try:
            keys = sorted(self.vocabulary)
        except TypeError:
            keys = list(self.vocabulary)
        for k in keys:
            first = True
            for rec in self.vocabulary[k]:
                line = rec.copy()
                if first:
                    try:
                        line[self.key] = 'Regex(' + k.pattern + ')'
                    except AttributeError:
                        line[self.key] = k
                    first = False
                else:
                    line[self.key] = ''
                res.append(line)
        columns = (self.key,) + tuple(self.attributes)
        df = DataFrame.from_records(res, columns=columns)
        set_option('display.max_colwidth', -1)
        table = df.to_html(index=False, escape=False)

        return '\n'.join(('<h4>' + 'Vocabulary' + '</h4>', table))
