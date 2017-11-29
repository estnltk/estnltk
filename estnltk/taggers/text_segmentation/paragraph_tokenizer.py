from typing import Union

from nltk import RegexpTokenizer
from estnltk.text import Layer, Text
from estnltk.taggers import Tagger


class ParagraphTokenizer(Tagger):
    description = 'Tags adjacent sentences that form a paragraph.'
    layer_name = 'paragraphs'
    attributes = []
    depends_on = ['sentences']
    configuration = None

    def __init__(self, regex='\s*\n\n'):
        self.paragraph_tokenizer = RegexpTokenizer(regex, gaps=True, discard_empty=True)
        self.configuration = {'regex': regex}

    def tag(self, text: Text, return_layer=False) ->  Union['Text', Layer]:
        '''
        Tag paragraphs layer.
        
        Paragraph can only end at the end of a sentence.
        '''
        layer = Layer(name=self.layer_name, enveloping ='sentences', ambiguous=False)
        paragraph_ends = {end for _, end in self.paragraph_tokenizer.span_tokenize(text.text)}
        start = 0
        if text.sentences:
            paragraph_ends.add(text.sentences[-1].end)
        for i, sentence in enumerate(text.sentences):
            if sentence.end in paragraph_ends:
                layer.add_span(text.sentences[start:i+1])
                start = i + 1
        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text
