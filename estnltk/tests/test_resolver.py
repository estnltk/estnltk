from estnltk.resolve_layer_dag import Resolver, Taggers
from estnltk.text import Layer, Text
from estnltk.taggers import Tagger

def test_redefine():
    class TestTagger(Tagger):
        description = 'Test tagger'
        layer_name = None
        attributes = ()
        depends_on = None
        configuration = {}
        
        def __init__(self, layer_name, depends_on):
            self.layer_name = layer_name
            self.depends_on = depends_on

        def tag(self, text):
            text[self.layer_name] = Layer(self.layer_name)
    
    taggers = Taggers([
                       TestTagger('tokens', depends_on=[]),
                       TestTagger('compound_tokens', depends_on=['tokens']),
                       TestTagger('words', depends_on=['compound_tokens']),
                       TestTagger('sentences', depends_on=['words']),
                       TestTagger('paragraphs', depends_on=['sentences']),
                       TestTagger('normalized_words', depends_on=['words']),
                       TestTagger('morph_analysis', depends_on=['normalized_words'])
                       ])

    resolver = Resolver(taggers)

    text = Text('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens','compound_tokens', 'words', 'sentences'}

    resolver.update(TestTagger('words2', depends_on=['tokens']))
    resolver.update(TestTagger('sentences', depends_on=['words2']))
    text = Text('test')
    resolver.apply(text, 'sentences')
    assert set(text.layers) == {'tokens', 'words2', 'sentences'}
