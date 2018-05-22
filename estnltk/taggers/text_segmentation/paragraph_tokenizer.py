from nltk import RegexpTokenizer
from estnltk import Layer, EnvelopingSpan
from estnltk.taggers import Tagger


class ParagraphTokenizer(Tagger):
    """Tags adjacent sentences that form a paragraph."""
    output_layer = 'paragraphs'
    layer_name = output_layer
    output_attributes = ()
    attributes = output_attributes
    input_layers = ['sentences']
    depends_on = input_layers
    conf_param = ['regex', 'paragraph_tokenizer']

    def __init__(self, regex='\s*\n\n'):
        self.paragraph_tokenizer = RegexpTokenizer(regex, gaps=True, discard_empty=True)
        self.regex = regex

    def _make_layer(self, raw_text: str, layers, status: dict):
        """
        Tag paragraphs layer.
        
        Paragraph can only end at the end of a sentence.
        """
        layer = Layer(name=self.output_layer, enveloping='sentences', ambiguous=False)
        paragraph_ends = {end for _, end in self.paragraph_tokenizer.span_tokenize(raw_text)}
        start = 0
        if layers['sentences']:
            paragraph_ends.add(layers['sentences'][-1].end)
        for i, sentence in enumerate(layers['sentences']):
            if sentence.end in paragraph_ends:
                span = EnvelopingSpan(spans=layers['sentences'][start:i+1].spans)
                layer.add_span(span)
                start = i + 1
        return layer
