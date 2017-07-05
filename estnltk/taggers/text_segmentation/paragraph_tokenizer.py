from nltk import RegexpTokenizer

from estnltk.text import Layer, Text


class ParagraphTokenizer:

    def __init__(self, regex='\s*\n\n'):
        self.paragraph_tokenizer = RegexpTokenizer(regex, gaps=True, discard_empty=True)

    def tag(self, text: Text) -> Text:
        '''
        Tag paragraphs layer.
        
        Paragraph can only end at the end of a sentence.
        '''
        layer = Layer(name='paragraphs', enveloping = 'sentences', ambiguous=False)
        paragraph_ends = {end for _, end in self.paragraph_tokenizer.span_tokenize(text.text)}
        start = 0
        paragraph_ends.add(text.sentences[-1].end)
        for i, sentence in enumerate(text.sentences):
            if sentence.end in paragraph_ends:
                layer.add_span(text.sentences[start:i+1])
                start = i + 1

        text['paragraphs'] = layer
        return text
