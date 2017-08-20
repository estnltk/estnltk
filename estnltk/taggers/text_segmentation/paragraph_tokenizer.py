from nltk import RegexpTokenizer

from estnltk.text import Layer, Text


class ParagraphTokenizer:

    def __init__(self, regex='\s*\n\n'):
        self._layer_name = 'paragraphs'
        self._attributes = []
        self._depends_on = ['sentences']

        self.paragraph_tokenizer = RegexpTokenizer(regex, gaps=True, discard_empty=True)
        self._conf = "regex = '"+regex+"'"

    def tag(self, text: Text) -> Text:
        '''
        Tag paragraphs layer.
        
        Paragraph can only end at the end of a sentence.
        '''
        layer = Layer(name=self._layer_name, enveloping ='sentences', ambiguous=False)
        paragraph_ends = {end for _, end in self.paragraph_tokenizer.span_tokenize(text.text)}
        start = 0
        paragraph_ends.add(text.sentences[-1].end)
        for i, sentence in enumerate(text.sentences):
            if sentence.end in paragraph_ends:
                layer.add_span(text.sentences[start:i+1])
                start = i + 1

        text[self._layer_name] = layer
        return text

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on': self._depends_on,
                  'conf':self._conf}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'conf'])
        return df.to_html(index=False)