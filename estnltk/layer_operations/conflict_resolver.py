from collections import defaultdict

def _delete_conflicting_spans(span_list, priority_key, map_conflicts, keep_equal):
    '''
    If keep_equal is True, two spans are in conflict and one of them has
    a strictly lower priority determined by the priority_key, then that span
    is removed from the span list layer.spans.spans
    If keep_equal is False, then one of the conflicting spans is removed
    even if the priorities are equal.
    Returns
        True, if some conflicts remained unsolved,
        False, otherwise.
    '''
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


def resolve_conflicts(layer, conflict_resolving_strategy='ALL', status={}):
    '''
    Removes conflicting spans from the layer.
    '''
    priorities = set()
    number_of_conflicts = 0
    span_list = list(enumerate(layer.spans.spans)) # enumerate is to distinguish equal spans
    map_conflicts = defaultdict(list)
    for obj in span_list:
        if '_priority_' in layer.attributes:
            priorities.add(obj[1]._priority_)
        for j in range(obj[0]+1, len(span_list)):
            if obj[1].end <= span_list[j][1].start:
                break
            number_of_conflicts += 1
            map_conflicts[obj].append(span_list[j])
            map_conflicts[span_list[j]].append(obj)
    status['number_of_conflicts'] = number_of_conflicts
    if number_of_conflicts == 0:
        return layer

    conflicts_exist = True
    if len(priorities) > 1:
        priority_key = lambda x: x[1]._priority_
        span_list, conflicts_exist = _delete_conflicting_spans(span_list, priority_key, map_conflicts, keep_equal=True)

    if not conflicts_exist or conflict_resolving_strategy=='ALL':
        layer.spans.spans = [span[1] for span in sorted(span_list, key=lambda s: s[0])]
        return layer
    
    if conflict_resolving_strategy == 'MAX':
        priority_key = lambda x: (x[1].start-x[1].end,x[1].start)
    elif conflict_resolving_strategy == 'MIN':
        priority_key = lambda x: (x[1].end-x[1].start,x[1].start)

    span_list, _ = _delete_conflicting_spans(span_list, priority_key, map_conflicts, keep_equal=False)
    layer.spans.spans = [span[1] for span in sorted(span_list, key=lambda s: s[0])]
    
    return layer
