import pytest
from estnltk.converters.cg3.cg3_annotation_parser import CG3AnnotationParser
from estnltk.converters.cg3.cg3_annotation_parser import get_reversed_mapping, get_cats

parser = CG3AnnotationParser()


def test_get_reversed_mapping():
    assert parser.reversed_cats['unkw'] == 'unknown_attribute'

    cats = {'cat1': {'nom', 'gen'},
            'cat2': {'gen'}}
    with pytest.raises(Exception):
        get_reversed_mapping(cats)

def test_get_cats():
    cats = {'cat1': {'nom', 'gen'},
            'cat2': {'gen'},
            'lemma' : 'see'}
    with pytest.raises(Exception):
        get_cats(cats)

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
        {
            'cats': 'cap',
            'postag': '',
            'line': '	"üle" cap @ADVL #1->4',
            'expected': ([], '')}
    ]
    assert parser.get_forms(test_forms[0]['cats'], test_forms[0]['postag'], test_forms[0]['line']) == test_forms[0][
        'expected']
    assert parser.get_forms(test_forms[1]['cats'], test_forms[1]['postag'], test_forms[1]['line']) == test_forms[1][
        'expected']
    assert parser.get_forms(test_forms[2]['cats'], test_forms[2]['postag'], test_forms[2]['line']) == test_forms[2][
        'expected']
    assert parser.get_forms(test_forms[3]['cats'], test_forms[3]['postag'], test_forms[3]['line']) == test_forms[3][
        'expected']
    assert parser.get_forms(test_forms[4]['cats'], test_forms[4]['postag'], test_forms[4]['line']) == test_forms[4][
        'expected']


def test_analysed_forms():
    test_analysed_forms = [
        {'forms': ['pos', 'sg', 'ad'],
         'expected': {'subtype': ['pos'], 'number': ['sg'], 'case': ['ad']}},
        {'forms': ['pos', 'det', 'refl', 'sg', 'gen'],
         'expected': {'case': ['gen'], 'number': ['sg'], 'subtype': ['pos', 'det', 'refl']}},
        {'forms': ['mod', 'indic', 'pres', 'ps3', 'sg', 'ps', 'af', '<FinV>', '<Intr>'],
         'expected': {'finiteness': ['<FinV>'],
                      'mood': ['indic'],
                      'number': ['sg'],
                      'person': ['ps3'],
                      'polarity': ['af'],
                      'subcat': ['<Intr>'],
                      'subtype': ['mod'],
                      'tense': ['pres'],
                      'voice': ['ps']}}
    ]
    assert parser.get_analysed_forms(test_analysed_forms[0]['forms']) == \
           test_analysed_forms[0]['expected']
    assert parser.get_analysed_forms(test_analysed_forms[1]['forms']) == \
           test_analysed_forms[1]['expected']
    assert parser.get_analysed_forms(test_analysed_forms[2]['forms']) == \
           test_analysed_forms[2]['expected']


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
    assert parser.get_postag(test_postags[0]['cats']) == test_postags[0]['expected']
    assert parser.get_postag(test_postags[1]['cats']) == test_postags[1]['expected']
    assert parser.get_postag(test_postags[2]['cats']) == test_postags[2]['expected']


def test_syntax():
    test_syntax = [
        {'syntax_analysis': '@FMV #3->0',
         'expected': (['@FMV'], '3', '0')},
        {'syntax_analysis': '@AN> @NN> #1->4',
         'expected': (['@AN>', '@NN>'], '1', '4')},
        {'syntax_analysis': '#1->1',
         'expected': ('_', '1', '1')}
    ]
    assert parser.get_syntax(test_syntax[0]['syntax_analysis']) == test_syntax[0]['expected']
    assert parser.get_syntax(test_syntax[1]['syntax_analysis']) == test_syntax[1]['expected']
    assert parser.get_syntax(test_syntax[2]['syntax_analysis']) == test_syntax[2]['expected']


def test_split_visl_analysis_line():
    test_split_valid = [
        {'line': '	"," Z Com CLB #23->23',
         'expected': (',', '', 'Z Com CLB ', '#23->23')},
        {'line': '	"käive" Ltega S com pl kom @NN> @<NN @ADVL #21->22',
         'expected': ('käive', 'Ltega', ' S com pl kom ', '@NN> @<NN @ADVL #21->22')},
        {'line': '	"suur" Lte A pos pl gen',
         'expected': ('suur', 'Lte', ' A pos pl gen', '')}
    ]
    assert parser.split_visl_analysis_line(test_split_valid[0]['line']) == test_split_valid[0]['expected']
    assert parser.split_visl_analysis_line(test_split_valid[1]['line']) == test_split_valid[1]['expected']
    assert parser.split_visl_analysis_line(test_split_valid[2]['line']) == test_split_valid[2]['expected']

    failed_analysis_case = {'line': '	mari cap @ADVL #1->4'}
    with pytest.raises(Exception):
        parser.split_visl_analysis_line(failed_analysis_case['line'])
    failed_nonanalysis_case = {'line': r'<\s>'}
    assert parser.split_visl_analysis_line(failed_nonanalysis_case['line']) == ('', '', '', '')


def test_process_visl_analysis_line():
    test_process_visl = [
        {'line': '	"käive" Ltega S com pl kom @NN> @<NN @ADVL #21->22',
         'expected': {'case': ['kom'],
                      'deprel': ['@NN>', '@<NN', '@ADVL'],
                      'ending': 'tega',
                      'head': '22',
                      'id': '21',
                      'lemma': 'käive',
                      'number': ['pl'],
                      'partofspeech': 'S',
                      'subtype': ['com']}},
        {'line': '	"käive" Ltega S com pl kom',
         'expected': {'case': ['kom'],
                      'deprel': '_',
                      'ending': 'tega',
                      'head': '_',
                      'lemma': 'käive',
                      'number': ['pl'],
                      'partofspeech': 'S',
                      'subtype': ['com']}}
    ]
    assert parser.parse(test_process_visl[0]['line']) == test_process_visl[0]['expected']
    assert parser.parse(test_process_visl[1]['line']) == test_process_visl[1]['expected']

    failed_analysis_case = {'line': '<s>'}
    with pytest.raises(Exception):
        parser.parse(failed_analysis_case['line'])


def test_supress_exceptions():
    parser = CG3AnnotationParser(supress_exceptions=True)
    assert parser.parse(r'<\s>') == {}
    assert parser.split_visl_analysis_line(r'<\s>') == ('', '', '', '')
    assert parser.split_visl_analysis_line(r'\t<\s>') == ('', '', '', '')
