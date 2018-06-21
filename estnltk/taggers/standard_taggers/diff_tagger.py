from typing import Sequence, Tuple

from estnltk import EnvelopingSpan
from estnltk import Layer
from estnltk.layer_operations import diff_layer
from estnltk.taggers import Tagger
from estnltk.layer.span_operations import symm_diff_ambiguous_spans
from estnltk.layer_operations import iterate_conflicting_spans


class DiffTagger(Tagger):
    """ Finds differences of input layers.
    """
    conf_param = ['input_layer_attribute', 'span_status_attribute']

    def __init__(self,
                 layer_a: str,
                 layer_b: str,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 input_layer_attribute: str = 'input_layer_name',
                 span_status_attribute: str = 'span_status'
                 ):
        self.input_layers = (layer_a, layer_b)
        self.output_layer = output_layer

        self.output_attributes = tuple(output_attributes)  # type: Tuple[str]
        if input_layer_attribute not in output_attributes:
            self.output_attributes = (input_layer_attribute,) + self.output_attributes
        if span_status_attribute not in output_attributes:
            self.output_attributes = (span_status_attribute,) + self.output_attributes

        assert input_layer_attribute != span_status_attribute
        self.input_layer_attribute = input_layer_attribute
        self.span_status_attribute = span_status_attribute

    def _make_layer(self, raw_text, layers, status):
        name_a = self.input_layers[0]
        name_b = self.input_layers[1]
        layer_a = layers[name_a]
        layer_b = layers[name_b]
        assert layer_a.attributes == layer_b.attributes
        assert layer_a.parent == layer_b.parent
        assert layer_a.enveloping == layer_b.enveloping
        assert layer_a.ambiguous == layer_b.ambiguous

        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            parent=layer_a.parent,
            enveloping=layer_a.enveloping,
            ambiguous=True
            )
        copy_attributes = [attr for attr in self.output_attributes if attr != self.span_status_attribute
                                                                  and attr != self.input_layer_attribute]
        span_status = None
        if layer_a.ambiguous:
            if layer_a.enveloping:
                for a_spans, b_spans in diff_layer(layer_a, layer_b):
                    if a_spans is None:
                        span_status = 'extra'
                    if b_spans is None:
                        span_status = 'missing'
                    if a_spans is not None and b_spans is not None:
                        span_status = 'modified'
                        a_spans, b_spans = symm_diff_ambiguous_spans(a_spans, b_spans)
                    if a_spans is not None:
                        for a in a_spans:
                            attributes = {attr: getattr(a, attr) for attr in copy_attributes}
                            attributes[self.span_status_attribute] = span_status
                            attributes[self.input_layer_attribute] = name_a
                            es = EnvelopingSpan(spans=a.spans, layer=layer, attributes=attributes)
                            layer.add_span(es)
                    if b_spans is not None:
                        for b in b_spans:
                            attributes = {attr: getattr(b, attr) for attr in copy_attributes}
                            attributes[self.span_status_attribute] = span_status
                            attributes[self.input_layer_attribute] = name_b
                            es = EnvelopingSpan(spans=b.spans, layer=layer, attributes=attributes)
                            layer.add_span(es)
            elif layer.parent:
                # TODO:
                raise NotImplementedError()
            else:
                for a_spans, b_spans in diff_layer(layer_a, layer_b):
                    if a_spans is None:
                        a_spans_missing = []
                    else:
                        a_spans_missing = list(a_spans)
                    if b_spans is None:
                        b_spans_extra = []
                    else:
                        b_spans_extra = list(b_spans)
                    if a_spans is not None and b_spans is not None:
                        a_spans_missing, b_spans_extra = symm_diff_ambiguous_spans(a_spans, b_spans)
                    for a in a_spans_missing:
                        attributes = {attr: getattr(a, attr) for attr in copy_attributes}
                        attributes[self.span_status_attribute] = name_a
                        layer.add_annotation(a_spans.span, **attributes)
                    for b in b_spans_extra:
                        attributes = {attr: getattr(b, attr) for attr in copy_attributes}
                        attributes[self.span_status_attribute] = name_b
                        layer.add_annotation(b_spans.span, **attributes)
        else:
            if layer_a.enveloping:
                for a, b in diff_layer(layer_a, layer_b):
                    if a is not None:
                        attributes = {attr: getattr(a, attr) for attr in copy_attributes}
                        attributes[self.span_status_attribute] = name_a
                        es = EnvelopingSpan(spans=a.spans, layer=layer, attributes=attributes)
                        layer.add_span(es)
                    if b is not None:
                        attributes = {attr: getattr(b, attr) for attr in copy_attributes}
                        attributes[self.span_status_attribute] = name_b
                        es = EnvelopingSpan(spans=b.spans, layer=layer, attributes=attributes)
                        layer.add_span(es)
            elif layer.parent:
                # TODO:
                raise NotImplementedError()
            else:
                # TODO:
                raise NotImplementedError()

        status.update(diff_summary(layer,
                                   self.span_status_attribute,
                                   self.input_layer_attribute,
                                   *self.input_layers))
        status['unchanged_spans'] = len(layer_a) - status['modified_spans'] - status['missing_spans']
        # TODO: remove these expensive assertions
        assert status['unchanged_spans'] == len(layer_b) - status['modified_spans'] - status['extra_spans']

        annotations_a = sum(len(s) for s in layer_a)
        status['unchanged_annotations'] = annotations_a - status['missing_annotations']
        annotations_b = sum(len(s) for s in layer_b)
        assert status['unchanged_annotations'] == annotations_b - status['extra_annotations']

        assert status['overlapped'] == len(tuple(iterate_overlapped(layer, self.span_status_attribute)))
        assert status['prolonged'] == len(tuple(iterate_prolonged(layer, self.span_status_attribute)))
        assert status['shortened'] == len(tuple(iterate_shortened(layer, self.span_status_attribute)))

        return layer


