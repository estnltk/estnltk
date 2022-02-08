#
# Note: Serialisation of 'syntax_v0' layer is not part of 'estnltk_core', 
# but it is added later in 'estnltk'. 
# Test that converters are aware of the added serialisation module and 
# can convert a Text object with 'syntax_v0' layer.
#

from estnltk_core.converters import dict_to_layer
from estnltk_core.converters import text_to_dict, dict_to_text
from estnltk_core.converters import text_to_json, json_to_text

test_text_dict = \
    {'layers': [{'ambiguous': True,
                 'attributes': ('normalized_form',),
                 'secondary_attributes': (),
                 'enveloping': None,
                 'meta': {},
                 'name': 'words',
                 'parent': None,
                 'serialisation_module': None,
                 'spans': [{'annotations': [{'normalized_form': None}],
                            'base_span': (0, 4)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (4, 5)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (6, 12)},
                           {'annotations': [{'normalized_form': None}],
                            'base_span': (12, 13)}]},
                {'ambiguous': True,
                 'attributes': ('normalized_text',
                                'lemma',
                                'root',
                                'root_tokens',
                                'ending',
                                'clitic',
                                'form',
                                'partofspeech'),
                 'secondary_attributes': (),
                 'enveloping': None,
                 'meta': {},
                 'name': 'morph_analysis',
                 'parent': 'words',
                 'serialisation_module': None,
                 'spans': [{'annotations': [{'clitic': '',
                                             'ending': '0',
                                             'form': '',
                                             'lemma': 'tere',
                                             'normalized_text': 'Tere',
                                             'partofspeech': 'I',
                                             'root': 'tere',
                                             'root_tokens': ['tere']}],
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
                                             'ending': '0',
                                             'form': 'sg n',
                                             'lemma': 'Kerttu',
                                             'normalized_text': 'Kerttu',
                                             'partofspeech': 'H',
                                             'root': 'Kerttu',
                                             'root_tokens': ['Kerttu']}],
                            'base_span': (6, 12)},
                           {'annotations': [{'clitic': '',
                                             'ending': '',
                                             'form': '',
                                             'lemma': '!',
                                             'normalized_text': '!',
                                             'partofspeech': 'Z',
                                             'root': '!',
                                             'root_tokens': ['!']}],
                            'base_span': (12, 13)}]},
                {'ambiguous': False,
                 'attributes': (),
                 'secondary_attributes': (),
                 'enveloping': 'words',
                 'meta': {},
                 'name': 'sentences',
                 'parent': None,
                 'serialisation_module': None,
                 'spans': [{'annotations': [{}],
                            'base_span': ((0, 4), (4, 5), (6, 12), (12, 13))}]},
                {'ambiguous': False,
                 'attributes': ('id',
                                'lemma',
                                'upostag',
                                'xpostag',
                                'feats',
                                'head',
                                'deprel',
                                'deps',
                                'misc',
                                'parent_span',
                                'children'),
                 'secondary_attributes': ('parent_span',
                                          'children'),
                 'enveloping': None,
                 'meta': {},
                 'name': 'stanza_syntax',
                 'parent': 'morph_analysis',
                 'serialisation_module': 'syntax_v0',
                 'spans': [{'annotations': [{'deprel': 'discourse',
                                             'deps': '_',
                                             'feats': {},
                                             'head': 3,
                                             'id': 1,
                                             'lemma': 'tere',
                                             'misc': '_',
                                             'upostag': 'I',
                                             'xpostag': 'I'}],
                            'base_span': (0, 4)},
                           {'annotations': [{'deprel': 'punct',
                                             'deps': '_',
                                             'feats': {},
                                             'head': 3,
                                             'id': 2,
                                             'lemma': ',',
                                             'misc': '_',
                                             'upostag': 'Z',
                                             'xpostag': 'Z'}],
                            'base_span': (4, 5)},
                           {'annotations': [{'deprel': 'root',
                                             'deps': '_',
                                             'feats': {'nom': 'nom',
                                                       'prop': 'prop',
                                                       'sg': 'sg'},
                                             'head': 0,
                                             'id': 3,
                                             'lemma': 'Kerttu',
                                             'misc': '_',
                                             'upostag': 'S',
                                             'xpostag': 'S'}],
                            'base_span': (6, 12)},
                           {'annotations': [{'deprel': 'punct',
                                             'deps': '_',
                                             'feats': {},
                                             'head': 3,
                                             'id': 4,
                                             'lemma': '!',
                                             'misc': '_',
                                             'upostag': 'Z',
                                             'xpostag': 'Z'}],
                            'base_span': (12, 13)}]}],
     'meta': {},
     'text': 'Tere, Kerttu!'}

def test_convert_syntax_v0_dict_to_text():
    text_obj = dict_to_text( test_text_dict )
    assert 'stanza_syntax' in text_obj.layers
    assert text_obj['stanza_syntax'].serialisation_module == 'syntax_v0'
    assert list(text_obj['stanza_syntax'].parent_span) == [ text_obj['stanza_syntax'][2], \
                                                            text_obj['stanza_syntax'][2], \
                                                            None, 
                                                            text_obj['stanza_syntax'][2] ]

def test_convert_syntax_v0_dict_to_text_and_back():
    text_obj = dict_to_text( test_text_dict )
    assert text_obj['stanza_syntax'].serialisation_module == 'syntax_v0'
    assert text_obj['stanza_syntax'].secondary_attributes == ('parent_span', 'children')
    assert list(text_obj['stanza_syntax'].parent_span) == [ text_obj['stanza_syntax'][2], \
                                                            text_obj['stanza_syntax'][2], \
                                                            None, 
                                                            text_obj['stanza_syntax'][2] ]
    assert text_to_dict(text_obj) == test_text_dict

def test_convert_syntax_v0_dict_to_layer():
    layer_obj = dict_to_layer( test_text_dict['layers'][3] )
    assert layer_obj.name == 'stanza_syntax'
    assert layer_obj.serialisation_module == 'syntax_v0'
    assert layer_obj.secondary_attributes == ('parent_span', 'children')
    assert list(layer_obj.parent_span) == [ layer_obj[2], \
                                            layer_obj[2], \
                                            None, 
                                            layer_obj[2] ]

def test_convert_syntax_v0_dict_to_json_and_back():
    text_obj = dict_to_text( test_text_dict )
    assert text_obj['stanza_syntax'].serialisation_module == 'syntax_v0'
    text_obj_json = text_to_json( text_obj )
    import_text_obj = json_to_text( text_obj_json )
    assert import_text_obj['stanza_syntax'].serialisation_module == 'syntax_v0'
    assert text_to_dict( import_text_obj ) == test_text_dict
