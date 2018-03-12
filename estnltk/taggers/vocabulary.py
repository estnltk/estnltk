import regex as re
from collections import defaultdict
from pandas import read_csv
from typing import Sequence


def read_vocabulary(vocabulary_file: str,
                    index: str,
                    str_attributes: Sequence=(),
                    eval_attributes: Sequence=(),
                    re_attributes: Sequence=(),
                    default_rec: dict=None
                    ):
    """
    Reads a csv file and returns a dict that is used by several taggers as an input vocabulary.

    :param vocabulary_file:
        Name of the input csv file.
    :param index:
        Name of the main column. This column contains the values that the tagger searches from the Text object.
    :param str_attributes:
        Names of the columns values of which that are interpreted as strings.
    :param eval_attributes:
        Names of columns. Values in these columns are evaluated as python code.
    :param re_attributes:
        Names of columns. Values in these columns are compiled as regular expressions.
    :param default_rec:
        Default vocabulary record to fill in missing columns in the file.
        example:
            default_rec = {'_validator_': lambda t, s: True,
                           '_group_': 'default_group',
                           '_priority_': 0}
        The str_attributes, eval_attributes, re_attributes overwrite the entries in default_rec.
    :return:
    """
    vocabulary = read_csv(vocabulary_file, na_filter=False, index_col=False).to_dict('records')

    assert vocabulary, 'empty vocabulary_file'
    len_attr = len(str_attributes) + len(re_attributes) + len(eval_attributes)
    assert len_attr, 'no attribute names given'
    union_attr = set(str_attributes) | set(re_attributes) | set(eval_attributes)
    assert index in union_attr, 'index not among attributes'
    assert len_attr == len(union_attr), 'same attribute in different categories'

    result = defaultdict(list)
    if default_rec is None:
        default_rec = {}

    for record in vocabulary:
        rec = default_rec.copy()
        for key in str_attributes:
            if key in record:
                value = record[key]
            elif key in rec:
                continue
            else:
                assert False, 'attribute not in input table and not in default_rec: ' + key
            rec[key] = value
        for key in re_attributes:
            if key in record:
                value = record[key]
            elif key in rec:
                continue
            else:
                assert False, 'attribute not in input table and not in default_rec: ' + key
            assert isinstance(value, str)
            value = re.compile(value)
            rec[key] = value
        for key in eval_attributes:
            if key in record:
                value = record[key]
            elif key in rec:
                continue
            else:
                assert False, 'attribute not in input table and not in default_rec: ' + key
            if isinstance(value, str):
                value = eval(value)
            else:
                assert isinstance(value, (int, float)), 'fix this assertion including the following type: ' + str(type(value))
            rec[key] = value
        index_value = rec[index]
        del rec[index]
        result[index_value].append(rec)
    return dict(result)
