import copy

from estnltk_core.common import load_text_class

from estnltk_core.converters import layer_to_dict
from estnltk_core.converters import dict_to_layer

from estnltk_core.taggers.annotation_rewriter import AnnotationRewriter

import pytest

def test_annotation_rewriter():
    Text = load_text_class()
    # Case 1: add an attribute to layer
    text = Text('Tere! Tsau-pakaa!')
    words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 4)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (4, 5)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (6, 16)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (16, 17)}]}
    text.add_layer( dict_to_layer(words_layer_dict) )
    
    def rewrite_add_uppercase( annotation ):
        # add attribute containing uppercase text
        annotation['uppercase'] = annotation.span.text.upper()

    rewriter = AnnotationRewriter('words', ('uppercase',), 
                                  rewrite_add_uppercase, 
                                  attr_change='ADD')
    rewriter.retag( text )
    expected_words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form', 'uppercase'),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None, 'uppercase': 'TERE'}],
                    'base_span': (0, 4)},
                   {'annotations': [{'normalized_form': None, 'uppercase': '!'}],
                    'base_span': (4, 5)},
                   {'annotations': [{'normalized_form': None, 'uppercase': 'TSAU-PAKAA'}],
                    'base_span': (6, 16)},
                   {'annotations': [{'normalized_form': None, 'uppercase': '!'}],
                    'base_span': (16, 17)}]}
    assert expected_words_layer_dict == layer_to_dict(text['words'])
    
    # Case 2: remove an attribute from the layer
    def rewrite_delete_norm_form( annotation ):
        # remove attribute
        del annotation['normalized_form']

    rewriter2 = AnnotationRewriter('words', ('normalized_form',), 
                                   rewrite_delete_norm_form, 
                                   attr_change='REMOVE')
    rewriter2.retag( text )
    expected_words_layer_dict2 = \
        {'ambiguous': True,
         'attributes': ('uppercase',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'uppercase': 'TERE'}], 'base_span': (0, 4)},
                   {'annotations': [{'uppercase': '!'}], 'base_span': (4, 5)},
                   {'annotations': [{'uppercase': 'TSAU-PAKAA'}], 'base_span': (6, 16)},
                   {'annotations': [{'uppercase': '!'}], 'base_span': (16, 17)}]}
    assert expected_words_layer_dict2 == layer_to_dict(text['words'])

    # Case 3: duplicate attribute values (strings)
    def rewrite_duplicate_attr_value( annotation ):
        # duplicate attribute
        annotation['uppercase'] = annotation['uppercase']+'-'+annotation['uppercase']
    
    rewriter3 = AnnotationRewriter('words', (), rewrite_duplicate_attr_value)
    rewriter3.retag( text )
    expected_words_layer_dict3 = \
        {'ambiguous': True,
         'attributes': ('uppercase',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'uppercase': 'TERE-TERE'}], 'base_span': (0, 4)},
                   {'annotations': [{'uppercase': '!-!'}], 'base_span': (4, 5)},
                   {'annotations': [{'uppercase': 'TSAU-PAKAA-TSAU-PAKAA'}], 'base_span': (6, 16)},
                   {'annotations': [{'uppercase': '!-!'}], 'base_span': (16, 17)}]}
    assert expected_words_layer_dict3 == layer_to_dict(text['words'])


