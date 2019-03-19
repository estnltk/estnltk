from collections import OrderedDict
import pytest
from estnltk.taggers.syntax.cg3_annotation_parser import CG3AnnotationParser

parser = CG3AnnotationParser()


def test_get_reversed_mapping():
    assert parser.reversed_cats['unkw'] == ['unknown_attribute']


def test_forms():
    test_forms = [
        {'cats': 'P pos det refl pl nom',
         'postag': 'P',
         'line': '    "ise" L0 P pos det refl pl nom',
         'expected': (['pos', 'det', 'refl', 'pl', 'nom'], 'P')},
        {'cats': 'Z Fst CLB',
         'postag': 'Z',
         'line': '	"." Z Fst CLB #32->32',
         'expected': (['Fst', 'CLB'], 'Z')},
        {'cats': 'D',
         'postag': 'D',
         'line': '	"automaatselt" L0 D @ADVL #15->9',
         'expected': ([], 'D')},
        {'cats': 'cap D ',
         'postag': 'D',
         'line': '	"üle" cap D @ADVL #1->4',
         'expected': (['cap'], 'D')},
        {'cats': 'cap',
         'postag': 'S',
         'line': '	"mari" cap @ADVL #1->4',
         'expected': ([''], 'X')}
    ]
    for test in test_forms:
        assert parser.get_forms(test['cats'], test['postag'], test['line']) == test['expected']


def test_analysed_forms():
    test_analysed_forms = [
        {'forms': ['pos', 'sg', 'ad'],
         'postag': 'A',
         'expected': OrderedDict([('adjective_type', ['pos']), ('number', ['sg']), ('case', ['ad'])])},
        {'forms': ['pos', 'det', 'refl', 'sg', 'gen'],
         'postag': 'P',
         'expected': OrderedDict([('pronoun_type', ['pos', 'det', 'refl']), ('number', ['sg']), ('case', ['gen'])])},
        {'forms': ['mod', 'indic', 'pres', 'ps3', 'sg', 'ps', 'af', '<FinV>', '<Intr>'],
         'postag': 'V',
         'expected': OrderedDict([('verb_type', ['mod']), ('mood', ['indic']), ('tense', ['pres']), \
                                  ('person', ['ps3']), ('number', ['sg']), ('voice', ['ps']), ('negation', ['af']), \
                                  ('finiteness', ['<FinV>']), ('subcat', ['<Intr>'])])}
    ]
    for test in test_analysed_forms:
        assert parser.get_analysed_forms(test['forms'], test['postag']) == test['expected']


def test_postag():
    test_postags = [
        {'cats': 'Z Fst CLB ',
         'expected': 'Z'},
        {'cats': ' V main indic pres ps1 sg ps af ',
         'expected': 'V'},
        {'cats': 'cap D ',
         'expected': 'D'
         }
    ]
    for test in test_postags:
        assert parser.get_postag(test['cats']) == test['expected']


def test_syntax():
    test_syntax = [
        {'syntax_analysis': '@FMV #3->0',
         'expected': ('@FMV ', '#3->0')},
        {'syntax_analysis': '@AN> @NN> #1->4',
         'expected': ('@AN> @NN> ', '#1->4')},
        {'syntax_analysis': '#1->1',
         'expected': ('', '#1->1')}
    ]
    for test in test_syntax:
        assert parser.get_syntax(test['syntax_analysis']) == test['expected']


def test_split_visl_analysis_line():
    test_split_valid = [
        {'line': '	"," Z Com CLB #23->23',
         'expected': (',', '', 'Z Com CLB ', '#23->23')},
        {'line': '	"käive" Ltega S com pl kom @NN> @<NN @ADVL #21->22',
         'expected': ('käive', 'Ltega', ' S com pl kom ', '@NN> @<NN @ADVL #21->22')},
        {'line': '	"suur" Lte A pos pl gen',
         'expected': ('suur', 'Lte', ' A pos pl gen', '')},
    ]
    for test in test_split_valid:
        assert parser.split_visl_analysis_line(test['line']) == test['expected']

    failed_analysis_case = {'line': '	mari cap @ADVL #1->4'}
    with pytest.raises(Exception):
        parser.split_visl_analysis_line(failed_analysis_case['line'])
    failed_nonanalysis_case = {'line': '<\s>'}
    assert parser.split_visl_analysis_line(failed_nonanalysis_case['line']) is None


def test_process_visl_analysis_line():
    test_process_visl = [
        {'line': '	"käive" Ltega S com pl kom @NN> @<NN @ADVL #21->22',
         'expected': {'deprel': '@NN> @<NN @ADVL ', 'feats': OrderedDict([('substantive_type', ['com']),
                                                                          ('number', ['pl']), ('case', ['kom'])]),
                      'lemma': 'käive', 'ending': 'tega', 'partofspeech': 'S', 'head': '#21->22'}},
        {'line': '	"käive" Ltega S com pl kom',
         'expected': {'ending': 'tega', 'feats': OrderedDict([('substantive_type', ['com']),
                                                              ('number', ['pl']), ('case', ['kom'])]),
                      'partofspeech': 'S', 'lemma': 'käive'}}
    ]
    for test in test_process_visl:
        assert parser.process_visl_analysis_line(test['line']) == test['expected']
    failed_analysis_case = {'line': '<s>'}
    with pytest.raises(Exception):
        parser.process_visl_analysis_line(failed_analysis_case['line'])
