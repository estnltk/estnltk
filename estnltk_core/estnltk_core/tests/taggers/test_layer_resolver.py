from typing import Union

from estnltk_core import Layer
from estnltk_core.taggers import Tagger, Retagger
from estnltk_core.taggers import TaggerLoader
from estnltk_core.taggers import TaggerLoaded
from estnltk_core.taggers.tagger_loader import TaggerClassNotFound
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

stubtagger_import_path = 'estnltk_core.tests.taggers.test_layer_resolver.StubTagger'
stubretagger_import_path = 'estnltk_core.tests.taggers.test_layer_resolver.StubRetagger'


def test_tagger_loader():
    # TaggerLoader declares the properties of a tagger (inputs, output, 
    # and importing path), and allows to load (import) the tagger on demand
    tagger_loader = TaggerLoader( 'compound_tokens', ['tokens'], 
                                  stubtagger_import_path, 
                                  {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} )
    assert tagger_loader.output_layer == 'compound_tokens'
    assert tagger_loader.input_layers == ['tokens']
    assert not tagger_loader.is_loaded()
    tagger = tagger_loader.tagger
    assert isinstance( tagger, StubTagger )
    assert tagger_loader.is_loaded()
    
    retagger_loader = TaggerLoader( 'morph_analysis', ['morph_analysis','compound_tokens' ], 
                                    stubretagger_import_path, 
                                    {'output_layer': 'morph_analysis', 
                                     'input_layers': ['morph_analysis', 'compound_tokens']} )
    assert retagger_loader.output_layer == 'morph_analysis'
    assert retagger_loader.input_layers == ['morph_analysis', 'compound_tokens']
    assert not retagger_loader.is_loaded()
    retagger = retagger_loader.tagger
    assert isinstance( retagger, StubRetagger )
    assert retagger_loader.is_loaded()
    
    # TaggerLoaded is a version of TaggerLoader that has its tagger 
    # already loaded
    tagger_loader2 = TaggerLoaded( tagger )
    assert tagger_loader.is_loaded()
    assert isinstance( tagger_loader2.tagger, StubTagger )


def test_tagger_loader_exceptions():
    # Test taggerloader with wrong module path (wrong path in the middle)
    tagger_loader = TaggerLoader( 'compound_tokens', ['tokens'], 
                                  'estnltk_core.tests.taggers2.test_layer_resolver.StubTagger', 
                                  {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} )
    with pytest.raises(ModuleNotFoundError):
        # (!) Unable to load 'StubTagger'. 
        # Please check that the module path 'estnltk_core.tests.taggers2.test_layer_resolver' is correct.
        tagger = tagger_loader.tagger
    # Test taggerloader with wrong module path (wrong first module)
    tagger_loader = TaggerLoader( 'compound_tokens', ['tokens'], 
                                  'estnltk_core2.StubTagger', 
                                  {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} )
    with pytest.raises(TaggerClassNotFound):
        # (!) Unable to load Tagger class from 'estnltk_core2.StubTagger'. 
        # Please check that the import path is correct.
        tagger = tagger_loader.tagger
    # Test taggerloader with wrong tagger name
    tagger_loader = TaggerLoader( 'compound_tokens', ['tokens'], 
                                  'estnltk_core.tests.taggers.test_layer_resolver.StubTagger2', 
                                  {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} )
    with pytest.raises(TaggerClassNotFound):
        # (!) Unable to load 'StubTagger2' from the module 'estnltk_core.tests.taggers.test_layer_resolver'. 
        # Please check that the Tagger's name and path are correct.
        tagger = tagger_loader.tagger


