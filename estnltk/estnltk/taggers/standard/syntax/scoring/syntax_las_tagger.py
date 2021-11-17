from collections import defaultdict

from estnltk import Layer
from estnltk.taggers import Tagger


class SyntaxLasTagger(Tagger):
    """Tag sliding Labeled Attachment Scores (LAS) and attach `aggregate_deprel_sequences` to the output layer meta.

    LAS is a standard evaluation metric in dependency syntax. It is the ratio of the number of words that are assigned
    both the correct syntactic head and the correct dependency label and the number of all words.
    This tagger creates an enveloping `las` layer each span of which is a `window`-tuple (3-tuple by default) of words
    annotated with `deprel_sequence` and 'score' attributes.

    There are two input layers: `layer_a` and `layer_b`. The output layer envelopes `layer_a`.
    The `deprel_sequence` is the sequence of `deprel` values of the corresponding `window`-tuple of spans of `layer_a`.
    The `score` attribute is calculated by comparing the corresponding `window`-tuple of spans in `layer_a` and
    `layer_b`.

    The `aggregate_deprel_sequences` field of the meta lists all LAS scores for every `deprel` sequence encountered.

    """
    conf_param = ['window']

    def __init__(self, layer_a: str, layer_b: str, output_layer: str = 'las', window: int = 3):
        assert window > 0
        self.input_layers = [layer_a, layer_b]
        self.output_layer = output_layer
        self.output_attributes = ['deprel_sequence', 'score']
        self.window = window

    def _make_layer(self, text, layers, status):
        layer_a = layers[self.input_layers[0]]
        layer_b = layers[self.input_layers[1]]

        aggregate_deprels = defaultdict(list)

        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                      enveloping=layer_a.name)

        for spans, deprels, scores in by_sentences(layer_a, layer_b):
            len_s = len(spans)
            window = min(len_s, self.window)

            for start in range(1 - window, len_s):
                end = start + window
                start = max(0, start)
                end = min(len_s, end)

                deprel_sequence = tuple(deprels[start:end])
                score = sum(scores[start:end]) / (end - start)
                aggregate_deprels[deprel_sequence].append(score)

                layer.add_annotation(spans[start:end], deprel_sequence=deprel_sequence, score=score)

        layer.meta['aggregate_deprel_sequences'] = dict(aggregate_deprels)

        return layer


def by_sentences(layer_a, layer_b):
    spans = None
    deprels = []
    scores = []
    for a, b in zip(layer_a, layer_b):
        if a.id == 1:
            if spans is not None:
                yield (spans, deprels, scores)
            spans = []
            deprels = []
            scores = []

        spans.append(a)
        deprels.append(a.deprel)
        scores.append(compare(a, b))

    yield (spans, deprels, scores)


def compare(span_a, span_b):
    if span_a.deprel == span_b.deprel:
        if span_a.parent_span is None or span_b.parent_span is None:
            if span_a.parent_span is None and span_b.parent_span is None:
                return 1
        elif span_a.parent_span.start == span_b.parent_span.start and span_a.parent_span.end == span_b.parent_span.end:
            return 1
    return 0
