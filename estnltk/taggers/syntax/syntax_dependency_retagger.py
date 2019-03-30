from collections import defaultdict
from typing import MutableMapping

from estnltk.layer.layer import Layer
from estnltk.taggers.retagger import Retagger


class SyntaxDependencyRetagger(Retagger):
    """Adds 'parent_span', 'children' and 'parent_deprel' attributes to syntax layer."""
    conf_param = []

    def __init__(self, conll_syntax_layer='conll_syntax'):
        self.input_layers = [conll_syntax_layer]
        self.output_layer = conll_syntax_layer
        self.output_attributes = ()

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]

        attributes = list(layer.attributes)
        attributes.extend(attr for attr in ['parent_span', 'children', 'parent_deprel']
                                   if attr not in layer.attributes)
        layer.attributes = tuple(attributes)

        id_to_span = {}
        id_to_children = defaultdict(list)

        for span in layer:
            span[0].parent_span = None
            span[0].children = ()
            span[0].parent_deprel = None
            if span[0].id == 1:
                annotate_spans(id_to_span, id_to_children)
                id_to_span = {}
                id_to_children = defaultdict(list)

            id_to_span[span[0].id] = span
            id_to_children[span[0].head].append(span)

        annotate_spans(id_to_span, id_to_children)


def annotate_spans(id_to_span, id_to_children):
    for id_, span in id_to_span.items():
        for annotation in span:
            annotation.parent_span = id_to_span.get(annotation.head)

            annotation.children = tuple(id_to_children[id_])
            if annotation.parent_span is None:
                annotation.parent_deprel = None
            else:
                annotation.parent_deprel = annotation.parent_span[0].deprel

