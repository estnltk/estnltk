from nltk import RegexpTokenizer
from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger


class ParagraphTokenizer(Tagger):
    """Tags adjacent sentences that form a paragraph."""
    output_layer = 'paragraphs'
    input_layers = ['sentences']
    output_attributes = ()
    conf_param = ['regex', 'paragraph_tokenizer', '_input_sentences_layer']

    def __init__(self, 
                 output_layer:str='paragraphs',
                 input_sentences_layer:str='sentences',
                 regex:str = r'\s*\n\n'):
        # Set input/output parameters
        self.output_layer = output_layer
        self._input_sentences_layer = input_sentences_layer
        self.input_layers = [input_sentences_layer]
        # Set regex
        self.paragraph_tokenizer = RegexpTokenizer(regex, gaps=True, discard_empty=True)
        self.regex = regex

    def _make_layer(self, text, layers, status: dict):
        """Tag paragraphs layer.
        
        Paragraph can only end at the end of a sentence.

        """
        layer = Layer(name=self.output_layer,
                      text_object=text,
                      enveloping=self._input_sentences_layer, 
                      ambiguous=False)
        paragraph_ends = {end for _, end in self.paragraph_tokenizer.span_tokenize(text.text)}
        start = 0
        if layers[ self._input_sentences_layer ]:
            paragraph_ends.add(layers[ self._input_sentences_layer ][-1].end)
        for i, sentence in enumerate(layers[ self._input_sentences_layer ]):
            if sentence.end in paragraph_ends:
                layer.add_annotation(layers[self._input_sentences_layer][start:i+1].spans)
                start = i + 1
        return layer
