import regex as re
from collections import defaultdict
from pandas import read_csv
from typing import Sequence


def read_vocabulary(vocabulary_file: str,
                    key: str,
                    string_attributes: Sequence=(),
                    regex_attributes: Sequence=(),
                    callable_attributes: Sequence=(),
                    default_rec: dict=None
                    ):
    """
    Reads a csv file and returns a dict that is used by several taggers as an input vocabulary.

    :param vocabulary_file:
        Name of the input csv file.
    :param key:
        Name of the index column. This column contains the values that the tagger searches from the Text object.
    :param string_attributes:
        Names of the columns values of which that are interpreted as strings.
    :param regex_attributes:
        Names of columns. Values in these columns are compiled as regular expressions.
    :param callable_attributes:
        Names of columns. Values in these columns are evaluated as python code.
    :param default_rec:
        Default _vocabulary record to fill in missing columns in the file.
        example:
            default_rec = {'_validator_': lambda t, s: True,
                           '_group_': 'default_group',
                           '_priority_': 0}
        The string_attributes, callable_attributes, regex_attributes overwrite the entries in default_rec.
    :return: dict
        Map key value to a list of dicts.
    """
    assert vocabulary_file, 'empty vocabulary_file'

    records = read_csv(vocabulary_file, na_filter=False, index_col=False).to_dict('records')

    len_attr = len(string_attributes) + len(regex_attributes) + len(callable_attributes)
    assert len_attr, 'no attribute names given'
    union_attr = set(string_attributes) | set(regex_attributes) | set(callable_attributes)
    assert key in union_attr, 'k not among attributes'
    assert len_attr == len(union_attr), 'same attribute in different categories'

    vocabulary = defaultdict(list)
    if default_rec is None:
        default_rec = {}

    for record in records:
        rec = default_rec.copy()
        for k in string_attributes:
            if k in record:
                value = record[k]
            elif k in rec:
                continue
            else:
                assert False, 'attribute not in input table and not in default_rec: ' + k
            rec[k] = value
        for k in regex_attributes:
            if k in record:
                value = record[k]
            elif k in rec:
                continue
            else:
                assert False, 'attribute not in input table and not in default_rec: ' + k
            assert isinstance(value, str)
            value = re.compile(value)
            rec[k] = value
        for k in callable_attributes:
            if k in record:
                value = record[k]
            elif k in rec:
                continue
            else:
                assert False, 'attribute not in input table and not in default_rec: ' + k
            if isinstance(value, str):
                value = eval(value)
            else:
                assert isinstance(value, (int, float)), 'fix this assertion including the following type: ' + str(type(value))
            rec[k] = value
        key_value = rec[key]
        del rec[key]
        vocabulary[key_value].append(rec)
    return dict(vocabulary)


def records_to_vocabulary(records, key):
    pass


def csv_to_records(vocabulary_file):
    return read_csv(vocabulary_file, na_filter=False, index_col=False).to_dict('records')


def records_to_df(records):
    pass


def vocabulary_to_records(vocabulary: dict, key: str):
    records = []
    try:
        key_value_list = sorted(vocabulary)
    except TypeError:
        key_value_list = list(vocabulary)
    for key_value in key_value_list:#, decorations in vocabulary.items():
        for record in vocabulary[key_value]:
            record[key] = key_value
            records.append(record)
    return records
