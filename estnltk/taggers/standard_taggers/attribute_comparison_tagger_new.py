from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger
from typing import Sequence, Dict, Set, Iterable

class AttributeComparisonTagger(Tagger):
    """Compares the attributes of two layers"""

    conf_param = ['attributes_to_compare', 'constant_attributes']

    def __init__(self,
                 output_layer: str,
                 input_layers: Sequence[str],
                 constant_attributes: Iterable[str],
                 attributes_to_compare: Iterable[str] = None):
        self.input_layers = input_layers
        self.output_layer = output_layer
        self.attributes_to_compare = attributes_to_compare
        self.constant_attributes = constant_attributes
        self.output_attributes = list(constant_attributes)
        self.output_attributes.extend([attr + "_" + str(i + 1) for attr in attributes_to_compare for i in range(len(input_layers))])

    def _make_layer(self, text, layers, status):
        layer = Layer(name=self.output_layer, text_object=text,
                      attributes=list(self.output_attributes))

        for spans in zip(*layers.values()):
            base_span = spans[0].base_span
            assert all(base_span == span.base_span for span in spans)

            annotation = {}

            for attr in self.constant_attributes:
                if attr not in self.attributes_to_compare:
                    annotation[attr] = spans[0].annotations[0][attr]
                else:
                    span_values = set()
                    for i, span in enumerate(spans):
                        span_values.add(span[attr])
                        annotation[attr + "_" + str(i + 1)] = span.annotations[0][attr]
                    if len(span_values) == 1:
                        annotation[attr] = spans[0].annotations[0][attr]
                    else:
                        annotation[attr] = None

            layer.add_annotation(base_span, **annotation)

        return layer
