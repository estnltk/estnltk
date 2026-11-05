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


# ===================================================================
#   Splitting discontinuous sections: span layers
# ===================================================================

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



# ===================================================================
#   Splitting discontinuous sections: relation layers
# ===================================================================

def create_example_text_with_relations():
    # 0         1         2         3         4         5         6
    # 0123456789012345678901234567890123456789012345678901234567890
    # Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).
    # 1   2 3    4    5        6 7   8      9  0       1    23  456
    # 0                                        1                   
    from estnltk_core import RelationLayer, EnvelopingBaseSpan
    text = create_example_text_1()
    text.add_layer( dict_to_layer( \
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
                    'base_span': ((54, 55), (55, 58), (58, 59), (59, 60))}] } ) )
    # Flat relation layer
    srl = RelationLayer('srl', span_names=('pred', 'arg'), attributes=('role',), text_object=text)
    srl.meta['source'] = 'test'
    srl.add_annotation(pred=(27, 30), arg=(0, 4),  role='subj')   # clause 0 (over the gap) # ['oli','Mees']       
    srl.add_annotation(pred=(16, 25), arg=(6, 10), role='obj')    # clause 1 (embedded)     # ['kohtasime','keda'] 
    srl.add_annotation(pred=(41, 48), arg=(49, 53), role='obj')   # clause 2                # ['teretas','meid']   
    srl.add_annotation(pred=(41, 48), arg=(0, 4),  role='subj')   # clause 2 -> clause 0    # ['teretas','Mees']   
    text.add_layer(srl)
    # Flat relation layer with a named span that covers the embedded clause
    phrases = RelationLayer('phrases', span_names=('phrase',), attributes=('id',), text_object=text)
    # relations covering clauses 0, 1 & 2 :
    phrases.add_annotation(phrase=(0, 30), id=0)   # 'Mees, keda seal kohtasime, oli'
    # relation covering clause 2 :
    phrases.add_annotation(phrase=(31, 37), id=1)  # 'tuttav'
    text.add_layer(phrases)
    # Enveloping relation layer (over words)
    w = {word.text: word.base_span for word in text['words']}
    deps = RelationLayer('deps', span_names=('head', 'dep'), attributes=('deprel',),
                         enveloping='words', ambiguous=True, text_object=text)
    # relations covering clauses 0 & 2 :
    deps.add_annotation(head=EnvelopingBaseSpan([w['oli']]), dep=EnvelopingBaseSpan([w['Mees']]), deprel='nsubj')
    deps.add_annotation(head=EnvelopingBaseSpan([w['oli']]), dep=EnvelopingBaseSpan([w['Mees']]), deprel='nsubj:cop')
    # relation covering clauses 0 & 1 :
    deps.add_annotation(head=EnvelopingBaseSpan([w['Mees']]), 
                        dep=EnvelopingBaseSpan([w['keda'], w['seal'], w['kohtasime']]), deprel='acl:relcl') 
    # Named span with words from both halves of clause 0 :
    # (relation covering clauses 0 & 2)
    deps.add_annotation(head=EnvelopingBaseSpan([w['Mees'], w['oli'], w['tuttav']]), deprel='phrase') 
    text.add_layer(deps)
    return text


def _rel_tuples(layer):
    return [ ( {ns.name: ns.text for ns in rel.spans}, [dict(a) for a in rel.annotations] ) for rel in layer ]


