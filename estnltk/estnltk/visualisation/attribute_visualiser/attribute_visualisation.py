from IPython.display import display_html
from estnltk.visualisation.attribute_visualiser.direct_attribute_visualiser import DirectAttributeVisualiser
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk.common import abs_path
from estnltk_core.layer_operations import merge_layers
import warnings


class DisplayAttributes:
    """Superclass for attribute visualisers"""

    js_file = abs_path("visualisation/attribute_visualiser/prettyprinter.js")
    general_js_file = abs_path("visualisation/attribute_visualiser/general_structure.js")
    css_file = abs_path("visualisation/attribute_visualiser/prettyprinter.css")
    html_displayed = False
    original_layer = None
    accepted_array = None
    chosen_annotations = None

    def __init__(self, name=""):
        self.span_decorator = DirectAttributeVisualiser(text_id=str(name))
        self.name = name
        display_html(self.insert_script_tag(), raw=True)

    def __call__(self, layer):
        display_html(self.html_output(layer), raw=True)
        self.original_layer = layer

    def html_output(self, layer):
        segments, span_list = decompose_to_elementary_spans(layer, layer.text_object.text)

        outputs = [self.css(), self.insert_event_handler_script()]

        for segment in segments:
            outputs.append(self.span_decorator(segment, span_list).replace("\n", "<br>"))

        outputs.append('<button onclick="' + str(self.name) + '.export_data(')
        outputs.append("'")
        outputs.append(self.name)
        outputs.append("'")
        outputs.append(')">Export data</button>')
        self.html_displayed = True
        return "".join(outputs)

    def css(self):
        with open(self.css_file) as css_file:
            contents = css_file.read()
            output = '\n'.join(["<style>", contents, "</style>"])
        return output

    def insert_script_tag(self):
        with open(self.general_js_file) as f:
            contents = f.read()
        return '\n'.join(["<script>", contents, "</script>"])

    def insert_event_handler_script(self):
        with open(self.js_file) as js_file:
            contents = js_file.read()
            output = ''.join(
                ["<script>var ", str(self.name), "= new estnltk.attribute_visualiser.DisplayCell('", str(self.name),
                 "',-1,0,0); \n",
                 contents, "\n</script>"])
        return output

    def delete_chosen_spans(self):
        new_layer = self.mark_chosen_spans()
        if new_layer is None:
            return None
        for i, span in enumerate(new_layer):
            for j, annotation in enumerate(span.annotations):
                if not annotation.approved:
                    del new_layer[i].annotations[j]
        return new_layer

    def mark_chosen_spans(self):
        if not self.html_displayed:
            warnings.warn("HTML of this attribute visualiser hasn't been displayed yet!"
                          " Call this visualiser with a layer as an argument to do it.")
            return None

        if self.accepted_array is None:
            warnings.warn("The annotation choices weren't saved! Click \"Export data\" to do it!")
            return None

        attribute_list = list(self.original_layer.attributes)
        attribute_list.append("approved")
        new_layer = merge_layers(layers=[self.original_layer],
                                 output_layer='new_layer',
                                 output_attributes=attribute_list)
        map = {'1': True, '2': False, '': None}
        for span, accept_value in zip(new_layer, self.accepted_array):
            for annotation, val in zip(span.annotations, accept_value):
                annotation.approved = map[val]

        return new_layer
