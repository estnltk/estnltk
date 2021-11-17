#
#   PretokenizedTextCompoundTokensTagger can be used for 
#  restoring the original tokenization of a pre-tokenized 
#  text, e.g. if you have some text that has already been 
#  manually / automatically tokenized, and  you  want to 
#  preserve exactly the original tokenization.
#  Basically, there are two usage cases:
#  1) Use PretokenizedTextCompoundTokensTagger to create an
#     empty 'compound_tokens' layer -- this is the case when
#     you want to follow exactly the original whitespace 
#     tokenization;
#
#     TODO: this is obsolete: you can now also make an empty
#           compound_tokens layer via calling
#              CompoundTokenTagger()._make_layer_template()
#
#  2) Use PretokenizedTextCompoundTokensTagger to create a
#     'compound_tokens' layer that preserves specific multi-
#     word units from the original text.
#     You should provide the list of preserved units upon
#     initialization of PretokenizedTextCompoundTokensTagger,
#     exactly in the same order as the appear in the text.
# 

from estnltk import Layer
from estnltk.taggers import Tagger


class PretokenizedTextCompoundTokensTagger(Tagger):
    """Tagger that can be used for restoring the original 
       tokenization of a pre-tokenized text.
       You can use PretokenizedTextCompoundTokensTagger 
       if you have some text that has already been manually 
       or automatically tokenized, and you want to preserve 
       exactly the original tokenization.
    """
    output_layer = 'compound_tokens'
    output_attributes = ('type', 'normalized')
    input_layers = ['tokens']
    conf_param   = ['_multiword_units', 
                    '_input_tokens_layer' ]

    def __init__(self, multiword_units = [],
                       output_layer:str='compound_tokens',
                       input_tokens_layer:str='tokens'):
        """Initializes PretokenizedTextCompoundTokensTagger. 
        
        Parameters
        ----------
        multiword_units: list of list of str (default: [])
            A list of multiword units from the analysable text that 
            need to be preserved as compound tokens.
            An element of the list (a multiword unit) must be 
            a list of strings, where strings are consecutive tokens
            that need to be joined into compound token.
            Elements/multiword units should appear in exactly the 
            same order as they appear in the analysable text. And 
            the  multiwords  in  the  list  should  also  include 
            repetitions (if a multiword occurs in the analysable 
            text more than once).

        output_layer: str (default: 'compound_tokens')
            Name for the compound_tokens layer;
        
        input_tokens_layer: str (default: 'tokens')
            Name of the input tokens layer;
        
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_tokens_layer = input_tokens_layer
        self.input_layers = [input_tokens_layer]
        # Add multiword units (if provided)
        if multiword_units:
           # Assert the format (should be a list of list of strings)
           assert all([isinstance(mw, list) for mw in multiword_units]), \
             '(!) Unexpected input parameter: multiword_units should be a list of list of strings.'
           assert all([isinstance(unit, str) for mw in multiword_units for unit in mw ]), \
             '(!) Unexpected input parameter: multiword_units should be a list of list of strings.'
        # Attach units
        self._multiword_units = multiword_units

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     text_object=None,
                     enveloping =self._input_tokens_layer,
                     attributes =self.output_attributes,
                     ambiguous=False)

    def _make_layer(self, text, layers, status: dict):
        """ Creates an empty 'compound_tokens' layer, or a 
            'compound_tokens' layer filled with multiword units 
            from the list _multiword_units.
        """
        # Create an empty layer 
        layer = self._make_layer_template()
        layer.text_object = text
        
        if self._multiword_units:
           # If the text has some multiword units that need to 
           # be preserved, find the multiword units from the 
           # tokens layer and mark as compound tokens
           mw_components = self._multiword_units
           mw_comp_id = 0
           mw_id      = 0
           token_layer = layers[self._input_tokens_layer]
           token_span_id = 0
           while token_span_id < len(token_layer):
                 token_span = token_layer[token_span_id]
                 if len(mw_components) == mw_comp_id:
                    # All multiword units have been located
                    break 
                 mw_text = mw_components[mw_comp_id][mw_id]
                 if token_span.text == mw_text:
                    token_span_id_2 = token_span_id
                    i = mw_id
                    while (i < len(mw_components[mw_comp_id])):
                         mw_text = mw_components[mw_comp_id][i]
                         word_span_text = token_layer[token_span_id_2].text
                         if mw_text != word_span_text:
                            break
                         i += 1
                         if token_span_id_2 + 1 < len(token_layer):
                            # Move on in tokens layer
                            token_span_id_2 += 1
                         else:
                            # End of tokens
                            break
                    if i == len(mw_components[mw_comp_id]):
                        # Create a new multiword unit
                        spans = layers[self._input_tokens_layer][token_span_id:token_span_id+i]
                        layer.add_annotation(spans, type=('multiword',), normalized=None)
                        mw_comp_id += 1
                        mw_id = 0
                 token_span_id += 1
        return layer
