#
#   WordTaggerOld uses layers 'tokens' and 'compound_tokens'
#  as input, and creates the layer 'words'. It also provides 
#  normalized forms of the words, which are used in the 
#  succeeding phase of morphological analysis.
# 

from estnltk.text import Layer, Span
from estnltk.taggers import TaggerOld

class WordTaggerOld(TaggerOld):
    description = """Creates layer 'words' based on the layers 'tokens' and 'compound_tokens'.
                     Provides normalized forms of the words, which are used in the succeeding 
                     phase of morphological analysis.
                  """
    layer_name = 'words'
    attributes = ('normalized_form',)
    depends_on = ['compound_tokens']
    configuration = {}

    def tag(self, text: 'Text', return_layer=False) -> 'Text':
        """Tags words layer.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed. It needs to have
            layers 'tokens' and 'compound_tokens'.

        return_layer: boolean (default: False)
            If True, then the new layer is returned; otherwise 
            the new layer is attached to the Text object, and 
            the Text object is returned;

        Returns
        -------
        Text or Layer
            If return_layer==True, then returns the new layer, 
            otherwise attaches the new layer to the Text object 
            and returns the Text object;
        """
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
        #    ( to be implemented if required )
        
        # 3) Return or attach the layer
        if return_layer:
            return words
        text[self.layer_name] = words
        return text
