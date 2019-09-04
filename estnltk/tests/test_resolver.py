from estnltk.resolve_layer_dag import Resolver, Taggers
from estnltk.text import Layer, Text
from estnltk.taggers import Tagger


def test_redefine():
    class TestTagger(Tagger):
        """Tagger for testing Resolver and Taggers.
        """
        conf_param = []

        def __init__(self, output_layer, input_layers):
            self.output_layer = output_layer
            self.input_layers = input_layers
            self.output_attributes = []

        def _make_layer(self, text: Text, layers, status=None) -> Layer:
            return Layer(self.output_layer, self.output_attributes, text_object=text)

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
