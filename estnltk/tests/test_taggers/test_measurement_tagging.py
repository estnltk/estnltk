from estnltk import Text
from estnltk.taggers.measurement_tagging.measurement_tagger import MeasurementTagger

measurement_tagger = MeasurementTagger(conflict_resolving_strategy='ALL')


def helper_function(line):
    line = Text(line)
    measurement_tagger.tag(line)
    numbers = []
    for n, r in zip(line.grammar_tags.text, line.grammar_tags.grammar_symbol):
        if r == 'NUMBER' or r == 'DATE' or r == 'DATENUM':
            numbers.append(n)
    return numbers


def more_complex_helper_function(line):
    line = Text(line)
    measurement_tagger.tag(line)
    return line.grammar_tags


def test_1():
    assert helper_function('PSA 2012. 1,53') == ['2012', '1,53']
    assert helper_function('PSA 12. 53') == ['12. ', '12. 53', '53']
    assert helper_function('PSA 12, 53') == ['12, ', '12, 53', '53']
    assert helper_function('PSA 12 , 53') == ['12 , ', '12 , 53', '53']
    assert helper_function('PSA 2012.1,53') == ['2012', '1,53']
    assert helper_function('PSA 20121,53') == ['2012', '1,53']
    assert helper_function('PSA ,315') == [' ,315']
    assert helper_function('PSA 030420121,53') == ['03042012', '1,53']


def test_2():
    t = more_complex_helper_function('PSA 2012. 1,53')
    assert t[0].regex_type == 'measurement_object'
    assert t[0].start == 0
    assert t[0].end == 3
    assert t[1].regex_type == 'date9'
    assert t[1].start == 4
    assert t[1].end == 8
    assert t[2].regex_type == 'anynumber'
    assert t[2].start == 10
    assert t[2].end == 14


def test_3():
    t = more_complex_helper_function('PSA 12. 53')
    assert t[0].regex_type, 'measurement_object'
    assert t[0].start == 0
    assert t[0].end == 3
    assert t[1].regex_type == 'numbercomma'
    assert t[1].start == 4
    assert t[1].end == 8
    assert t[2].regex_type == 'anynumber'
    assert t[2].start == 4
    assert t[2].end == 10
    assert t[3].regex_type == 'anynumber'
    assert t[3].start == 8
    assert t[3].end == 10


def test_4():
    t = more_complex_helper_function('PSA 2012. 1,53')
    assert t[0].grammar_symbol == 'MO'
    assert t[0].start == 0
    assert t[0].end ==3
    assert t[1].grammar_symbol == 'DATE'
    assert t[1].start == 4
    assert t[1].end == 8
    assert t[2].grammar_symbol == 'NUMBER'
    assert t[2].start == 10
    assert t[2].end == 14
