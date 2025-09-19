from estnltk.visualisation.core.span_visualiser import SpanVisualiser
import copy
import warnings


class PlainSpanVisualiser(SpanVisualiser):

    def __init__(self, text_id, fill_empty_spans=False, styles:'Union[str, Callable[[str, List[Annotation]], str]]'=None, 
                                                        mapping_dict=None):
        self.fill_empty_spans = fill_empty_spans
        if styles is None and mapping_dict is not None:
            styles = mapping_dict
            # Issue a DeprecationWarning
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn('Parameter mapping_dict is deprecated. Please use parameter styles instead. '+\
                          'In future versions, parameter mapping_dict will be removed.', DeprecationWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
        self.mapping_dict = styles or {"background":self.default_bg_mapping}
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
                if callable(value):
                    output.append(key + ":" + value(mapping_segment) + ";")
                elif isinstance(value, str):
                    output.append(key + ":" + value + ";")
                else:
                    raise ValueError(f'(!) Unexpected value {value} in styles. Expected str or callable.')
        output.append(' "')
        # TODO: attributes "class" and "id" should not be defined under `styles` 
        for key, value in self.mapping_dict.items():
            if key == "class" or key == "id":
                if callable(value):
                    output.append(' ' + key + "=" + value(mapping_segment))
                else:
                    raise ValueError(f'(!) Unexpected value {value} in styles. Expected callable.')
        if len(segment[1]) > 1:
            rows = []
            for i in segment[1]:
                rows.append(spans[i].text)
            output.append(' span_info=' + ','.join(rows))  # text of spans for javascript
        output.append('>')
        output.append(segment[0])
        output.append('</span>')
        return "".join(output)