def test_create_resolver():
    # Test that the resolver can be created in two ways:
    # 1) providing the list of taggers upon creation
    # 2) adding taggers one by one 
    taggers = TaggersRegistry([ TaggerLoader( 'tokens', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'tokens', 'input_layers': []} ),
                                TaggerLoader( 'compound_tokens', ['tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} ),
                                TaggerLoader( 'words', ['compound_tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words', 'input_layers': ['compound_tokens']} ),
                                TaggerLoader( 'sentences', ['words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'sentences', 'input_layers': ['words']} ),
                                TaggerLoader( 'morph_analysis', ['words', 'sentences'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'morph_analysis', 'input_layers': ['words', 'sentences']} )
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
    
    # 3) new tagger loaders can also be added 
    # (but only for new layers or layers that have their tagger loaders uninitialized)
    resolver2.taggers().add_tagger_loader( TaggerLoader( 'syntax_preprocessing', ['sentences', 'morph_analysis'], 
                                                         stubtagger_import_path, 
                                                         {'output_layer': 'syntax_preprocessing', 
                                                         'input_layers': ['sentences', 'morph_analysis']} ) )
    resolver2.taggers().add_tagger_loader( TaggerLoader( 'syntax_preprocessing', 
                                                         ['syntax_preprocessing', 'compound_tokens'], 
                                                         stubretagger_import_path, 
                                                         {'output_layer': 'syntax_preprocessing', 
                                                          'input_layers': ['syntax_preprocessing', 'compound_tokens']} ),
                                         is_retagger=True )
    resolver2.taggers().add_tagger_loader( TaggerLoader( 'syntax', ['sentences', 'syntax_preprocessing'], 
                                                         stubtagger_import_path, 
                                                         {'output_layer': 'syntax', 
                                                         'input_layers': ['sentences', 'syntax_preprocessing']} ) )
    resolver2.apply(text2, 'syntax')
    assert set(text2.layers) == {'tokens', 'compound_tokens', 'words', 'sentences', \
                                 'morph_analysis', 'syntax_preprocessing', 'syntax'}
    assert text2['syntax_preprocessing'].meta['modified'] == 1


def test_create_resolver_exceptions():
    # Test that exceptions will be thrown upon problematic tagger registry & resolver creation
    
    # Case 1: trying to initiate with non-taggers; trying to update non-taggers
    with pytest.raises(TypeError):
        # TypeError: (!) Expected instance of TaggerLoader, but got <class 'int'>.
        taggers = TaggersRegistry([ 55, 
                                    TaggerLoader( 'words', [], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'words', 'input_layers': []} )
                                  ])
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
        taggers = TaggersRegistry([ TaggerLoader( 'tokens', [], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'tokens', 'input_layers': []} ),
                                    TaggerLoader( 'compound_tokens', ['tokens'], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} ),
                                    TaggerLoader( 'words', ['compound_tokens_v2'], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'words', 'input_layers': ['compound_tokens_v2']} ),
                                    TaggerLoader( 'sentences', ['words'], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'sentences', 'input_layers': ['words']} ) ])
    resolver1 = LayerResolver(taggers)
    text1 = create_text_object('test')
    # But applying the resolver should throw an exception
    with pytest.raises(Exception):
        # Exception: (!) No tagger registered for creating layer 'compound_tokens_v2'.
        resolver1.apply(text1, 'sentences')
    with pytest.raises(Exception):
        # Exception: (!) No tagger registered for creating layer 'morph_analysis'.
        resolver1.apply(text1, 'morph_analysis')