def test_split_by_clauses_with_relation_layers():
    from estnltk_core import ElementaryBaseSpan, EnvelopingBaseSpan
    text = create_example_text_with_relations()
    layers_to_keep = list(text.layers) + list(text.relation_layers)
    clause_texts = _split_by_discontinuous_layer(text, 'clauses', layers_to_keep=layers_to_keep)
    assert [t.text for t in clause_texts] == \
        ['Mees oli tuttav ja', ', keda seal kohtasime,', 'teretas meid.', '(sic!)']
    for t in clause_texts:
        assert t.relation_layers == {'srl', 'phrases', 'deps'}
        assert t['srl'].text_object is t
        assert t['srl'].meta == {'source': 'test'}
        assert t['deps'].enveloping == 'words'
        assert t['deps'].ambiguous
    t0, t1, t2, t3 = clause_texts
    # Clause 0 ('Mees' + 'oli tuttav ja'): relation over the gap is preserved
    assert _rel_tuples(t0['srl']) == [({'pred': 'oli', 'arg': 'Mees'}, [{'role': 'subj'}])]
    assert t0['srl'][0]['pred'].base_span == ElementaryBaseSpan(5, 8) # 'oli'
    assert t0['srl'][0]['arg'].base_span == ElementaryBaseSpan(0, 4)  # 'Mees'
    # 'Mees, keda seal kohtasime, oli' covers the gap -> dropped without trimming
    assert _rel_tuples(t0['phrases']) == [({'phrase': 'tuttav'}, [{'id': 1}])]
    assert t0['phrases'][0]['phrase'].base_span == ElementaryBaseSpan(9, 15)
    # Preserve 'deps' that cover clauses 0 & 2
    assert _rel_tuples(t0['deps']) == [({'head': ['oli'], 'dep': ['Mees']}, [{'deprel': 'nsubj'}, {'deprel': 'nsubj:cop'}]),
                                       ({'head': ['Mees', 'oli', 'tuttav']}, [{'deprel': 'phrase'}])]
    # t0['deps'][1]['head'] --> ['Mees', 'oli', 'tuttav']
    assert t0['deps'][1]['head'].base_span == \
        EnvelopingBaseSpan([ElementaryBaseSpan(0, 4), ElementaryBaseSpan(5, 8), ElementaryBaseSpan(9, 15)])
    # Clause 1 (embedded) (', keda seal kohtasime,')
    assert _rel_tuples(t1['srl']) == [({'pred': 'kohtasime', 'arg': 'keda'}, [{'role': 'obj'}])]
    assert t1['srl'][0]['pred'].base_span == ElementaryBaseSpan(12, 21)
    # 'phrases' & 'deps' are empty, because they only contain relations covering multiple clauses
    assert len(t1['phrases']) == 0
    assert len(t1['deps']) == 0
    # Clause 2 ('teretas meid.'): relation that points to clause 0 is dropped
    assert _rel_tuples(t2['srl']) == [({'pred': 'teretas', 'arg': 'meid'}, [{'role': 'obj'}])]
    # Clause 3 ('(sic!)'): no relations
    assert [len(t3[l]) for l in ('srl', 'phrases', 'deps')] == [0, 0, 0]


def test_split_by_clauses_with_relation_layers_partial_relations():
    text = create_example_text_with_relations()
    layers_to_keep = list(text.layers) + list(text.relation_layers)
    t0, t1, t2, t3 = _split_by_discontinuous_layer(text, 'clauses', layers_to_keep=layers_to_keep,
                                                   keep_partial_relations=True)
    assert _rel_tuples(t0['srl']) == [({'pred': 'oli', 'arg': 'Mees'}, [{'role': 'subj'}]),
                                      ({'arg': 'Mees'}, [{'role': 'subj'}])] # dropped 'pred':'teretas'
    assert _rel_tuples(t2['srl']) == [({'pred': 'teretas', 'arg': 'meid'}, [{'role': 'obj'}]),
                                      ({'pred': 'teretas'}, [{'role': 'subj'}])] # dropped 'arg': 'Mees'
    # dropped: 'head':['oli'] (clause 2) from the following:
    assert _rel_tuples(t0['deps'])[1] == ({'head': ['Mees']}, [{'deprel': 'acl:relcl'}]) 
    # dropped: 'head': ['Mees'] (clause 0) from the following:
    assert _rel_tuples(t1['deps']) == [({'dep': ['keda', 'seal', 'kohtasime']}, [{'deprel': 'acl:relcl'}])]
    # without trimming, a named span covering the gap is still dropped
    assert _rel_tuples(t0['phrases']) == [({'phrase': 'tuttav'}, [{'id': 1}])]
    assert len(t1['phrases']) == 0


