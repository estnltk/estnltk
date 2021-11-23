from estnltk_core import Layer

from estnltk_core.layer_operations.iterators.splitting_discontinuous import group_consecutive_spans
from estnltk_core.layer_operations.iterators.splitting_discontinuous import _split_by_discontinuous_layer

from estnltk_core.converters import layer_to_dict
from estnltk_core.converters import dict_to_layer

from estnltk_core.common import load_text_class


def test_group_consecutive_spans():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Test grouping consecutive spans on the clauses layer
    text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).')
    words_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 4)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (4, 5)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (6, 10)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (11, 15)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (16, 25)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (25, 26)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (27, 30)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (31, 37)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (38, 40)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (41, 48)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (49, 53)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (54, 55)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (55, 58)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (58, 59)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (59, 60)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (60, 61)}]} )
    text.add_layer( words_layer )
    clauses_layer = dict_to_layer( \
       { 'ambiguous': False,
         'attributes': ('clause_type',),
         'enveloping': 'words',
         'meta': {},
         'name': 'clauses',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((0, 4), (27, 30), (31, 37), (38, 40))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((4, 5), (6, 10), (11, 15), (16, 25), (25, 26))},
                   {'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((41, 48), (49, 53), (60, 61))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((54, 55), (55, 58), (58, 59), (59, 60))}] } )
    text.add_layer( clauses_layer )
    all_consecutive_locs = []
    for clause in text['clauses']:
        consecutive_span_locs = group_consecutive_spans(text.text, clause)
        all_consecutive_locs.append( consecutive_span_locs )
    expected_all_consecutive_locs = \
        [[(0, 4), (26, 40)], [(4, 26)], [(41, 53), (60, 61)], [(54, 60)]]
    assert expected_all_consecutive_locs == all_consecutive_locs
    expected_consecutive_loc_texts = \
        [['Mees', ' oli tuttav ja'], [', keda seal kohtasime,'], ['teretas meid', '.'], ['(sic!)']]
    all_consecutive_loc_texts = \
        [[text.text[start:end] for start,end in sublist] for sublist in all_consecutive_locs]
    assert expected_consecutive_loc_texts == all_consecutive_loc_texts



def create_example_text_1():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).')
    words_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 4)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (4, 5)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (6, 10)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (11, 15)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (16, 25)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (25, 26)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (27, 30)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (31, 37)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (38, 40)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (41, 48)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (49, 53)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (54, 55)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (55, 58)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (58, 59)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (59, 60)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (60, 61)}]} )
    text.add_layer( words_layer )
    sentences_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': 'words',
         'meta': {},
         'name': 'sentences',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{}],
                    'base_span': ((0, 4),
                                  (4, 5),
                                  (6, 10),
                                  (11, 15),
                                  (16, 25),
                                  (25, 26),
                                  (27, 30),
                                  (31, 37),
                                  (38, 40),
                                  (41, 48),
                                  (49, 53),
                                  (54, 55),
                                  (55, 58),
                                  (58, 59),
                                  (59, 60),
                                  (60, 61))}]} )
    text.add_layer( sentences_layer )
    morph_analysis_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mees',
                                     'normalized_text': 'Mees',
                                     'partofspeech': 'S',
                                     'root': 'mees',
                                     'root_tokens': ['mees']}],
                    'base_span': (0, 4)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (4, 5)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'da',
                                     'form': 'pl p',
                                     'lemma': 'kes',
                                     'normalized_text': 'keda',
                                     'partofspeech': 'P',
                                     'root': 'kes',
                                     'root_tokens': ['kes']},
                                    {'clitic': '',
                                     'ending': 'da',
                                     'form': 'sg p',
                                     'lemma': 'kes',
                                     'normalized_text': 'keda',
                                     'partofspeech': 'P',
                                     'root': 'kes',
                                     'root_tokens': ['kes']}],
                    'base_span': (6, 10)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'seal',
                                     'normalized_text': 'seal',
                                     'partofspeech': 'D',
                                     'root': 'seal',
                                     'root_tokens': ['seal']}],
                    'base_span': (11, 15)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'sime',
                                     'form': 'sime',
                                     'lemma': 'kohtama',
                                     'normalized_text': 'kohtasime',
                                     'partofspeech': 'V',
                                     'root': 'kohta',
                                     'root_tokens': ['kohta']}],
                    'base_span': (16, 25)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (25, 26)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'i',
                                     'form': 's',
                                     'lemma': 'olema',
                                     'normalized_text': 'oli',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (27, 30)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'tuttav',
                                     'normalized_text': 'tuttav',
                                     'partofspeech': 'A',
                                     'root': 'tuttav',
                                     'root_tokens': ['tuttav']}],
                    'base_span': (31, 37)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'ja',
                                     'normalized_text': 'ja',
                                     'partofspeech': 'J',
                                     'root': 'ja',
                                     'root_tokens': ['ja']}],
                    'base_span': (38, 40)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 's',
                                     'lemma': 'teretama',
                                     'normalized_text': 'teretas',
                                     'partofspeech': 'V',
                                     'root': 'tereta',
                                     'root_tokens': ['tereta']}],
                    'base_span': (41, 48)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl p',
                                     'lemma': 'mina',
                                     'normalized_text': 'meid',
                                     'partofspeech': 'P',
                                     'root': 'mina',
                                     'root_tokens': ['mina']}],
                    'base_span': (49, 53)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '(',
                                     'normalized_text': '(',
                                     'partofspeech': 'Z',
                                     'root': '(',
                                     'root_tokens': ['(']}],
                    'base_span': (54, 55)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'sic',
                                     'normalized_text': 'sic',
                                     'partofspeech': 'S',
                                     'root': 'sic',
                                     'root_tokens': ['sic']}],
                    'base_span': (55, 58)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '!',
                                     'normalized_text': '!',
                                     'partofspeech': 'Z',
                                     'root': '!',
                                     'root_tokens': ['!']}],
                    'base_span': (58, 59)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ')',
                                     'normalized_text': ')',
                                     'partofspeech': 'Z',
                                     'root': ')',
                                     'root_tokens': [')']}],
                    'base_span': (59, 60)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (60, 61)}]} )
    text.add_layer( morph_analysis_layer )
    return text



