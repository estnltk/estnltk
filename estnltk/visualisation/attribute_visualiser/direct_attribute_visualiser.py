from estnltk.visualisation.core.span_visualiser import SpanVisualiser
from estnltk.core import rel_path
import html
class DirectAttributeVisualiser(SpanVisualiser):
    """Attribute visualiser that maps css elements one by one to the segment and has javascript to display
    attributes in tables. Takes css_file as argument (path to the file) and the same css elements as in
    direct_span_visualiser"""
    def __init__(self, colour_mapping=None, bg_mapping=None, font_mapping=None,
                 weight_mapping=None, italics_mapping=None, underline_mapping=None,
                 size_mapping=None, tracking_mapping=None,fill_empty_spans=False,
                 event_attacher=None, js_added=False, css_added=False,
                 css_file=rel_path("visualisation/attribute_visualiser/prettyprinter.css")):
        self.bg_mapping = bg_mapping or self.default_bg_mapping
        self.colour_mapping = colour_mapping
        self.font_mapping = font_mapping
        self.weight_mapping = weight_mapping
        self.italics_mapping = italics_mapping
        self.underline_mapping = underline_mapping
        self.size_mapping = size_mapping
        self.tracking_mapping = tracking_mapping
        self.fill_empty_spans = fill_empty_spans
        self.event_attacher = event_attacher
        self.js_added = js_added
        self.css_added = css_added
        self.css_file = css_file
        self.js_file = rel_path("visualisation/attribute_visualiser/prettyprinter.js")
        self.class_mapping = self.default_class_mapper

    def __call__(self, segment):
        segment[0] = html.escape(segment[0])

        output=''

        if not self.css_added:
            output += self.css()
            self.css_added = True

        if not self.js_added:
            output += self.event_handler_code()
            self.js_added = True

        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]
        else:
            # There is a span to decorate
            output += '<span style='
            if self.colour_mapping is not None:
                output += 'color:' + self.colour_mapping(segment)+";"
            if self.bg_mapping is not None:
                output += 'background:'+ self.bg_mapping(segment)+";"
            if self.font_mapping is not None:
                output += 'font-family:'+ self.font_mapping(segment)+";"
            if self.weight_mapping is not None:
                output += 'font-weight:'+ self.weight_mapping(segment)+";"
            if self.italics_mapping is not None:
                output += 'font-style:'+ self.italics_mapping(segment)+";"
            if self.underline_mapping is not None:
                output += 'text-decoration:'+ self.underline_mapping(segment)+";"
            if self.size_mapping is not None:
                output += 'font-size:'+ self.size_mapping(segment)+";"
            if self.tracking_mapping is not None:
                output += 'letter-spacing:'+ self.tracking_mapping(segment)+";"
            if self.class_mapping is not None:
                output += ' class=' + self.class_mapping(segment) + " "

            spans = []
            for a_span in segment[1]:
                spans.append(str(a_span))

            output += ' span_info='
            for attribute_span in spans:
                output += "".join(attribute_span).replace(" ","")  # span info for javascript
            output += '>'
            output += segment[0]
            output += '</span>'

        return output

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