def test_split_by_clauses_with_relation_layers_trim_overlapping():
    from estnltk_core import ElementaryBaseSpan
    text = create_example_text_with_relations()
    layers_to_keep = list(text.layers) + list(text.relation_layers)
    # keep_partial_relations='auto' -> follows trim_overlapping=True
    t0, t1, t2, t3 = _split_by_discontinuous_layer(text, 'clauses', layers_to_keep=layers_to_keep,
                                                   trim_overlapping=True)
    #
    # Original 'phrases':
    #     [{'phrase': 'Mees, keda seal kohtasime, oli', 'id': 0}, 
    #      {'phrase': 'tuttav', 'id': 1}]
    #
    # 'Mees, keda seal kohtasime, oli' is trimmed to its parts inside the clause:
    # 'Mees' + ' oli' that are joined in the clause text
    assert _rel_tuples(t0['phrases']) == [({'phrase': 'Mees oli'}, [{'id': 0}]),
                                          ({'phrase': 'tuttav'}, [{'id': 1}])]
    assert t0['phrases'][0].spans[0].base_span == ElementaryBaseSpan(0, 8)
    # Embedded clause is completely inside the phrase
    assert _rel_tuples(t1['phrases']) == [({'phrase': ', keda seal kohtasime,'}, [{'id': 0}])]
    assert _rel_tuples(t2['srl']) == [({'pred': 'teretas', 'arg': 'meid'}, [{'role': 'obj'}]),
                                      ({'pred': 'teretas'}, [{'role': 'subj'}])]  # dropped: 'arg': 'Mees'
    # trimming without partial relations
    t0, t1, t2, t3 = _split_by_discontinuous_layer(text, 'clauses', layers_to_keep=layers_to_keep,
                                                   trim_overlapping=True, keep_partial_relations=False)
    # dropped partial relation ({'pred': 'teretas'}, [{'role': 'subj'}]) in the following:
    assert _rel_tuples(t2['srl']) == [({'pred': 'teretas', 'arg': 'meid'}, [{'role': 'obj'}])]
    # the 'phrases' layer is not affected:
    assert _rel_tuples(t0['phrases']) == [({'phrase': 'Mees oli'}, [{'id': 0}]),
                                          ({'phrase': 'tuttav'}, [{'id': 1}])]


def test_extract_discontinuous_sections_with_relation_layers():
    import copy, pickle
    from estnltk_core.converters import text_to_json, json_to_text
    from estnltk_core.layer_operations.iterators.splitting_discontinuous import extract_discontinuous_sections
    text = create_example_text_with_relations()
    # layers_to_keep=None: all layers (including relation layers) are kept
    # Extract: [['Mees', 'oli tuttav ja'], ['Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).']]
    t0, t_all = extract_discontinuous_sections(text, [[(0, 4), (26, 40)], [(0, 61)]])
    assert t0.relation_layers == {'srl', 'phrases', 'deps'}
    # Dropped {'pred': 'teretas', 'arg': 'Mees', 'role': 'subj'} in the following:
    assert _rel_tuples(t0['srl']) == [({'pred': 'oli', 'arg': 'Mees'}, [{'role': 'subj'}])]
    # A section covering the whole text reproduces the text
    assert t_all == text, t_all.diff(text)
    # Extracted texts survive copying and serialisation
    for t in (t0, t_all):
        assert copy.deepcopy(t) == t
        assert pickle.loads(pickle.dumps(t)) == t
        assert json_to_text(text_to_json(t)) == t
    # Relation layer without its enveloped layer in layers_to_keep
    import pytest
    with pytest.raises(AssertionError):
        # layers_to_keep missing 'words' required by 'deps'
        extract_discontinuous_sections(text, [[(0, 4), (26, 40)]], layers_to_keep=['deps'])
    # Only selected relation layers
    t0, = extract_discontinuous_sections(text, [[(0, 4), (26, 40)]], layers_to_keep=['srl'])
    assert t0.layers == set()
    assert t0.relation_layers == {'srl'}
    # Dropped {'pred': 'teretas', 'arg': 'Mees', 'role': 'subj'} in the following:
    assert _rel_tuples(t0['srl']) == [({'pred': 'oli', 'arg': 'Mees'}, [{'role': 'subj'}])]


