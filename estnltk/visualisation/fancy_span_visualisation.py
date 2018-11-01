from IPython.display import display_html
from estnltk.visualisation.DirectPlainSpanVisualiser import DirectPlainSpanVisualiser
from estnltk.visualisation.IndirectPlainSpanVisualiser import IndirectPlainSpanVisualiser
from estnltk.visualisation.prettyprinter import decompose_to_elementary_spans

class DisplaySpans:
    """Displays spans defined by the layer. By default spans are coloured green, overlapping spans are red.
    To change the behaviour, redefine ..._mapping"""
    def __init__(self):
        self.span_decorator = DirectPlainSpanVisualiser(bg_mapping=self._default_bg_mapping)
    
    def __call__(self,layer):

        segments = decompose_to_elementary_spans(layer, layer.text_object.text)

        outputs=[]
        for segment in segments:
            outputs.append(self.span_decorator(segment))

        return display_html("".join(outputs), raw=True)
        
    def _default_bg_mapping(self, segment):
        if 'SADA' in segment[1][0].attr_1:
            return "green"
        else:
            return "yellow"