def test_apply_resolver_exceptions():
    # Test that exceptions will be thrown upon using problematic tagger's registry / resolver
    # Note that a conflicting taggers registry can be created (because of lazy loading), 
    # errors occur if layer creation is requested
    
    # retaggers instead of taggers; adding retagger before tagger
    text1 = create_text_object('test')
    taggers = TaggersRegistry([TaggerLoader( 'words', [], 
                                             stubtagger_import_path, 
                                             {'output_layer': 'words', 'input_layers': []} ),
                               TaggerLoader( 'sentences', ['words', 'sentences'], 
                                             stubretagger_import_path, 
                                             {'output_layer': 'sentences', 
                                             'input_layers': ['words', 'sentences']} )
                              ])
    with pytest.raises(TypeError):
        # TypeError: (!) Error at loading taggers for layer 'sentences': Expected a subclass of Tagger, not Retagger 
        taggers.create_layer_for_text( 'sentences',  text1 )
    with pytest.raises(Exception):
        # Exception: (!) Cannot add a retagger for the layer 'morph_analysis': no tagger for creating the layer!
        resolver1.update( StubRetagger('morph_analysis', input_layers=['words', 'morph_analysis']) )
    # wrong output_layer in retagger
    taggers = TaggersRegistry([ [TaggerLoader( 'words', [], 
                                               stubtagger_import_path, 
                                               {'output_layer': 'words', 'input_layers': []} ),
                                 TaggerLoader( 'words_2', ['words'], 
                                               stubretagger_import_path, 
                                               {'output_layer': 'words_2', 'input_layers': ['words']} ),
                                ]])
    with pytest.raises(ValueError):
        # ValueError: (!) Error at loading taggers for layer 'words': 
        # Expected StubRetagger with output_layer 'words', not 'words_2'
        taggers.create_layer_for_text( 'words',  text1 )
    # wrong order: first retagger, then tagger
    taggers = TaggersRegistry([ [TaggerLoader( 'words', ['words'], 
                                               stubretagger_import_path, 
                                               {'output_layer': 'words', 'input_layers': ['words']} ),
                                 TaggerLoader( 'words_2', ['words'], 
                                               stubtagger_import_path, 
                                               {'output_layer': 'words', 'input_layers': []} ),
                                ]])
    with pytest.raises(TypeError):
        # TypeError: (!) Error at loading taggers for layer 'words': 
        # Expected a subclass of Tagger, not Retagger StubRetagger
        taggers.create_layer_for_text( 'words',  text1 )
    # wrong order: retagger followed by tagger in the end
    taggers = TaggersRegistry([ [TaggerLoader( 'words', [], 
                                               stubtagger_import_path, 
                                               {'output_layer': 'words', 'input_layers': []} ),
                                 TaggerLoader( 'words', ['words'], 
                                               stubretagger_import_path, 
                                               {'output_layer': 'words', 'input_layers': ['words']} ),
                                 TaggerLoader( 'words', ['words'], 
                                               stubtagger_import_path, 
                                               {'output_layer': 'words', 'input_layers': ['words']} ),
                                ]] )
    with pytest.raises(TypeError):
        # TypeError: (!) Error at loading taggers for layer 'words': 
        # Expected a subclass of Retagger, but got StubTagger
        taggers.create_layer_for_text( 'words',  text1 )
    
    #
    # Test mismatches between TaggerLoader's configuration declarations and Tagger's actual configuration
    #
    # Mismatching tagger's output layer
    taggers = TaggersRegistry([ TaggerLoader( 'words', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words2', 'input_layers': []} )
                              ])
    with pytest.raises(ValueError):
        # ValueError: (!) Error at loading taggers for layer 'words': 
        # Expected StubTagger with output_layer 'words', not 'words2'
        taggers.create_layer_for_text( 'words',  text1 )
    # Mismatching retagger's output layer
    taggers = TaggersRegistry([[ TaggerLoader( 'words', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words', 'input_layers': []} ),
                                TaggerLoader( 'words', [], 
                                              stubretagger_import_path, 
                                              {'output_layer': 'words2', 'input_layers': ['words2']} )
                               ]])
    with pytest.raises(ValueError):
        # ValueError: (!) Error at loading taggers for layer 'words': 
        # Expected StubRetagger with output_layer 'words', not 'words2'
        taggers.create_layer_for_text( 'words',  text1 )
    # Mismatching (missing) input layers
    taggers = TaggersRegistry([ TaggerLoader( 'words', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words', 'input_layers': []} ),
                                TaggerLoader( 'phrases', ['words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'phrases', 'input_layers': ['words2']} ),
                              ])
    with pytest.raises(ValueError):
        # ValueError: (!) Error at loading taggers for layer 'phrases': 
        # StubTagger's input_layer 'words2' is not listed in TaggerLoader's input layers ['words']
        taggers.create_layer_for_text( 'phrases',  text1 )
    # Mismatching (redundant) input layers
    with pytest.warns(UserWarning, match=".+'lower_tokens' is missing.+Layer 'merged_tokens' cannot be created"):
        taggers = TaggersRegistry([ TaggerLoader( 'tokens', [], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'tokens', 'input_layers': []} ),
                                    TaggerLoader( 'merged_tokens', ['tokens', 'lower_tokens'], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'merged_tokens', 'input_layers': ['tokens']} ),
                                  ])
    with pytest.raises(ValueError):
        # ValueError: (!) Error at loading taggers for layer 'merged_tokens': 
        # input layers {'lower_tokens'} declared, but not used by any Tagger or Retagger.
        taggers.create_layer_for_text( 'merged_tokens',  text1 )
    # Mismatching output_attributes
    taggers = TaggersRegistry([ TaggerLoader( 'my_words', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'my_words', 'input_layers': []},
                                              output_attributes=['normalized_form'] ) 
                              ])
    with pytest.raises(ValueError):
        # ValueError: (!) Error at loading taggers for layer 'my_words': 
        # StubTagger's output_attributes () do not match with TaggerLoader's output_attributes ['normalized_form']
        taggers.create_layer_for_text( 'my_words',  text1 )


def test_create_resolver_circular_dependencies():
    # Test that an exception will be thrown if the layer graph contains circular dependencies
    with pytest.raises(Exception):
        # Exception: (!) The layer graph is not acyclic! Please eliminate circular dependencies between taggers/retaggers.
        taggers = TaggersRegistry([ TaggerLoader( 'tokens', ['words'], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'tokens', 'input_layers': ['words']} ),
                                    TaggerLoader( 'compound_tokens', ['tokens'], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} ),
                                    TaggerLoader( 'words', ['compound_tokens', 'tokens'], 
                                                  stubtagger_import_path, 
                                                  {'output_layer': 'words', 'input_layers': ['compound_tokens', 'tokens']} ) ])


