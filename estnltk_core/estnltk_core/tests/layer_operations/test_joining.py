from estnltk_core import Layer

from estnltk_core.converters import layer_to_dict
from estnltk_core.converters import dict_to_layer

from estnltk_core.layer_operations import join_texts
from estnltk_core.layer_operations import join_layers
from estnltk_core.layer_operations import join_layers_while_reusing_spans
from estnltk_core.layer_operations import split_by, split_by_sentences

from estnltk_core.common import load_text_class

def test_join_layers():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Create test text and layers
    text = Text('See on üks väike lause')
    full_words_layer = \
        {'name': 'words',
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'parent': None,
         'enveloping': None,
         'ambiguous': True,
         'serialisation_module': None,
         'meta': {},
         'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
          {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
          {'base_span': (7, 10), 'annotations': [{'normalized_form': None}]},
          {'base_span': (11, 16), 'annotations': [{'normalized_form': None}]},
          {'base_span': (17, 22), 'annotations': [{'normalized_form': None}]}]}
    text.add_layer( dict_to_layer(full_words_layer) )
    split_words_layers = [ \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 3)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 2)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 3)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 5)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 5)}]} ]
    split_texts = [t for t in split_by(text, 'words', layers_to_keep=text.layers)]
    layers = [ dict_to_layer(layer_dict) for layer_dict in split_words_layers ]
    # Add Text objects to layers (join_layers needs texts to determine span shifts)
    for i, layer in enumerate(layers):
        layer.text_object = split_texts[i]
    # Join layers
    joined_layer = join_layers(layers, [' ', ' ', ' ', ' '])
    # Check the results
    new_text = Text( text.text )
    new_text.add_layer( joined_layer )
    assert layer_to_dict( joined_layer ) == full_words_layer
    assert layer_to_dict( new_text['words'] ) == full_words_layer


