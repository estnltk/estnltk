from copy import copy
from typing import Sequence, Iterable

from estnltk import Layer
from estnltk.taggers import Tagger

class AttributeComparator(Tagger):
    """Compares the specified attributes of input layers.
    The new layer created will have attributes corresponding to
    the comparable attributes in all input layers and an attribute
    corresponding to the result of the comparison.

    For example, if there are two layers and the attribute 'head' is
    in attributes_to_compare, the output_attributes will include
    head_1, head_2 and head. For each head value, if the respective
    values in all input layers are equal, the head attribute will get
    the same value, otherwise its value will be None.

    Attributes that are not to be compared will receive the values of
    the first input layer."""

    conf_param = ['attributes_to_compare', 'constant_attributes']

    def __init__(self,
                 output_layer: str,
                 input_layers: Sequence[str],
                 input_attributes: Iterable[str],
                 attributes_to_compare: Iterable[str] = None):
        self.input_layers = input_layers
        self.output_layer = output_layer
        self.attributes_to_compare = attributes_to_compare
        self.constant_attributes = [attr for attr in input_attributes if attr not in attributes_to_compare]
        self.output_attributes = copy(self.constant_attributes)
        for attr in attributes_to_compare:
            self.output_attributes.append(attr)
            self.output_attributes.extend("{}_{}".format(attr, i + 1) for i in range(len(input_layers)))

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, text_object=None,
                     attributes=list(self.output_attributes))

    def _make_layer(self, text, layers, status):
        layer = self._make_layer_template()
        layer.text_object = text

        for spans in zip(*layers.values()):
            base_span = spans[0].base_span
            assert all(base_span == span.base_span for span in spans)

            annotation = {}

            for attr in self.constant_attributes:
                annotation[attr] = spans[0].annotations[0][attr]

            for attr in self.attributes_to_compare:
                span_values = set()
                for i, span in enumerate(spans):
                    span_values.add(span[attr])
                    annotation["{}_{}".format(attr, i + 1)] = span.annotations[0][attr]
                if len(span_values) == 1:
                    annotation[attr] = spans[0].annotations[0][attr]
                else:
                    annotation[attr] = None

            layer.add_annotation(base_span, **annotation)

        return layer
