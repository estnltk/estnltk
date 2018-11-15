from estnltk.visualisation.span_decorator import SpanDecorator
from IPython.display import display_html
from estnltk.core import rel_path


class IndirectPlainSpanVisualiser(SpanDecorator):

    def __init__(self, id_mapping=None, class_mapping=None, css_file=rel_path("visualisation/prettyprinter.css"),
                 fill_empty_spans=False, css_added=False):
        self.id_mapping = id_mapping
        self.class_mapping = class_mapping
        self.css_file = css_file
        self.fill_empty_spans = fill_empty_spans
        self.css_added = css_added
    
    def __call__(self, segment):

        output = ''

        if not self.css_added:
            output += self.css()
            self.css_added = True
    
        # Simple text no span to fill
        if not self.fill_empty_spans and self.is_pure_text(segment):
            output += segment[0]
        else:
            # There is a span to decorate
            output += '<span'
            if self.id_mapping is not None:
                output += ' id=' + self.id_mapping(segment)+" "
            if self.class_mapping is not None:
                output += ' class='+ self.class_mapping(segment)+" "
            output += '>'
            output += segment[0]
            output += '</span>'

        return output

    def update_class_mapping(self, class_mapping, css_file=None):
        self.class_mapping = class_mapping
        if css_file is not None:
            self.update_css(css_file)

    def update_css(self, css_file):
        self.css_file = css_file
        display_html(self.css())

    def css(self):
        with open(self.css_file) as css_file:
            contents = css_file.read()
            output = ''.join(["<style>\n", contents, "</style>"])
        return output