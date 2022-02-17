from typing import Iterable, Sequence, List, Union
from estnltk_core import ElementaryBaseSpan
from estnltk_core.layer.span import Span
from estnltk_core.common import create_text_object

from estnltk_core.layer_operations.iterators.splitting_discontinuous import _split_by_discontinuous_layer
from estnltk_core.layer_operations.iterators.splitting_discontinuous import split_by_clauses

from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies


def extract_sections(text: Union['Text', 'BaseText'],
                     sections: Iterable,
                     layers_to_keep: Sequence = None,
                     trim_overlapping: bool = False):
    """Split text into a list of texts by sections.

    This method is slow on long texts.

    Parameters
    ----------
    text: Union['Text', 'BaseText']
        text object which will be split
    sections: List[Tuple(int, int)]
        list of ``(start, end)`` pairs defining the sections
    layers_to_keep: List[str]
        list of layers to be kept in section texts.
        The dependencies must be included, that is, if a layer in the list
        has a parent or is enveloping, then the parent or enveloped layer
        must also be in this list.
        If None (default), all layers are kept
    trim_overlapping: bool
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.

    Returns
    -------
    List[Union['Text', 'BaseText']]
          list containing a `Text` object for every section in `sections`.

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
        new_text = create_text_object( text.text[start:end] )
        for layer in text.sorted_layers():
            layer_name = layer.name
            if layers_to_keep is not None:
                if layer_name not in layers_to_keep:
                    continue
            attribute_names = layer.attributes
            secondary_attributes = layer.secondary_attributes
            parent = layer.parent
            enveloping = layer.enveloping
            ambiguous = layer.ambiguous
            new_layer = layer.__class__(name=layer.name,
                                        attributes=attribute_names,
                                        secondary_attributes=secondary_attributes,
                                        parent=parent,
                                        enveloping=enveloping,
                                        ambiguous=ambiguous)
            new_layer.meta.update(layer.meta)
            new_layer.serialisation_module = layer.serialisation_module
            new_text.add_layer(new_layer)

            if parent:
                if ambiguous:
                    for span in layer:
                        span_parent = map_spans.get((span.parent.base_span, span.parent.layer.name))
                        if span_parent:
                            new_span = Span(base_span=span_parent.base_span, layer=new_layer)
                            map_spans[(span.base_span, span.layer.name)] = new_span
                            for annotation in span.annotations:
                                new_layer.add_annotation(new_span, **annotation)
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
                        # If the section is in a gap between two discontinuous 
                        # spans, then it should be skipped ...
                        section_inside_gap = False
                        for sid, s in enumerate( span ):
                            if sid+1 < len( span ):
                                next_s = span[sid+1]
                                if s.end <= start and end <= next_s.start:
                                    section_inside_gap = True
                                    break
                        if section_inside_gap:
                            continue
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
    """Shorthand for ``extract_sections(text, [(start, end)], layers_to_keep, trim_overlapping)[0]``.
    """
    return extract_sections(text, [(start, end)], layers_to_keep, trim_overlapping)[0]



def layers_to_keep_default(text, layer):
    dependency_layers = find_layer_dependencies(text, layer, 
                                        include_enveloping=True,
                                        include_parents=True,
                                        add_bidirectional_parents=True)
    return set(dependency_layers) | {layer}



def split_by(text: Union['Text', 'BaseText'], layer: str, layers_to_keep: Sequence[str] = None, trim_overlapping: bool = False
             ) -> List[ Union['Text', 'BaseText'] ]:
    """Split text into a list of texts by layer.

    This method is slow on long texts.

    Parameters
    ----------
    text: Union['Text', 'BaseText']
        text object which will be split
    layer: str
        name of the layer to split by
    layers_to_keep: List[str]
        list of layers to be kept while splitting. The dependencies must be
        included, that is, if a layer in the list has a parent or is
        enveloping, then the parent or enveloped layer must also be in this
        list. If None (default), all layers are kept
    trim_overlapping: bool
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.

    Returns
    -------
    List[Union['Text', 'BaseText']]
         list containing a `Text` object for every span in the `layer`.

    """
    if layers_to_keep is None:
        layers_to_keep = layers_to_keep_default(text, layer)
    if layer == 'clauses':
        # If we are splitting clauses, we need to consider discontinuous spans / annotations
        return _split_by_discontinuous_layer(text, layer, layers_to_keep=layers_to_keep,
                                                   trim_overlapping=trim_overlapping )
    sections = [(span.start, span.end) for span in text[layer]]
    return extract_sections(text, sections, layers_to_keep, trim_overlapping)


def split_by_sentences(text, layers_to_keep=None, trim_overlapping=False, input_sentences_layer='sentences'):
    """Shorthand for ``split_by(text, 'sentences', layers_to_keep, trim_overlapping)``
    """
    return split_by(text, input_sentences_layer, layers_to_keep, trim_overlapping)
