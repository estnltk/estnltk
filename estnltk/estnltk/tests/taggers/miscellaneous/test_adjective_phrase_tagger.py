from estnltk.taggers import AdjectivePhraseTagger
from estnltk import Text
from estnltk_core.converters import layer_to_dict

def test_adjective_phrase_tagger():
    text = Text("Eile leitud koer oli väga energiline ja mänguhimuline.").tag_layer('morph_analysis')

    tagger = AdjectivePhraseTagger()
    tagger.tag(text)
    
    assert layer_to_dict( text.grammar_tags ) == \
        {'ambiguous': True,
         'attributes': ('grammar_symbol',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'grammar_tags',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'grammar_symbol': 'ADV2'}], 'base_span': (0, 4)},
                   {'annotations': [{'grammar_symbol': 'ADJ'}], 'base_span': (5, 11)},
                   {'annotations': [{'grammar_symbol': 'RANDOM_TEXT'}],
                    'base_span': (12, 20)},
                   {'annotations': [{'grammar_symbol': 'ADJ_M'},
                                    {'grammar_symbol': 'ADV2'}],
                    'base_span': (21, 25)},
                   {'annotations': [{'grammar_symbol': 'ADJ'}], 'base_span': (26, 36)},
                   {'annotations': [{'grammar_symbol': 'CONJ'}], 'base_span': (37, 39)},
                   {'annotations': [{'grammar_symbol': 'ADJ'}], 'base_span': (40, 53)},
                   {'annotations': [{'grammar_symbol': 'RANDOM_TEXT'}],
                    'base_span': (53, 54)}]}
    assert layer_to_dict( text.adjective_phrases ) == \
        {'ambiguous': False,
         'attributes': ('type', 'adverb_class', 'adverb_weight'),
         'secondary_attributes': (),
         'enveloping': 'grammar_tags',
         'meta': {},
         'name': 'adjective_phrases',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'adverb_class': None,
                                     'adverb_weight': None,
                                     'type': 'adjective phrase'}],
                    'base_span': ((5, 11),)},
                   {'annotations': [{'adverb_class': None,
                                     'adverb_weight': None,
                                     'type': 'adjective phrase'}],
                    'base_span': ((21, 25), (26, 36), (37, 39), (40, 53))}]}