def test_split_by_clauses_relation_layers_via_split_by():
    import warnings
    from estnltk_core.layer_operations import split_by, split_by_clauses
    text = create_example_text_with_relations()
    layers_to_keep = list(text.layers) + list(text.relation_layers)
    clause_texts = split_by(text, 'clauses', layers_to_keep=layers_to_keep)
    assert [len(t['srl']) for t in clause_texts] == [1, 1, 1, 0]
    clause_texts = split_by_clauses(text, layers_to_keep=layers_to_keep, keep_partial_relations=True)
    assert [len(t['srl']) for t in clause_texts] == [2, 1, 2, 0]
    # default layers_to_keep only contains span-layer dependencies
    # (and, actually, a relation layer also cannot be a dependency 
    #  of a span layer in the current implementation)
    clause_texts = split_by_clauses(text)
    assert all(t.relation_layers == set() for t in clause_texts)


def test_split_by_split_discontinuous_parameter():
    import pytest
    from estnltk_core.layer_operations import split_by
    text = create_example_text_with_relations()
    # Preparation: Copy of the clauses layer under a different name
    clauses_dict = layer_to_dict(text['clauses'])
    clauses_dict['name'] = 'my_clauses'
    text.add_layer( dict_to_layer(clauses_dict) )
    clauses_dict['name'] = 'segments'
    text.add_layer( dict_to_layer(clauses_dict) )
    layers_to_keep = ['words', 'srl']
    discontinuous_texts = ['Mees oli tuttav ja', ', keda seal kohtasime,', 'teretas meid.', '(sic!)']
    continuous_texts    = ['Mees, keda seal kohtasime, oli tuttav ja', ', keda seal kohtasime,', 
                           'teretas meid (sic!).', '(sic!)']
    # split_discontinuous="auto" (default): discontinuous iff the layer name contains 'clauses'
    for layer in ['clauses', 'my_clauses']:
        texts = split_by(text, layer, layers_to_keep=layers_to_keep+[layer])
        assert [t.text for t in texts] == discontinuous_texts
        assert [len(t['srl']) for t in texts] == [1, 1, 1, 0]
    texts = split_by(text, 'segments', layers_to_keep=layers_to_keep+['segments'])
    assert [t.text for t in texts] == continuous_texts
    assert [len(t['srl']) for t in texts] == [2, 1, 1, 0]
    # split_discontinuous=True: always discontinuous
    texts = split_by(text, 'segments', layers_to_keep=layers_to_keep+['segments'], split_discontinuous=True)
    assert [t.text for t in texts] == discontinuous_texts
    # split_discontinuous=False: never discontinuous
    texts = split_by(text, 'clauses', layers_to_keep=layers_to_keep+['clauses'], split_discontinuous=False)
    assert [t.text for t in texts] == continuous_texts
    # With continuous sections, the main clause also contains the embedded clause
    assert texts[0]['words'].text == ['Mees', ',', 'keda', 'seal', 'kohtasime', ',', 'oli', 'tuttav', 'ja']
    assert [len(t['srl']) for t in texts] == [2, 1, 1, 0]
    # Default layers_to_keep
    texts = split_by(text, 'my_clauses')
    assert [t.text for t in texts] == discontinuous_texts
    assert set(texts[0].layers) == {'words', 'my_clauses', 'morph_analysis'}
    # Non-enveloping layer: split_discontinuous=True gives an error:
    with pytest.raises(ValueError):
        # (!) Cannot split discontinuously by layer 'words': the layer must be enveloping.
        split_by(text, 'words', layers_to_keep=['words'], split_discontinuous=True)
    words_dict = layer_to_dict(text['words'])
    words_dict['name'] = 'flat_clauses'
    text.add_layer( dict_to_layer(words_dict) )
    # Non-enveloping layer: split_discontinuous="auto" (default) falls back to continuous splitting:
    texts = split_by(text, 'flat_clauses', layers_to_keep=['flat_clauses'])
    assert [t.text for t in texts[:8]] == ['Mees', ',', 'keda', 'seal', 'kohtasime', ',', 'oli', 'tuttav']
    # Invalid value
    with pytest.raises(ValueError):
        # split_discontinuous should be True, False or 'auto', not 'yes'
        split_by(text, 'clauses', split_discontinuous='yes')


# ===================================================================
#   Splitting by relation layers
# ===================================================================

