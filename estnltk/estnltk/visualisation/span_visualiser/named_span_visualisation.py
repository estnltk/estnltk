from IPython.display import display_html
from estnltk.visualisation.span_visualiser.named_span_visualiser import NamedSpanVisualiser
from estnltk.visualisation.core.named_span_decomposition import decompose_to_elementary_named_spans
from estnltk.common import abs_path

from estnltk_core import RelationLayer

class DisplayNamedSpans:
    """Displays named spans defined by a relation layer. 
       By default spans are coloured light yellow, and overlapping spans are orange. 
       To change the behaviour, use `styles` parameter to define a mapping from CSS property name (e.g. "background", 
       "font-weight") to either a static CSS value (`str`) or `Callable[[str, List[RelationAnnotation]], str]` that 
       returns the CSS value correponding to the input named span (defined as `[str, List[RelationAnnotation]]`)."""

    js_file = abs_path("visualisation/span_visualiser/span_visualiser.js")
    css_file = abs_path("visualisation/span_visualiser/prettyprinter.css")
    _text_id = 0

    def __init__(self, add_relation_ids=False, **kwargs):
        self.span_decorator = NamedSpanVisualiser(text_id=self._text_id, **kwargs)
        self.add_relation_ids = add_relation_ids

    def __call__(self, layer):
        display_html(self.html_output(layer), raw=True)
        self.__class__._text_id += 1

    def html_output(self, layer):
        assert isinstance(layer, RelationLayer), \
            f"(!) layer must be an instance of RelationLayer, not {type(layer)}"

        outputs = [self.js()]
        outputs.append(self.css())

        segments, named_spans = decompose_to_elementary_named_spans(layer, layer.text_object.text, 
                                                                    add_relation_ids=self.add_relation_ids)
        if len(named_spans) > 0:
            # A) non-empty layer
            # put html together from js, css and html spans
            for segment in segments:
                outputs.append(self.span_decorator(segment, named_spans).replace("\n","<br>"))
        elif len(named_spans) == 0:
            # B) empty layer
            segment, span_list = segments[0][0], []
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