from typing import Union

from estnltk_core import Layer
from estnltk_core.taggers import Tagger, Retagger
from estnltk_core.taggers_registry import TaggersRegistry
from estnltk_core.layer_resolver import LayerResolver
from estnltk_core.common import create_text_object

import pytest

class StubTagger(Tagger):
    """A stub tagger for testing LayerResolver and TaggersRegistry.
    """
    conf_param = []

    def __init__(self, output_layer, input_layers):
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = []

    def _make_layer(self, text: Union['BaseText', 'Text'], layers, status=None) -> Layer:
        layer = Layer(self.output_layer, self.output_attributes, text_object=text)
        layer.meta['modified'] = 0
        return layer


class StubRetagger(Retagger):
    """A stub retagger for testing LayerResolver and TaggersRegistry.
    """
    conf_param = []

    def __init__(self, output_layer, input_layers):
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = []

    def _change_layer(self, text: Union['BaseText', 'Text'], layers, status=None) -> None:
        target_layer = layers[self.output_layer]
        target_layer.meta['modified'] += 1
        return None


def test_create_resolver():
    # Test that the resolver can be created in two ways:
    # 1) providing the list of taggers upon creation
    # 2) adding taggers one by one 
    taggers = TaggersRegistry([StubTagger('tokens', input_layers=[]),
                       StubTagger('compound_tokens', input_layers=['tokens']),
                       StubTagger('words', input_layers=['compound_tokens']),
                       StubTagger('sentences', input_layers=['words']),
                       StubTagger('morph_analysis', input_layers=['words', 'sentences'])
                       ])
    resolver1 = LayerResolver(taggers)
    text1 = create_text_object('test')
    resolver1.apply(text1, 'morph_analysis')
    assert set(text1.layers) == {'tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'}
    
    resolver2 = LayerResolver( TaggersRegistry([]) )
    resolver2.update( StubTagger('tokens', input_layers=[]) )
    resolver2.update( StubTagger('compound_tokens', input_layers=['tokens']) )
    resolver2.update( StubTagger('words', input_layers=['compound_tokens']) )
    resolver2.update( StubTagger('sentences', input_layers=['words']) )
    resolver2.update( StubTagger('morph_analysis', input_layers=['words', 'sentences']) )
    text2 = create_text_object('test')
    resolver2.apply(text2, 'morph_analysis')
    assert set(text2.layers) == {'tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'}


