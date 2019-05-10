from typing import List
import html


def decompose_to_elementary_spans(layer, text) -> (List, List):
    '''Function to map all the spans on a layer to corresponding text.
    Arguments should be a layer and the text the layer is applied to.
    Output is two lists: first is a list where each element is composed
    of text and a list of numbers that correspond to the number of spans
    that cover this part of the text. The second list is composed of
    all the spans.'''

    if not layer.spans:
        # Default for when there are no spans
        return [[text, []]]

    spanindexes = set()

    for s in layer.spans:
        spanindexes.add(s.start)
        spanindexes.add(s.end)

    html_spans = []

    spanindexes = sorted(spanindexes)

    # Now we process layers with spans
    if spanindexes[0] != 0:
        spanindexes.insert(0, 0)
    if spanindexes[-1] != len(text):
        spanindexes.append(len(text))

    for i in range(len(spanindexes) - 1):
        span_text = text[spanindexes[i]:spanindexes[i + 1]]
        html_spans.append([spanindexes[i], spanindexes[i + 1], span_text])

    i = 0
    for k, span in enumerate(layer.spans):
        # Safe as there exist  html_spans[i][0] == span.start
        while html_spans[i][0] != span.start:
            i += 1
        j = i
        # Safe as there exists html_spans[j][1] == span.end
        while html_spans[j][1] <= span.end:
            if len(html_spans[j]) == 3:
                html_spans[j].append([])
            html_spans[j][3].append(k)
            if len(html_spans) != j + 1:
                j += 1
            else:
                break

    for html_span in html_spans:
        del html_span[0:2]
        if len(html_span) == 1:
            html_span.append([])

    return html_spans, layer.spans
