from typing import List

def decompose_to_elementary_spans(layer, text) -> List:
    spanindexes = set()

    for s in layer.spans:
        spanindexes.add(s.start)
        spanindexes.add(s.end)

    html_spans = []

    spanindexes = sorted(spanindexes)

    if not layer.spans:
        # Default for when there are no spans
        return [[text, []]]
    # Now we process layers with spans
    if spanindexes[0] != 0:
        spanindexes.insert(0, 0)
    if spanindexes[-1] != len(text):
        spanindexes.append(len(text))
    
    for i in range(len(spanindexes)-1):
        span_text = text[spanindexes[i]:spanindexes[i+1]]
        html_spans.append([spanindexes[i], spanindexes[i+1], span_text])

    for html_span in html_spans:
        span_list = []
        span_start = html_span[0]
        for s in layer.spans:
            if span_start in range(s.start, s.end):
                span_list.append(s)
        html_span.append(span_list)
        del html_span[0:2]

    return html_spans