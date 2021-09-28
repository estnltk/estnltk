from IPython.display import display_html
from estnltk.visualisation.span_visualiser.plain_span_visualiser import PlainSpanVisualiser
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk.common import abs_path


class DisplaySpans:
    """Displays spans defined by the layer. By default spans are coloured green, overlapping spans are red.
    To change the behaviour, redefine ..._mapping. Arguments that can be changed are bg_mapping, colour_mapping,
    font_mapping, weight_mapping, italics_mapping, underline_mapping, size_mapping and tracking_mapping."""

    js_file = abs_path("visualisation/span_visualiser/span_visualiser.js")
    css_file = abs_path("visualisation/span_visualiser/prettyprinter.css")
    _text_id = 0

    def __init__(self, **kwargs):
        self.span_decorator = PlainSpanVisualiser(text_id=self._text_id, **kwargs)

    def __call__(self, layer):

        display_html(self.html_output(layer), raw=True)
        self.__class__._text_id += 1

    def html_output(self, layer):

        outputs = [self.js()]
        outputs.append(self.css())

        #
        #  This is a hack to solve issue related to Layer.display() crashing
        #  on empty layer. 
        #  TODO: find a more elegant way for fixing the problem ...
        #
        decomposed = decompose_to_elementary_spans(layer, layer.text_object.text)
        if len(decomposed) == 2:
            # A) non-empty layer
            segments, span_list = decomposed
            # put html together from js, css and html spans
            for segment in segments:
                outputs.append(self.span_decorator(segment, span_list).replace("\n","<br>"))
        elif len(decomposed) == 1:
            # B) empty layer
            segment, span_list = decomposed[0][0], []
            outputs.append( segment.replace("\n","<br>") )

        return "".join(outputs)

    def update_css(self, css_file):
        self.css_file = css_file
        display_html(self.css())

    def js(self):
        with open(self.js_file) as js_file:
            contents = js_file.read()
            output = ''.join(["<script>\n", contents, "</script>"])
        return output

    def css(self):
        with open(self.css_file) as css_file:
            contents = css_file.read()
            output = ''.join(["<style>\n", contents, "</style>"])
        return output