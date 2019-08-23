from estnltk.resolve_layer_dag import Resolver, Taggers
from estnltk.text import Layer, Text
from estnltk.taggers import TaggerOld

def test_redefine():
    class TestTaggerOld(TaggerOld):
        description = 'Test tagger'
        layer_name = None
        attributes = ()
        depends_on = None
        configuration = {}
        
        def __init__(self, layer_name, depends_on):
            self.layer_name = layer_name
            self.depends_on = depends_on

        def tag(self, text):
            text.add_layer(Layer(self.layer_name))
    
    taggers = Taggers([
                       TestTaggerOld('tokens', depends_on=[]),
                       TestTaggerOld('compound_tokens', depends_on=['tokens']),
                       TestTaggerOld('words', depends_on=['compound_tokens']),
                       TestTaggerOld('sentences', depends_on=['words']),
                       TestTaggerOld('paragraphs', depends_on=['sentences']),
                       TestTaggerOld('normalized_words', depends_on=['words']),
                       TestTaggerOld('morph_analysis', depends_on=['normalized_words'])
                       ])

    resolver = Resolver(taggers)

    text = Text('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens','compound_tokens', 'words', 'sentences'}

    resolver.update(TestTaggerOld('words2', depends_on=['tokens']))
    resolver.update(TestTaggerOld('sentences', depends_on=['words2']))
    text = Text('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens', 'words2', 'sentences'}
