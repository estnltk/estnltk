from collections import defaultdict

from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger


class GapTagger(Tagger):
    """Tags all text regions that are not covered by any span of any input layer.
    These regions can be trimmed by trim function and annotated by decorator function.

    """
    conf_param = ['decorator','trim', 'ambiguous']

    def __init__(self,
                 output_layer,
                 input_layers,
                 trim=None,
                 output_attributes=(),
                 decorator=None,
                 ambiguous=False):
        self.input_layers = input_layers
        self.output_layer = output_layer
        self.trim = trim
        assert bool(output_attributes) == bool(decorator),\
            'decorator without attributes or attributes without decorator'
        self.output_attributes = tuple(output_attributes)
        self.decorator = decorator
        self.ambiguous = ambiguous

    def _make_layer_template(self):
        return Layer( name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=None,
                      parent=None,
                      enveloping=None,
                      ambiguous=self.ambiguous )

    def _make_layer(self, text, layers, status):
        new_layer = self._make_layer_template()
        new_layer.text_object = text
        raw_text = text.text
        layers = [layers[layer] for layer in self.input_layers]
        for start, end in find_gaps(layers, len(raw_text)):
            assert start < end, (start, end)
            if self.trim:
                t = self.trim(raw_text[start:end])
                start_new = raw_text.find(t, start)
                if start_new < start:
                    raise ValueError('misbehaving trim function: "{}"->"{}"'.format(raw_text[start:end], t))
                start = start_new
                end = start + len(t)
            if start < end:
                decorations = {}
                if self.decorator:
                    decorations = self.decorator(raw_text[start:end])
                new_layer.add_annotation((start, end), **decorations)
        return new_layer


def find_gaps(layers, text_length):
    if text_length == 0:
        return
    cover_change = defaultdict(int)
    for layer in layers:
        for span in layer:
            cover_change[span.start] += 1
            cover_change[span.end] -= 1
    if not cover_change:
        yield (0, text_length)
        return
    indexes = sorted(cover_change)
    if indexes[0] > 0:
        yield (0, indexes[0])
    cover = 0
    for i, j in zip(indexes, indexes[1:]):
        cover += cover_change[i]
        assert cover >= 0
        if not cover:
            yield (i, j)
    assert not cover + cover_change[indexes[-1]]
    if indexes[-1] < text_length:
        yield (indexes[-1], text_length)
