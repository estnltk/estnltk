from estnltk_core.converters import dict_to_text
from estnltk.taggers.standard.syntax.ud_validation.ud_validation_retagger import UDValidationRetagger


def test_ud_validation_retagger():
    input_text_dict = {'text': 'Võid mõelda nii, et ise oledki mulla sees ja mis sulle seal hea on, mis mitte.',
                       'meta': {}, 'layers': [
            {'name': 'words', 'attributes': ('normalized_form',), 'parent': None, 'enveloping': None, 'ambiguous': True,
             'serialisation_module': None, 'meta': {},
             'spans': [{'base_span': (0, 4), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (5, 11), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (12, 15), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (15, 16), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (17, 19), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (20, 23), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (24, 30), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (31, 36), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (37, 41), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (42, 44), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (45, 48), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (49, 54), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (55, 59), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (60, 63), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (64, 66), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (66, 67), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (68, 71), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (72, 77), 'annotations': [{'normalized_form': None}]},
                       {'base_span': (77, 78), 'annotations': [{'normalized_form': None}]}]}, {'name': 'morph_analysis',
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
                    {'base_span': (0, 4), 'annotations': [
                        {'normalized_text': 'Võid', 'lemma': 'võima', 'root': 'või', 'root_tokens': ['või'],
                         'ending': 'd', 'clitic': '', 'form': 'd', 'partofspeech': 'V'}]}, {'base_span': (5, 11),
                                                                                            'annotations': [{
                                                                                                'normalized_text': 'mõelda',
                                                                                                'lemma': 'mõtlema',
                                                                                                'root': 'mõtle',
                                                                                                'root_tokens': [
                                                                                                    'mõtle'],
                                                                                                'ending': 'da',
                                                                                                'clitic': '',
                                                                                                'form': 'da',
                                                                                                'partofspeech': 'V'}]},
                    {'base_span': (12, 15), 'annotations': [
                        {'normalized_text': 'nii', 'lemma': 'nii', 'root': 'nii', 'root_tokens': ['nii'], 'ending': '0',
                         'clitic': '', 'form': '', 'partofspeech': 'D'}]}, {'base_span': (15, 16), 'annotations': [
                        {'normalized_text': ',', 'lemma': ',', 'root': ',', 'root_tokens': [','], 'ending': '',
                         'clitic': '', 'form': '', 'partofspeech': 'Z'}]}, {'base_span': (17, 19), 'annotations': [
                        {'normalized_text': 'et', 'lemma': 'et', 'root': 'et', 'root_tokens': ['et'], 'ending': '0',
                         'clitic': '', 'form': '', 'partofspeech': 'J'}]}, {'base_span': (20, 23), 'annotations': [
                        {'normalized_text': 'ise', 'lemma': 'ise', 'root': 'ise', 'root_tokens': ['ise'], 'ending': '0',
                         'clitic': '', 'form': 'pl n', 'partofspeech': 'P'},
                        {'normalized_text': 'ise', 'lemma': 'ise', 'root': 'ise', 'root_tokens': ['ise'], 'ending': '0',
                         'clitic': '', 'form': 'sg n', 'partofspeech': 'P'}]}, {'base_span': (24, 30), 'annotations': [
                        {'normalized_text': 'oledki', 'lemma': 'olema', 'root': 'ole', 'root_tokens': ['ole'],
                         'ending': 'd', 'clitic': 'ki', 'form': 'd', 'partofspeech': 'V'}]}, {'base_span': (31, 36),
                                                                                              'annotations': [{
                                                                                                  'normalized_text': 'mulla',
                                                                                                  'lemma': 'muld',
                                                                                                  'root': 'muld',
                                                                                                  'root_tokens': [
                                                                                                      'muld'],
                                                                                                  'ending': '0',
                                                                                                  'clitic': '',
                                                                                                  'form': 'sg g',
                                                                                                  'partofspeech': 'S'},
                                                                                                  {
                                                                                                      'normalized_text': 'mulla',
                                                                                                      'lemma': 'mulla',
                                                                                                      'root': 'mulla',
                                                                                                      'root_tokens': [
                                                                                                          'mulla'],
                                                                                                      'ending': '0',
                                                                                                      'clitic': '',
                                                                                                      'form': 'sg g',
                                                                                                      'partofspeech': 'S'}]},
                    {'base_span': (37, 41), 'annotations': [
                        {'normalized_text': 'sees', 'lemma': 'sees', 'root': 'sees', 'root_tokens': ['sees'],
                         'ending': '0', 'clitic': '', 'form': '', 'partofspeech': 'K'}]}, {'base_span': (42, 44),
                                                                                           'annotations': [
                                                                                               {'normalized_text': 'ja',
                                                                                                'lemma': 'ja',
                                                                                                'root': 'ja',
                                                                                                'root_tokens': ['ja'],
                                                                                                'ending': '0',
                                                                                                'clitic': '',
                                                                                                'form': '',
                                                                                                'partofspeech': 'J'}]},
                    {'base_span': (45, 48), 'annotations': [
                        {'normalized_text': 'mis', 'lemma': 'mis', 'root': 'mis', 'root_tokens': ['mis'], 'ending': '0',
                         'clitic': '', 'form': 'pl n', 'partofspeech': 'P'},
                        {'normalized_text': 'mis', 'lemma': 'mis', 'root': 'mis', 'root_tokens': ['mis'], 'ending': '0',
                         'clitic': '', 'form': 'sg n', 'partofspeech': 'P'}]}, {'base_span': (49, 54), 'annotations': [
                        {'normalized_text': 'sulle', 'lemma': 'sina', 'root': 'sina', 'root_tokens': ['sina'],
                         'ending': 'lle', 'clitic': '', 'form': 'sg all', 'partofspeech': 'P'}]},
                    {'base_span': (55, 59), 'annotations': [
                        {'normalized_text': 'seal', 'lemma': 'seal', 'root': 'seal', 'root_tokens': ['seal'],
                         'ending': '0', 'clitic': '', 'form': '', 'partofspeech': 'D'}]}, {'base_span': (60, 63),
                                                                                           'annotations': [{
                                                                                               'normalized_text': 'hea',
                                                                                               'lemma': 'hea',
                                                                                               'root': 'hea',
                                                                                               'root_tokens': [
                                                                                                   'hea'],
                                                                                               'ending': '0',
                                                                                               'clitic': '',
                                                                                               'form': 'sg n',
                                                                                               'partofspeech': 'A'}]},
                    {'base_span': (64, 66), 'annotations': [
                        {'normalized_text': 'on', 'lemma': 'olema', 'root': 'ole', 'root_tokens': ['ole'],
                         'ending': '0', 'clitic': '', 'form': 'b', 'partofspeech': 'V'},
                        {'normalized_text': 'on', 'lemma': 'olema', 'root': 'ole', 'root_tokens': ['ole'],
                         'ending': '0', 'clitic': '', 'form': 'vad', 'partofspeech': 'V'}]}, {'base_span': (66, 67),
                                                                                              'annotations': [{
                                                                                                  'normalized_text': ',',
                                                                                                  'lemma': ',',
                                                                                                  'root': ',',
                                                                                                  'root_tokens': [
                                                                                                      ','],
                                                                                                  'ending': '',
                                                                                                  'clitic': '',
                                                                                                  'form': '',
                                                                                                  'partofspeech': 'Z'}]},
                    {'base_span': (68, 71), 'annotations': [
                        {'normalized_text': 'mis', 'lemma': 'mis', 'root': 'mis', 'root_tokens': ['mis'], 'ending': '0',
                         'clitic': '', 'form': 'pl n', 'partofspeech': 'P'},
                        {'normalized_text': 'mis', 'lemma': 'mis', 'root': 'mis', 'root_tokens': ['mis'], 'ending': '0',
                         'clitic': '', 'form': 'sg n', 'partofspeech': 'P'}]}, {'base_span': (72, 77), 'annotations': [
                        {'normalized_text': 'mitte', 'lemma': 'mitte', 'root': 'mitte', 'root_tokens': ['mitte'],
                         'ending': '0', 'clitic': '', 'form': '', 'partofspeech': 'D'}]}, {'base_span': (77, 78),
                                                                                           'annotations': [
                                                                                               {'normalized_text': '.',
                                                                                                'lemma': '.',
                                                                                                'root': '.',
                                                                                                'root_tokens': ['.'],
                                                                                                'ending': '',
                                                                                                'clitic': '',
                                                                                                'form': '',
                                                                                                'partofspeech': 'Z'}]}]},
            {'name': 'stanza_ma', 'attributes': (
                'id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'),
             'parent': 'morph_analysis', 'enveloping': None, 'ambiguous': False, 'serialisation_module': None,
             'meta': {}, 'spans': [{'base_span': (0, 4), 'annotations': [
                {'id': 1, 'lemma': 'võima', 'upostag': 'V', 'xpostag': 'V', 'feats': 'd=d', 'head': 2, 'deprel': 'aux',
                 'deps': '_', 'misc': '_'}]}, {'base_span': (5, 11), 'annotations': [
                {'id': 2, 'lemma': 'mõtlema', 'upostag': 'V', 'xpostag': 'V', 'feats': 'da=da', 'head': 0,
                 'deprel': 'root', 'deps': '_', 'misc': '_'}]}, {'base_span': (12, 15),
                                                                                  'annotations': [
                                                                                      {'id': 3, 'lemma': 'nii',
                                                                                       'upostag': 'D', 'xpostag': 'D',
                                                                                       'feats': '_', 'head': 1,
                                                                                       'deprel': 'advmod', 'deps': '_',
                                                                                       'misc': '_'}]},
                                   {'base_span': (15, 16), 'annotations': [
                                       {'id': 4, 'lemma': ',', 'upostag': 'Z', 'xpostag': 'Z', 'feats': '_', 'head': 8,
                                        'deprel': 'punct', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (17, 19), 'annotations': [
                                       {'id': 5, 'lemma': 'et', 'upostag': 'J', 'xpostag': 'J', 'feats': '_', 'head': 8,
                                        'deprel': 'mark', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (20, 23), 'annotations': [
                                       {'id': 6, 'lemma': 'ise', 'upostag': 'P', 'xpostag': 'P', 'feats': 'pl=pl|n=n',
                                        'head': 8, 'deprel': 'obl', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (24, 30), 'annotations': [
                                       {'id': 7, 'lemma': 'olema', 'upostag': 'V', 'xpostag': 'V', 'feats': 'd=d',
                                        'head': 8, 'deprel': 'cop', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (31, 36), 'annotations': [
                                       {'id': 8, 'lemma': 'muld', 'upostag': 'S', 'xpostag': 'S', 'feats': 'sg=sg|g=g',
                                        'head': 2, 'deprel': 'ccomp', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (37, 41), 'annotations': [
                                       {'id': 9, 'lemma': 'sees', 'upostag': 'K', 'xpostag': 'K', 'feats': '_',
                                        'head': 8, 'deprel': 'case', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (42, 44), 'annotations': [
                                       {'id': 10, 'lemma': 'ja', 'upostag': 'J', 'xpostag': 'J', 'feats': '_',
                                        'head': 14, 'deprel': 'cc', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (45, 48), 'annotations': [
                                       {'id': 11, 'lemma': 'mis', 'upostag': 'P', 'xpostag': 'P', 'feats': 'pl=pl|n=n',
                                        'head': 14, 'deprel': 'nsubj:cop', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (49, 54), 'annotations': [
                                       {'id': 12, 'lemma': 'sina', 'upostag': 'P', 'xpostag': 'P',
                                        'feats': 'sg=sg|all=all', 'head': 14, 'deprel': 'obl', 'deps': '_', 'misc': '_'}]}, {'base_span': (55, 59), 'annotations': [
                    {'id': 13, 'lemma': 'seal', 'upostag': 'D', 'xpostag': 'D', 'feats': '_', 'head': 14,
                     'deprel': 'advmod', 'deps': '_', 'misc': '_'}]}, {'base_span': (60, 63),
                                                                                        'annotations': [
                                                                                            {'id': 14, 'lemma': 'hea',
                                                                                             'upostag': 'A',
                                                                                             'xpostag': 'A',
                                                                                             'feats': 'sg=sg|n=n',
                                                                                             'head': 8,
                                                                                             'deprel': 'conj',
                                                                                             'deps': '_', 'misc': '_'}]},
                                   {'base_span': (64, 66), 'annotations': [
                                       {'id': 15, 'lemma': 'olema', 'upostag': 'V', 'xpostag': 'V', 'feats': 'b=b',
                                        'head': 14, 'deprel': 'cop', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (66, 67), 'annotations': [
                                       {'id': 16, 'lemma': ',', 'upostag': 'Z', 'xpostag': 'Z', 'feats': '_',
                                        'head': 17, 'deprel': 'punct', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (68, 71), 'annotations': [
                                       {'id': 17, 'lemma': 'mis', 'upostag': 'P', 'xpostag': 'P', 'feats': 'pl=pl|n=n',
                                        'head': 14, 'deprel': 'nsubj:cop', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (72, 77), 'annotations': [
                                       {'id': 18, 'lemma': 'mitte', 'upostag': 'D', 'xpostag': 'D', 'feats': '_',
                                        'head': 17, 'deprel': 'orphan', 'deps': '_', 'misc': '_'}]},
                                   {'base_span': (77, 78), 'annotations': [
                                       {'id': 19, 'lemma': '.', 'upostag': 'Z', 'xpostag': 'Z', 'feats': '_', 'head': 2,
                                        'deprel': 'punct', 'deps': '_', 'misc': '_'}]}]}]}

    text = dict_to_text(input_text_dict)
    retagger = UDValidationRetagger(output_layer='stanza_ma')
    retagger.retag(text)

    layer = text.stanza_ma

    assert list(layer.syntax_error) == [0, 0, 1, 0, 0,
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0,
                                      0, 0, 1, 0]

    assert layer.error_message[2] is not None and layer.error_message[-2] is not None
