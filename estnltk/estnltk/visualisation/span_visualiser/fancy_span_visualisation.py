from IPython.display import display_html
from estnltk.visualisation.span_visualiser.plain_span_visualiser import PlainSpanVisualiser
from estnltk.visualisation.span_visualiser.ruby_span_visualiser import RubySpanVisualiser
from estnltk.visualisation.core.span_decomposition import decompose_to_elementary_spans
from estnltk.common import abs_path


class DisplaySpans:
    """Displays spans defined by the layer. By default spans are coloured light yellow, overlapping spans are red. 
       To change the behaviour, use `styles` parameter to define a mapping from CSS property name (e.g. "background", 
       "font-weight") to either a static CSS value (`str`) or `Callable[[str, List[Annotation]], str]` that 
       returns the CSS value corresponding to the input span (defined as `[str, List[Annotation]]`).
       
       Optinally, you can add a small text to be displayed on top of each span by providing `ruby_text` parameter. 
       The `ruby_text` parameter should either define a static value for a ruby text (`str`) or 
       `Callable[[str, List[Annotation]], str]` that computes ruby texts (`str`) based on properties of 
       the input span (defined as `[str, List[Annotation]]`). 
       More information about the ruby tags, please see: https://www.w3schools.com/tags/tag_ruby.asp 
       
       If `ruby_text` parameter is provided, you can also change the CSS style of the ruby annotation. Use parameter 
       `ruby_styles` to provide either a static CSS value (`str`) or `Callable[[str, List[Annotation]], str]` that 
       provides CSS value corresponding to the input span.
       The default style for all ruby annotations is "font-size:75%".
    """

    js_file = abs_path("visualisation/span_visualiser/span_visualiser.js")
    css_file = abs_path("visualisation/span_visualiser/prettyprinter.css")
    _text_id = 0

    def __init__(self, **kwargs):
        if kwargs.get('ruby_text', None) is not None:
            # Add span decorations along with ruby texts (optional)
            self.span_decorator = RubySpanVisualiser(text_id=self._text_id, **kwargs)
        else:
            # Add only span decorations
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