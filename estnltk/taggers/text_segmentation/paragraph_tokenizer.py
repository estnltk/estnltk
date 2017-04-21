from nltk import RegexpTokenizer

from estnltk.text import Layer, SpanList, Text


class ParagraphTokenizer:

    def __init__(self, regex = '\n\n'):
        # Use a simple regular expression-based tokenizer, 
        # assume that a double-newline is a paragraph-boundary
        self.paragraph_tokenizer = RegexpTokenizer(regex, gaps=True, discard_empty=True)


    def tag(self, text: Text) -> Text:
        # Apply paragraph tokenization on whole text
        spans = list( self.paragraph_tokenizer.span_tokenize(text.text) )
        # Create a new layer of paragraphs
        # Note: the new layer has no connection to other layers
        paragraphs = Layer(name='paragraphs').from_records([{
                                              'start': start,
                                                'end': end
                                                            } for start, end in spans], rewriting=True)
        text['paragraphs'] = paragraphs
        return text
