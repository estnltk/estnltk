from typing import List

from estnltk_core import RelationLayer
import html


def decompose_to_elementary_named_spans(relation_layer, text, add_relation_ids=False) -> (List, List):
    '''Function that splits text into consecutive subsections in a way 
       that each subsection is either covered by one (or more) named spans 
       of the relation layer, or is not covered by any named spans. 
       So, as a result, each subsection in text will be associated with 
       relations/named spans that cover it. 
       Returns a tuple: (segments, named_spans). Returnable segments is a 
       list where each element is a sublist: [span_text, covering_named_spans].
       span_text is a subsection from input text, and covering_named_spans is 
       a list of indexes of named_spans covering that subsection (is empty if 
       no spans cover the subsection). 
       If add_relation_ids is set, then covering_named_spans contains tuples 
       (named_span_index, relation_index) instead of integers. 
       Returnable named_spans is a list with all named spans of the layer in 
       the order in which they (first) appear in text. Each named span will be 
       referred to in some covering_named_spans, and some named_spans can also 
       be referred to multiple times (in case of overlapping spans).
    '''
    assert isinstance(text, str), \
        f"(!) text must be an instance of str, not {type(text)}"
    assert isinstance(relation_layer, RelationLayer), \
        f"(!) relation_layer must be an instance of RelationLayer, not {type(relation_layer)}"

    if not relation_layer.relations:
        # Default for case when there are no spans
        return [[text, []]], []

    spanindexes = set()
    spanmapping = {}

    for rel_id, rel in enumerate(relation_layer.relations):
        for s in rel.spans:
            spanindexes.add(s.start)
            spanindexes.add(s.end)
            if s.start not in spanmapping:
                spanmapping[s.start] = []
            spanmapping[s.start].append( (s.end, rel_id, s) )

    html_spans = []

    spanindexes = sorted(spanindexes)

    # Complete text subsections by adding text's 
    # start and end if necessary
    if spanindexes[0] != 0:
        spanindexes.insert(0, 0)
    if spanindexes[-1] != len(text):
        spanindexes.append(len(text))

    # 1) Collect named spans in the order in which they appear 
    # in text (can be different from the order they appear
    # in layer).
    # 2) Associate each subsection of text with a list of 
    # corresponding named spans indexes (which can also be 
    # an empty list). Optionally, add also relation indexes. 
    named_spans_in_text_order = []
    spans_continued = []
    spans_continued_indexes = []
    for i in range(len(spanindexes) - 1):
        s_start = spanindexes[i]
        s_end = spanindexes[i + 1]
        span_text = text[s_start:s_end]
        covering_named_spans = []
        if len(spans_continued) > 0:
            for sid, continued_span in enumerate(spans_continued):
                (s_end_2, rel_id, n_span) = continued_span
                nsp_index = spans_continued_indexes[sid]
                covering_named_spans.append( nsp_index )
        if s_start in spanmapping.keys():
            for (s_end_2, rel_id, n_span) in spanmapping[s_start]:
                named_spans_in_text_order.append(n_span)
                nsp_index = len(named_spans_in_text_order)-1
                if add_relation_ids:
                    nsp_index = (nsp_index, rel_id)
                covering_named_spans.append( nsp_index )
                if s_end < s_end_2:
                    # This covering span does not end here. 
                    # Add it to the list of continuing long spans
                    spans_continued.append( (s_end_2, rel_id, n_span) )
                    spans_continued_indexes.append( nsp_index )
        html_span = [span_text, covering_named_spans]
        html_spans.append( html_span )
        if len(spans_continued) > 0:
            # Remove long spans that end here
            to_delete = []
            to_delete_indexes = []
            for sid, long_span in enumerate(spans_continued):
                if s_end >= long_span[0]:
                    to_delete.append(long_span)
                    to_delete_indexes.append( \
                        spans_continued_indexes[sid] )
            for del_long_span in to_delete:
                spans_continued.remove(del_long_span)
            for del_long_span_index in to_delete_indexes:
                spans_continued_indexes.remove(del_long_span_index)

    return html_spans, named_spans_in_text_order
