from estnltk import Text, Layer

from estnltk.layer_operations.splitting_discontinuous import group_consecutive_spans
from estnltk.layer_operations.splitting_discontinuous import _split_by_discontinuous_layer

from estnltk.converters import layer_to_dict
from estnltk.converters import dict_to_layer


def test_group_consecutive_spans():
    # Test grouping consecutive spans on the clauses layer
    text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).')
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
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
    #from pprint import pprint
    #pprint(layer_to_dict(text['clauses']))
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



def test_split_by_clauses_1():
    # Test split by clauses (do not trim overlapping layers)
    text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).')
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
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
    assert clause_texts[0].words.text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1].words.text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2].words.text == ['teretas', 'meid', '.']
    assert clause_texts[3].words.text == ['(', 'sic', '!', ')']
    assert clause_texts[0].morph_analysis.text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1].morph_analysis.text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2].morph_analysis.text == ['teretas', 'meid', '.']
    assert clause_texts[3].morph_analysis.text == ['(', 'sic', '!', ')']
    assert len(clause_texts[0]['clauses']) == 0
    assert len(clause_texts[-1]['sentences']) == 0



def test_split_by_clauses_2():
    # Test split by clauses (trim overlapping layers)
    text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid (sic!).')
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
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
    assert clause_texts[0].words.text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1].words.text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2].words.text == ['teretas', 'meid', '.']
    assert clause_texts[3].words.text == ['(', 'sic', '!', ')']
    assert clause_texts[0].morph_analysis.text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1].morph_analysis.text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2].morph_analysis.text == ['teretas', 'meid', '.']
    assert clause_texts[3].morph_analysis.text == ['(', 'sic', '!', ')']
    assert clause_texts[0].clauses.text == ['Mees', 'oli', 'tuttav', 'ja']
    assert clause_texts[1].sentences.text == [',', 'keda', 'seal', 'kohtasime', ',']
    assert clause_texts[2].clauses.text == ['teretas', 'meid', '.']
    assert clause_texts[3].sentences.text == ['(', 'sic', '!', ')']



def test_split_by_clauses_3_verb_chains():
    # Test split by clauses (trim overlapping layers) with verb chain annotations
    text = Text('Und pole, aga ma ei näe põhjust öö läbi üleval olla (sest magada on vaja!).')
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    #from pprint import pprint
    #pprint(layer_to_dict(text['clauses']))
    # Add clauses layer
    clauses_layer_dict = \
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
                                  (73, 74))}]}
    text.add_layer( dict_to_layer(clauses_layer_dict) )
    # Add verb chains layer
    from estnltk.taggers import VerbChainDetector
    vc_detector = VerbChainDetector()
    vc_detector.tag(text)
    # Split by clauses
    clause_texts = _split_by_discontinuous_layer(text, 'clauses',
                                                 layers_to_keep=list(text.layers),
                                                 trim_overlapping=True)
    # Validate results
    assert len(clause_texts) == len(text['clauses'])
    assert clause_texts[0].clauses.text == ['Und', 'pole', ',']
    assert clause_texts[1].clauses.text == ['aga', 'ma', 'ei', 'näe', 'põhjust', 'öö', 'läbi', 'üleval', 'olla', '.']
    assert clause_texts[2].clauses.text == ['(', 'sest', 'magada', 'on', 'vaja', '!', ')']
    assert clause_texts[0].verb_chains.text == ['pole']
    assert clause_texts[1].verb_chains.text == ['ei', 'näe']
    assert clause_texts[2].verb_chains.text == ['magada', 'on', 'vaja']


