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
#  2) Use PretokenizedTextCompoundTokensTagger to create a
#     'compound_tokens' layer that preserves specific multi-
#     word units from the original text.
#     You should provide the list of preserved units upon
#     initialization of PretokenizedTextCompoundTokensTagger,
#     exactly in the same order as the appear in the text.
# 


from estnltk import EnvelopingSpan
from estnltk.text import Layer
from estnltk.taggers import Tagger


class PretokenizedTextCompoundTokensTagger(Tagger):
    """Tagger that can be used for restoring the original 
       tokenization of a pre-tokenized text.
       You can use PretokenizedTextCompoundTokensTagger 
       if you have some text that has already been manually 
       or automatically tokenized, and you want to preserve 
       exactly the original tokenization.
    """
    output_attributes = ('type', 'normalized')
    input_layers = ['tokens']
    depends_on   = input_layers
    output_layer = 'compound_tokens'
    layer_name   = output_layer
    conf_param   = ['_multiword_units']

    def __init__(self, multiword_units = []):
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
        
        """
        if multiword_units:
           # Assert the format (should be a list of list of strings)
           assert all([isinstance(mw, list) for mw in multiword_units]), \
             '(!) Unexpected input parameter: multiword_units should be a list of list of strings.'
           assert all([isinstance(unit, str) for mw in multiword_units for unit in mw ]), \
             '(!) Unexpected input parameter: multiword_units should be a list of list of strings.'
        # Attach units
        self._multiword_units = multiword_units

    def _make_layer(self, text, layers, status: dict):
        """ Creates an empty 'compound_tokens' layer, or a 
            'compound_tokens' layer filled with multiword units 
            from the list _multiword_units.
        """
        # Create an empty layer 
        layer = Layer(name=self.output_layer,
                      text_object=text,
                      enveloping='tokens',
                      attributes=self.output_attributes,
                      ambiguous=False)
        if self._multiword_units:
           # If the text has some multiword units that need to 
           # be preserved, find the multiword units from the 
           # tokens layer and mark as compound tokens
           mw_components = self._multiword_units
           mw_comp_id = 0
           mw_id      = 0
           token_spans = layers['tokens'].span_list
           token_span_id = 0
           while token_span_id < len(token_spans):
                 token_span = token_spans[token_span_id]
                 if len(mw_components) == mw_comp_id:
                    # All multiword units have been located
                    break 
                 mw_text = mw_components[mw_comp_id][mw_id]
                 if token_span.text == mw_text:
                    token_span_id_2 = token_span_id
                    i = mw_id
                    while (i < len(mw_components[mw_comp_id])):
                         mw_text = mw_components[mw_comp_id][i]
                         word_span_text = token_spans[token_span_id_2].text
                         if mw_text != word_span_text:
                            break
                         if token_span_id_2 + 1 < len(token_spans):
                            token_span_id_2 += 1
                         else:
                            break
                         i += 1
                    if i == len(mw_components[mw_comp_id]):
                       # Create a new multiword unit
                       spans = layers['tokens'][token_span_id:token_span_id+i]
                       spl = EnvelopingSpan(spans=spans)
                       spl.type = ('multiword',)
                       spl.normalized = None
                       layer.add_span(spl)
                       mw_comp_id += 1
                       mw_id = 0
                 token_span_id += 1
        return layer
