from IPython.display import display_html
from estnltk.visualisation.attribute_visualiser.direct_attribute_visualiser import DirectAttributeVisualiser
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk.core import rel_path

class DisplayAttributes:
    """Superclass for attribute visualisers"""

    js_file = rel_path("visualisation/attribute_visualiser/prettyprinter.js")
    css_file = rel_path("visualisation/attribute_visualiser/prettyprinter.css")

    def __init__(self):
        self.span_decorator = DirectAttributeVisualiser()

    def __call__(self, layer):
        display_html(self.html_output(layer), raw=True)

    def html_output(self, layer):
        segments = decompose_to_elementary_spans(layer, layer.text_object.text)

        outputs = self.event_handler_code()
        outputs += self.css()
        for segment in segments:
            outputs += self.span_decorator(segment).replace("\n", "<br>")

        outputs += '<button onclick="export_data()">Export data</button>'
        return outputs


    def css(self):
        with open(self.css_file) as css_file:
            contents = css_file.read()
            output = ''.join(["<style>\n", contents, "</style>"])
        return output

    def event_handler_code(self):
        with open(self.js_file) as js_file:
            contents = js_file.read()
            output = ''.join(["<script>\n", contents, "</script>"])
        return output