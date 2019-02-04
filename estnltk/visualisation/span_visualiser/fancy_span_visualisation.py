from IPython.display import display_html
from estnltk.visualisation.span_visualiser.direct_plain_span_visualiser import DirectPlainSpanVisualiser
from estnltk.visualisation.span_visualiser.indirect_plain_span_visualiser import IndirectPlainSpanVisualiser
from estnltk.visualisation.core.prettyprinter import decompose_to_elementary_spans
from estnltk.core import rel_path


class DisplaySpans:
    """Displays spans defined by the layer. By default spans are coloured green, overlapping spans are red.
    To change the behaviour, redefine ..._mapping. Arguments that can be changed are bg_mapping, colour_mapping,
    font_mapping, weight_mapping, italics_mapping, underline_mapping, size_mapping and tracking_mapping."""

    js_file = rel_path("visualisation/span_visualiser/span_visualiser.js")
    css_file = rel_path("visualisation/span_visualiser/prettyprinter.css")

    def __init__(self, styling="direct", **kwargs):
        self.styling = styling
        if self.styling == "direct":
            self.span_decorator = DirectPlainSpanVisualiser(**kwargs)
        elif self.styling == "indirect":
            self.span_decorator = IndirectPlainSpanVisualiser(**kwargs)
        else:
            raise ValueError(styling)
        display_html(self.css())

    def __call__(self, layer):

        display_html(self.html_output(layer), raw=True)

    def html_output(self, layer):

        segments = decompose_to_elementary_spans(layer, layer.text_object.text)

        outputs = [self.js()]

        # put html together from js, css and html spans
        if self.styling == "indirect":
            outputs.append(self.css())
        for segment in segments:
            outputs.append(self.span_decorator(segment))

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

    def update_class_mapping(self, class_mapping, css_file=None):
        if self.styling == "indirect":
            self.class_mapping = class_mapping
            if self.css_file is not None:
                self.update_css(css_file)