def test_create_resolver_exceptions():
    # Test that exceptions will be thrown upon problematic tagger registry & resolver creation
    
    # Case 1: trying to initiate with non-taggers; trying to update non-taggers
    with pytest.raises(TypeError):
        # TypeError: (!) Expected a subclass of Tagger, but got <class 'int'>.
        taggers = TaggersRegistry([ 55, StubTagger('words', input_layers=[]) ])
    with pytest.raises(TypeError):
        taggers = TaggersRegistry([])
        # TypeError: (!) Expected a subclass of Tagger or Retagger, not <class 'str'>.
        taggers.update( "Tere!" )
    
    # Case 2: missing dependencies and missing taggers
    # Note that the resolver can be created even if some layers are missing. 
    # But an UserWarning will be encountered
    with pytest.warns(UserWarning, match=".+'compound_tokens_v2' is missing.+Layer 'words' cannot be created"):
        # UserWarning: (!) StubTagger's input layer 'compound_tokens_v2' is missing from the layer graph. 
        # Layer 'words' cannot be created.
        taggers = TaggersRegistry([StubTagger('tokens', input_layers=[]),
                           StubTagger('compound_tokens', input_layers=['tokens']),
                           StubTagger('words', input_layers=['compound_tokens_v2']),
                           StubTagger('sentences', input_layers=['words']) ])
    resolver1 = LayerResolver(taggers)
    text1 = create_text_object('test')
    # But applying the resolver should throw an exception
    with pytest.raises(Exception):
        # Exception: (!) No tagger registered for creating layer 'compound_tokens_v2'.
        resolver1.apply(text1, 'sentences')
    with pytest.raises(Exception):
        # Exception: (!) No tagger registered for creating layer 'morph_analysis'.
        resolver1.apply(text1, 'morph_analysis')
    
    # Case 3: retaggers instead of taggers; adding retagger before tagger
    with pytest.raises(TypeError):
        # TypeError: (!) Expected a subclass of Tagger, not Retagger (StubRetagger).
        taggers = TaggersRegistry([StubTagger('words', input_layers=[]),
                           StubRetagger('sentences', input_layers=['words', 'sentences']) ])
    with pytest.raises(Exception):
        # Exception: (!) Cannot add a retagger for the layer 'morph_analysis': no tagger for creating the layer!
        resolver1.update( StubRetagger('morph_analysis', input_layers=['words', 'morph_analysis']) )
    with pytest.raises(ValueError):
        #  ValueError: (!) Unexpected output_layer 'words_2' in StubRetagger! Expecting 'words' as the output_layer.
        taggers = TaggersRegistry([ [StubTagger('words', input_layers=[]),
                             StubRetagger('words_2', input_layers=['words'])] ])
    with pytest.raises(TypeError):
        # TypeError: (!) The first entry in the taggers list should be a tagger, 
        # not retagger (<class 'StubRetagger'>).
        taggers = TaggersRegistry([ [StubRetagger('words', input_layers=['words']),
                             StubTagger('words', input_layers=[])] ])
    with pytest.raises(TypeError):
        # TypeError: (!) Expected a subclass of Retagger, but got <class 'StubTagger'>
        taggers = TaggersRegistry([ [StubTagger('words', input_layers=[]),
                             StubRetagger('words', input_layers=['words']),
                             StubTagger('words', input_layers=['words'])] ])


def test_create_resolver_circular_dependencies():
    # Test that an exception will be thrown if the layer graph contains circular dependencies
    with pytest.raises(Exception):
        # Exception: (!) The layer graph is not acyclic! Please eliminate circular dependencies between taggers/retaggers.
        taggers = TaggersRegistry([StubTagger('tokens', input_layers=['words']),
                           StubTagger('compound_tokens', input_layers=['tokens']),
                           StubTagger('words', input_layers=['compound_tokens', 'tokens']) ])


def test_resolver_list_layers():
    # Test that resolver's registered layers can be returned in the order of their dependencies
    taggers = TaggersRegistry([StubTagger('compound_tokens', input_layers=['tokens']),
                       StubTagger('words', input_layers=['compound_tokens']),
                       StubTagger('morph_analysis', input_layers=['words', 'sentences']),
                       StubTagger('sentences', input_layers=['words']),
                       StubTagger('tokens', input_layers=[])
                       ])
    resolver = LayerResolver(taggers)
    assert list(resolver.list_layers()) == ['tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'] 


def test_resolver_access_and_update_default_layers():
    # Test that resolver's default layers can be accessed and updated
    taggers = TaggersRegistry([StubTagger('compound_tokens', input_layers=['tokens']),
                       StubTagger('words', input_layers=['compound_tokens']),
                       StubTagger('morph_analysis', input_layers=['words', 'sentences']),
                       StubTagger('sentences', input_layers=['words']),
                       StubTagger('tokens', input_layers=[])
                       ])
    resolver = LayerResolver(taggers)
    assert resolver.get_default_layers() == ()
    resolver.set_default_layers( ['morph_analysis', 'sentences'] )
    assert resolver.get_default_layers() == ('morph_analysis', 'sentences')
    # Passing a tuple instead of a list should also work
    resolver.set_default_layers( resolver.get_default_layers() )
    resolver.set_default_layers( 'morph_analysis' )
    assert resolver.get_default_layers() == ('morph_analysis',)
    with pytest.raises(ValueError):
        # ValueError: (!) TaggersRegistry has no entry for layer 'morph_extended'. Registered layers are: 
        # ['tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis']
        resolver.set_default_layers( 'morph_extended' )


