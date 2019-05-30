from estnltk.visualisation.core.span_visualiser import SpanVisualiser
from estnltk.core import rel_path
import html
from estnltk.converters import annotation_to_json
import copy


class DirectAttributeVisualiser(SpanVisualiser):
    """Attribute visualiser that maps css elements one by one to the segment and has javascript to display
    attributes in tables. Takes css_file as argument (path to the file) and the same css elements as in
    direct_span_visualiser"""

    def __init__(self, colour_mapping=None, bg_mapping=None, font_mapping=None,
                 weight_mapping=None, italics_mapping=None, underline_mapping=None,
                 size_mapping=None, tracking_mapping=None, fill_empty_spans=False,
                 event_attacher=None, js_added=False, css_added=False,
                 css_file=rel_path("visualisation/attribute_visualiser/prettyprinter.css"),
                 mapping_dict=None):
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
        self.mapping_dict = {"class": self.default_class_mapper}

    def __call__(self, segment, spans):
        segment[0] = html.escape(segment[0])

        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]
        else:
            # There is a span to decorate
            output = ['<span style=']
            mapping_segment = copy.deepcopy(segment)
            if len(segment[1]) == 1:
                mapping_segment[1] = spans[mapping_segment[1][0]]
            for key, value in self.mapping_dict.items():
                if key == "class" or key == "id":
                    pass
                else:
                    output.append(key + ":" + value(mapping_segment) + ";")
            for key, value in self.mapping_dict.items():
                if key == "class" or key == "id":
                    output.append(' ' + key + "=" + value(mapping_segment))

            for segment_index, all_spans_index in enumerate(segment[1]):
                output.append(" span_info")
                output.append(str(segment_index))
                output.append("='")
                output.append(annotation_to_json(spans[all_spans_index].annotations))
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
