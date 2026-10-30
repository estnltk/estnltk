from typing import Iterable, Sequence, List, Union, Optional, Dict, Tuple, Literal
from estnltk_core import ElementaryBaseSpan, EnvelopingBaseSpan, BaseSpan
from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer.span import Span
from estnltk_core.layer.relation_layer import RelationLayer, Relation
from estnltk_core.common import create_text_object

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
    if not (isinstance(keep_partial_relations, bool) or keep_partial_relations == "auto"):
        raise ValueError(f"keep_partial_relations should be True, False or 'auto', not {keep_partial_relations!r}")
    if keep_partial_relations == "auto":
        # keep_partial_relations gets the value from trim_overlapping
        keep_partial_relations = trim_overlapping
    if layers_to_keep is not None:
        for layer in layers_to_keep:
            layer_obj = text[layer]
            # RelationLayer has no `parent` attribute (and raises AttributeError
            # on access), so only span layers are checked for parents
            parent = layer_obj.parent if isinstance(layer_obj, BaseLayer) else None
            enveloping = layer_obj.enveloping
            if parent:
                assert parent in layers_to_keep, 'parent of '+layer+' missing in layers_to keep: '+parent
            if enveloping:
                assert enveloping in layers_to_keep, 'enveloping of '+layer+' missing in layers_to keep: '+enveloping
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
                new_layer = _extract_relation_layer_section(layer, start, end, map_spans,
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


def _extract_named_base_span(base_span: BaseSpan,
                             start: int,
                             end: int,
                             enveloped_layer: Optional[str],
                             map_spans: Dict,
                             trim_overlapping: bool) -> Optional[BaseSpan]:
    """Maps a base span of a relation's named span into the coordinates of
    the section [start, end).
    Returns the new base span, or None if the named span does not fit into
    the section.

    * Non-enveloping relation layer (ElementaryBaseSpan): the span is shifted
      by -start; if it crosses the section boundary, it is either trimmed
      (trim_overlapping=True) or discarded.
    * Enveloping relation layer (EnvelopingBaseSpan): every component of the
      span is looked up among the already extracted spans of the enveloped
      layer (map_spans). If some components are missing, the named span is
      either reduced to the found components (trim_overlapping=True) or
      discarded.
    """
    if enveloped_layer is None:
        span_start = base_span.start
        span_end = base_span.end
        if trim_overlapping:
            span_start = max(span_start, start)
            span_end = min(span_end, end)
            if span_start >= span_end:
                return None
        elif span_start < start or end < span_end:
            return None
        return ElementaryBaseSpan(span_start-start, span_end-start)
    else:
        if not trim_overlapping and (base_span.start < start or end < base_span.end):
            return None
        new_components = []
        for component in base_span:
            new_span = map_spans.get((component, enveloped_layer))
            if new_span is not None:
                new_components.append(new_span.base_span)
            elif not trim_overlapping:
                return None
        if not new_components:
            return None
        return EnvelopingBaseSpan(new_components)


def _extract_relation_layer_section(layer: RelationLayer,
                                    start: int,
                                    end: int,
                                    map_spans: Dict,
                                    trim_overlapping: bool = False,
                                    keep_partial_relations: bool = False) -> RelationLayer:
    """Creates a copy of the relation layer which contains only relations
    (and named spans) from the section [start, end), with positions of the
    named spans re-mapped to the section coordinates.
    The returned layer is not attached to any Text object yet.
    See `extract_sections` for details on `trim_overlapping` and
    `keep_partial_relations`.
    """
    new_layer = layer.__class__(name=layer.name,
                                span_names=layer.span_names,
                                attributes=layer.attributes,
                                secondary_attributes=layer.secondary_attributes,
                                display_order=layer.display_order,
                                text_object=None,
                                enveloping=layer.enveloping,
                                ambiguous=layer.ambiguous,
                                serialisation_module=layer.serialisation_module)
    new_layer.meta.update(layer.meta)
    # Relations are created directly (instead of via new_layer.add_annotation)
    # to avoid the linear-time duplicate lookup on every insertion; duplicates
    # are detected with a dictionary instead.
    new_relations: Dict[Tuple, Relation] = {}
    for relation in layer:
        new_named_spans: List[Tuple[str, BaseSpan]] = []
        skip_relation = False
        for named_span in relation.spans:
            new_base_span = _extract_named_base_span(named_span.base_span, start, end,
                                                     layer.enveloping, map_spans,
                                                     trim_overlapping)
            if new_base_span is None:
                if not keep_partial_relations:
                    # if one named span is missing, skip the whole relation
                    skip_relation = True
                    break
            else:
                new_named_spans.append( (named_span.name, new_base_span) )
        if skip_relation or not new_named_spans:
            continue
        relation_key = tuple(new_named_spans)
        new_relation = new_relations.get(relation_key)
        if new_relation is None:
            new_relation = Relation(new_named_spans, new_layer)
            new_relations[relation_key] = new_relation
            # TODO: there should be a better way for adding a new relation 
            # than appending it to new_layer._relation_list, but currently 
            # RelationLayer.add_annotation(...) prohibits adding Relation 
            # objects directly 
            new_layer._relation_list.append(new_relation)
        elif not layer.ambiguous:
            # Trimming / removing named spans made two relations of a
            # non-ambiguous layer identical: keep the first one
            continue
        for annotation in relation.annotations:
            new_relation.add_annotation( {attr: annotation[attr] for attr in layer.attributes} )
    return new_layer


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
             keep_partial_relations: bool | Literal["auto"] = "auto") -> List[ Union['Text', 'BaseText'] ]:
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

    Returns
    -------
    List[Union['Text', 'BaseText']]
         list containing a `Text` object for every span in the `layer`.

    """
    if isinstance(text[layer], RelationLayer):
        raise NotImplementedError(f'(!) Spltting by RelationLayer ({layer!r}) is not implemented.')
    if layers_to_keep is None:
        layers_to_keep = layers_to_keep_default(text, layer)
    if layer == 'clauses':
        # Check for relation layers
        if layers_to_keep:
            relation_layers = [l for l in layers_to_keep if isinstance(text[l], RelationLayer)]
            if relation_layers:
                import warnings
                warnings.warn('(!) layers_to_keep contains relation layer(s) for which splitting '+\
                              'discontinuous spans has not been implemented yet. Relation layer(s) '+\
                              'will be discarded.')
                # Discard relation layers (not implemented yet)
                layers_to_keep = [l for l in layers_to_keep if not l in relation_layers]
        # If we are splitting clauses, we need to consider discontinuous spans / annotations
        return _split_by_discontinuous_layer(text, layer, layers_to_keep=layers_to_keep,
                                                   trim_overlapping=trim_overlapping )
    sections = [(span.start, span.end) for span in text[layer]]
    return extract_sections(text, sections, layers_to_keep, trim_overlapping, keep_partial_relations)


def split_by_sentences(text, layers_to_keep=None, trim_overlapping=False, keep_partial_relations="auto", \
                       input_sentences_layer='sentences'):
    """Shorthand for ``split_by(text, 'sentences', layers_to_keep, trim_overlapping, keep_partial_relations)``
    """
    return split_by(text, input_sentences_layer, layers_to_keep, trim_overlapping, keep_partial_relations)
