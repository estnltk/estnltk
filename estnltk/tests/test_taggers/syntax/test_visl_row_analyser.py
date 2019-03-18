from collections import OrderedDict

from estnltk.taggers.syntax.visl_row_analyser import CG3AnnotationParser

parser = CG3AnnotationParser()

def test_forms():
    test_forms = [
        {'cats': 'P pos det refl pl nom',
         'postag': 'P',
         'line' : '    "ise" L0 P pos det refl pl nom',
         'expected': (['pos', 'det', 'refl', 'pl', 'nom'], 'P')},
        {'cats': 'Z Fst CLB',
         'postag': 'Z',
         'line': '	"." Z Fst CLB #32->32',
         'expected': (['Fst', 'CLB'], 'Z')},
        {'cats': 'D',
         'postag': 'D',
         'line': '	"automaatselt" L0 D @ADVL #15->9',
         'expected': ([], 'D')}
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
                                  ('finiteness', ['<FinV>']), ('subcat', ['<Intr>'])])},
        {'forms': ['_'],
         'postag': 'D',
         'expected': OrderedDict()}
    ]
    for test in test_analysed_forms:
        assert parser.get_analysed_forms(test['forms'], test['postag']) == test['expected']


def test_postag():
    test_postags = [
        {'cats': 'Z Fst CLB #5->5',
         'expected': 'Z'},
        {'cats': 'V main indic pres ps1 sg ps af @FMV #3->0',
         'expected': 'V'}
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
    test_split = [
    {'line': '	"," Z Com CLB #23->23',
     'expected': (',', '', 'Z Com CLB ', '#23->23')},
    {'line': '	"käive" Ltega S com pl kom @NN> @<NN @ADVL #21->22',
     'expected': ('käive', 'Ltega', ' S com pl kom ', '@NN> @<NN @ADVL #21->22')},
    {'line': '	"suur" Lte A pos pl gen',
     'expected': ('suur', 'Lte', ' A pos pl gen', '')}
    ]
    for test in test_split:
        assert parser.split_visl_analysis_line(test['line']) == test['expected']
