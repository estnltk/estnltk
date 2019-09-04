#
#   WordTagger uses tokens and compound_tokens layers 
#  as input, and creates the words layer. It also provides 
#  normalized forms of the words, which are used in the 
#  succeeding phase of morphological analysis.
# 

from typing import MutableMapping

from estnltk import ElementaryBaseSpan
from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger


class WordTagger(Tagger):
    """Creates words layer based on the tokens and compound_tokens layers.
       Provides normalized forms of the words, which are used in the succeeding 
       phase of morphological analysis.
    """
    output_layer = 'words'
    output_attributes = ('normalized_form',)
    input_layers = ['tokens', 'compound_tokens']
    conf_param = [  # Names of the specific input layers
                    '_input_tokens_layer', '_input_compound_tokens_layer',
                  ]

    def __init__(self,
                 output_layer:str='words',
                 input_tokens_layer:str='tokens',
                 input_compound_tokens_layer:str='compound_tokens',
                 ):
        """Initializes WordTagger.

        Parameters
        ----------
        output_layer: str (default: 'words')
            Name for the words layer;
        
        input_tokens_layer: str (default: 'tokens')
            Name of the input tokens layer;

        input_compound_tokens_layer: str (default: 'compound_tokens')
            Name of the input compound_tokens layer;
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_tokens_layer = input_tokens_layer
        self._input_compound_tokens_layer = input_compound_tokens_layer
        self.input_layers = [input_tokens_layer, input_compound_tokens_layer]

    def _make_layer(self, text, layers, status: dict):
        """Creates words layer.
        
        Parameters
        ----------
        raw_text: str
           Text string corresponding to the text in which 
           words layer will be created;
          
        layers: MutableMapping[str, Layer]
           Layers of the raw_text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           the tokens and compound_tokens layers.
          
        status: dict
           This can be used to store metadata on layer tagging.

        """
        # 1) Create layer 'words' based on the layers 
        #    'tokens' and 'compound_tokens';
        #    ( include 'normalized' word forms from 
        #      previous layers if available )
        words = Layer(name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=text,
                      ambiguous=False)

        compounds = set()
        for spl in layers[self._input_compound_tokens_layer]:
            words.add_annotation(ElementaryBaseSpan(spl.start, spl.end), normalized_form=spl.normalized)
            for sp in spl:
                compounds.add(sp.base_span)

        for span in layers[self._input_tokens_layer]:
            if span.base_span not in compounds:
                words.add_annotation(span.base_span, normalized_form=None)

        # 2) Apply custom word normalization 
        #    ( to be implemented if required )

        # 3) Return results
        return words
