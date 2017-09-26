from estnltk.text import Layer, Span
from estnltk.taggers import Tagger

class WordTagger(Tagger):
    description = """Creates layer 'words' based on the layers 'tokens' and 'compound_tokens'.
                     Provides normalized forms of the words, which are used in the succeeding 
                     phase of morphological analysis.
                  """
    layer_name = 'words'
    attributes = ['normalized_form']
    depends_on = ['compound_tokens']
    configuration = {}

    def tag(self, text: 'Text') -> 'Text':
        # 1) Create layer 'words' based on the layers 
        #    'tokens' and 'compound_tokens';
        #    ( include 'normalized' word forms from 
        #      previous layers if available )
        compounds = dict()
        for spl in text.compound_tokens:
            compounds[spl[0]] = Span(start=spl.start,
                                     end=spl.end)
            compounds[spl[0]].normalized_form = spl.normalized                       
        words = Layer(name=self.layer_name, 
                      attributes=self.attributes,
                      ambiguous=False)
        for span in text.tokens:
            if span in compounds:
                words.add_span(compounds[span])
            elif words.spans: 
                if span.start >= words.spans[-1].end: 
                    token_span = Span(start=span.start,
                                      end=span.end)
                    token_span.normalized_form = None
                    words.add_span(token_span)
            else:
                token_span = Span(start=span.start,
                                  end=span.end)
                token_span.normalized_form = None
                words.add_span(token_span)

        # 2) Apply custom word normalization 
        #    ( if required )
        
        # 3) Attach the layer
        text[self.layer_name] = words
        return text
