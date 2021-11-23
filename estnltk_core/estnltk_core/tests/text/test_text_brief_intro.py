#
#  Tests from an old tutorial about basics of 1.6:
#    https://github.com/estnltk/estnltk/blob/8184f6d17b6b99d90dadd3f7fc6cf64434a7bed7/tutorials/brief_intro_to_text_layers_and_tools.ipynb
#
import pytest

import itertools
from estnltk_core import Layer
from estnltk_core import Annotation
from estnltk_core.layer import AmbiguousAttributeList, AttributeTupleList
from estnltk_core.layer import AttributeList

from estnltk_core.common import load_text_class

example_text_str = '''Ilm on ilus. Päike paistab.'''

def test_general_access():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    #
    # General test: analysis and access to Text
    #
    # Example: creating a Text based on raw text data
    t = Text( example_text_str )

    with pytest.raises(AssertionError):
        text_of_text = Text(t)
    
    # Example: add segmentation (word, sentence and paragraph tokenization) annotations
    words_layer = dict_to_layer({'name': 'words',
     'attributes': ('normalized_form',),
     'parent': None,
     'enveloping': None,
     'ambiguous': True,
     'serialisation_module': None,
     'meta': {},
     'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
      {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
      {'base_span': (7, 11), 'annotations': [{'normalized_form': None}]},
      {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
      {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
      {'base_span': (19, 26), 'annotations': [{'normalized_form': None}]},
      {'base_span': (26, 27), 'annotations': [{'normalized_form': None}]}]})
    t.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
     'attributes': (),
     'parent': None,
     'enveloping': 'words',
     'ambiguous': False,
     'serialisation_module': None,
     'meta': {},
     'spans': [{'base_span': ((0, 3), (4, 6), (7, 11), (11, 12)),
       'annotations': [{}]},
      {'base_span': ((13, 18), (19, 26), (26, 27)), 'annotations': [{}]}]})
    t.add_layer(sentences_layer)
    paragraphs_layer = dict_to_layer({'name': 'paragraphs',
     'attributes': (),
     'parent': None,
     'enveloping': 'sentences',
     'ambiguous': False,
     'serialisation_module': None,
     'meta': {},
     'spans': [{'base_span': (((0, 3), (4, 6), (7, 11), (11, 12)),
        ((13, 18), (19, 26), (26, 27))),
    'annotations': [{}]}]})
    t.add_layer(paragraphs_layer)

    assert t.layers == {'words', 'sentences', 'paragraphs'}
    
    # Example: add metadata about the text
    t.meta['author'] = 'O. Luts'
    t.meta['source'] = '"Kevade"'
    assert t.meta == {'author': 'O. Luts', 'source': '"Kevade"'}
    
    # Raw text (string)
    assert t.text == example_text_str

    # Texts from layer 'words' (list of strings)
    assert t['words'].text == ['Ilm', 'on', 'ilus', '.', 'Päike', 'paistab', '.']
    
    # Texts from layer 'sentences' (list of lists of strings)
    assert [s.text for s in t['sentences']] == [['Ilm', 'on', 'ilus', '.'], ['Päike', 'paistab', '.']]
     
    # Raw text corresponding to the 1st element from layer 'sentences' (string)
    assert t['sentences'][0].enclosing_text == 'Ilm on ilus.'
    
    # Raw texts of all sentences (list of strings)
    assert [s.enclosing_text for s in t['sentences']] == ['Ilm on ilus.', 'Päike paistab.']

from estnltk_core.converters import dict_to_layer, layer_to_dict


