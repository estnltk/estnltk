from estnltk_core.taggers import Tagger, Retagger
from estnltk_core import Layer
from estnltk.resolve_layer_dag import Resolver, Taggers
from estnltk import Text

import pytest

class TestTagger(Tagger):
    """Tagger for testing Resolver and Taggers.
    """
    conf_param = []

    def __init__(self, output_layer, input_layers):
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = []

    def _make_layer(self, text: Text, layers, status=None) -> Layer:
        layer = Layer(self.output_layer, self.output_attributes, text_object=text)
        layer.meta['modified'] = 0
        return layer


class TestRetagger(Retagger):
    """Retagger for testing Resolver and Taggers.
    """
    conf_param = []

    def __init__(self, output_layer, input_layers):
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = []

    def _change_layer(self, text: Text, layers, status=None) -> Layer:
        target_layer = layers[self.output_layer]
        target_layer.meta['modified'] += 1
        return None


def test_create_resolver():
    # Test that the resolver can be created in two ways:
    # 1) providing the list of taggers upon creation
    # 2) adding taggers one by one 
    taggers = Taggers([TestTagger('tokens', input_layers=[]),
                       TestTagger('compound_tokens', input_layers=['tokens']),
                       TestTagger('words', input_layers=['compound_tokens']),
                       TestTagger('sentences', input_layers=['words']),
                       TestTagger('morph_analysis', input_layers=['words', 'sentences'])
                       ])
    resolver1 = Resolver(taggers)
    text1 = Text('test')
    resolver1.apply(text1, 'morph_analysis')
    assert set(text1.layers) == {'tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'}
    
    resolver2 = Resolver( Taggers([]) )
    resolver2.update( TestTagger('tokens', input_layers=[]) )
    resolver2.update( TestTagger('compound_tokens', input_layers=['tokens']) )
    resolver2.update( TestTagger('words', input_layers=['compound_tokens']) )
    resolver2.update( TestTagger('sentences', input_layers=['words']) )
    resolver2.update( TestTagger('morph_analysis', input_layers=['words', 'sentences']) )
    text2 = Text('test')
    resolver2.apply(text2, 'morph_analysis')
    assert set(text2.layers) == {'tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'}


def test_create_resolver_exceptions():
    # Test that exceptions will be thrown upon problematic layer creation
    
    # Note that the resolver can be created even if some input layers are missing
    taggers = Taggers([TestTagger('tokens', input_layers=[]),
                       TestTagger('compound_tokens', input_layers=['tokens']),
                       TestTagger('words', input_layers=['compound_tokens_v2']),
                       TestTagger('sentences', input_layers=['words']) 
                      ])
    resolver1 = Resolver(taggers)
    text1 = Text('test')
    # But applying the resolver should throw an exception
    with pytest.raises(Exception):
        # Exception: (!) No tagger registered for creating layer 'compound_tokens_v2'.
        resolver1.apply(text1, 'sentences')


def test_resolver_add_and_remove_retaggers():
    # Test that the resolver can be updated with new retaggers
    # and that retaggers can also be removed
    taggers = Taggers([TestTagger('tokens', input_layers=[]),
                       TestTagger('compound_tokens', input_layers=['tokens']),
                       TestTagger('words', input_layers=['compound_tokens']),
                       TestTagger('sentences', input_layers=['words']),
                       [TestTagger('morph_analysis', input_layers=['words']),
                        TestRetagger('morph_analysis', input_layers=['morph_analysis', 'sentences']),
                        TestRetagger('morph_analysis', input_layers=['morph_analysis', 'compound_tokens'])],
                       ])
    resolver = Resolver(taggers)

    text = Text('test')
    resolver.apply(text, 'morph_analysis')
    assert set(text.layers) == {'tokens','compound_tokens', 'words', 'sentences', 'morph_analysis'}
    assert text['morph_analysis'].meta['modified'] == 2
    
    # Remove retaggers
    resolver.taggers.clear_retaggers('morph_analysis')
    print( resolver.taggers.rules['morph_analysis'] )
    text2 = Text('test')
    resolver.apply(text2, 'morph_analysis')
    assert set(text2.layers) == {'tokens','compound_tokens', 'words', 'morph_analysis'}
    assert text2['morph_analysis'].meta['modified'] == 0


def test_redefine_resolver_with_new_taggers():
    # Test that the resolver can be updated with new taggers
    taggers = Taggers([TestTagger('tokens', input_layers=[]),
                       TestTagger('compound_tokens', input_layers=['tokens']),
                       TestTagger('words', input_layers=['compound_tokens']),
                       TestTagger('sentences', input_layers=['words']),
                       TestTagger('paragraphs', input_layers=['sentences']),
                       TestTagger('normalized_words', input_layers=['words']),
                       TestTagger('morph_analysis', input_layers=['normalized_words'])
                       ])

    resolver = Resolver(taggers)

    text = Text('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens','compound_tokens', 'words', 'sentences'}

    resolver.update(TestTagger('words2', input_layers=['tokens']))
    resolver.update(TestTagger('sentences', input_layers=['words2']))
    text = Text('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens', 'words2', 'sentences'}

