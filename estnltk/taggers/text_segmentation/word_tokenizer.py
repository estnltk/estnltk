from estnltk.text import Layer, Span
from estnltk.taggers import Tagger

class WordTokenizer(Tagger):
    layer_name = 'words'
    attributes = []
    depends_on = ['compound_tokens']
    parameters = {}

    def tag(self, text: 'Text') -> 'Text':
        compounds = dict()
        for spl in text.compound_tokens:
            compounds[spl[0]] = Span(start=spl.start, end=spl.end)
        words = Layer(name=self.layer_name, ambiguous=False)
        for span in text.tokens:
            if span in compounds:
                words.add_span(compounds[span])
            elif words.spans: 
                if span.start >= words.spans[-1].end: 
                    words.add_span(span)
            else:
                words.add_span(span)
        text[self.layer_name] = words
        return text
