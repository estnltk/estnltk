from collections import OrderedDict

from estnltk.taggers.syntax.visl_row_analyser import get_analysed_forms, get_postag, get_ending, get_syntax_info


def test_analysed_forms():
    test_forms = [
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
    for test in test_forms:
        assert get_analysed_forms(test['forms'], test['postag']) == test['expected']


def test_postag():
    test_postags = [
        {'cats': 'Z Fst CLB #5->5',
         'expected': 'Z'},
        {'cats': 'Ln V main indic pres ps1 sg ps af @FMV #3->0',
         'expected': 'V'}
    ]
    for test in test_postags:
        assert get_postag(test['cats']) == test['expected']


def test_ending():
    test_endings = [
        {'cats': 'Z Com #5->5',
         'expected': ''},
        {'cats': 'Llle P pers ps1 sg all cap @ADVL #1->2',
         'expected': 'lle'}
    ]
    for test in test_endings:
        assert get_ending(test['cats']) == test['expected']


def test_syntax():
    test_syntax = [
        {'cats': 'Z Fst CLB #4->4',
         'expected': ('xxx', '#4->4')},
        {'cats': 'Ld S com pl nom @SUBJ #3->2',
         'expected': ('@SUBJ', '#3->2')}
    ]
    for test in test_syntax:
        assert get_syntax_info(test['cats']) == test['expected']
