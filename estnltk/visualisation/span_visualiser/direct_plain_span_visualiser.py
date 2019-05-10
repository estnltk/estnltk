from estnltk.visualisation.core.span_visualiser import SpanVisualiser
import html


class DirectPlainSpanVisualiser(SpanVisualiser):
    """Class that visualises spans, arguments can be css elements.
    Arguments that can be changed are bg_mapping, colour_mapping, font_mapping, weight_mapping,
    italics_mapping, underline_mapping, size_mapping and tracking_mapping. These should
    be functions that take the span as the argument and return a string that will be
    the value of the corresponding attribute in the css."""

    def __init__(self, colour_mapping=None, bg_mapping=None, font_mapping=None,
                 weight_mapping=None, italics_mapping=None, underline_mapping=None,
                 size_mapping=None, tracking_mapping=None, fill_empty_spans=False):

        self.bg_mapping = bg_mapping or self.default_bg_mapping
        self.colour_mapping = colour_mapping
        self.font_mapping = font_mapping
        self.weight_mapping = weight_mapping
        self.italics_mapping = italics_mapping
        self.underline_mapping = underline_mapping
        self.size_mapping = size_mapping
        self.tracking_mapping = tracking_mapping
        self.fill_empty_spans = fill_empty_spans

    def __call__(self, segment, spans):

        segment[0] = html.escape(segment[0])

        # Simple text no span to fill
        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]

        # There is a span to decorate
        output = ['<span style=']
        if self.colour_mapping is not None:
            output.append('color:' + self.colour_mapping(segment) + ";")
        if self.bg_mapping is not None:
            output.append('background:' + self.bg_mapping(segment) + ";")
        if self.font_mapping is not None:
            output.append('font-family:' + self.font_mapping(segment) + ";")
        if self.weight_mapping is not None:
            output.append('font-weight:' + self.weight_mapping(segment) + ";")
        if self.italics_mapping is not None:
            output.append('font-style:' + self.italics_mapping(segment) + ";")
        if self.underline_mapping is not None:
            output.append('text-decoration:' + self.underline_mapping(segment) + ";")
        if self.size_mapping is not None:
            output.append('font-size:' + self.size_mapping(segment) + ";")
        if self.tracking_mapping is not None:
            output.append('letter-spacing:' + self.tracking_mapping(segment) + ";")
        if len(segment[1]) > 1:
            output.append(' class=overlapping-span ')
            rows = []
            for i in segment[1]:
                rows.append(spans[i].text)
            output.append(' span_info=' + html.escape(','.join(rows)))  # text of spans for javascript
        output.append('>')
        output.append(segment[0])
        output.append('</span>')
        return "".join(output)
