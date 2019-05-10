from typing import Sequence, Tuple, Callable

from collections import defaultdict
import itertools
import bisect
import random
from operator import eq
import pandas as pd

from estnltk.layer.enveloping_span import EnvelopingSpan
from estnltk.layer.layer import Layer
from estnltk.layer_operations import diff_layer
from estnltk.taggers import Tagger
from estnltk.layer.span_operations import symm_diff_ambiguous_spans
from estnltk.layer_operations import iterate_conflicting_spans


class DiffTagger(Tagger):
    """ Finds differences of input layers.
    """
    conf_param = ['input_layer_attribute', 'span_status_attribute', 'compare_function']

    def __init__(self,
                 layer_a: str,
                 layer_b: str,
                 output_layer: str,
                 output_attributes: Sequence[str],
                 compare_function: Callable = eq,
                 input_layer_attribute: str = 'input_layer_name',
                 span_status_attribute: str = 'span_status'
                 ):
        self.input_layers = (layer_a, layer_b)
        self.output_layer = output_layer
        self.compare_function = compare_function

        self.output_attributes = tuple(output_attributes)  # type: Tuple[str]
        if input_layer_attribute not in output_attributes:
            self.output_attributes = (input_layer_attribute,) + self.output_attributes
        if span_status_attribute not in output_attributes:
            self.output_attributes = (span_status_attribute,) + self.output_attributes

        assert input_layer_attribute != span_status_attribute
        self.input_layer_attribute = input_layer_attribute
        self.span_status_attribute = span_status_attribute

    def _make_layer(self, text, layers, status):
        name_a = self.input_layers[0]
        name_b = self.input_layers[1]
        layer_a = layers[name_a]
        layer_b = layers[name_b]
        # assert layer_a.attributes == layer_b.attributes
        assert layer_a.text_object is layer_b.text_object
        assert layer_a.parent == layer_b.parent
        assert layer_a.enveloping == layer_b.enveloping
        assert layer_a.ambiguous == layer_b.ambiguous

        layer = Layer(
            name=self.output_layer,
            attributes=self.output_attributes,
            text_object=layer_a.text_object,
            parent=layer_a.parent,
            enveloping=layer_a.enveloping,
            ambiguous=True
            )
        copy_attributes = [attr for attr in self.output_attributes if attr != self.span_status_attribute
                                                                  and attr != self.input_layer_attribute]

        span_status = None
        if layer_a.ambiguous:
            if layer_a.enveloping:
                for a_spans, b_spans in diff_layer(layer_a, layer_b, comp=self.compare_function):
                    base_span = None
                    if a_spans is None:
                        span_status = 'extra'
                        base_span = b_spans.span
                    if b_spans is None:
                        span_status = 'missing'
                        base_span = a_spans.span
                    if a_spans is not None and b_spans is not None:
                        base_span = a_spans.span
                        span_status = 'modified'
                        a_spans, b_spans = symm_diff_ambiguous_spans(a_spans, b_spans)
                    if a_spans is not None:
                        for a in a_spans:
                            attributes = {attr: getattr(a, attr, None) for attr in copy_attributes}
                            attributes[self.span_status_attribute] = span_status
                            attributes[self.input_layer_attribute] = name_a
                            layer.add_annotation(base_span, **attributes)
                    if b_spans is not None:
                        for b in b_spans:
                            attributes = {attr: getattr(b, attr, None) for attr in copy_attributes}
                            attributes[self.span_status_attribute] = span_status
                            attributes[self.input_layer_attribute] = name_b
                            layer.add_annotation(base_span, **attributes)
            elif layer.parent:
                # TODO:
                raise NotImplementedError()
            else:
                for a_spans, b_spans in diff_layer(layer_a, layer_b):
                    if a_spans is None:
                        a_spans_missing = []
                        span_status = 'extra'
                    else:
                        a_spans_missing = list(a_spans)
                    if b_spans is None:
                        b_spans_extra = []
                        span_status = 'missing'
                    else:
                        b_spans_extra = list(b_spans)
                    if a_spans is not None and b_spans is not None:
                        span_status = 'modified'
                        a_spans_missing, b_spans_extra = symm_diff_ambiguous_spans(a_spans, b_spans,
                                                                                   attributes=copy_attributes)
                    for a in a_spans_missing:
                        attributes = {attr: getattr(a, attr, None) for attr in copy_attributes}
                        attributes[self.span_status_attribute] = span_status
                        attributes[self.input_layer_attribute] = name_a
                        layer.add_annotation(a_spans.span, **attributes)
                    for b in b_spans_extra:
                        attributes = {attr: getattr(b, attr, None) for attr in copy_attributes}
                        attributes[self.span_status_attribute] = span_status
                        attributes[self.input_layer_attribute] = name_b
                        layer.add_annotation(b_spans.span, **attributes)
        else:
            if layer_a.enveloping:
                for a, b in diff_layer(layer_a, layer_b):
                    if a is not None:
                        attributes = {attr: getattr(a, attr, None) for attr in copy_attributes}
                        attributes[self.span_status_attribute] = name_a
                        es = EnvelopingSpan(spans=a.spans, layer=layer, attributes=attributes)
                        layer.add_span(es)
                    if b is not None:
                        attributes = {attr: getattr(b, attr, None) for attr in copy_attributes}
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


