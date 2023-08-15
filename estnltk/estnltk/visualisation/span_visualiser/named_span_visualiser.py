import copy

from estnltk_core.layer.relation_layer import NamedSpan

class NamedSpanVisualiser:
    default_overlap_colour = "#FFCC00"  # darker yellow / orange

    def __init__(self,text_id,fill_empty_spans=False,mapping_dict=None,span_names_formatting=None):
        self.fill_empty_spans = fill_empty_spans
        self.mapping_dict = mapping_dict or {"background":self.default_bg_mapping}
        self.span_names_formatting = span_names_formatting or self.default_span_names_formatting
        self.text_id = text_id

    def default_bg_mapping(self, segment):
        if len(segment[1]) > 1:
            return self.default_overlap_colour
        return "yellow"

    def is_pure_text(self, segment):
        if len(segment[1]) > 0:
            return False
        return True
    
    def default_span_names_formatting(self, span_names):
        # add covered span names as a super-script, approx 75% size of the regular text
        output=[]
        output.append('<sup style="font-size:75%">')
        output.append(', '.join(span_names))
        output.append('</sup>')
        return ''.join(output)

    def _extract_covering_span_names_and_indexes(self, covering_named_span_indexes, all_spans):
        covering_span_names = []
        covering_span_indexes = []
        for i in covering_named_span_indexes:
            if isinstance(i,  int):
                index = i
                relation_index = None
            elif isinstance(i, tuple) and len(i)==2:
                index = i[0]
                relation_index = i[1]
            else:
                raise Exception('(!) Unexpected covering_named_span_index: {!r}.'.format(i))
            if index < len(all_spans):
                span = all_spans[index]
                assert isinstance(span, NamedSpan), \
                    f"(!) span must be an instance of NamedSpan, not {type(span)}"
                out_str = f'{span.name}'
                if relation_index is not None:
                    # add relation index, if provided
                    out_str = f'{out_str}({relation_index})'
                covering_span_names.append(out_str)
                covering_span_indexes.append(index)
            else:
                raise IndexError(f'(!) covering_named_span_index {i!r} '+\
                                 f'out of bounds of all named spans ({len(all_spans)}).')
        return covering_span_names, covering_span_indexes

    def __call__(self, segment, spans):

        if not self.fill_empty_spans and self.is_pure_text(segment):
            return segment[0]

        if self.mapping_dict is None:
            return segment[0]

        # There is a span to decorate
        output = ['<span style="']
        # copy to make it readable for mappers
        mapping_segment = copy.deepcopy(segment)
        [span_text, covering_named_span_indexes] = mapping_segment
        # Extract covering span names and indexes
        covering_span_names, covering_span_indexes = \
            self._extract_covering_span_names_and_indexes(covering_named_span_indexes, spans)
        # Fetch corresponding annotations
        mapping_segment[1] = []
        for i in covering_span_indexes:
            annotations = spans[i].relation.annotations
            mapping_segment[1].extend( annotations )
        # Provide style
        for key, value in self.mapping_dict.items():
            if key == "class" or key == "id":
                pass
            else:
                output.append(key + ":" + value(mapping_segment) + ";")
        output.append('"')
        for key, value in self.mapping_dict.items():
            if key == "class" or key == "id":
                output.append(' ' + key + "=" + value(mapping_segment))
        if len(covering_span_indexes) > 1:
            rows = []
            for i in covering_span_indexes:
                rows.append(spans[i].text)
            output.append(' span_info=' + ','.join(rows))  # text of spans for javascript
        output.append('>')
        output.append(segment[0])
        output.append('</span>')
        # Add covering span names as a super-script
        if covering_span_names:
            output.append(self.span_names_formatting(covering_span_names))
        return "".join(output)

