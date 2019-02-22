from estnltk.visualisation.core.span_visualiser import SpanVisualiser

class PlainSpanVisualiser(SpanVisualiser):

    def __init__(self,fill_empty_spans=False,mapping_dict=None):
        self.fill_empty_spans = fill_empty_spans
        self.mapping_dict = mapping_dict

    def __call__(self, segment):

        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]

        # There is a span to decorate
        output = ['<span style=']
        for key, value in self.mapping_dict.items():
            if key=="class" or key == "id":
                pass
            else:
                output.append(key + ":" + value(segment) + ";")
        for key, value in self.mapping_dict.items():
            if key == "class" or key == "id":
                output.append(' ' + key + "=" + value(segment))
        if len(segment[1]) > 1:
            rows = []
            for row in segment[1]:
                rows.append(row.text)
            output.append(' span_info=' + ','.join(rows))  # text of spans for javascript
        output.append('>')
        output.append(segment[0])
        output.append('</span>')
        return "".join(output)