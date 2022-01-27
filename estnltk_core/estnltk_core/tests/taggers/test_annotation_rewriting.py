import copy

from estnltk_core.common import load_text_class

from estnltk_core.converters import layer_to_dict
from estnltk_core.converters import dict_to_layer

from estnltk_core.taggers.annotation_rewriter import AnnotationRewriter
from estnltk_core.taggers.span_annotations_rewriter import SpanAnnotationsRewriter

import pytest

def test_annotation_rewriter():
    # Create example text für testing
    Text = load_text_class()
    text = Text('Tere! Tsau-pakaa!')
    words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
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

    # Case 1: add an attribute to layer    
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
         'secondary_attributes': (),
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
         'secondary_attributes': (),
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

    # Case 3: duplicate attribute values (string duplication)
    def rewrite_duplicate_attr_value( annotation ):
        # remove attribute
        annotation['uppercase'] = annotation['uppercase']+'-'+annotation['uppercase']
    
    rewriter3 = AnnotationRewriter('words', (), 
                                   rewrite_duplicate_attr_value)
    rewriter3.retag( text )
    expected_words_layer_dict3 = \
        {'ambiguous': True,
         'attributes': ('uppercase',),
         'secondary_attributes': (),
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



def test_span_annotations_rewriter():
    # Create example text für testing
    Text = load_text_class()
    text = Text('Tere! Tsau-pakaa!')
    words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'secondary_attributes': (),
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
    
    # Case 1: duplicate annotations and add an attribute to layer
    def duplicate_annotations_and_add_indexes( annotations_list ):
        # duplicate annotations
        new_annotations = []
        for annotation in annotations_list:
            # insert Annotation object
            new_annotations.append( annotation )
            # insert dict
            ann_dict = {attr:annotation[attr] for attr in annotation.legal_attribute_names if attr in annotation}
            new_annotations.append( ann_dict )
        # add indexes
        for aid, annotation in enumerate(new_annotations):
            annotation['index'] = aid
        return new_annotations

    rewriter1 = SpanAnnotationsRewriter('words', ('index',), 
                                       duplicate_annotations_and_add_indexes, 
                                       attr_change='ADD')
    rewriter1.retag( text )
    
    expected_words_layer_dict1 = \
        {'ambiguous': True,
         'attributes': ('normalized_form', 'index'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'index': 0, 'normalized_form': None},
                                    {'index': 1, 'normalized_form': None}],
                    'base_span': (0, 4)},
                   {'annotations': [{'index': 0, 'normalized_form': None},
                                    {'index': 1, 'normalized_form': None}],
                    'base_span': (4, 5)},
                   {'annotations': [{'index': 0, 'normalized_form': None},
                                    {'index': 1, 'normalized_form': None}],
                    'base_span': (6, 16)},
                   {'annotations': [{'index': 0, 'normalized_form': None},
                                    {'index': 1, 'normalized_form': None}],
                    'base_span': (16, 17)}]}
    assert expected_words_layer_dict1 == layer_to_dict(text['words'])
    
    # Case 2: remove 1 annotation from the first span and remove an attribute from layer
    def remove_first_span_annotation_and_attributes( annotations_list ):
        if annotations_list[0].span.start == 0:
            annotations_list.pop(0)
        for aid, annotation in enumerate( annotations_list ):
            del annotation['normalized_form']
        return annotations_list

    rewriter2 = SpanAnnotationsRewriter('words', ('normalized_form',), 
                                       remove_first_span_annotation_and_attributes, 
                                       attr_change='REMOVE')
    rewriter2.retag( text )
    expected_words_layer_dict2 = \
        {'ambiguous': True,
         'attributes': ('index',),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'index': 1}], 'base_span': (0, 4)},
                   {'annotations': [{'index': 0}, {'index': 1}], 'base_span': (4, 5)},
                   {'annotations': [{'index': 0}, {'index': 1}], 'base_span': (6, 16)},
                   {'annotations': [{'index': 0}, {'index': 1}], 'base_span': (16, 17)}]}
    assert expected_words_layer_dict2 == layer_to_dict( text['words'] )

    # Case 3: completely replace old annotations with new ones
    def replace_attributes_add_new_index_and_lowercase( annotations_list ):
        new_annotations = []
        for aid, annotation in enumerate( annotations_list ):
            ann_dict = { 'new_index':aid+1, \
                         'lowercase':annotation.span.text.lower() }
            new_annotations.append( ann_dict )
        return new_annotations
    
    rewriter3 = SpanAnnotationsRewriter('words', ('new_index', 'lowercase'), 
                                        replace_attributes_add_new_index_and_lowercase, 
                                        attr_change='SET')
    rewriter3.retag( text )
    expected_words_layer_dict3 = \
        {'ambiguous': True,
         'attributes': ('new_index', 'lowercase'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'lowercase': 'tere', 'new_index': 1}],
                    'base_span': (0, 4)},
                   {'annotations': [{'lowercase': '!', 'new_index': 1},
                                    {'lowercase': '!', 'new_index': 2}],
                    'base_span': (4, 5)},
                   {'annotations': [{'lowercase': 'tsau-pakaa', 'new_index': 1},
                                    {'lowercase': 'tsau-pakaa', 'new_index': 2}],
                    'base_span': (6, 16)},
                   {'annotations': [{'lowercase': '!', 'new_index': 1},
                                    {'lowercase': '!', 'new_index': 2}],
                    'base_span': (16, 17)}]}
    assert expected_words_layer_dict3 == layer_to_dict( text['words'] )
    #from pprint import pprint
    #pprint( layer_to_dict(text['words']) ) 
    
