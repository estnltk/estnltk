from IPython.display import display_html
from estnltk.visualisation.attribute_visualiser.direct_attribute_visualiser import DirectAttributeVisualiser
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk.core import rel_path


class DisplayAttributes:
    """Superclass for attribute visualisers"""

    js_file = rel_path("visualisation/attribute_visualiser/prettyprinter.js")
    css_file = rel_path("visualisation/attribute_visualiser/prettyprinter.css")
    _text_id = 0
    html_displayed = False
    original_layer = None
    accepted_array = None

    def __init__(self, name=""):
        self.span_decorator = DirectAttributeVisualiser()
        self.name = name

    def __call__(self, layer):
        display_html(self.html_output(layer), raw=True)
        self.original_layer = layer
        self.__class__._text_id += 1

    def html_output(self, layer):
        segments, span_list = decompose_to_elementary_spans(layer, layer.text_object.text)

        outputs = self.css()
        outputs += self.event_handler_code()

        for segment in segments:
            outputs += self.span_decorator(segment, span_list).replace("\n", "<br>")

        outputs += '<button onclick="export_data()">Export data</button>'
        self.html_displayed = True
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

    def delete_chosen_spans(self):
        assert self.html_displayed, "HTML of this attribute visualiser hasn't been displayed yet!" \
                                    " Call this visualiser with a layer as an argument to do it."

        assert self.accepted_array is not None, "The annotation choices weren't saved! Click \"Export data\" to do it!"
