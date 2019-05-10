from collections import defaultdict

from estnltk import AmbiguousSpan


# TODO: use this generator in the resolve_conflicts function below
def iterate_conflicting_spans(layer):
    """
    :param layer: Layer
        input layer
    :return: tuple
        Returns all pairs of spans in the layer such that
        a.start <= b.start and a.end > b.start
    """
    for i, a in enumerate(layer):
        a_end = a.end
        for j in range(i + 1, len(layer)):
            b = layer[j]
            if a_end <= b.start:
                break
            yield a, b


def _delete_conflicting_spans(span_list, priority_key, map_conflicts, keep_equal):
    """
    If keep_equal is True, two spans are in conflict and one of them has
    a strictly lower priority determined by the priority_key, then that span
    is removed from the span list layer.span_list.spans
    If keep_equal is False, then one of the conflicting spans is removed
    even if the priorities are equal.
    Returns
        True, if some conflicts remained unsolved,
        False, otherwise.
    """
    conflicts_exist = False
    span_list = sorted(span_list, key=priority_key)
    for obj in span_list:
        for c in map_conflicts[obj]:
            if not keep_equal or priority_key(obj) < priority_key(c):
                # üldjuhul ebaefektiivne
                try:
                    span_list.remove(c)
                except ValueError:
                    pass
            elif priority_key(obj) == priority_key(c) and c in span_list:
                conflicts_exist = True
    return span_list, conflicts_exist


def _resolve_ambiguous_span(ambiguous_span: AmbiguousSpan, priority_attribute: str, keep_equal: bool) -> None:
    result = []
    for s in ambiguous_span:
        if not result or getattr(result[-1], priority_attribute) > getattr(s, priority_attribute):
            result = [s]
        elif getattr(result[-1], priority_attribute) == getattr(s, priority_attribute):
            result.append(s)
    if not keep_equal:
        result = result[:1]
    ambiguous_span.annotations = result


def resolve_conflicts(layer,
                      conflict_resolving_strategy: str='ALL',
                      priority_attribute: str=None,
                      status: dict=None,
                      keep_equal: bool=False
                      ):
    """
    Removes conflicting spans from the input layer.

    Parameters
    ----------
    layer: Layer
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

    Returns
    -------
    Input layer with removed conflicts.
    """
    if conflict_resolving_strategy == 'ALL' and priority_attribute is None and status is None:
        return layer
    if layer.ambiguous and priority_attribute is not None:
        for span in layer:
            _resolve_ambiguous_span(span, priority_attribute, keep_equal)
    priorities = set()
    number_of_conflicts = 0
    enumerated_spans = list(enumerate(layer.span_list.spans))  # enumeration is to distinguish equal spans
    map_conflicts = defaultdict(list)
    for obj in enumerated_spans:
        if priority_attribute is not None:
            if layer.ambiguous:
                priorities.add(getattr(obj[1][0], priority_attribute))
            else:
                priorities.add(getattr(obj[1], priority_attribute))
        for j in range(obj[0]+1, len(enumerated_spans)):
            if obj[1].end <= enumerated_spans[j][1].start:
                break
            number_of_conflicts += 1
            map_conflicts[obj].append(enumerated_spans[j])
            map_conflicts[enumerated_spans[j]].append(obj)
    if isinstance(status, dict):
        status['number_of_conflicts'] = number_of_conflicts
    if number_of_conflicts == 0:
        return layer

    conflicts_exist = True
    if len(priorities) > 1:
        if layer.ambiguous:
            def priority_key(num_span):
                return getattr(num_span[1][0], priority_attribute)
        else:
            def priority_key(num_span):
                return getattr(num_span[1], priority_attribute)

        enumerated_spans, conflicts_exist = _delete_conflicting_spans(enumerated_spans,
                                                                      priority_key,
                                                                      map_conflicts,
                                                                      keep_equal=True)

    if not conflicts_exist or conflict_resolving_strategy == 'ALL':
        layer.span_list.spans = [span[1] for span in sorted(enumerated_spans, key=lambda s: s[0])]
        return layer

    if conflict_resolving_strategy == 'MAX':
        def priority_key(num_span):
            return num_span[1].start-num_span[1].end, num_span[1].start
    elif conflict_resolving_strategy == 'MIN':
        def priority_key(num_span):
            return num_span[1].end-num_span[1].start, num_span[1].start
    else:
        raise ValueError('Unknown conflict_resolving_strategy: ' + str(conflict_resolving_strategy))

    enumerated_spans, _ = _delete_conflicting_spans(enumerated_spans, priority_key, map_conflicts, keep_equal=keep_equal)
    layer.span_list.spans = [span[1] for span in sorted(enumerated_spans, key=lambda s: s[0])]
    
    return layer
