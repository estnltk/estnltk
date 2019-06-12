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
                 decorator: callable = None, validator: callable = None, include_header: bool = False):
        self.input_layers = [input_layer]

        self.output_attributes = output_attributes
        if output_attributes is None:
            self.output_attributes = ()
        self.output_layer = output_layer
        self.decorator = decorator or default_decorator
        self.validator = validator or default_validator
        self.include_header = include_header

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        headers_layer = layers[self.input_layers[0]]

        layer = Layer(self.output_layer, attributes=self.output_attributes, text_object=text)
        conflict_counter = 0

        if self.include_header:
            last_span = None
            for span in headers_layer:
                if not self.validator(span):
                    continue

                if last_span is None:
                    if span.start > 0:
                        layer.add_annotation(ElementaryBaseSpan(0, span.start))
                else:
                    layer.add_annotation(ElementaryBaseSpan(last_span.start, span.start), **self.decorator(last_span))
                last_span = span

            if last_span is None:
                layer.add_annotation(ElementaryBaseSpan(0, len(text.text)))
            else:
                layer.add_annotation(ElementaryBaseSpan(last_span.start, len(text.text)), **self.decorator(last_span))
        else:
            last_span = None
            for span in headers_layer:
                if not self.validator(span):
                    continue

                if last_span is None:
                    if span.start > 0:
                        layer.add_annotation(ElementaryBaseSpan(0, span.start))
                else:
                    start = last_span.end
                    end = span.start
                    if start > end:
                        end = start
                        conflict_counter += 1
                    layer.add_annotation(ElementaryBaseSpan(start, end), **self.decorator(last_span))
                last_span = span

            if last_span is None:
                layer.add_annotation(ElementaryBaseSpan(0, len(text.text)))
            else:
                layer.add_annotation(ElementaryBaseSpan(last_span.end, len(text.text)), **self.decorator(last_span))

        layer.meta['conflicts_in_input_layer'] = conflict_counter
        return layer