def test_split_by_clauses_1():
    # Test split by clauses (do not trim overlapping layers)
    # text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).')
    text = create_example_text_1()
    clauses_layer_dict = \
       { 'ambiguous': False,
         'attributes': ('clause_type',),
         'enveloping': 'words',
         'meta': {},
         'name': 'clauses',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((0, 4), (27, 30), (31, 37), (38, 40))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((4, 5), (6, 10), (11, 15), (16, 25), (25, 26))},
                   {'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((41, 48), (49, 53), (60, 61))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((54, 55), (55, 58), (58, 59), (59, 60))}] }
    text.add_layer( dict_to_layer(clauses_layer_dict) )
    
    clause_texts = _split_by_discontinuous_layer(text, 'clauses',
                                                 layers_to_keep=list(text.layers),
                                                 trim_overlapping=False)
    
    assert len(clause_texts) == len(text['clauses'])
    assert clause_texts[0]['words'].text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1]['words'].text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2]['words'].text == ['teretas', 'meid', '.']
    assert clause_texts[3]['words'].text == ['(', 'sic', '!', ')']
    assert clause_texts[0]['morph_analysis'].text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1]['morph_analysis'].text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2]['morph_analysis'].text == ['teretas', 'meid', '.']
    assert clause_texts[3]['morph_analysis'].text == ['(', 'sic', '!', ')']
    assert len(clause_texts[0]['clauses']) == 0
    assert len(clause_texts[-1]['sentences']) == 0



def test_split_by_clauses_2():
    # Test split by clauses (trim overlapping layers)
    # text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).')
    text = create_example_text_1()
    clauses_layer_dict = \
       { 'ambiguous': False,
         'attributes': ('clause_type',),
         'enveloping': 'words',
         'meta': {},
         'name': 'clauses',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((0, 4), (27, 30), (31, 37), (38, 40))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((4, 5), (6, 10), (11, 15), (16, 25), (25, 26))},
                   {'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((41, 48), (49, 53), (60, 61))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((54, 55), (55, 58), (58, 59), (59, 60))}] }
    text.add_layer( dict_to_layer(clauses_layer_dict) )
    
    clause_texts = _split_by_discontinuous_layer(text, 'clauses',
                                                 layers_to_keep=list(text.layers),
                                                 trim_overlapping=True)
    
    assert len(clause_texts) == len(text['clauses'])
    assert clause_texts[0]['words'].text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1]['words'].text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2]['words'].text == ['teretas', 'meid', '.']
    assert clause_texts[3]['words'].text == ['(', 'sic', '!', ')']
    assert clause_texts[0]['morph_analysis'].text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1]['morph_analysis'].text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2]['morph_analysis'].text == ['teretas', 'meid', '.']
    assert clause_texts[3]['morph_analysis'].text == ['(', 'sic', '!', ')']
    assert clause_texts[0]['clauses'].text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1]['sentences'].text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2]['clauses'].text == ['teretas', 'meid', '.']
    assert clause_texts[3]['sentences'].text == ['(', 'sic', '!', ')']



