from estnltk.visualisation.core.span_visualiser import SpanVisualiser
from estnltk.common import abs_path
import html
from estnltk.converters import to_json
import copy


class DirectAttributeVisualiser(SpanVisualiser):
    """Attribute visualiser that maps css elements one by one to the segment and has javascript to display
    attributes in tables. Takes css_file as argument (path to the file) and the same css elements as in
    direct_span_visualiser"""

    def __init__(self, text_id, fill_empty_spans=False, event_attacher=None, js_added=False, css_added=False,
                 css_file=abs_path("visualisation/attribute_visualiser_outputs/prettyprinter.css")):
        self.fill_empty_spans = fill_empty_spans
        self.event_attacher = event_attacher
        self.js_added = js_added
        self.css_added = css_added
        self.css_file = css_file
        self.js_file = abs_path("visualisation/attribute_visualiser_outputs/prettyprinter.js")
        self.mapping_dict = {"class": self.default_class_mapper}
        self.text_id = text_id

    def __call__(self, segment, spans):
        segment[0] = html.escape(segment[0])

        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]
        else:
            # There is a span to decorate
            output = ['<span style="']
            # copy to make it readable for mappers
            mapping_segment = copy.deepcopy(segment)
            if len(segment[1]) == 1:
                mapping_segment[1] = spans[mapping_segment[1][0]].annotations
            for key, value in self.mapping_dict.items():
                if key == "class" or key == "id":
                    pass
                else:
                    output.append(key + ":" + value(mapping_segment,self.text_id) + ";")
            output.append(' "')
            for key, value in self.mapping_dict.items():
                if key == "class" or key == "id":
                    output.append(' ' + key + "=" + value(mapping_segment,self.text_id))

            for segment_index, all_spans_index in enumerate(segment[1]):
                output.append(" span_info")
                output.append(str(segment_index))
                output.append("='")
                output.append(to_json([dict(annotation) for annotation in spans[all_spans_index].annotations]))
                output.append("'")
                output.append(" span_index")
                output.append(str(segment_index))
                output.append("='")
                output.append(str(all_spans_index))
                output.append("'")
            rows = []
            for i in segment[1]:
                rows.append(spans[i].text)
            if type(rows[0]) is list:  # if the text objects are as lists (e.g. diff layer)
                for i in range(len(rows)):
                    rows[i] = '●'.join(rows[i])
            output.append(' span_texts="' + ','.join(rows))  # text of spans for javascript
            output.append('">')
            output.append(segment[0])
            output.append('</span>')
        return "".join(output)
