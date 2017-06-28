from collections import defaultdict

def _delete_conflicting_spans(layer, priority_key, map_conflicts, delete_equal):
    '''
    If delete_equal is False, two spans are in conflict and one of them has
    a strictly lower priority determined by the priority_key, then that span
    is removed from the span list layer.spans.spans
    If delete_equal is True, then one of the conflicting spans is removed
    even if the priorities are equal.
    Returns
        True, if some conflicts remained unsolved,
        False, otherwise.
    '''
    conflicts_exist = False
    span_removed = False
    span_list = sorted(layer.spans.spans, key=priority_key)
    for obj in span_list:
        #for c in obj.conflicting:
        for c in map_conflicts[obj]:
            if delete_equal or priority_key(obj) < priority_key(c):
                # üldjuhul ebaefektiivne
                # peab mõtlema, mis juhtub kahe ühesuguse spani korral
                try:
                    span_list.remove(c)
                    span_removed = True
                except ValueError:
                    pass
            elif priority_key(obj) == priority_key(c) and c in span_list:
                conflicts_exist = True
    if span_removed:
        layer.spans.spans = sorted(span_list)
    return conflicts_exist


def resolve_conflicts(layer, conflict_resolving_strategy='ALL', status={}):
    priorities = set()
    number_of_conflicts = 0
    span_list = layer.spans.spans
    for span in span_list:
        span.conflicting = []
    map_conflicts = defaultdict(list)
    for i, obj in enumerate(span_list):
        if '_priority_' in layer.attributes:
            priorities.add(obj._priority_)
        for j in range(i+1, len(span_list)):
            if obj.end <= span_list[j].start:
                break
            number_of_conflicts += 1
            map_conflicts[obj].append(span_list[j])
            map_conflicts[span_list[j]].append(obj)
            obj.conflicting.append(span_list[j])
            span_list[j].conflicting.append(obj)
    status['number_of_conflicts'] = number_of_conflicts
    if number_of_conflicts == 0:
        return layer

    conflicts_exist = True
    if len(priorities) > 1:
        priority_key = lambda x: x._priority_
        conflicts_exist = _delete_conflicting_spans(layer, priority_key, map_conflicts, delete_equal=False)

    if not conflicts_exist or conflict_resolving_strategy=='ALL':
        return layer
    
    if conflict_resolving_strategy == 'MAX':
        priority_key = lambda x: (x.start-x.end,x.start)
    elif conflict_resolving_strategy == 'MIN':
        priority_key = lambda x: (x.end-x.start,x.start)

    _delete_conflicting_spans(layer, priority_key, map_conflicts, delete_equal=True)
    return layer