def test_join_texts():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Construct test Text obj
    text = Text('Esimene lause. Teine lause. Kolmas lause')
    words_layer_dict = \
        {'name': 'words',
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'parent': None,
         'enveloping': None,
         'ambiguous': True,
         'serialisation_module': None,
         'meta': {},
         'spans': [{'base_span': (0, 7), 'annotations': [{'normalized_form': None}]},
          {'base_span': (8, 13), 'annotations': [{'normalized_form': None}]},
          {'base_span': (13, 14), 'annotations': [{'normalized_form': None}]},
          {'base_span': (15, 20), 'annotations': [{'normalized_form': None}]},
          {'base_span': (21, 26), 'annotations': [{'normalized_form': None}]},
          {'base_span': (26, 27), 'annotations': [{'normalized_form': None}]},
          {'base_span': (28, 34), 'annotations': [{'normalized_form': None}]},
          {'base_span': (35, 40), 'annotations': [{'normalized_form': None}]}]}
    sentences_layer_dict = \
        {'name': 'sentences',
         'attributes': (),
         'secondary_attributes': (),
         'parent': None,
         'enveloping': 'words',
         'ambiguous': False,
         'serialisation_module': None,
         'meta': {},
         'spans': [{'base_span': ((0, 7), (8, 13), (13, 14)), 'annotations': [{}]},
          {'base_span': ((15, 20), (21, 26), (26, 27)), 'annotations': [{}]},
          {'base_span': ((28, 34), (35, 40)), 'annotations': [{}]}]}
    morph_layer_dict = \
        {'name': 'morph_analysis',
         'attributes': ('normalized_text',
          'lemma',
          'root',
          'root_tokens',
          'ending',
          'clitic',
          'form',
          'partofspeech'),
         'secondary_attributes': (),
         'parent': 'words',
         'enveloping': None,
         'ambiguous': True,
         'serialisation_module': None,
         'meta': {},
         'spans': [{'base_span': (0, 7),
           'annotations': [{'normalized_text': 'Esimene',
             'lemma': 'esimene',
             'root': 'esimene',
             'root_tokens': ['esimene'],
             'ending': '0',
             'clitic': '',
             'form': 'sg n',
             'partofspeech': 'O'}]},
          {'base_span': (8, 13),
           'annotations': [{'normalized_text': 'lause',
             'lemma': 'lause',
             'root': 'lause',
             'root_tokens': ['lause'],
             'ending': '0',
             'clitic': '',
             'form': 'sg n',
             'partofspeech': 'S'}]},
          {'base_span': (13, 14),
           'annotations': [{'normalized_text': '.',
             'lemma': '.',
             'root': '.',
             'root_tokens': ['.'],
             'ending': '',
             'clitic': '',
             'form': '',
             'partofspeech': 'Z'}]},
          {'base_span': (15, 20),
           'annotations': [{'normalized_text': 'Teine',
             'lemma': 'teine',
             'root': 'teine',
             'root_tokens': ['teine'],
             'ending': '0',
             'clitic': '',
             'form': 'sg n',
             'partofspeech': 'P'},
            {'normalized_text': 'Teine',
             'lemma': 'teine',
             'root': 'teine',
             'root_tokens': ['teine'],
             'ending': '0',
             'clitic': '',
             'form': 'sg n',
             'partofspeech': 'O'}]},
          {'base_span': (21, 26),
           'annotations': [{'normalized_text': 'lause',
             'lemma': 'lause',
             'root': 'lause',
             'root_tokens': ['lause'],
             'ending': '0',
             'clitic': '',
             'form': 'sg n',
             'partofspeech': 'S'}]},
          {'base_span': (26, 27),
           'annotations': [{'normalized_text': '.',
             'lemma': '.',
             'root': '.',
             'root_tokens': ['.'],
             'ending': '',
             'clitic': '',
             'form': '',
             'partofspeech': 'Z'}]},
          {'base_span': (28, 34),
           'annotations': [{'normalized_text': 'Kolmas',
             'lemma': 'kolmas',
             'root': 'kolmas',
             'root_tokens': ['kolmas'],
             'ending': '0',
             'clitic': '',
             'form': 'sg n',
             'partofspeech': 'O'}]},
          {'base_span': (35, 40),
           'annotations': [{'normalized_text': 'lause',
             'lemma': 'lause',
             'root': 'lause',
             'root_tokens': ['lause'],
             'ending': '0',
             'clitic': '',
             'form': 'sg n',
             'partofspeech': 'S'}]}]}
    text.add_layer( dict_to_layer(words_layer_dict) )
    text.add_layer( dict_to_layer(sentences_layer_dict) )
    text.add_layer( dict_to_layer(morph_layer_dict) )
    
    # Split Text into smaller texts by sentences
    split_texts = split_by_sentences(text, layers_to_keep=text.layers)
    assert len(split_texts) == 3
    
    # Join split Texts into a single Text
    joined_text = join_texts( split_texts, [' ', ' '] )
    
    # Check results
    assert text.text == joined_text.text
    assert text.layers == joined_text.layers
    assert layer_to_dict( joined_text['words'] ) == words_layer_dict
    assert layer_to_dict( joined_text['sentences'] ) == sentences_layer_dict
    assert layer_to_dict( joined_text['morph_analysis'] ) == morph_layer_dict


def test_join_layers_while_reusing_spans():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Create test text and layers
    text = Text('See on üks väike lause')
    full_words_layer = \
        {'name': 'words',
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'parent': None,
         'enveloping': None,
         'ambiguous': True,
         'serialisation_module': None,
         'meta': {},
         'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
          {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
          {'base_span': (7, 10), 'annotations': [{'normalized_form': None}]},
          {'base_span': (11, 16), 'annotations': [{'normalized_form': None}]},
          {'base_span': (17, 22), 'annotations': [{'normalized_form': None}]}]}
    text.add_layer( dict_to_layer(full_words_layer) )
    split_words_layers = [ \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 3)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 2)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 3)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 5)}]},
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 5)}]} ]
    split_texts = [t for t in split_by(text, 'words', layers_to_keep=text.layers)]
    layers = [ dict_to_layer(layer_dict) for layer_dict in split_words_layers ]
    # Add Text objects to layers (join_layers* needs texts to determine span shifts)
    for i, layer in enumerate(layers):
        layer.text_object = split_texts[i]
    # Join layers
    joined_layer = join_layers_while_reusing_spans(layers, [' ', ' ', ' ', ' '])
    # Check the results
    new_text = Text( text.text )
    new_text.add_layer( joined_layer )
    assert layer_to_dict( joined_layer ) == full_words_layer
    assert layer_to_dict( new_text['words'] ) == full_words_layer

