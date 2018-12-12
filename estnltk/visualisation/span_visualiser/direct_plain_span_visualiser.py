from estnltk.visualisation.span_decorator import SpanDecorator
from estnltk.core import rel_path


class DirectPlainSpanVisualiser(SpanDecorator):
    """Class that visualises spans, arguments can be css elements. Class can be called
    by specifying styling="direct" when calling DisplaySpans. Other arguments can be specified
    when calling DisplaySpans or changing them later by changing
    DisplaySpans_object.span_decorator.argument (see notebook for examples). Arguments that
    can be changed are bg_mapping, colour_mapping, font_mapping, weight_mapping,
    italics_mapping, underline_mapping, size_mapping and tracking_mapping. These should
    be functions that take the span as the argument and return a string that will be
    the value of the corresponding attribute in the css."""
    
    default_conf_colour = "red"
    js_added = False
    
    def __init__(self, colour_mapping=None, bg_mapping=None, font_mapping=None,
                 weight_mapping=None, italics_mapping=None, underline_mapping=None,
                 size_mapping=None, tracking_mapping=None,fill_empty_spans=False,
                 js_file=rel_path("visualisation/new_prettyprinter.js")):

        self.bg_mapping = bg_mapping or self.default_bg_mapping
        self.colour_mapping = colour_mapping
        self.font_mapping = font_mapping
        self.weight_mapping = weight_mapping
        self.italics_mapping = italics_mapping
        self.underline_mapping = underline_mapping
        self.size_mapping = size_mapping
        self.tracking_mapping = tracking_mapping
        self.fill_empty_spans = fill_empty_spans
        self.js_file = js_file
    
    def __call__(self, segment):
        
        output = ''

        if not self.js_added:
            output += self.js()
            self.js_added = True
    
        # Simple text no span to fill
        if not self.fill_empty_spans and self.is_pure_text(segment):
            output += segment[0]
        else:
            # There is a span to decorate
            output += '<span style='
            if self.colour_mapping is not None:
                output += 'color:' + self.colour_mapping(segment) + ";"
            if self.bg_mapping is not None:
                output += 'background:' + self.bg_mapping(segment) + ";"
            if self.font_mapping is not None:
                output += 'font-family:' + self.font_mapping(segment) + ";"
            if self.weight_mapping is not None:
                output += 'font-weight:' + self.weight_mapping(segment) + ";"
            if self.italics_mapping is not None:
                output += 'font-style:' + self.italics_mapping(segment) + ";"
            if self.underline_mapping is not None:
                output += 'text-decoration:' + self.underline_mapping(segment) + ";"
            if self.size_mapping is not None:
                output += 'font-size:' + self.size_mapping(segment) + ";"
            if self.tracking_mapping is not None:
                output += 'letter-spacing:' + self.tracking_mapping(segment) + ";"
            output += '>'
            output += segment[0]
            output += '</span>'

        return output
