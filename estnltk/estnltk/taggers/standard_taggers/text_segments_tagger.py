from typing import MutableMapping, List

from estnltk import ElementaryBaseSpan
from estnltk.layer.layer import Layer
from estnltk.text import Text
from estnltk.taggers import Tagger


def default_decorator(span):
    return {}


def default_validator(span):
    return True


class TextSegmentsTagger(Tagger):
    """Segments text by header layer.

    """
    conf_param = ['decorator', 'validator', 'include_header']

    def __init__(self, input_layer: str, output_layer: str, output_attributes: List[str] = None,
                 decorator: callable = default_decorator, validator: callable = default_validator,
                 include_header: bool = False):
        self.input_layers = [input_layer]

        self.output_attributes = output_attributes
        if output_attributes is None:
            self.output_attributes = ()
        self.output_layer = output_layer
        self.decorator = decorator
        self.validator = validator
        self.include_header = include_header

    def _make_layer_template(self):
        return Layer(self.output_layer, attributes=self.output_attributes, text_object=None)

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        headers_layer = layers[self.input_layers[0]]

        layer = self._make_layer_template()
        layer.text_object = text
        conflict_counter = 0

        last_span = None
        last_span_start = None
        last_span_end = None

        for span in headers_layer:
            if not self.validator(span):
                continue

            span_start = span.start
            span_end = span.end

            if last_span is None:
                if span_start > 0:
                    layer.add_annotation(ElementaryBaseSpan(0, span_start))
            else:
                if last_span_end >= span_end:
                    conflict_counter += 1
                    continue

                if self.include_header:
                    start = last_span_start
                else:
                    start = last_span_end

                if last_span_end > span_start:
                    end = last_span_end
                    conflict_counter += 1
                else:
                    end = span_start

                layer.add_annotation(ElementaryBaseSpan(start, end), **self.decorator(last_span))

            last_span_start = span_start
            last_span_end = span_end
            last_span = span

        if last_span is None:
            layer.add_annotation(ElementaryBaseSpan(0, len(text.text)))
        else:
            if self.include_header:
                start = last_span.start
            else:
                start = last_span.end

            layer.add_annotation(ElementaryBaseSpan(start, len(text.text)), **self.decorator(last_span))

        layer.meta['conflicts_in_input_layer'] = conflict_counter
        return layer
