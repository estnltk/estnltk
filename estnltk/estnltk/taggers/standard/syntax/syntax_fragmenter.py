from collections import defaultdict
from estnltk import Tagger, Layer, EnvelopingSpan


class SyntaxFragmentTagger(Tagger):
    """Tag fragments on syntax layer"""

    conf_param = ['window']

    def __init__(self, syntax_layer: str, output_layer: str = 'syntax_fragments', window: int = 3):
        assert window > 0
        self.input_layers = [layer_a, layer_b]
        self.output_layer = output_layer
        self.output_attributes = ['deprel_sequence', 'score']
        self.window = window

    def _make_layer(self, text, layers, status):
        layer_a = layers[self.input_layers[0]]
        layer_b = layers[self.input_layers[1]]
        window = self.window

        aggregate_deprels = defaultdict(list)

        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                      enveloping=layer_a.name)

        for spans, deprels, scores in by_sentences(layer_a, layer_b):
            len_s = len(spans)
            window = min(len_s, window)

            for start in range(1 - window, len_s):
                end = start + window
                start = max(0, start)
                end = min(len_s, end)

                deprel_sequence = tuple(deprels[start:end])
                score = sum(scores[start:end]) / (end - start)
                aggregate_deprels[deprel_sequence].append(score)

                span = EnvelopingSpan(spans=spans[start:end],
                                      layer=layer,
                                      attributes={'deprel_sequence': deprel_sequence,
                                                  'score': score})
                layer.add_span(span)

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
