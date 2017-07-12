from estnltk.text import Layer, Span


class WordTokenizer:
    
    def tag(self, text: 'Text') -> 'Text':
        compounds = dict()
        for spl in text.compound_tokens:
            compounds[spl[0]] = Span(start=spl.start, end=spl.end)
        words = Layer(name='words')
        for span in text.tokens:
            if span in compounds:
                words.add_span(compounds[span])
            elif words.spans: 
                if span.start >= words.spans[-1].end: 
                    words.add_span(span)
            else:
                words.add_span(span)
        text['words'] = words
        return text
