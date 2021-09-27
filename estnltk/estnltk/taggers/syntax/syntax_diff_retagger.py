from typing import MutableMapping

from estnltk import Layer
from estnltk.taggers import Retagger


class SyntaxDiffRetagger(Retagger):
    """Compares with reference syntax layer and adds 'arc_error', 'label_error' attributes to the syntax layer.

    """
    conf_param = ['reference_layer']

    def __init__(self, syntax_layer: str = 'syntax', reference_layer: str = 'syntax_gold'):
        self.input_layers = [syntax_layer, reference_layer]
        self.output_layer = syntax_layer
        self.output_attributes = ()
        self.reference_layer = reference_layer

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        reference_layer = layers[self.reference_layer]

        attributes = list(layer.attributes)
        attributes.extend(attr for attr in ['arc_error', 'label_error']
                                   if attr not in layer.attributes)
        layer.attributes = tuple(attributes)

        for span_a, span_b in zip(layer, reference_layer):
            for annotation_a, annotation_b in zip(span_a.annotations, span_b.annotations):
                annotation_a.arc_error = (annotation_a.head != annotation_b.head)
                annotation_a.label_error = (annotation_a.deprel != annotation_b.deprel)