def test_get_sorted_named_base_spans():
    from estnltk_core import RelationLayer, ElementaryBaseSpan, EnvelopingBaseSpan
    from estnltk_core.layer_operations.iterators.splitting_common import _get_sorted_named_base_spans
    text = create_example_text_with_relations()
    # Flat relation layer
    # Keep only unique spans by default:  
    # 'Mees', 'keda', 'kohtasime', 'oli', 'teretas', 'meid'
    assert _get_sorted_named_base_spans(text['srl']) == \
        [ElementaryBaseSpan(*loc) for loc in [(0, 4), (6, 10), (16, 25), (27, 30), (41, 48), (49, 53)]]
    # Keep all spans (incl duplicates) with unique=False: 
    # 'Mees', 'Mees', 'keda', 'kohtasime', 'oli', 'teretas', 'teretas', 'meid'
    assert len(_get_sorted_named_base_spans(text['srl'], unique=False)) == 8
    # Enveloping relation layer: spans with equal start are ordered by end
    assert [[text.text[s:e] for (s, e) in bs.flatten()] for bs in _get_sorted_named_base_spans(text['deps'])] == \
        [['Mees'], ['Mees', 'oli', 'tuttav'], ['keda', 'seal', 'kohtasime'], ['oli']]
    # Order of relations and named spans does not matter
    reversed_srl = RelationLayer('srl_rev', span_names=('arg', 'pred'), attributes=('role',), text_object=text)
    for relation in reversed(list(text['srl'])):
        reversed_srl.add_annotation(arg=relation['arg'].base_span, pred=relation['pred'].base_span,
                                    role=relation.annotations[0]['role'])
    text.add_layer(reversed_srl)
    assert _get_sorted_named_base_spans(text['srl_rev']) == _get_sorted_named_base_spans(text['srl'])
    # Empty layer
    text.add_layer(RelationLayer('empty_rel', span_names=('a',), text_object=text))
    assert _get_sorted_named_base_spans(text['empty_rel']) == []
    import pytest
    with pytest.raises(TypeError):
        # f'(!) Expected RelationLayer, but got Layer.'
        _get_sorted_named_base_spans(text['words'])


def test_layers_to_keep_default_for_relation_layers():
    from estnltk_core.layer_operations.iterators.splitting import layers_to_keep_default
    text = create_example_text_with_relations()
    # Splitting by a relation layer without dependencies only gives the input layer
    assert layers_to_keep_default(text, 'srl') == {'srl'}
    # Splitting by a relation layer with dependencies gives the input layer and corresponding dependencies
    assert layers_to_keep_default(text, 'deps') == {'deps', 'words', 'morph_analysis'}


def test_split_by_flat_relation_layer():
    import pytest
    from estnltk_core.layer_operations import split_by
    from estnltk_core.layer_operations.iterators.splitting_discontinuous import _split_by_discontinuous_layer
    text = create_example_text_with_relations()
    # Splitting by a relation layer that has no dependencies
    texts = split_by(text, 'srl')
    assert [t.text for t in texts] == ['Mees', 'keda', 'kohtasime', 'oli', 'teretas', 'meid']
    assert all(t.layers == set() and t.relation_layers == {'srl'} for t in texts)
    # By default, trim_overlapping/keep_partial_relations are switched off, so relations 
    # exceeding (named) span boundaries will be deleted
    assert [len(t['srl']) for t in texts] == [0, 0, 0, 0, 0, 0]
    # Relations with all named spans inside a section are carried over
    #
    # Original 'phrases':
    #     [{'phrase': 'Mees, keda seal kohtasime, oli', 'id': 0}, 
    #      {'phrase': 'tuttav', 'id': 1}]
    #
    texts = split_by(text, 'phrases', layers_to_keep=['words', 'srl', 'phrases'])
    assert [t.text for t in texts] == ['Mees, keda seal kohtasime, oli', 'tuttav']
    assert texts[0]['words'].text == ['Mees', ',', 'keda', 'seal', 'kohtasime', ',', 'oli']
    assert texts[1]['words'].text == ['tuttav']
    assert [len(t['srl']) for t in texts] == [2, 0]
    assert [len(t['phrases']) for t in texts] == [1, 1]
    # A flat relation layer cannot be split discontinuously
    with pytest.raises(ValueError):
        # (!) Cannot split discontinuously by layer 'srl': the layer must be enveloping.
        split_by(text, 'srl', split_discontinuous=True)
    with pytest.raises(ValueError):
        # (!) Cannot split discontinuously by layer 'srl': the layer must be enveloping.
        _split_by_discontinuous_layer(text, 'srl', layers_to_keep=['srl'])


