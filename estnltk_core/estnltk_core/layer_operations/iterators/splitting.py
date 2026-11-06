from typing import Iterable, Sequence, List, Union, Literal
from estnltk_core import ElementaryBaseSpan
from estnltk_core.layer.span import Span
from estnltk_core.layer.relation_layer import RelationLayer
from estnltk_core.common import create_text_object

from estnltk_core.layer_operations.iterators.splitting_common import _check_layers_to_keep
from estnltk_core.layer_operations.iterators.splitting_common import _resolve_keep_partial_relations
from estnltk_core.layer_operations.iterators.splitting_common import _extract_relation_layer_section
from estnltk_core.layer_operations.iterators.splitting_common import _get_sorted_named_base_spans

from estnltk_core.layer_operations.iterators.splitting_discontinuous import _split_by_discontinuous_layer
from estnltk_core.layer_operations.iterators.splitting_discontinuous import split_by_clauses

from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies


def extract_sections(text: Union['Text', 'BaseText'],
                     sections: Iterable,
                     layers_to_keep: Sequence = None,
                     trim_overlapping: bool = False,
                     keep_partial_relations: bool | Literal["auto"] = "auto"):
    """Split text into a list of texts by sections.

    Both span layers and relation layers are carried over to the section texts.

    This method is slow on long texts.

    Parameters
    ----------
    text: Union['Text', 'BaseText']
        text object which will be split
    sections: List[Tuple(int, int)]
        list of ``(start, end)`` pairs defining the sections
    layers_to_keep: List[str]
        list of layers (span layers and/or relation layers) to be kept in
        section texts.
        The dependencies must be included, that is, if a layer in the list
        has a parent or is enveloping, then the parent or enveloped layer
        must also be in this list.
        If None (default), all layers (including relation layers) are kept
    trim_overlapping: bool
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.
        For relation layers, this applies to individual named spans: a named
        span crossing the section boundary is trimmed (non-enveloping relation
        layer) or reduced to its enveloped spans that fall inside the section
        (enveloping relation layer).
    keep_partial_relations: bool | Literal["auto"] 
        Only affects relation layers. 
        If `False`, a relation is kept only if all of its named
        spans fall inside the section (after optional trimming).
        If `True`, named spans that fall outside the section are removed from
        the relation, and the relation is kept if at least one of its named
        spans remains inside the section. (RelationLayer allows relations
        with some, but not all, named spans unassigned.)
        Note: if removing / trimming named spans makes two relations of a
        non-ambiguous layer identical, only the first relation's annotation
        is kept.
        If "auto" (default), then the value of this parameter follows the 
        value of parameter `trim_overlapping`, e.g. if `trim_overlapping` is 
        `False`, then `keep_partial_relations` is also `False`. 

    Returns
    -------
    List[Union['Text', 'BaseText']]
          list containing a `Text` object for every section in `sections`.

    """
    keep_partial_relations = _resolve_keep_partial_relations(keep_partial_relations, trim_overlapping)
    _check_layers_to_keep(text, layers_to_keep)
    # Span layers and relation layers in the order of dependencies:
    # a relation layer always comes after the span layer it envelops
    all_sorted_layers = text.sorted_layers(span_layers=True, relation_layers=True)
    result = []
    for start, end in sections:
        map_spans = {}
        new_text = create_text_object( text.text[start:end] )
        for layer in all_sorted_layers:
            layer_name = layer.name
            if layers_to_keep is not None:
                if layer_name not in layers_to_keep:
                    continue
            if isinstance(layer, RelationLayer):
                # a) relation layer
                new_layer = _extract_relation_layer_section(layer, [(start, end)], map_spans,
                                                            trim_overlapping=trim_overlapping,
                                                            keep_partial_relations=keep_partial_relations)
                new_text.add_layer(new_layer)
                continue
            # b) span layer
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
                for span in layer:
                    span_parent = map_spans.get((span.parent.base_span, span.parent.layer.name))
                    if span_parent:
                        new_span = Span(base_span=span_parent.base_span, layer=new_layer)
                        map_spans[(span.base_span, span.layer.name)] = new_span
                        for annotation in span.annotations:
                            new_layer.add_annotation(new_span, **annotation)
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
                    trim_overlapping: bool=False,
                    keep_partial_relations: bool|Literal["auto"]="auto"):
    """Shorthand for ``extract_sections(text, [(start, end)], layers_to_keep, trim_overlapping, keep_partial_relations)[0]``.
    """
    return extract_sections(text, [(start, end)], layers_to_keep, trim_overlapping,
                            keep_partial_relations=keep_partial_relations)[0]



def layers_to_keep_default(text, layer):
    dependency_layers = find_layer_dependencies(text, layer, 
                                        include_enveloping=True,
                                        include_parents=True,
                                        add_bidirectional_parents=True,
                                        include_relation_layers=True)
    return set(dependency_layers) | {layer}