def test_adding_layer():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    #
    # General test: adding a layer
    #
    # Example: creating a Text based on raw text data
    t = Text( example_text_str )
    
    # Example: add word, sentence and paragraph tokenization annotations
    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (7, 11), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (19, 26), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (26, 27), 'annotations': [{'normalized_form': None}]}]})
    t.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
                                     'attributes': (),
                                     'parent': None,
                                     'enveloping': 'words',
                                     'ambiguous': False,
                                     'serialisation_module': None,
                                     'meta': {},
                                     'spans': [{'base_span': ((0, 3), (4, 6), (7, 11), (11, 12)),
                                                'annotations': [{}]},
                                               {'base_span': ((13, 18), (19, 26), (26, 27)), 'annotations': [{}]}]})
    t.add_layer(sentences_layer)
    paragraphs_layer = dict_to_layer({'name': 'paragraphs',
                                      'attributes': (),
                                      'parent': None,
                                      'enveloping': 'sentences',
                                      'ambiguous': False,
                                      'serialisation_module': None,
                                      'meta': {},
                                      'spans': [{'base_span': (((0, 3), (4, 6), (7, 11), (11, 12)),
                                                               ((13, 18), (19, 26), (26, 27))),
                                                 'annotations': [{}]}]})
    t.add_layer(paragraphs_layer)
    
    # Example: creating a new layer
    dep = Layer(name='uppercase', # name of the layer
                parent='words',   # name of the parent layer (i.e. each element of this layer should have a parent in 'words' layer)
                attributes=['upper', 'reverse'] # list of attributes that the new layer will have
                )
    t.add_layer(dep) # attach the layer to the Text
    
    # NB! Currently, you cannot attach a layer with the same name twice (unless you delete the old layer).
    assert 'uppercase' in t.layers
    
    # Example: populating the new layer with elements
    for word in t['words']:
        dep.add_annotation(word, upper=word.text.upper(), reverse=word.text.upper()[::-1])
    
    # Validate the layer
    expected_layer_dict = {'name': 'uppercase',
         'attributes': ('upper', 'reverse'),
         'parent': 'words',
         'enveloping': None,
         'ambiguous': False,
         'serialisation_module': None,
         'meta': {},
         'spans': [{'base_span': (0, 3),
           'annotations': [{'upper': 'ILM', 'reverse': 'MLI'}]},
          {'base_span': (4, 6), 'annotations': [{'upper': 'ON', 'reverse': 'NO'}]},
          {'base_span': (7, 11),
           'annotations': [{'upper': 'ILUS', 'reverse': 'SULI'}]},
          {'base_span': (11, 12), 'annotations': [{'upper': '.', 'reverse': '.'}]},
          {'base_span': (13, 18),
           'annotations': [{'upper': 'PÄIKE', 'reverse': 'EKIÄP'}]},
          {'base_span': (19, 26),
           'annotations': [{'upper': 'PAISTAB', 'reverse': 'BATSIAP'}]},
          {'base_span': (26, 27), 'annotations': [{'upper': '.', 'reverse': '.'}]}]}
    assert t['uppercase'] == dict_to_layer( expected_layer_dict )
    
    #from pprint import pprint
    #pprint(layer_to_dict(t.uppercase))
    
    # Example: accessing new annotations (attribute values) through the parent layer ('words')
    assert [word.uppercase.upper for word in t['words'][:11]] == ['ILM', 'ON', 'ILUS', '.', 'PÄIKE', 'PAISTAB', '.']
    assert [word.uppercase.reverse for word in t['words'][:11]] == ['MLI', 'NO', 'SULI', '.', 'EKIÄP', 'BATSIAP', '.']
    
    # Validate a subset of Layer (which is also a Layer)
    expected_layer_subset_dict = \
        {'name': 'uppercase',
         'attributes': ('upper', 'reverse'),
         'parent': 'words',
         'enveloping': None,
         'ambiguous': False,
         'serialisation_module': None,
         'meta': {},
         'spans': [{'base_span': (0, 3),
                    'annotations': [{'upper': 'ILM', 'reverse': 'MLI'}]},
                   {'base_span': (4, 6), 'annotations': [{'upper': 'ON', 'reverse': 'NO'}]},
                   {'base_span': (7, 11),
                    'annotations': [{'upper': 'ILUS', 'reverse': 'SULI'}]},
                   {'base_span': (11, 12), 'annotations': [{'upper': '.', 'reverse': '.'}]},
                   {'base_span': (13, 18),
                    'annotations': [{'upper': 'PÄIKE', 'reverse': 'EKIÄP'}]},
                   {'base_span': (19, 26),
                    'annotations': [{'upper': 'PAISTAB', 'reverse': 'BATSIAP'}]},
                   {'base_span': (26, 27), 'annotations': [{'upper': '.', 'reverse': '.'}]}]}
    assert t['uppercase'][:11] == dict_to_layer( expected_layer_subset_dict )
    
    #from pprint import pprint
    #pprint(layer_to_dict(t['uppercase'][:11]))
