from estnltk.resolve_layer_dag import Resolver, Taggers, make_resolver
from estnltk_core import Layer
from estnltk import Text
from estnltk.taggers import Tagger


def test_simple_resolver_update():
    # Example: Modifying the pipeline -- replacing an existing tagger
    my_resolver = make_resolver()  # Create a copy of the default pipeline

    # Create a new sentence tokenizer that does not split sentences by emoticons
    from estnltk.taggers import SentenceTokenizer
    new_sentence_tokenizer = SentenceTokenizer(use_emoticons_as_endings=False)

    # Replace the sentence tokenizer on the pipeline with the new one
    my_resolver.update( new_sentence_tokenizer )

    # Test out the new tokenizer
    t = Text('No mida teksti :) Äge!')
    t.analyse('segmentation', resolver=my_resolver)  # Use new resolver instead of the default one
    assert t.sentences.text == ['No', 'mida', 'teksti', ':)', 'Äge', '!']


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

