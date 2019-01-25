from estnltk.visualisation.core.span_visualiser import SpanVisualiser
from IPython.display import display_html
from estnltk.core import rel_path


class IndirectPlainSpanVisualiser(SpanVisualiser):
    """Class that visualises spans, arguments can give ids and classes to spans.
    Arguments that can be changed are id_mapping and class_mapping. These should
    be functions that take the span as the argument and return a string that will be
    the value of the corresponding attribute in the css."""

    # use None as default for css_file and js_file and define default file names in the __init__ body
    def __init__(self, id_mapping=None, class_mapping=None, css_file=rel_path("visualisation/span_visualiser/prettyprinter.css"),
                 fill_empty_spans=False, css_added=False, js_file=rel_path("visualisation/span_visualiser/span_visualiser.js")):

        self.id_mapping = id_mapping
        self.class_mapping = class_mapping
        self.css_file = css_file
        self.fill_empty_spans = fill_empty_spans
        self.css_added = css_added
        self.js_file = js_file
    
    def __call__(self, segment):

        # Simple text no span to fill
        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]
        else:
            output = []
            # There is a span to decorate
            output.append('<span')
            rows = []
            for row in segment[1]:
                rows.append(row.text)
            output.append(' span_info='+','.join(rows))#text of spans for javascript
            if self.id_mapping is not None:
                output.append(' id=' + self.id_mapping(segment)+" ")
            if self.class_mapping is not None:
                output.append(' class='+ self.class_mapping(segment)+" ")
            output.append('>')
            output.append(segment[0])
            output.append('</span>')
            return "".join(output)

    def update_class_mapping(self, class_mapping, css_file=None):
        self.class_mapping = class_mapping
        if css_file is not None:
            self.update_css(css_file)

    def update_css(self, css_file):
        self.css_file = css_file
        display_html(self.css())
