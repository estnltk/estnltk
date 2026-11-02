#
#   Helper functions shared by splitting.py (extraction of continuous sections)
#   and splitting_discontinuous.py (extraction of discontinuous sections).
#
#   A section is represented as a list of subsections: (start, end) pairs that
#   are sorted increasingly and do not overlap. A continuous section has exactly
#   one subsection: [(start, end)]. A discontinuous section (e.g. a clause that
#   has an embedded clause inside it) has several subsections, and the text of
#   the extracted section is a concatenation of the texts of the subsections.
#
#   This module contains:
#   1) Functions `_check_layers_to_keep` and `_resolve_keep_partial_relations` 
#      which are required to validate input parameters of `extract_sections` 
#      and `extract_discontinuous_sections`;
#   2) Functions `_map_flat_base_span`, `_extract_named_base_span`, and 
#      `_extract_relation_layer_section` which are required for extraction 
#      of relation layers in `extract_sections` and 
#      `extract_discontinuous_sections`;
#

from typing import Sequence, List, Union, Optional, Dict, Tuple, Literal

from estnltk_core import ElementaryBaseSpan, EnvelopingBaseSpan, BaseSpan
from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer.relation_layer import RelationLayer, Relation


def _check_layers_to_keep(text: Union['Text', 'BaseText'], layers_to_keep: Optional[Sequence[str]]) -> None:
    """Asserts that all dependencies (parent layers and enveloped layers) of the
    layers in `layers_to_keep` are also in `layers_to_keep`.
    Both span layers and relation layers are supported.
    Does nothing if `layers_to_keep` is None.
    """
    if layers_to_keep is None:
        return
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


def _resolve_keep_partial_relations(keep_partial_relations: Union[bool, Literal["auto"]],
                                    trim_overlapping: bool) -> bool:
    """Validates the value of `keep_partial_relations` and resolves "auto":
    if `keep_partial_relations == "auto"`, returns the value of `trim_overlapping`.
    """
    if not (isinstance(keep_partial_relations, bool) or keep_partial_relations == "auto"):
        raise ValueError(f"keep_partial_relations should be True, False or 'auto', not {keep_partial_relations!r}")
    if keep_partial_relations == "auto":
        # keep_partial_relations gets the value from trim_overlapping
        return trim_overlapping
    return keep_partial_relations


def _map_flat_base_span(span_start: int,
                        span_end: int,
                        subsections: Sequence[Tuple[int, int]],
                        trim_overlapping: bool) -> Optional[ElementaryBaseSpan]:
    """Maps location (span_start, span_end) of the original text to the location
    in the text of the extracted section. The section consists of subsections
    which are concatenated in the new text.

    * If the span is completely inside one subsection, it is shifted to the
      position of that subsection in the new text;
    * Otherwise (the span crosses a boundary of the section, or spans over a
      gap between two subsections):
      * if trim_overlapping=False, then the span is discarded: None is returned;
      * if trim_overlapping=True, the span is trimmed to the parts that fall
        inside the subsections. The parts are contiguous in the new text, so
        the new span starts at the beginning of the first part and ends at the
        end of the last part. If no part of the span falls inside the section,
        None is returned;
    """
    new_start = None
    new_end = None
    offset = 0  # cumulative length of the previous subsections
    for sub_start, sub_end in subsections:
        if sub_start <= span_start and span_end <= sub_end:
            # span is completely inside the subsection
            return ElementaryBaseSpan(offset + span_start - sub_start,
                                      offset + span_end - sub_start)
        if trim_overlapping:
            # span can cross subsection boundaries only with trimming
            overlap_start = max(span_start, sub_start)
            overlap_end = min(span_end, sub_end)
            if overlap_start < overlap_end:
                if new_start is None:
                    new_start = offset + overlap_start - sub_start
                new_end = offset + overlap_end - sub_start
        offset += sub_end - sub_start
    if new_start is not None:
        return ElementaryBaseSpan(new_start, new_end)
    return None


def _extract_named_base_span(base_span: BaseSpan,
                             subsections: Sequence[Tuple[int, int]],
                             enveloped_layer: Optional[str],
                             map_spans: Dict,
                             trim_overlapping: bool) -> Optional[BaseSpan]:
    """Maps a base span of a relation's named span into the coordinates of
    the extracted section. The section is given as a list of subsections:
    ``(start, end)`` pairs sorted increasingly (a continuous section consists
    of a single subsection).
    Returns the new base span, or None if the named span does not fit into
    the section.

    * Non-enveloping relation layer (ElementaryBaseSpan): see
      `_map_flat_base_span` for details.
    * Enveloping relation layer (EnvelopingBaseSpan): every component of the
      span is looked up among the already extracted spans of the enveloped
      layer (map_spans). If some components are missing, the named span is
      either reduced to the found components (trim_overlapping=True) or
      discarded.
    """
    if enveloped_layer is None:
        return _map_flat_base_span(base_span.start, base_span.end, subsections, trim_overlapping)
    else:
        if not trim_overlapping and \
           (base_span.start < subsections[0][0] or subsections[-1][1] < base_span.end):
            # Quick exit: the span is not inside the outer boundaries of the section
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
                                    subsections: Sequence[Tuple[int, int]],
                                    map_spans: Dict,
                                    trim_overlapping: bool = False,
                                    keep_partial_relations: bool = False) -> RelationLayer:
    """Creates a copy of the relation layer which contains only relations
    (and named spans) from the section, with positions of the named spans
    re-mapped to the section coordinates.
    The section is given as a list of subsections: ``(start, end)`` pairs
    sorted increasingly. Use ``[(start, end)]`` for a continuous section.
    If the enveloped layer of the relation layer (if any) has already been
    extracted, then `map_spans` must map ``(old_base_span, layer_name)`` to
    the corresponding new span.
    The returned layer is not attached to any Text object yet.
    See `extract_sections` and `extract_discontinuous_sections` for details
    on `trim_overlapping` and `keep_partial_relations`.
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
            new_base_span = _extract_named_base_span(named_span.base_span, subsections,
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
