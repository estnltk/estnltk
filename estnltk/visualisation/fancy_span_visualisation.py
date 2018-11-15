from IPython.display import display_html
from estnltk.visualisation.direct_plain_span_visualiser import DirectPlainSpanVisualiser
from estnltk.visualisation.indirect_plain_span_visualiser import IndirectPlainSpanVisualiser
from estnltk.visualisation.prettyprinter import decompose_to_elementary_spans


class DisplaySpans:
    """Displays spans defined by the layer. By default spans are coloured green, overlapping spans are red.
    To change the behaviour, redefine ..._mapping"""
    def __init__(self, styling="direct"):
        self.styling = styling
        if self.styling=="direct":
            self.span_decorator = DirectPlainSpanVisualiser()
        elif self.styling=="indirect":
            self.span_decorator = IndirectPlainSpanVisualiser()
        else:
            raise ValueError(styling)
        display_html(self.span_decorator.css())

    def __call__(self, layer):

        display_html(self.html_output(layer), raw=True)

    def html_output(self, layer):

        segments = decompose_to_elementary_spans(layer, layer.text_object.text)

        outputs=[]
        for segment in segments:
            outputs.append(self.span_decorator(segment))

        print(outputs)
        return "".join(outputs)

    def update_css(self, css_file):
        self.span_decorator.update_css(css_file)
        display_html(self.span_decorator.css())