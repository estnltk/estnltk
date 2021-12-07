import regex as re
from collections import defaultdict
import pandas as pd
from pandas import DataFrame, set_option
from typing import Sequence, Mapping

from estnltk_core.layer.to_html import to_str


class VocabularyException(Exception):
    pass


class Vocabulary:
    def __init__(self,
                 mapping: Mapping[str, Sequence[Mapping]],
                 key: str,
                 attributes: Sequence[str],
                 ):
        r"""
        Input data object for SpanTagger, PhraseTagger, RegexTagger.

        :param vocabulary:
            Name of the input csv file, a DataFrame, records or a dict in the vocabulary format.
        :param key:
            Name of the index attribute. In csv file, DataFrame or records points to the values that the tagger searches
            from the Text object.
        :param default_rec:
            Default vocabulary record to fill in missing columns in the input vocabulary.
            example:
                default_rec = {'_validator_': lambda s, t: True,
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
        assert isinstance(mapping, Mapping), 'vocabulary must be dict, not ' + str(type(mapping))
        assert isinstance(key, str), 'key must be a string, not ' + str(type(key))
        assert key in attributes, (key, attributes)

        attribute_set = set(attributes)
        assert len(attribute_set) == len(attributes), attributes
        assert all(set(record) == attribute_set for records in mapping.values() for record in records)
        assert all(record[key] == key_value for key_value, records in mapping.items() for record in records)

        self.key = key
        self.attributes = attributes
        self.mapping = dict(mapping)

    def to_lower(self):
        """Changes vocabulary key value to lowercase. If an exception occurs the vocabulary stays unchanged."""
        return Vocabulary.from_vocabulary(self, to_lower=True)

    def to_regex(self, ignore_case=False):
        """compiles vocabulary key values to regex expressions if the key is str"""
        return Vocabulary.from_vocabulary(self, to_regex=True, ignore_case=ignore_case)

    def items(self):
        return self.mapping.items()

    def values(self):
        return self.mapping.values()

    def __getitem__(self, item):
        return self.mapping[item]

    def __contains__(self, item):
        return item in self.mapping

    def __iter__(self):
        return iter(self.mapping)

    @staticmethod
    def from_vocabulary(vocabulary: 'Vocabulary', attributes: Sequence[str] = None, default_rec: Mapping=None,
                        to_lower=False, to_regex=False, ignore_case=False):
        mapping = vocabulary.mapping
        key = vocabulary.key
        if attributes is None:
            attributes = vocabulary.attributes
        else:
            attribute_set = set(attributes)
            default_rec = {k: v for k, v in default_rec.items() if k in attribute_set-set(vocabulary.attributes)}
            assert attribute_set <= set(vocabulary.attributes) | set(default_rec), '{} <= {} not satisfied'.format(
                     attribute_set, set(vocabulary.attributes) | set(default_rec))
            new_mapping = defaultdict(list)
            for k, records in mapping.items():
                for record in records:
                    rec = default_rec.copy()
                    rec.update({k: v for k, v in record.items() if k in attribute_set})
                    new_mapping[k].append(rec)
            mapping = new_mapping
        if to_lower:
            lower_case_mapping = defaultdict(list)
            for k, records in mapping.items():
                if isinstance(k, str):
                    k_low = k.lower()
                elif isinstance(k, tuple):
                    k_low = tuple(t.lower() for t in k)
                elif isinstance(k, (int, float)):
                    k_low = k
                else:
                    raise VocabularyException("can't convert vocabulary key to lowercase: {!r}".format(k))
                if k_low in lower_case_mapping:
                    raise VocabularyException("this vocabulary contains keys that are lowercase equal: {!r}".format(k))
                for record in records:
                    record = dict(record)
                    record[key] = k_low
                    lower_case_mapping[k_low].append(record)
                mapping = lower_case_mapping
        if to_regex:
            new_mapping = defaultdict(list)
            flag = re.IGNORECASE if ignore_case else 0
            for k, records in mapping.items():
                if ignore_case and isinstance(k, re.regex.Pattern):
                    k = k.pattern
                try:
                    k_new = re.compile(k, flag)
                except Exception as e:
                    e.args += ("can't compile vocabulary key as regex pattern",)
                    raise
                for record in records:
                    record = dict(record)
                    record[key] = k_new
                    new_mapping[k_new].append(record)
                mapping = new_mapping

        return Vocabulary(mapping=mapping, key=key, attributes=attributes)

    @staticmethod
    def from_records(records: Sequence[dict], key: str, attributes: Sequence[str],
                     default_rec: dict=None) -> 'Vocabulary':

        if attributes is None:
            for record in records:
                if attributes is None:
                    attributes = set(record)
                attributes &= set(record)
            assert key in attributes, (key, attributes)
            attributes = (key, *sorted(attributes - {key}))
        else:
            if key not in attributes:
                attributes = (key, *attributes)

        attribute_set = set(attributes)

        default_rec = default_rec or {}
        default_rec = {k: v for k, v in default_rec.items() if k in attribute_set}

        assert key in attribute_set, (key, attributes)
        mapping = defaultdict(list)
        for record in records:
            rec = default_rec.copy()
            rec.update({k: v for k, v in record.items() if k in attribute_set})
            # TODO: remove next 3 lines
            for k, v in rec.items():
                if isinstance(v, str) and v.startswith('lambda m'):
                    rec[k] = eval(v)

            mapping[rec[key]].append(rec)
        return Vocabulary(mapping=mapping, key=key, attributes=attributes)

    # TODO:
    def write_csv(self):
        raise NotImplementedError()

    @staticmethod
    def read_csv(vocabulary_file: str, key: str = None, attributes: Sequence = None, default_rec: dict = None):
        """
        Reads a csv file and returns a dict that is used by several taggers as an input vocabulary.

        :return: dict
            Map key value to a list of dicts.

        """
        df = pd.read_csv(vocabulary_file,
                         na_filter=False,
                         index_col=False,
                         dtype=str
                         )
        default_rec = default_rec or {}
        if attributes is None:
            attributes = list(df.columns)
            for attr in default_rec:
                if attr not in attributes:
                    attributes.append(attr)
            key = key or attributes[0]
        else:
            if key not in attributes:
                attributes = tuple((key, *attributes))
        attributes = tuple(attributes)
        assert isinstance(key, str), key
        assert key in attributes, (key, attributes)

        lines = df.to_dict('records')
        lines = iter(lines)
        attribute_types = next(lines)
        string_attributes = []
        regex_attributes = []
        callable_attributes = []
        for k, v in attribute_types.items():
            if k not in attributes:
                continue
            if v == 'string':
                string_attributes.append(k)
            elif v == 'callable':
                callable_attributes.append(k)
            elif v == 'regex':
                regex_attributes.append(k)
            else:
                raise ValueError('unexpected column format type: ' + k)

        records = []
        for record in lines:
            rec = {}
            for k in string_attributes:
                rec[k] = str(record[k])
            try:
                for k in callable_attributes:
                    rec[k] = eval(record[k])
            except SyntaxError as e:
                e.msg += ": can't eval value {!r} from the callable vocabulary column {!r}".format(record[k], k)
                raise
            for k in regex_attributes:
                rec[k] = re.compile(record[k])
            records.append(rec)

        return Vocabulary.from_records(records=records, key=key, attributes=attributes, default_rec=default_rec)

    @staticmethod
    def parse(vocabulary, key=None, attributes=None, default_rec=None):
        if key is not None and attributes is not None and key not in attributes:
            attributes = tuple((key, *attributes))
        if isinstance(vocabulary, Vocabulary):
            return Vocabulary.from_vocabulary(vocabulary=vocabulary, attributes=attributes, default_rec=default_rec)
        if isinstance(vocabulary, list):
            return Vocabulary.from_records(records=vocabulary, key=key, default_rec=default_rec, attributes=attributes)
        if isinstance(vocabulary, str):
            return Vocabulary.read_csv(vocabulary_file=vocabulary,key=key, attributes=attributes, default_rec=default_rec)
        raise TypeError('unexpected type of vocabulary', type(vocabulary))

    def to_dict(self):
        return self.mapping

    def to_records(self):
        try:
            key_value_list = sorted(self.mapping)
        except TypeError:
            key_value_list = sorted(self.mapping, key=lambda x: to_str(x))
        return [rec for key_value in key_value_list for rec in self.mapping[key_value]]

    def _records_to_df(self, records):
        return DataFrame(data=records, columns=self.attributes)

    def to_df(self):
        return self._records_to_df(self.to_records())

    def __repr__(self):
        return 'Vocabulary(key={!r}, len={})'.format(self.key, len(self.mapping))

    class Instance:
        def __init__(self, instance):
            self.instance = instance

        def __str__(self):
            return ''

    def color_value_types(self, val):
        color = 'white'
        if isinstance(val, self.Instance):
            val = val.instance
        if isinstance(val, tuple):
            color = 'LightPink'
        elif isinstance(val, list):
            color = 'OrangeRed'
        elif isinstance(val, str):
            color = 'LightSteelBlue'
        elif isinstance(val, int):
            color = 'Moccasin'
        elif isinstance(val, float):
            color = 'cyan'
        elif isinstance(val, re.regex.Pattern):
            color = 'yellow'
        elif callable(val):
            color = 'magenta'

        return 'background-color: %s;' % color

    def _repr_html_(self):
        res = []
        keys = sorted(self.mapping, key=lambda x: to_str(x))
        for k in keys:
            first = True
            for rec in self.mapping[k]:
                line = {k: v for k, v in rec.items()}
                if first:
                    line[self.key] = k
                    first = False
                else:
                    line[self.key] = self.Instance(k)
                res.append(line)
        columns = tuple(self.attributes)
        style = DataFrame.from_records(res, columns=columns).style
        style = style.applymap(self.color_value_types).format(lambda v: to_str(v, escape_html=True)).hide_index()
        try:
            # pandas < 1.2.0; python <= 3.6
            style = style.set_table_styles( dict(selector="tr:hover", props=[("background-color", "%s" % "#11ff99")]) )
        except TypeError:
            # pandas >= 1.2.0; python > 3.6
            style = style.set_table_styles( [dict(selector="tr:hover", props=[("background-color", "%s" % "#11ff99")])] )
        except:
            raise
        table = style.render()

        return '\n'.join(('<h4>' + 'Vocabulary' + '</h4>', 'key: '+repr(self.key), table))
