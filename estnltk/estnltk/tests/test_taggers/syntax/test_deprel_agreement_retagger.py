from collections import OrderedDict

from estnltk_core.converters import dict_to_text
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from estnltk.taggers.standard.syntax.ud_validation.deprel_agreement_retagger import DeprelAgreementRetagger


def test_deprel_agreement_retagger():
    input_text = {'text': 'Hispaanias oli kombeks anda jootrahaks 25 peseetat. Iga osavõtja tundis ennast targemana.',
                  'meta': {}, 'layers': [
            {'name': 'tokens', 'attributes': (), 'parent': None, 'enveloping': None, 'ambiguous': False,
             'serialisation_module': None, 'meta': {},
             'spans': [{'base_span': (0, 10), 'annotations': [{}]}, {'base_span': (11, 14), 'annotations': [{}]},
                       {'base_span': (15, 22), 'annotations': [{}]}, {'base_span': (23, 27), 'annotations': [{}]},
                       {'base_span': (28, 38), 'annotations': [{}]}, {'base_span': (39, 41), 'annotations': [{}]},
                       {'base_span': (42, 50), 'annotations': [{}]}, {'base_span': (50, 51), 'annotations': [{}]},
                       {'base_span': (52, 55), 'annotations': [{}]}, {'base_span': (56, 64), 'annotations': [{}]},
                       {'base_span': (65, 71), 'annotations': [{}]}, {'base_span': (72, 78), 'annotations': [{}]},
                       {'base_span': (79, 88), 'annotations': [{}]}, {'base_span': (88, 89), 'annotations': [{}]}]},
            {'name': 'compound_tokens', 'attributes': ('type', 'normalized'), 'parent': None, 'enveloping': 'tokens',
             'ambiguous': False, 'serialisation_module': None, 'meta': {}, 'spans': []},
            {'name': 'words', 'attributes': ('normalized_form',), 'parent': None, 'enveloping': None, 'ambiguous': True,
             'serialisation_module': None, 'meta': {},
             'spans': [{'base_span': (0, 10), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (11, 14), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (15, 22), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (23, 27), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (28, 38), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (39, 41), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (42, 50), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (50, 51), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (52, 55), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (56, 64), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (65, 71), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (72, 78), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (79, 88), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (88, 89), 'annotations': [{'normalized_form': None}]}]}, {'name': 'morph_analysis',
                                                                                               'attributes': (
                                                                                                   'normalized_text',
                                                                                                   'lemma', 'root',
                                                                                                   'root_tokens',
                                                                                                   'ending',
                                                                                                   'clitic', 'form',
                                                                                                   'partofspeech'),
                                                                                               'parent': 'words',
                                                                                               'enveloping': None,
                                                                                               'ambiguous': True,
                                                                                               'serialisation_module': None,
                                                                                               'meta': {}, 'spans': [
                    {'base_span': (0, 10), 'annotations': [
                        {'normalized_text': 'Hispaanias', 'lemma': 'Hispaania', 'root': 'Hispaania',
                         'root_tokens': ['Hispaania'], 'ending': 's', 'clitic': '', 'form': 'sg in',
                         'partofspeech': 'H'}]}, {'base_span': (11, 14), 'annotations': [
                        {'normalized_text': 'oli', 'lemma': 'olema', 'root': 'ole', 'root_tokens': ['ole'],
                         'ending': 'i', 'clitic': '', 'form': 's', 'partofspeech': 'V'}]}, {'base_span': (15, 22),
                                                                                            'annotations': [{
                                                                                                'normalized_text': 'kombeks',
                                                                                                'lemma': 'komme',
                                                                                                'root': 'komme',
                                                                                                'root_tokens': [
                                                                                                    'komme'],
                                                                                                'ending': 'ks',
                                                                                                'clitic': '',
                                                                                                'form': 'sg tr',
                                                                                                'partofspeech': 'S'}]},
                    {'base_span': (23, 27), 'annotations': [
                        {'normalized_text': 'anda', 'lemma': 'andma', 'root': 'and', 'root_tokens': ['and'],
                         'ending': 'a', 'clitic': '', 'form': 'da', 'partofspeech': 'V'}]}, {'base_span': (28, 38),
                                                                                             'annotations': [{
                                                                                                 'normalized_text': 'jootrahaks',
                                                                                                 'lemma': 'jootraha',
                                                                                                 'root': 'joot_raha',
                                                                                                 'root_tokens': [
                                                                                                     'joot',
                                                                                                     'raha'],
                                                                                                 'ending': 'ks',
                                                                                                 'clitic': '',
                                                                                                 'form': 'sg tr',
                                                                                                 'partofspeech': 'S'}]},
                    {'base_span': (39, 41), 'annotations': [
                        {'normalized_text': '25', 'lemma': '25', 'root': '25', 'root_tokens': ['25'], 'ending': '0',
                         'clitic': '', 'form': '?', 'partofspeech': 'N'}]}, {'base_span': (42, 50), 'annotations': [
                        {'normalized_text': 'peseetat', 'lemma': 'peseeta', 'root': 'peseeta',
                         'root_tokens': ['peseeta'], 'ending': 't', 'clitic': '', 'form': 'sg p',
                         'partofspeech': 'S'}]}, {'base_span': (50, 51), 'annotations': [
                        {'normalized_text': '.', 'lemma': '.', 'root': '.', 'root_tokens': ['.'], 'ending': '',
                         'clitic': '', 'form': '', 'partofspeech': 'Z'}]}, {'base_span': (52, 55), 'annotations': [
                        {'normalized_text': 'Iga', 'lemma': 'iga', 'root': 'iga', 'root_tokens': ['iga'], 'ending': '0',
                         'clitic': '', 'form': 'sg n', 'partofspeech': 'P'}]}, {'base_span': (56, 64), 'annotations': [
                        {'normalized_text': 'osavõtja', 'lemma': 'osavõtja', 'root': 'osa_võtja',
                         'root_tokens': ['osa', 'võtja'], 'ending': '0', 'clitic': '', 'form': 'sg n',
                         'partofspeech': 'S'}]}, {'base_span': (65, 71), 'annotations': [
                        {'normalized_text': 'tundis', 'lemma': 'tundma', 'root': 'tund', 'root_tokens': ['tund'],
                         'ending': 'is', 'clitic': '', 'form': 's', 'partofspeech': 'V'}]}, {'base_span': (72, 78),
                                                                                             'annotations': [{
                                                                                                 'normalized_text': 'ennast',
                                                                                                 'lemma': 'ise',
                                                                                                 'root': 'ise',
                                                                                                 'root_tokens': [
                                                                                                     'ise'],
                                                                                                 'ending': 't',
                                                                                                 'clitic': '',
                                                                                                 'form': 'sg p',
                                                                                                 'partofspeech': 'P'}]},
                    {'base_span': (79, 88), 'annotations': [
                        {'normalized_text': 'targemana', 'lemma': 'targem', 'root': 'targem', 'root_tokens': ['targem'],
                         'ending': 'na', 'clitic': '', 'form': 'sg es', 'partofspeech': 'C'}]}, {'base_span': (88, 89),
                                                                                                 'annotations': [{
                                                                                                     'normalized_text': '.',
                                                                                                     'lemma': '.',
                                                                                                     'root': '.',
                                                                                                     'root_tokens': [
                                                                                                         '.'],
                                                                                                     'ending': '',
                                                                                                     'clitic': '',
                                                                                                     'form': '',
                                                                                                     'partofspeech': 'Z'}]}]},
            {'name': 'sentences', 'attributes': (), 'parent': None, 'enveloping': 'words', 'ambiguous': False,
             'serialisation_module': None, 'meta': {}, 'spans': [
                {'base_span': ((0, 10), (11, 14), (15, 22), (23, 27), (28, 38), (39, 41), (42, 50), (50, 51)),
                 'annotations': [{}]},
                {'base_span': ((52, 55), (56, 64), (65, 71), (72, 78), (79, 88), (88, 89)), 'annotations': [{}]}]},
            {'name': 'stanza_syntax',
             'attributes': ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'),
             'parent': 'morph_analysis', 'enveloping': None, 'ambiguous': False, 'serialisation_module': None,
             'meta': {}, 'spans': [{'base_span': (0, 10), 'annotations': [
                {'id': 1, 'lemma': 'Hispaania', 'upostag': 'H', 'xpostag': 'H',
                 'feats': OrderedDict([('sg', 'sg'), ('in', 'in')]), 'head': 3, 'deprel': 'obl', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (11, 14), 'annotations': [
                {'id': 2, 'lemma': 'olema', 'upostag': 'V', 'xpostag': 'V', 'feats': OrderedDict([('s', 's')]),
                 'head': 3, 'deprel': 'cop', 'deps': '_', 'misc': '_'}]}, {'base_span': (15, 22), 'annotations': [
                {'id': 3, 'lemma': 'komme', 'upostag': 'S', 'xpostag': 'S',
                 'feats': OrderedDict([('sg', 'sg'), ('tr', 'tr')]), 'head': 0, 'deprel': 'root', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (23, 27), 'annotations': [
                {'id': 4, 'lemma': 'andma', 'upostag': 'V', 'xpostag': 'V', 'feats': OrderedDict([('da', 'da')]),
                 'head': 3, 'deprel': 'csubj:cop', 'deps': '_', 'misc': '_'}]}, {'base_span': (28, 38), 'annotations': [
                {'id': 5, 'lemma': 'jootraha', 'upostag': 'S', 'xpostag': 'S',
                 'feats': OrderedDict([('sg', 'sg'), ('tr', 'tr')]), 'head': 4, 'deprel': 'xcomp', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (39, 41), 'annotations': [
                {'id': 6, 'lemma': '25', 'upostag': 'N', 'xpostag': 'N', 'feats': OrderedDict([('?', '?')]), 'head': 7,
                 'deprel': 'nummod', 'deps': '_', 'misc': '_'}]}, {'base_span': (42, 50), 'annotations': [
                {'id': 7, 'lemma': 'peseeta', 'upostag': 'S', 'xpostag': 'S',
                 'feats': OrderedDict([('sg', 'sg'), ('p', 'p')]), 'head': 4, 'deprel': 'obj', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (50, 51), 'annotations': [
                {'id': 8, 'lemma': '.', 'upostag': 'Z', 'xpostag': 'Z', 'feats': OrderedDict(), 'head': 3,
                 'deprel': 'punct', 'deps': '_', 'misc': '_'}]}, {'base_span': (52, 55), 'annotations': [
                {'id': 1, 'lemma': 'iga', 'upostag': 'P', 'xpostag': 'P',
                 'feats': OrderedDict([('sg', 'sg'), ('n', 'n')]), 'head': 2, 'deprel': 'det', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (56, 64), 'annotations': [
                {'id': 2, 'lemma': 'osavõtja', 'upostag': 'S', 'xpostag': 'S',
                 'feats': OrderedDict([('sg', 'sg'), ('n', 'n')]), 'head': 3, 'deprel': 'nsubj', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (65, 71), 'annotations': [
                {'id': 3, 'lemma': 'tundma', 'upostag': 'V', 'xpostag': 'V', 'feats': OrderedDict([('s', 's')]),
                 'head': 0, 'deprel': 'root', 'deps': '_', 'misc': '_'}]}, {'base_span': (72, 78), 'annotations': [
                {'id': 4, 'lemma': 'ise', 'upostag': 'P', 'xpostag': 'P',
                 'feats': OrderedDict([('sg', 'sg'), ('p', 'p')]), 'head': 5, 'deprel': 'obj', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (79, 88), 'annotations': [
                {'id': 5, 'lemma': 'targem', 'upostag': 'C', 'xpostag': 'C',
                 'feats': OrderedDict([('sg', 'sg'), ('es', 'es')]), 'head': 3, 'deprel': 'advcl', 'deps': '_',
                 'misc': '_'}]}, {'base_span': (88, 89), 'annotations': [
                {'id': 6, 'lemma': '.', 'upostag': 'Z', 'xpostag': 'Z', 'feats': OrderedDict(), 'head': 3,
                 'deprel': 'punct', 'deps': '_', 'misc': '_'}]}]}]}

    text = dict_to_text(input_text)
    dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer='stanza_syntax')
    agreement_retagger = DeprelAgreementRetagger(output_layer='stanza_syntax')
    dependency_retagger.retag(text)
    agreement_retagger.retag(text)

    layer = text['stanza_syntax']
    assert list(layer.agreement_deprel) == [None, None, None, None,
                                            {'obl'}, None, None, None,
                                            None, None, None, None,
                                            {'xcomp'}, None]
