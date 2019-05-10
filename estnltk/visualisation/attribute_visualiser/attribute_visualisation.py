from IPython.display import display_html
from estnltk.visualisation.attribute_visualiser.direct_attribute_visualiser import DirectAttributeVisualiser
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk.core import rel_path


class DisplayAttributes:
    """Superclass for attribute visualisers"""

    js_file = rel_path("visualisation/attribute_visualiser/prettyprinter.js")
    css_file = rel_path("visualisation/attribute_visualiser/prettyprinter.css")
    _text_id = 0

    def __init__(self):
        self.span_decorator = DirectAttributeVisualiser()

    def __call__(self, layer):
        display_html(self.html_output(layer), raw=True)
        self.__class__._text_id += 1

    def html_output(self, layer):
        segments, span_list = decompose_to_elementary_spans(layer, layer.text_object.text)

        outputs = self.css()
        outputs += self.event_handler_code()

        for segment in segments:
            outputs += self.span_decorator(segment, span_list).replace("\n", "<br>")

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
            output = ''.join(["<script>\n var text_id=", str(self._text_id),"\n", contents, "</script>"])
        return output