def test_split_by_clauses_3_verb_chains():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Test split by clauses (trim overlapping layers) with verb chain annotations
    # A) Set up text and layers
    text = Text('Und pole, aga ma ei näe põhjust öö läbi üleval olla (sest magada on vaja!).')
    words_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 3)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (4, 8)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (8, 9)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (10, 13)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (14, 16)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (17, 19)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (20, 23)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (24, 31)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (32, 34)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (35, 39)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (40, 46)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (47, 51)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (52, 53)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (53, 57)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (58, 64)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (65, 67)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (68, 72)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (72, 73)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (73, 74)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (74, 75)}]} )
    text.add_layer( words_layer )
    sentences_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': 'words',
         'meta': {},
         'name': 'sentences',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{}],
                    'base_span': ((0, 3),
                                  (4, 8),
                                  (8, 9),
                                  (10, 13),
                                  (14, 16),
                                  (17, 19),
                                  (20, 23),
                                  (24, 31),
                                  (32, 34),
                                  (35, 39),
                                  (40, 46),
                                  (47, 51),
                                  (52, 53),
                                  (53, 57),
                                  (58, 64),
                                  (65, 67),
                                  (68, 72),
                                  (72, 73),
                                  (73, 74),
                                  (74, 75))}]} )
    text.add_layer( sentences_layer )
    clauses_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': ('clause_type',),
         'enveloping': 'words',
         'meta': {},
         'name': 'clauses',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((0, 3), (4, 8), (8, 9))},
                   {'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((10, 13),
                                  (14, 16),
                                  (17, 19),
                                  (20, 23),
                                  (24, 31),
                                  (32, 34),
                                  (35, 39),
                                  (40, 46),
                                  (47, 51),
                                  (74, 75))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((52, 53),
                                  (53, 57),
                                  (58, 64),
                                  (65, 67),
                                  (68, 72),
                                  (72, 73),
                                  (73, 74))}]} )
    text.add_layer( clauses_layer )
    verb_chains_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': ('pattern',
                        'roots',
                        'word_ids',
                        'mood',
                        'polarity',
                        'tense',
                        'voice',
                        'remaining_verbs'),
         'enveloping': 'words',
         'meta': {},
         'name': 'verb_chains',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'mood': 'indic',
                                     'pattern': ['pole'],
                                     'polarity': 'NEG',
                                     'remaining_verbs': False,
                                     'roots': ['ole'],
                                     'tense': 'present',
                                     'voice': 'personal',
                                     'word_ids': [1]}],
                    'base_span': ((4, 8),)},
                   {'annotations': [{'mood': 'indic',
                                     'pattern': ['ei', 'verb'],
                                     'polarity': 'NEG',
                                     'remaining_verbs': True,
                                     'roots': ['ei', 'näge'],
                                     'tense': 'present',
                                     'voice': 'personal',
                                     'word_ids': [5, 6]}],
                    'base_span': ((17, 19), (20, 23))},
                   {'annotations': [{'mood': 'indic',
                                     'pattern': ['ole', 'nom/adv', 'verb'],
                                     'polarity': 'POS',
                                     'remaining_verbs': True,
                                     'roots': ['ole', 'vaja', 'maga'],
                                     'tense': 'present',
                                     'voice': 'personal',
                                     'word_ids': [15, 16, 14]}],
                    'base_span': ((58, 64), (65, 67), (68, 72))}]} )
    text.add_layer( verb_chains_layer )

    # Test split by clauses (trim overlapping layers) with verb chain annotations
    # B) Split by clauses
    clause_texts = _split_by_discontinuous_layer(text, 'clauses',
                                                 layers_to_keep=list(text.layers),
                                                 trim_overlapping=True)
    # Validate results
    assert len(clause_texts) == len(text['clauses'])
    assert clause_texts[0]['clauses'].text == ['Und', 'pole', ',']
    assert clause_texts[1]['clauses'].text == ['aga', 'ma', 'ei', 'näe', 'põhjust', 'öö', 'läbi', 'üleval', 'olla', '.']
    assert clause_texts[2]['clauses'].text == ['(', 'sest', 'magada', 'on', 'vaja', '!', ')']
    assert clause_texts[0]['verb_chains'].text == ['pole']
    assert clause_texts[1]['verb_chains'].text == ['ei', 'näe']
    assert clause_texts[2]['verb_chains'].text == ['magada', 'on', 'vaja']


