def las_score(layer_a, layer_b, start=None, end=None):
    assert len(layer_a) == len(layer_b)

    if start is None:
        start = 0
    if end is None:
        end = len(layer_a)

    assert 0 <= start < end <= len(layer_a)

    match_count = 0
    for i in range(start, end):
        span_a = layer_a[i]
        span_b = layer_b[i]
        if span_a.deprel == span_b.deprel:
            if span_a.head is None or span_b.head is None:
                if span_a.head is None and span_b.head is None:
                    match_count += 1
            elif span_a.head.start == span_b.head.start and span_a.head.end == span_b.head.end:
                match_count += 1

    return match_count / (end - start)