def test_resolver_access_taggers_retaggers():
    # Test that taggers and retaggers can be accessed by their output layer names in the resolver
    compound_tokens_tagger = StubTagger('compound_tokens', input_layers=['tokens'])
    sentence_tokenizer = StubTagger('sentences', input_layers=['words'])
    morph_analyzer = StubTagger('morph_analysis', input_layers=['words'])
    morph_retagger1 = StubRetagger('morph_analysis', input_layers=['morph_analysis', 'sentences'])
    morph_retagger2 = StubRetagger('morph_analysis', input_layers=['morph_analysis', 'compound_tokens'])
    taggers = TaggersRegistry([StubTagger('tokens', input_layers=[]),
                               compound_tokens_tagger,
                               StubTagger('words', input_layers=['compound_tokens']),
                               sentence_tokenizer,
                               [morph_analyzer, morph_retagger1, morph_retagger2]])
    resolver = LayerResolver(taggers)
    assert resolver.get_tagger('sentences') == sentence_tokenizer
    assert resolver.get_tagger('compound_tokens') == compound_tokens_tagger
    assert resolver.get_tagger('morph_analysis') == morph_analyzer
    morph_retaggers = resolver.get_retaggers('morph_analysis')
    assert len(morph_retaggers) == 2
    assert morph_retaggers[0] == morph_retagger1
    assert morph_retaggers[1] == morph_retagger2


def test_resolver_add_and_remove_retaggers():
    # Test that the resolver can be updated with new retaggers
    # and that retaggers can also be removed
    taggers = TaggersRegistry([StubTagger('tokens', input_layers=[]),
                       StubTagger('compound_tokens', input_layers=['tokens']),
                       StubTagger('words', input_layers=['compound_tokens']),
                       StubTagger('sentences', input_layers=['words']),
                       [StubTagger('morph_analysis', input_layers=['words']),
                        StubRetagger('morph_analysis', input_layers=['morph_analysis', 'sentences']),
                        StubRetagger('morph_analysis', input_layers=['morph_analysis', 'compound_tokens'])],
                       ])
    resolver = LayerResolver(taggers)
    text = create_text_object('test')
    resolver.apply(text, 'morph_analysis')
    assert set(text.layers) == {'tokens','compound_tokens', 'words', 'sentences', 'morph_analysis'}
    assert text['morph_analysis'].meta['modified'] == 2
    
    # Add one more retagger
    resolver.update( StubRetagger('morph_analysis', input_layers=['morph_analysis']) )
    text = create_text_object('test')
    resolver.apply(text, 'morph_analysis')
    assert set(text.layers) == {'tokens','compound_tokens', 'words', 'sentences', 'morph_analysis'}
    assert text['morph_analysis'].meta['modified'] == 3
    
    # Remove retaggers
    resolver.clear_retaggers('morph_analysis')
    text2 = create_text_object('test')
    resolver.apply(text2, 'morph_analysis')
    assert set(text2.layers) == {'tokens','compound_tokens', 'words', 'morph_analysis'}
    assert text2['morph_analysis'].meta['modified'] == 0


def test_redefine_resolver_with_new_taggers():
    # Test that the resolver can be updated with new taggers
    taggers = TaggersRegistry([StubTagger('tokens', input_layers=[]),
                       StubTagger('compound_tokens', input_layers=['tokens']),
                       StubTagger('words', input_layers=['compound_tokens']),
                       StubTagger('sentences', input_layers=['words']),
                       StubTagger('paragraphs', input_layers=['sentences']),
                       StubTagger('normalized_words', input_layers=['words']),
                       StubTagger('morph_analysis', input_layers=['normalized_words'])
                       ])

    resolver = LayerResolver(taggers)

    text = create_text_object('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens','compound_tokens', 'words', 'sentences'}

    resolver.update(StubTagger('words2', input_layers=['tokens']))
    resolver.update(StubTagger('sentences', input_layers=['words2']))
    text = create_text_object('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens', 'words2', 'sentences'}


