from typing import Iterable, Sequence, List
from estnltk import ElementaryBaseSpan
from estnltk.layer.span import Span
from estnltk.layer.layer import Layer
from estnltk.text import Text

import networkx as nx


def extract_sections(text: Text,
                     sections: Iterable,
                     layers_to_keep: Sequence = None,
                     trim_overlapping: bool = False):
    """Split text into a list of texts by sections.

    This method is slow on long texts.

    :param text: `Text` object
    :param sections: list of ``(start, end)`` pairs
    :param layers_to_keep: list of layer names to be kept
        The dependencies must be included, that is, if a layer in the list
        has a parent or is enveloping, then the parent or enveloped layer
        must also be in this list.
        If None (default), all layers are kept
    :param trim_overlapping
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.
    :return list of texts
        A `Text` object for every section in `sections`.

    """
    if layers_to_keep:
        for layer in layers_to_keep:
            parent = text[layer].parent
            enveloping = text[layer].enveloping
            if parent:
                assert parent in layers_to_keep, 'parent of '+layer+' missing in layers_to keep: '+parent
            if enveloping:
                assert enveloping in layers_to_keep, 'enveloping of '+layer+' missing in layers_to keep: '+enveloping
    result = []
    for start, end in sections:
        map_spans = {}
        new_text = Text(text.text[start:end])
        for layer in text.list_layers():
            layer_name = layer.name
            if layers_to_keep is not None:
                if layer_name not in layers_to_keep:
                    continue
            attribute_names = layer.attributes
            parent = layer.parent
            enveloping = layer.enveloping
            ambiguous = layer.ambiguous
            new_layer = Layer(name=layer.name,
                              attributes=attribute_names,
                              parent=parent,
                              enveloping=enveloping,
                              ambiguous=ambiguous)
            new_layer._base = layer._base
            new_text[layer_name] = new_layer
    
            if parent:
                if ambiguous:
                    for span in layer:
                        span_parent = map_spans.get((span.parent.base_span, span.parent.layer.name))
                        if span_parent:
                            new_span = Span(base_span=span_parent.base_span, parent=span_parent, layer=new_layer)
                            map_spans[(span.base_span, span.layer.name)] = new_span
                            for sp in span:
                                attributes = {attr: getattr(sp, attr) for attr in attribute_names}
                                new_layer.add_annotation(new_span, **attributes)
                else:
                    raise NotImplementedError('not ambiguous layer with parent: ' + layer_name)
            elif enveloping:
                if ambiguous:
                    raise NotImplementedError('ambiguous enveloping layer: '+ layer_name)
                else:
                    for span in layer.spans:
                        span_start = span.start
                        span_end = span.end
                        if trim_overlapping:
                            span_start = max(span_start, start)
                            span_end = min(span_end, end)
                            if span_start >= span_end:
                                continue
                        elif span_start < start or end < span_end:
                            continue
                        spans = []
                        for s in span:
                            parent = map_spans.get((s.base_span, s.layer.name))
                            if parent:
                                spans.append(parent)
                        attributes = {attr: getattr(span, attr) for attr in attribute_names}
                        new_annotation = new_layer.add_annotation(spans, **attributes)
                        map_spans[(span.base_span, span.layer.name)] = new_annotation.span
            else:
                for span in layer:
                    span_start = span.start
                    span_end = span.end
                    if trim_overlapping:
                        span_start = max(span_start, start)
                        span_end = min(span_end, end)
                        if span_start >= span_end:
                            continue
                    elif span_start < start or end < span_end:
                        continue

                    base_span = ElementaryBaseSpan(span_start-start, span_end-start)
                    new_annotation = None
                    for annotation in span.annotations:
                        new_annotation = new_layer.add_annotation(base_span, **annotation)

                    assert new_annotation is not None
                    map_spans[(span.base_span, span.layer.name)] = new_annotation.span

        result.append(new_text)
    return result


def extract_section(text,
                    start: int,
                    end: int,
                    layers_to_keep: list=None,
                    trim_overlapping: bool=False):
    return extract_sections(text, [(start, end)], layers_to_keep, trim_overlapping)[0]


def layers_to_keep_default(text, layer):
    graph = nx.DiGraph()
    for layer_name, layer_object in text.layers.items():
        if layer_object.enveloping:
            graph.add_edge(layer_name, layer_object.enveloping)
        elif layer_object.parent:
            graph.add_edge(layer_name, layer_object.parent)
            graph.add_edge(layer_object.parent, layer_name)
    return nx.descendants(graph, layer) | {layer}


def split_by(text: Text, layer: str, layers_to_keep: Sequence[str] = None, trim_overlapping: bool = False
             ) -> List[Text]:
    """Split text into a list of texts by layer.

    This method is slow on long texts.

    :param text: `Text` object
    :param layer: name of the layer to split by
    :param layers_to_keep: list of layer names to be kept
        The dependencies must be included, that is, if a layer in the list
        has a parent or is enveloping, then the parent or enveloped layer
        must also be in this list.
        If None (default), all layers are kept
    :param trim_overlapping
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.
    :return list of texts
        A `Text` object for every span in the `layer`.

    """
    if layers_to_keep is None:
        layers_to_keep = layers_to_keep_default(text, layer)
    sections = [(span.start, span.end) for span in text[layer]]
    return extract_sections(text, sections, layers_to_keep, trim_overlapping)


def split_by_sentences(text, layers_to_keep=None, trim_overlapping=False):
    """The same as
    >>> split_by(text, 'sentences', layers_to_keep, trim_overlapping)

    """
    return split_by(text, 'sentences', layers_to_keep, trim_overlapping)
