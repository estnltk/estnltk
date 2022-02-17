from typing import Sequence, Tuple, Callable

from collections import defaultdict
import itertools
import bisect
import random
from operator import eq
import pandas as pd

from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk_core.layer_operations import diff_layer
from estnltk_core.layer.span_operations import symm_diff_ambiguous_spans
from estnltk_core.layer_operations.iterators import iterate_intersecting_spans


class DiffTagger(Tagger):
    """Finds differences of input layers.

    DiffTagger compares two layers (old_layer and new_layer),
    and finds differences in spans and annotations.
    The output layer contains spans marking differences:

    * missing span -- base span is in old_layer but not in new_layer;
    * extra span -- base span is in new_layer but not in old_layer;
    * modified span -- base span exists in both old_layer and new_layer, but the annotations are different;

    In case of a partial overlap between spans of two layers,
    corresponding missing and extra spans are produced and annotations 
    are not compared.

    By default, the diff layer has 2 attributes:

    * input_layer_name -- name of the layer (old_layer or new_layer) where the different span belongs to;
    * span_status -- type of the difference: 'missing', 'extra' or 'modified';

    You can use output_attributes to add more attributes from comparable 
    layers to the diff layer. This helps to inspect which specific 
    annotations were different. 
    
    The diff layer's meta contains summary of differences (counts of 
    unchanged, extra and missing spans/annotations). The following
    conditions about statistics hold:
    
    * unchanged_spans + modified_spans + missing_spans = length_of_old_layer
    * unchanged_spans + modified_spans + extra_spans = length_of_new_layer
    * unchanged_annotations + missing_annotations = number_of_annotations_in_old_layer
    * unchanged_annotations + extra_annotations = number_of_annotations_in_new_layer
    * overlapped + prolonged + shortened = conflicts <= missing_spans * extra_spans
    
    Notes:

    * In case of a modified span, DiffTagger finds a symmetric difference of annotations.
      If a modified span contains both different and common annotations, DiffTagger only
      outputs different annotations, and excludes common ones. If you need the "complete
      picture of annotations", you can use the basespan of the diff span to retrieve
      corresponding spans from comparable layers and then find common annotations;
       
    * DiffTagger is rather sensitive while comparing enveloping layers: if two enveloping
      spans cover exactly the same text region, but their content spans are different
      (e.g. there is tokenization difference such as ['H', '.', 'L', '.'] vs ['H.', 'L.']),
      then DiffTagger records the difference. If you only need to detect mismatching text
      regions and don't care about inner tokenization differences, you should flatten
      enveloping layers before the comparison;
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

    def _make_layer_template(self):
        raise NotImplementedError( '(!) Unable to create the template layer. '+\
                                  ('Exact configuration of the new layer depends on the input layer {!r}').format(self.input_layers[0]) )

    def _make_layer(self, text, layers, status):
        name_a, name_b = self.input_layers
        layer_a = layers[name_a]
        layer_b = layers[name_b]

        layer = Layer(name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=layer_a.text_object,
                      parent=layer_a.parent,
                      enveloping=layer_a.enveloping,
                      ambiguous=True
                      )

        for span_a, span_b in diff_layer(layer_a, layer_b, comp=self.compare_function):
            annotations_a = []
            annotations_b = []
            if span_a is None:
                span_status = 'extra'
                base_span = span_b
                annotations_b = span_b.annotations
            elif span_b is None:
                span_status = 'missing'
                base_span = span_a
                annotations_a = span_a.annotations
            else:
                span_status = 'modified'
                base_span = span_a
                annotations_a, annotations_b = symm_diff_ambiguous_spans(span_a, span_b)

            for a in annotations_a:
                attributes = {self.span_status_attribute: span_status,
                              self.input_layer_attribute: name_a}
                layer.add_annotation(base_span, **attributes, **a)

            for a in annotations_b:
                attributes = {self.span_status_attribute: span_status,
                              self.input_layer_attribute: name_b}
                layer.add_annotation(base_span, **attributes, **a)

        layer.meta.update(diff_summary(layer, self.span_status_attribute, self.input_layer_attribute, layer_a, layer_b))

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
    layer_a_name = layer_a.name
    layer_b_name = layer_b.name
    for span in difference_layer:
        span_status = getattr(span.annotations[0], span_status_attribute)
        if span_status == 'modified':
            result['modified_spans'] += 1
            for s in span.annotations:
                layer_name = getattr(s, input_layer_attribute)
                if layer_name == layer_b_name:
                    result['extra_annotations'] += 1
                elif layer_name == layer_a_name:
                    result['missing_annotations'] += 1
                else:
                    raise ValueError('unknown input_layer: ' + layer_name)
        elif span_status == 'missing':
            result['missing_spans'] += 1
            result['missing_annotations'] += len(span.annotations)
        elif span_status == 'extra':
            result['extra_spans'] += 1
            result['extra_annotations'] += len(span.annotations)
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

    result['unchanged_spans'] = len(layer_a) - result['modified_spans'] - result['missing_spans']
    annotations_a = sum(len(s.annotations) for s in layer_a)
    result['unchanged_annotations'] = annotations_a - result['missing_annotations']

    return result


def iterate_diff_conflicts(diff_layer, span_status_attribute):
    for a, b in iterate_intersecting_spans(diff_layer):
        a_status = getattr(a.annotations[0], span_status_attribute)
        b_status = getattr(b.annotations[0], span_status_attribute)
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
    yield from (s for s in difference_layer if getattr(s.annotations[0], span_status_attribute) == 'modified')


def iterate_missing(difference_layer: Layer, span_status_attribute='span_status'):
    yield from (s for s in difference_layer if getattr(s.annotations[0], span_status_attribute) == 'missing')


def iterate_extra(difference_layer: Layer, span_status_attribute='span_status'):
    yield from (s for s in difference_layer if getattr(s.annotations[0], span_status_attribute) == 'extra')


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