def test_split_by_enveloping_relation_layer():
    from estnltk_core import RelationLayer
    from estnltk_core.layer_operations import split_by
    from estnltk_core.layer_operations.iterators.splitting_discontinuous import _split_by_discontinuous_layer
    text = create_example_text_with_relations()
    #
    # Original 'deps':
    #    [ ({'dep': ['Mees'], 'head': ['oli']}, 
    #                         [{'deprel': 'nsubj'}, {'deprel': 'nsubj:cop'}]), 
    #      ({'head': ['Mees'], 'dep': ['keda', 'seal', 'kohtasime']}, 
    #                         [{'deprel': 'acl:relcl'}]), 
    #      ({'head': ['Mees', 'oli', 'tuttav']}, 
    #                         [{'deprel': 'phrase'}]) 
    #    ]

    # continuous sections (default for a layer without 'clauses' in its name)
    texts = split_by(text, 'deps', layers_to_keep=['words', 'deps', 'srl'])
    assert [t.text for t in texts] == ['Mees', 'Mees, keda seal kohtasime, oli tuttav', 'keda seal kohtasime', 'oli']
    assert [len(t['deps']) for t in texts] == [0, 3, 0, 0]
    assert [len(t['srl']) for t in texts] == [0, 2, 1, 0]
    # discontinuous sections: the embedded clause is left out of the 2nd section
    texts = split_by(text, 'deps', layers_to_keep=['words', 'deps', 'srl'], split_discontinuous=True)
    assert [t.text for t in texts] == ['Mees', 'Mees oli tuttav', 'keda seal kohtasime', 'oli']
    assert texts[1]['words'].text == ['Mees', 'oli', 'tuttav']
    assert [len(t['deps']) for t in texts] == [0, 2, 0, 0]
    assert [len(t['srl']) for t in texts] == [0, 1, 1, 0]
    # keep_partial_relations
    texts = split_by(text, 'deps', layers_to_keep=['words', 'deps'], split_discontinuous=True,
                     keep_partial_relations=True)
    assert [len(t['deps']) for t in texts] == [2, 3, 1, 1]
    # default layers_to_keep
    texts = split_by(text, 'deps', split_discontinuous=True)
    assert [t.text for t in texts] == ['Mees', 'Mees oli tuttav', 'keda seal kohtasime', 'oli']
    assert texts[1].layers == {'words', 'morph_analysis'}
    assert texts[1].relation_layers == {'deps'}
    # _split_by_discontinuous_layer directly
    texts = _split_by_discontinuous_layer(text, 'deps', layers_to_keep=['words', 'deps'])
    assert [t.text for t in texts] == ['Mees', 'Mees oli tuttav', 'keda seal kohtasime', 'oli']
    # keep_partial_relations="auto": a relation layer with 'clauses' in its name is split discontinuously
    clause_rels = RelationLayer('clauses_rel', span_names=('clause',), attributes=('clause_type',),
                                enveloping='words', text_object=text)
    for clause in text['clauses']:
        clause_rels.add_annotation(clause=clause.base_span, clause_type=clause.annotations[0]['clause_type'])
    text.add_layer(clause_rels)
    texts = split_by(text, 'clauses_rel', layers_to_keep=['words', 'clauses_rel', 'srl'])
    assert [t.text for t in texts] == ['Mees oli tuttav ja', ', keda seal kohtasime,', 'teretas meid.', '(sic!)']
    assert [len(t['srl']) for t in texts] == [1, 1, 1, 0]
    # ... which gives the same results as splitting by the clauses layer
    clause_texts = split_by(text, 'clauses', layers_to_keep=['words', 'srl'])
    assert [t.text for t in texts] == [t.text for t in clause_texts]
    assert [t['words'] for t in texts] == [t['words'] for t in clause_texts]
    assert [t['srl'] for t in texts] == [t['srl'] for t in clause_texts]