def test_resolver_list_layers():
    # Test that resolver's registered layers can be returned in the order of their dependencies
    taggers = TaggersRegistry([ TaggerLoader( 'compound_tokens', ['tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} ),
                                TaggerLoader( 'words', ['compound_tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words', 'input_layers': ['compound_tokens']} ),
                                TaggerLoader( 'morph_analysis', ['words', 'sentences'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'morph_analysis', 'input_layers': ['words', 'sentences']} ),
                                TaggerLoader( 'sentences', ['words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'sentences', 'input_layers': ['words']} ),
                                TaggerLoader( 'tokens', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'tokens', 'input_layers': []} ),
                              ])
    resolver = LayerResolver(taggers)
    assert list(resolver.layers) == ['tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'] 


def test_resolver_access_and_update_default_layers():
    # Test that resolver's default layers can be accessed and updated
    taggers = TaggersRegistry([ TaggerLoader( 'compound_tokens', ['tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} ),
                                TaggerLoader( 'words', ['compound_tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words', 'input_layers': ['compound_tokens']} ),
                                TaggerLoader( 'morph_analysis', ['words', 'sentences'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'morph_analysis', 'input_layers': ['words', 'sentences']} ),
                                TaggerLoader( 'sentences', ['words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'sentences', 'input_layers': ['words']} ),
                                TaggerLoader( 'tokens', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'tokens', 'input_layers': []} ),
                              ])
    resolver = LayerResolver(taggers)
    assert resolver.default_layers == ()
    resolver.default_layers = ['morph_analysis', 'sentences']
    assert resolver.default_layers == ('morph_analysis', 'sentences')
    # Passing a tuple instead of a list should also work
    resolver.default_layers = resolver.default_layers
    resolver.default_layers = 'morph_analysis'
    assert resolver.default_layers == ('morph_analysis',)
    with pytest.raises(ValueError):
        # ValueError: (!) TaggersRegistry has no entry for layer 'morph_extended'. Registered layers are: 
        # ['tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis']
        resolver.default_layers = 'morph_extended'


def test_resolver_access_taggers_retaggers():
    # Test that taggers and retaggers can be accessed by their output layer names in the resolver
    compound_tokens_tagger = StubTagger('compound_tokens', input_layers=['tokens'])
    sentence_tokenizer = StubTagger('sentences', input_layers=['words'])
    morph_analyzer = StubTagger('morph_analysis', input_layers=['words'])
    morph_retagger1 = StubRetagger('morph_analysis', input_layers=['morph_analysis', 'sentences'])
    morph_retagger2 = StubRetagger('morph_analysis', input_layers=['morph_analysis', 'compound_tokens'])
    taggers = TaggersRegistry([])
    taggers.add_tagger( StubTagger('tokens', input_layers=[]) )
    taggers.add_tagger( compound_tokens_tagger )
    taggers.add_tagger( StubTagger('words', input_layers=['compound_tokens']) )
    taggers.add_tagger( sentence_tokenizer )
    taggers.add_tagger( morph_analyzer )
    taggers.add_retagger( morph_retagger1 )
    taggers.add_retagger( morph_retagger2 )
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
    taggers = TaggersRegistry([ TaggerLoader( 'tokens', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'tokens', 'input_layers': []} ),
                                TaggerLoader( 'compound_tokens', ['tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} ),
                                TaggerLoader( 'words', ['compound_tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words', 'input_layers': ['compound_tokens']} ),
                                TaggerLoader( 'sentences', ['words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'sentences', 'input_layers': ['words']} ),
                                [TaggerLoader( 'morph_analysis', ['words', 'sentences'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'morph_analysis', 'input_layers': ['words', 'sentences']} ),
                                 TaggerLoader( 'morph_analysis', ['morph_analysis', 'sentences'], 
                                              stubretagger_import_path, 
                                              {'output_layer': 'morph_analysis', 'input_layers': ['morph_analysis', 'sentences']} ),
                                 TaggerLoader( 'morph_analysis', ['morph_analysis', 'compound_tokens'], 
                                              stubretagger_import_path, 
                                              {'output_layer': 'morph_analysis', 'input_layers': ['morph_analysis', 'compound_tokens']} ),
                                 ]
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
    assert set(text2.layers) == {'tokens','compound_tokens', 'words', 'sentences', 'morph_analysis'}
    assert text2['morph_analysis'].meta['modified'] == 0


def test_redefine_resolver_with_new_taggers():
    # Test that the resolver can be updated with new taggers
    taggers = TaggersRegistry([ TaggerLoader( 'tokens', [], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'tokens', 'input_layers': []} ),
                                TaggerLoader( 'compound_tokens', ['tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'compound_tokens', 'input_layers': ['tokens']} ),
                                TaggerLoader( 'words', ['compound_tokens'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'words', 'input_layers': ['compound_tokens']} ),
                                TaggerLoader( 'sentences', ['words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'sentences', 'input_layers': ['words']} ),
                                TaggerLoader( 'paragraphs', ['sentences'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'paragraphs', 'input_layers': ['sentences']} ),
                                TaggerLoader( 'normalized_words', ['words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'normalized_words', 'input_layers': ['words']} ),
                                TaggerLoader( 'morph_analysis', ['normalized_words'], 
                                              stubtagger_import_path, 
                                              {'output_layer': 'morph_analysis', 'input_layers': ['normalized_words']} )
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


