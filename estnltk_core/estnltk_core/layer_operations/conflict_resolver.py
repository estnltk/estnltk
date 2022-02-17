"""The main functon in this module is resolve_conflicts that removes conflicting spans from the input layer
according to the given conflict resolving strategy..

Possible Enhancements: another possibility to resolve conflicts is to split conflicting spans into smaller disjoint
spans. That would preserve all annotations but may also create meaningless spans.

"""
from typing import Union
from collections import defaultdict

from estnltk_core import Span
from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer_operations.iterators import iterate_intersecting_spans


def _resolve_ambiguous_span(ambiguous_span: Span, priority_attribute: str, keep_equal: bool) -> None:
    result = []
    for s in ambiguous_span.annotations:
        if not result or getattr(result[-1], priority_attribute) > getattr(s, priority_attribute):
            result = [s]
        elif getattr(result[-1], priority_attribute) == getattr(s, priority_attribute):
            result.append(s)
    if not keep_equal:
        result = result[:1]
    ambiguous_span.annotations.clear()
    ambiguous_span.annotations.extend(result)


def resolve_conflicts(layer: Union[BaseLayer, 'Layer'],
                      conflict_resolving_strategy: str = 'ALL',
                      priority_attribute: str = None,
                      status: dict = None,
                      keep_equal: bool = True
                      ):
    """Removes conflicting spans from the input layer.

    Parameters
    ----------
    layer: Union[BaseLayer, 'Layer']
        The layer with conflicts.
    conflict_resolving_strategy: str ('ALL', 'MAX', 'MIN')
        Conflict resolving strategy.
    priority_attribute: str
        Name of the priority attribute of spans. Not necessarily legal layer attribute.
        If None, priorities are not used to resolve conflicts.
    status: dict
        Used to store status information (number of conflicts).
    keep_equal: bool
        If True, keeps spans with equal priorities/lengths.
        If False, keeps the foremost of the conflicting spans in the sense of the span ordering in the layer.

    Returns
    -------
    Layer
        Input layer with removed conflicts.
    """
    if conflict_resolving_strategy not in {'ALL', 'MAX', 'MIN'}:
        raise ValueError('unexpected conflict_resolving_strategy: ' + str(conflict_resolving_strategy))
    if conflict_resolving_strategy == 'ALL' and priority_attribute is None and status is None:
        return layer

    if layer.ambiguous and priority_attribute is not None:
        for span in layer:
            _resolve_ambiguous_span(span, priority_attribute, keep_equal)

    number_of_conflicts = 0

    map_conflicts_new = defaultdict(set)
    for a, b in iterate_intersecting_spans(layer):
    
        map_conflicts_new[a.base_span].add(b.base_span)
        map_conflicts_new[b.base_span].add(a.base_span)
        number_of_conflicts += 1

    if isinstance(status, dict):
        status['number_of_conflicts'] = number_of_conflicts

    if priority_attribute is None:
        priority_0 = lambda span: 0
    else:
        priority_0 = lambda span: span.annotations[0][priority_attribute]

    if conflict_resolving_strategy == 'MAX':
        priority_1 = lambda span: span.start - span.end
    elif conflict_resolving_strategy == 'ALL':
        priority_1 = lambda span: 0
    else:  # 'MIN'
        priority_1 = lambda span: span.end - span.start

    if keep_equal:
        priority_2 = lambda span: 0
    else:
        priority_2 = lambda span: span.base_span

    def priority_key(span):
        return priority_0(span), priority_1(span), priority_2(span)

    delete_from_layer = set()
    for base_span in (span.base_span for span in sorted((layer[bs] for bs in map_conflicts_new), key=priority_key)):
        delete_from_conflict_mapping = set()
        if base_span in map_conflicts_new:
            for conflicting_base_span in map_conflicts_new[base_span]:
                if not keep_equal or priority_key(layer[base_span]) < priority_key(layer[conflicting_base_span]):
                    delete_from_conflict_mapping.add(conflicting_base_span)
            for conflict in delete_from_conflict_mapping:
                for conflict_conflict in map_conflicts_new[conflict]:
                    if len(map_conflicts_new[conflict_conflict]) == 1:
                        assert conflict in map_conflicts_new[conflict_conflict], (conflict, map_conflicts_new[conflict_conflict])
                        del map_conflicts_new[conflict_conflict]
                    else:
                        map_conflicts_new[conflict_conflict].remove(conflict)
                del map_conflicts_new[conflict]

        delete_from_layer.update(delete_from_conflict_mapping)

    for base_span in delete_from_layer:
        del layer[base_span]

    return layer
