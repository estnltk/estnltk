from estnltk.text import Layer, Span


class WordTokenizer:
    
    def __init__(self):
        self._layer_name = 'words'
        self._attributes = []
        self._depends_on = ['compound_tokens']
    
    def tag(self, text: 'Text') -> 'Text':
        compounds = dict()
        for spl in text.compound_tokens:
            compounds[spl[0]] = Span(start=spl.start, end=spl.end)
        words = Layer(name=self._layer_name, ambiguous=False)
        for span in text.tokens:
            if span in compounds:
                words.add_span(compounds[span])
            elif words.spans: 
                if span.start >= words.spans[-1].end: 
                    words.add_span(span)
            else:
                words.add_span(span)
        text[self._layer_name] = words
        return text

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on': self._depends_on,
                  'conf':''}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'conf'])
        return df.to_html(index=False)