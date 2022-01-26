from collections import defaultdict
from typing import MutableMapping

from estnltk_core.layer.layer import Layer
from estnltk_core.taggers.retagger import Retagger
from estnltk.converters.serialisation_modules import syntax_v0


class SyntaxDependencyRetagger(Retagger):
    """Adds `parent_span` and `children` attributes to the syntax layer.

    Here the syntax layer is a layer that has at least `id` and `head` attributes as described by the `conll` format.

    The `parent_span` and `children` attributes help to navigate from a span to the parent and children of that span.

    The value of the `parent_span` attribute is the `span` in the current sentence for which `span.id == HEAD` and the
    value of the `children` attribute is a list of `span`s of the current sentence for each of which `span.head == ID`
    where `HEAD` is the value of the `head` attribute and `ID` is the value of the `id` attribute of the current span.

    If 'parent_span' or 'children' attribute already exists in the layer then the values are updated. Therefore, to
    update the dependencies in the syntax layer first update the values of head attributes and then run this retagger.

    """
    conf_param = []

    def __init__(self, conll_syntax_layer='conll_syntax'):
        self.input_layers = [conll_syntax_layer]
        self.output_layer = conll_syntax_layer
        self.output_attributes = ()

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        attributes = list(layer.attributes)
        attributes.extend(attr for attr in ['parent_span', 'children']
                          if attr not in layer.attributes)
        layer.attributes = tuple(attributes)
        secondary_attributes = list(layer.secondary_attributes)
        secondary_attributes.extend(attr for attr in ['parent_span', 'children']
                                    if attr not in secondary_attributes)
        layer.secondary_attributes = secondary_attributes

        id_to_span = {}
        id_to_children = defaultdict(list)

        for i, span in enumerate(layer):

            id_ = span.annotations[0].id
            head = span.annotations[0].head
            assert all(annotation.id == id_ for annotation in span.annotations)
            assert all(annotation.head == head for annotation in span.annotations)

            if id_ == 1:  # new sentence starts

                annotate_spans(id_to_span, id_to_children)
                id_to_span = {}
                id_to_children = defaultdict(list)

            id_to_span[id_] = span

            id_to_children[head].append(span)

        annotate_spans(id_to_span, id_to_children)

        layer.serialisation_module = syntax_v0.__version__


def annotate_spans(id_to_span, id_to_children):
    for id_, span in id_to_span.items():
        for annotation in span.annotations:
            annotation.parent_span = id_to_span.get(annotation.head)
            annotation.children = tuple(id_to_children[id_])
