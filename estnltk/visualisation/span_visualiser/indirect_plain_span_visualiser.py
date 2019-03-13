from estnltk.visualisation.core.span_visualiser import SpanVisualiser
import html


class IndirectPlainSpanVisualiser(SpanVisualiser):
    """Class that visualises spans, arguments can give ids and classes to spans.
    Arguments that can be changed are id_mapping and class_mapping. These should
    be functions that take the span as the argument and return a string that will be
    the value of the corresponding attribute in the css."""

    def __init__(self, id_mapping=None, class_mapping=None, fill_empty_spans=False):

        self.id_mapping = id_mapping
        self.class_mapping = class_mapping
        self.fill_empty_spans = fill_empty_spans

    def __call__(self, segment):
        segment[0] = html.escape(segment[0])

        # Simple text no span to fill
        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]
        # There is a span to decorate
        output = ['<span']
        rows = []
        for row in segment[1]:
            rows.append(row.text)
        output.append(' span_info=' + html.escape(','.join(rows)))  # text of spans for javascript
        if self.id_mapping is not None:
            output.append(' id=' + self.id_mapping(segment) + " ")
        if self.class_mapping is not None:
            output.append(' class=' + self.class_mapping(segment) + " ")
        output.append('>')
        output.append(segment[0])
        output.append('</span>')
        return "".join(output)