def iterate_diff_conflicts(diff_layer, span_status_attribute):
    for a, b in iterate_conflicting_spans(diff_layer):
        a_status = getattr(a[0], span_status_attribute)
        b_status = getattr(b[0], span_status_attribute)
        if a_status == 'missing' and b_status == 'extra':
            yield a, b
        elif b_status == 'missing' and a_status == 'extra':
            yield b, a


def iterate_shortened(difference_layer, span_status_attribute):
    for a, b in iterate_diff_conflicts(difference_layer, span_status_attribute):
        if a.start <= b.start and b.end <= a.end:
            yield a, b


def iterate_prolonged(difference_layer, span_status_attribute):
    for a, b in iterate_diff_conflicts(difference_layer, span_status_attribute):
        if b.start <= a.start and a.end <= b.end:
            yield a, b


def iterate_overlapped(difference_layer, span_status_attribute):
    for a, b in iterate_diff_conflicts(difference_layer, span_status_attribute):
        if a.start < b.start and a.end < b.end or a.start > b.start and a.end > b.end:
            yield a, b


def iterate_modified(difference_layer: Layer, span_status_attribute='span_status'):
    yield from (s for s in difference_layer if getattr(s[0], span_status_attribute) == 'modified')


def iterate_missing(difference_layer: Layer, span_status_attribute='span_status'):
    yield from (s for s in difference_layer if getattr(s[0], span_status_attribute) == 'missing')


def iterate_extra(difference_layer: Layer, span_status_attribute='span_status'):
    yield from (s for s in difference_layer if getattr(s[0], span_status_attribute) == 'extra')


def print_diff_summary(summary):
    m = summary
    m = m.append(pd.Series({'annotations_in_old_layer': m.unchanged_annotations + m.missing_annotations,
                            'annotations_in_new_layer': m.unchanged_annotations + m.extra_annotations,
                            'spans_in_old_layer': m.unchanged_spans + m.modified_spans + m.missing_spans,
                            'spans_in_new_layer': m.unchanged_spans + m.modified_spans + m.extra_spans
                            }))

    s = (
        'annotations in old layer  {m.annotations_in_old_layer:10}\n'
        '    unchanged_annotations       {m.unchanged_annotations:10}\n'
        '    missing_annotations         {m.missing_annotations:10}\n'
        'annotations in new layer  {m.annotations_in_new_layer:10}\n'
        '    unchanged_annotations       {m.unchanged_annotations:10}\n'
        '    extra_annotations           {m.extra_annotations:10}\n'
        'spans in old layer        {m.spans_in_old_layer:10}\n'
        '    unchanged_spans             {m.unchanged_spans:10}\n'
        '    modified_spans              {m.modified_spans:10}\n'
        '    missing_spans               {m.missing_spans:10}\n'
        'spans in new layer        {m.spans_in_new_layer:10}\n'
        '    unchanged_spans             {m.unchanged_spans:10}\n'
        '    modified_spans              {m.modified_spans:10}\n'
        '    extra_spans                 {m.extra_spans:10}\n'
        'conflicts                 {m.conflicts:10}\n'
        '   overlapped                   {m.overlapped:10}\n'
        '   prolonged                    {m.prolonged:10}\n'
        '   shortened                    {m.shortened:10}').format(m=m)
    print(s)


class DiffSampler:
    def __init__(self, collection, layer):
        self.collection = collection
        self.layer = layer
        self.layer_meta = self.collection.get_layer_meta(self.layer)

    def print_summary(self):
        m = self.layer_meta.sum()
        print_diff_summary(m)

    def sample_indexes(self, distribution, ids, k):
        result = defaultdict(list)
        cumdist = list(itertools.accumulate(distribution))
        all_diff = cumdist[-1]
        for i in sorted(random.sample(range(all_diff), min(all_diff, k))):
            doc_nr = bisect.bisect(cumdist, i)
            doc_id = ids[doc_nr]
            span_nr = i - cumdist[doc_nr] + distribution[doc_nr]
            result[doc_id].append(span_nr)
        return result

    def sample_spans(self, k, domain):
        iterator = {'modified_spans': iterate_modified,
                    'missing_spans': iterate_missing,
                    'extra_spans': iterate_extra,
                    'conflicts': iterate_diff_conflicts,
                    'overlapped': iterate_overlapped,
                    'prolonged': iterate_prolonged,
                    'shortened': iterate_shortened
                    }[domain]
        dist = list(self.layer_meta[domain])

        ids = list(self.layer_meta['text_id'])
        indexes = self.sample_indexes(dist, ids, k)

        for text_id, text in self.collection.select(layers=[self.layer], keys=list(indexes)):
            span_indexes = set(indexes[text_id])
            for span_index, span in enumerate(iterator(text[self.layer], span_status_attribute='span_status')):
                if span_index in span_indexes:
                    yield text_id, span_index, span
                    span_indexes.remove(span_index)
                    if not span_indexes:
                        break