def split_by(text: Union['Text', 'BaseText'], layer: str, layers_to_keep: Sequence[str] = None, trim_overlapping: bool = False, 
             keep_partial_relations: bool | Literal["auto"] = "auto", 
             split_discontinuous: bool | Literal["auto"] = "auto") -> List[ Union['Text', 'BaseText'] ]:
    """Split text into a list of texts by layer.

    This method is slow on long texts.

    Parameters
    ----------
    text: Union['Text', 'BaseText']
        text object which will be split
    layer: str
        name of the layer to split by. Can be a span layer or a relation 
        layer. In case of a relation layer, the text is split by named 
        spans of all relations: named spans are collected from all 
        relations, sorted by text positions and duplicates are removed 
        (see `_get_sorted_named_base_spans` for details). 
    layers_to_keep: List[str]
        list of layers (span layers and/or relation layers) to be kept 
        while splitting. The dependencies must be included, that is, if 
        a layer in the list has a parent or is enveloping, then the parent 
        or enveloped layer must also be in this list. If None (default), 
        then the `layer` and the layers it depends on are kept
    trim_overlapping: bool
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.
    keep_partial_relations: bool | Literal["auto"] 
        Only affects relation layers. 
        If `False`, a relation is kept only if all of its named spans fall 
        inside the section (after optional trimming).
        If `True`, named spans that fall outside the section are removed from 
        the relation, and the relation is kept if at least one of its named 
        spans remains inside the section. (RelationLayer allows relations 
        with some, but not all, named spans unassigned.) 
        Note: if removing / trimming named spans makes two relations of a
        non-ambiguous layer identical, only the first relation's annotation
        is kept.
        If "auto" (default), then the value of this parameter follows the 
        value of parameter `trim_overlapping`, e.g. if `trim_overlapping` is 
        `False`, then `keep_partial_relations` is also `False`. 
    split_discontinuous: bool | Literal["auto"]
        Whether spans of the `layer` are handled as discontinuous sections. 
        A discontinuous span (e.g. a clause that has an embedded clause 
        inside it) is split into groups of consecutive enveloped spans, 
        and only the text inside the groups is extracted, while the gaps 
        between the groups are left out. See `_split_by_discontinuous_layer` 
        and `extract_discontinuous_sections` for details. 
        If `True`, then spans of the `layer` are always handled as 
        discontinuous sections. This requires the `layer` to be enveloping. 
        If `False`, then spans of the `layer` are always handled as 
        continuous sections: each section spans from the start of the 
        span to its end, gaps included. 
        If "auto" (default), then spans of the `layer` are handled as 
        discontinuous sections if the name of the `layer` contains 
        "clauses" and the `layer` is enveloping, and as continuous 
        sections otherwise. 
        In case of a relation layer, this applies to named spans of the 
        relations. 

    Returns
    -------
    List[Union['Text', 'BaseText']]
         list containing a `Text` object for every span in the `layer`; 
         or, if the `layer` is a relation layer, for every unique named 
         span in the `layer` (in the order of text positions). 
         In case of a relation layer, each `Text` object gets meta key 
         'named_spans' listing labels of all named spans that were origins 
         of the section. Labels follow the format `f'{span_name}_{relation_id}'`, 
         where `relation_id` is the index of the relation in the `layer`, e.g. 
         label 'arg_3' refers to the named span `text[layer][3]['arg']`.

    """
    if not (isinstance(split_discontinuous, bool) or split_discontinuous == "auto"):
        raise ValueError(f"split_discontinuous should be True, False or 'auto', not {split_discontinuous!r}")
    layer_obj = text[layer]
    if split_discontinuous == "auto":
        # Layers of clauses can contain discontinuous spans (because of embedded clauses).
        # Only enveloping layers can have discontinuous spans.
        split_discontinuous = 'clauses' in layer and layer_obj.enveloping is not None
    if split_discontinuous and layer_obj.enveloping is None:
        raise ValueError(f'(!) Cannot split discontinuously by layer {layer!r}: the layer must be enveloping.')
    if layers_to_keep is None:
        layers_to_keep = layers_to_keep_default(text, layer)
    if split_discontinuous:
        # Consider discontinuous spans / annotations
        return _split_by_discontinuous_layer(text, layer, layers_to_keep=layers_to_keep,
                                                   trim_overlapping=trim_overlapping,
                                                   keep_partial_relations=keep_partial_relations )
    if isinstance(layer_obj, RelationLayer):
        # Split by named spans of the relation layer
        spans_with_labels = _get_sorted_named_base_spans(layer_obj, add_labels=True)
        sections = [(base_span.start, base_span.end) for base_span, _ in spans_with_labels]
        section_texts = extract_sections(text, sections, layers_to_keep, trim_overlapping, keep_partial_relations)
        # Record origins of the sections
        assert len(section_texts) == len(spans_with_labels)
        for section_text, (_, labels) in zip(section_texts, spans_with_labels):
            section_text.meta['named_spans'] = labels
        return section_texts
    # Split by span layer
    sections = [(span.start, span.end) for span in layer_obj]
    return extract_sections(text, sections, layers_to_keep, trim_overlapping, keep_partial_relations)


def split_by_sentences(text, layers_to_keep=None, trim_overlapping=False, keep_partial_relations="auto", \
                       input_sentences_layer='sentences'):
    """Shorthand for ``split_by(text, 'sentences', layers_to_keep, trim_overlapping, keep_partial_relations)``
    """
    return split_by(text, input_sentences_layer, layers_to_keep, trim_overlapping, keep_partial_relations)
