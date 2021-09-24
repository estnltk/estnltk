from estnltk.visualisation.core.span_visualiser import SpanVisualiser
import copy

class PlainSpanVisualiser(SpanVisualiser):

    def __init__(self,text_id,fill_empty_spans=False,mapping_dict=None):
        self.fill_empty_spans = fill_empty_spans
        self.mapping_dict = mapping_dict or {"background":self.default_bg_mapping}
        self.text_id = text_id

    def __call__(self, segment, spans):

        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]

        if self.mapping_dict is None:
            return segment[0]

        # There is a span to decorate
        output = ['<span style=']
        # copy to make it readable for mappers
        mapping_segment = copy.deepcopy(segment)
        if len(segment[1]) == 1:
            mapping_segment[1] = spans[mapping_segment[1][0]].annotations
        for key, value in self.mapping_dict.items():
            if key == "class" or key == "id":
                pass
            else:
                output.append(key + ":" + value(mapping_segment) + ";")
        output.append(' "')
        for key, value in self.mapping_dict.items():
            if key == "class" or key == "id":
                output.append(' ' + key + "=" + value(mapping_segment))
        if len(segment[1]) > 1:
            rows = []
            for i in segment[1]:
                rows.append(spans[i].text)
            output.append(' span_info=' + ','.join(rows))  # text of spans for javascript
        output.append('>')
        output.append(segment[0])
        output.append('</span>')
        return "".join(output)