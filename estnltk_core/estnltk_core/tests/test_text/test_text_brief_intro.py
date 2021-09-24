#
#  Tests from an old tutorial about basics of 1.6:
#    https://github.com/estnltk/estnltk/blob/8184f6d17b6b99d90dadd3f7fc6cf64434a7bed7/tutorials/brief_intro_to_text_layers_and_tools.ipynb
#
import pytest

import itertools
from estnltk_core import Layer
from estnltk_core import Text
from estnltk_core import Annotation
from estnltk_core.layer import AmbiguousAttributeList, AttributeTupleList
from estnltk_core.layer import AttributeList

example_text_str = '''Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud. 
Kooliõpetaja kutsus mõlemad oma tuppa, kõneles nendega natuke aega, 
käskis Arnol olla hoolas ja korralik ja seadis ta siis pinki ühe pikkade juustega poisi kõrvale istuma.'''

@pytest.mark.xfail(reason="TODO needs fixing")
def test_general_access():
    #
    # General test: analysis and access to Text
    #
    # Example: creating a Text based on raw text data
    t = Text( example_text_str )
    
    # Example: add segmentation (word, sentence and paragraph tokenization) annotations
    t.analyse('segmentation')
    assert t.layers == {'words', 'sentences', 'paragraphs'}
    
    # Example: add metadata about the text
    t.meta['author'] = 'O. Luts'
    t.meta['source'] = '"Kevade"'
    assert t.meta == {'author': 'O. Luts', 'source': '"Kevade"'}
    
    # Raw text (string)
    assert t.text == 'Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud. \nKooliõpetaja kutsus mõlemad oma tuppa, kõneles nendega natuke aega, \nkäskis Arnol olla hoolas ja korralik ja seadis ta siis pinki ühe pikkade juustega poisi kõrvale istuma.'
    
    # Texts from layer 'words' (list of strings)
    assert t.words.text == ['Kui', 'Arno', 'isaga', 'koolimajja', 'jõudis', ',', 'olid', 'tunnid', 'juba', 'alanud', '.', \
       'Kooliõpetaja', 'kutsus', 'mõlemad', 'oma', 'tuppa', ',', 'kõneles', 'nendega', 'natuke', 'aega', ',', 'käskis', 'Arnol', \
       'olla', 'hoolas', 'ja', 'korralik', 'ja', 'seadis', 'ta', 'siis', 'pinki', 'ühe', 'pikkade', 'juustega', 'poisi', 'kõrvale', \
       'istuma', '.']
    
    # Texts from layer 'sentences' (list of lists of strings)
    assert [s.text for s in t.sentences] == [['Kui', 'Arno', 'isaga', 'koolimajja', 'jõudis', ',', 'olid', 'tunnid', 'juba', 'alanud', '.'], \
                                             ['Kooliõpetaja', 'kutsus', 'mõlemad', 'oma', 'tuppa', ',', 'kõneles', 'nendega', 'natuke', 'aega', ',', 'käskis', \
                                              'Arnol', 'olla', 'hoolas', 'ja', 'korralik', 'ja', 'seadis', 'ta', 'siis', 'pinki', 'ühe', 'pikkade', 'juustega', \
                                              'poisi', 'kõrvale', 'istuma', '.']]
     
    # Raw text corresponding to the 1st element from layer 'sentences' (string)
    assert t.sentences[0].enclosing_text == 'Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud.'
    
    # Raw texts of all sentences (list of strings)
    assert [s.enclosing_text for s in t.sentences] == ['Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud.',
                                                       'Kooliõpetaja kutsus mõlemad oma tuppa, kõneles nendega natuke aega, \n'+\
                                                       'käskis Arnol olla hoolas ja korralik ja seadis ta siis pinki ühe pikkade juustega poisi kõrvale istuma.']


from estnltk_core.converters import dict_to_layer, layer_to_dict