def diff_summary(difference_layer: Layer, span_status_attribute, input_layer_attribute, layer_a, layer_b):
    result = {'modified_spans': 0,
              'missing_spans': 0,
              'extra_spans': 0,
              'extra_annotations': 0,
              'missing_annotations': 0,
              'overlapped': 0,
              'prolonged': 0,
              'shortened': 0,
              }
    for span in difference_layer:
        span_status = getattr(span[0], span_status_attribute)
        if span_status == 'modified':
            result['modified_spans'] += 1
            for s in span:
                layer_name = getattr(s, input_layer_attribute)
                if layer_name == layer_a:
                    result['extra_annotations'] += 1
                elif layer_name == layer_b:
                    result['missing_annotations'] += 1
                else:
                    raise ValueError('unknown input_layer: ' + layer_name)
        elif span_status == 'missing':
            result['missing_spans'] += 1
            result['missing_annotations'] += len(span)
        elif span_status == 'extra':
            result['extra_spans'] += 1
            result['extra_annotations'] += len(span)
        else:
            raise ValueError('unknown span_status: ' + span_status)
    for a, b in iterate_diff_conflicts(difference_layer, span_status_attribute):
        a_start = a.start
        a_end = a.end
        b_start = b.start
        b_end = b.end
        if a_start < b_start and a_end < b_end or a_start > b_start and a_end > b_end:
            result['overlapped'] += 1
        elif b_start <= a_start and a_end <= b_end:
            result['prolonged'] += 1
        elif a_start <= b_start and b_end <= a_end:
            result['shortened'] += 1
        else:
            raise ValueError(a_start, a_end, b_start, b_end)
    result['conflicts'] = result['overlapped'] + result['prolonged'] + result['shortened']
    return result


def iterate_modified(difference_layer: Layer, span_status_attribute):
    yield from (s for s in difference_layer if getattr(s[0], span_status_attribute) == 'modified')


def iterate_missing(difference_layer: Layer, span_status_attribute):
    yield from (s for s in difference_layer if getattr(s[0], span_status_attribute) == 'missing')


def iterate_extra(difference_layer: Layer, span_status_attribute):
    yield from (s for s in difference_layer if getattr(s[0], span_status_attribute) == 'extra')


def iterate_diff_conflicts(difference_layer, span_status_attribute):
    for a, b in iterate_conflicting_spans(difference_layer):
        a_status = getattr(a[0], span_status_attribute)
        b_status = getattr(b[0], span_status_attribute)
        if a_status == 'missing' and b_status == 'extra':
            yield a, b
        elif b_status == 'missing' and a_status == 'extra':
            yield b, a


def iterate_shortened(diff_layer, span_status_attribute):
    for a, b in iterate_diff_conflicts(diff_layer, span_status_attribute):
        if a.start <= b.start and b.end <= a.end:
            yield a, b


def iterate_prolonged(diff_layer, span_status_attribute):
    for a, b in iterate_diff_conflicts(diff_layer, span_status_attribute):
        if b.start <= a.start and a.end <= b.end:
            yield a, b


def iterate_overlapped(diff_layer, span_status_attribute):
    for a, b in iterate_diff_conflicts(diff_layer, span_status_attribute):
        if a.start < b.start and a.end < b.end or a.start > b.start and a.end > b.end:
            yield a, b