@pytest.mark.xfail(reason="TODO needs fixing")
def test_adding_layer():
    #
    # General test: adding a layer
    #
    # Example: creating a Text based on raw text data
    t = Text( example_text_str )
    
    # Example: add word, sentence and paragraph tokenization annotations
    t.tag_layer(['words', 'sentences', 'paragraphs'])
    assert t.layers == {'compound_tokens', 'tokens', 'words', 'sentences', 'paragraphs'}
    
    # Example: creating a new layer
    dep = Layer(name='uppercase', # name of the layer
                parent='words',   # name of the parent layer (i.e. each element of this layer should have a parent in 'words' layer)
                attributes=['upper', 'reverse'] # list of attributes that the new layer will have
                )
    t.add_layer(dep) # attach the layer to the Text
    
    # NB! Currently, you cannot attach a layer with the same name twice (unless you delete the old layer).
    assert 'uppercase' in t.layers
    
    # Example: populating the new layer with elements
    for word in t.words:
        dep.add_annotation(word, upper=word.text.upper(), reverse=word.text.upper()[::-1])
    
    # Validate the layer
    expected_layer_dict = {  'ambiguous': False,
                             'attributes': ('upper', 'reverse'),
                             'enveloping': None,
                             'meta': {},
                             'name': 'uppercase',
                             'parent': 'words',
                             'serialisation_module': None,
                             'spans': [{'annotations': [{'reverse': 'IUK', 'upper': 'KUI'}],
                                        'base_span': (0, 3)},
                                       {'annotations': [{'reverse': 'ONRA', 'upper': 'ARNO'}],
                                        'base_span': (4, 8)},
                                       {'annotations': [{'reverse': 'AGASI', 'upper': 'ISAGA'}],
                                        'base_span': (9, 14)},
                                       {'annotations': [{'reverse': 'AJJAMILOOK', 'upper': 'KOOLIMAJJA'}],
                                        'base_span': (15, 25)},
                                       {'annotations': [{'reverse': 'SIDUÕJ', 'upper': 'JÕUDIS'}],
                                        'base_span': (26, 32)},
                                       {'annotations': [{'reverse': ',', 'upper': ','}],
                                        'base_span': (32, 33)},
                                       {'annotations': [{'reverse': 'DILO', 'upper': 'OLID'}],
                                        'base_span': (34, 38)},
                                       {'annotations': [{'reverse': 'DINNUT', 'upper': 'TUNNID'}],
                                        'base_span': (39, 45)},
                                       {'annotations': [{'reverse': 'ABUJ', 'upper': 'JUBA'}],
                                        'base_span': (46, 50)},
                                       {'annotations': [{'reverse': 'DUNALA', 'upper': 'ALANUD'}],
                                        'base_span': (51, 57)},
                                       {'annotations': [{'reverse': '.', 'upper': '.'}],
                                        'base_span': (57, 58)},
                                       {'annotations': [{'reverse': 'AJATEPÕILOOK',
                                                         'upper': 'KOOLIÕPETAJA'}],
                                        'base_span': (60, 72)},
                                       {'annotations': [{'reverse': 'SUSTUK', 'upper': 'KUTSUS'}],
                                        'base_span': (73, 79)},
                                       {'annotations': [{'reverse': 'DAMELÕM', 'upper': 'MÕLEMAD'}],
                                        'base_span': (80, 87)},
                                       {'annotations': [{'reverse': 'AMO', 'upper': 'OMA'}],
                                        'base_span': (88, 91)},
                                       {'annotations': [{'reverse': 'APPUT', 'upper': 'TUPPA'}],
                                        'base_span': (92, 97)},
                                       {'annotations': [{'reverse': ',', 'upper': ','}],
                                        'base_span': (97, 98)},
                                       {'annotations': [{'reverse': 'SELENÕK', 'upper': 'KÕNELES'}],
                                        'base_span': (99, 106)},
                                       {'annotations': [{'reverse': 'AGEDNEN', 'upper': 'NENDEGA'}],
                                        'base_span': (107, 114)},
                                       {'annotations': [{'reverse': 'EKUTAN', 'upper': 'NATUKE'}],
                                        'base_span': (115, 121)},
                                       {'annotations': [{'reverse': 'AGEA', 'upper': 'AEGA'}],
                                        'base_span': (122, 126)},
                                       {'annotations': [{'reverse': ',', 'upper': ','}],
                                        'base_span': (126, 127)},
                                       {'annotations': [{'reverse': 'SIKSÄK', 'upper': 'KÄSKIS'}],
                                        'base_span': (129, 135)},
                                       {'annotations': [{'reverse': 'LONRA', 'upper': 'ARNOL'}],
                                        'base_span': (136, 141)},
                                       {'annotations': [{'reverse': 'ALLO', 'upper': 'OLLA'}],
                                        'base_span': (142, 146)},
                                       {'annotations': [{'reverse': 'SALOOH', 'upper': 'HOOLAS'}],
                                        'base_span': (147, 153)},
                                       {'annotations': [{'reverse': 'AJ', 'upper': 'JA'}],
                                        'base_span': (154, 156)},
                                       {'annotations': [{'reverse': 'KILARROK', 'upper': 'KORRALIK'}],
                                        'base_span': (157, 165)},
                                       {'annotations': [{'reverse': 'AJ', 'upper': 'JA'}],
                                        'base_span': (166, 168)},
                                       {'annotations': [{'reverse': 'SIDAES', 'upper': 'SEADIS'}],
                                        'base_span': (169, 175)},
                                       {'annotations': [{'reverse': 'AT', 'upper': 'TA'}],
                                        'base_span': (176, 178)},
                                       {'annotations': [{'reverse': 'SIIS', 'upper': 'SIIS'}],
                                        'base_span': (179, 183)},
                                       {'annotations': [{'reverse': 'IKNIP', 'upper': 'PINKI'}],
                                        'base_span': (184, 189)},
                                       {'annotations': [{'reverse': 'EHÜ', 'upper': 'ÜHE'}],
                                        'base_span': (190, 193)},
                                       {'annotations': [{'reverse': 'EDAKKIP', 'upper': 'PIKKADE'}],
                                        'base_span': (194, 201)},
                                       {'annotations': [{'reverse': 'AGETSUUJ', 'upper': 'JUUSTEGA'}],
                                        'base_span': (202, 210)},
                                       {'annotations': [{'reverse': 'ISIOP', 'upper': 'POISI'}],
                                        'base_span': (211, 216)},
                                       {'annotations': [{'reverse': 'ELAVRÕK', 'upper': 'KÕRVALE'}],
                                        'base_span': (217, 224)},
                                       {'annotations': [{'reverse': 'AMUTSI', 'upper': 'ISTUMA'}],
                                        'base_span': (225, 231)},
                                       {'annotations': [{'reverse': '.', 'upper': '.'}],
                                        'base_span': (231, 232)}] }
    assert t['uppercase'] == dict_to_layer( expected_layer_dict )
    
    #from pprint import pprint
    #pprint(layer_to_dict(t.uppercase))
    
    # Example: accessing new annotations (attribute values) through the parent layer ('words')
    assert [word.uppercase.upper for word in t.words[:11]] == ['KUI', 'ARNO', 'ISAGA', 'KOOLIMAJJA', 'JÕUDIS', ',', 'OLID', 'TUNNID', 'JUBA', 'ALANUD', '.']
    assert [word.uppercase.reverse for word in t.words[:11]] == ['IUK', 'ONRA', 'AGASI', 'AJJAMILOOK', 'SIDUÕJ', ',', 'DILO', 'DINNUT', 'ABUJ', 'DUNALA', '.']
    
    # Validate a subset of Layer (which is also a Layer)
    expected_layer_subset_dict = \
    {'ambiguous': False,
     'attributes': ('upper', 'reverse'),
     'enveloping': None,
     'meta': {},
     'name': 'uppercase',
     'parent': 'words',
     'serialisation_module': None,
     'spans': [{'annotations': [{'reverse': 'IUK', 'upper': 'KUI'}],
                'base_span': (0, 3)},
               {'annotations': [{'reverse': 'ONRA', 'upper': 'ARNO'}],
                'base_span': (4, 8)},
               {'annotations': [{'reverse': 'AGASI', 'upper': 'ISAGA'}],
                'base_span': (9, 14)},
               {'annotations': [{'reverse': 'AJJAMILOOK', 'upper': 'KOOLIMAJJA'}],
                'base_span': (15, 25)},
               {'annotations': [{'reverse': 'SIDUÕJ', 'upper': 'JÕUDIS'}],
                'base_span': (26, 32)},
               {'annotations': [{'reverse': ',', 'upper': ','}],
                'base_span': (32, 33)},
               {'annotations': [{'reverse': 'DILO', 'upper': 'OLID'}],
                'base_span': (34, 38)},
               {'annotations': [{'reverse': 'DINNUT', 'upper': 'TUNNID'}],
                'base_span': (39, 45)},
               {'annotations': [{'reverse': 'ABUJ', 'upper': 'JUBA'}],
                'base_span': (46, 50)},
               {'annotations': [{'reverse': 'DUNALA', 'upper': 'ALANUD'}],
                'base_span': (51, 57)},
               {'annotations': [{'reverse': '.', 'upper': '.'}],
                'base_span': (57, 58)}]}
    assert t.uppercase[:11] == dict_to_layer( expected_layer_subset_dict )
    
    #from pprint import pprint
    #pprint(layer_to_dict(t.uppercase[:11]))


@pytest.mark.xfail(reason="TODO needs fixing")
def test_tag_layer_with_string_input():
    #
    # Test that tag_layer also accepts string as an input
    #
    t = Text( example_text_str )
    t.tag_layer('words')
    assert t.layers == {'compound_tokens', 'tokens', 'words'}
    t.tag_layer('sentences')
    t.tag_layer('paragraphs')
    assert t.layers == {'compound_tokens', 'tokens', 'words', 'sentences', 'paragraphs'}
