#
#   What?
#      Splitting logic that can handle discontinuous spans / annotations, 
#      as in 'clauses' layer. 
#   Status:
#      The implementation is OK, but the method is very slow on long texts.
#      Optimization is desirable.
#

from typing import Iterable, Sequence, List, Union
from estnltk_core import ElementaryBaseSpan
from estnltk_core.layer.span import Span
from estnltk_core.common import create_text_object

from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies

def extract_discontinuous_sections(text: Union['Text', 'BaseText'],
                                   sections: Iterable,
                                   layers_to_keep: Sequence = None,
                                   trim_overlapping: bool = False):
    """Split text into a list of texts by discontinuous sections.
    
    A discontinuous section is a list of ``(start, end)`` pairs:
    text inside the pairs will be extracted,  and  gaps between
    every two pairs will be kept out.
    Note: pairs ``(start, end)`` must be sorted increasingly.

    This method is slow on long texts.

    Parameters
    ----------
    text: Union['Text', 'BaseText']
        text object which will be split
    sections: List[Tuple(int, int)]
        list of lists of ``(start, end)`` pairs defining discontinuous sections
    layers_to_keep: List[str]
        list of layers to be kept while splitting.
        The dependencies must be included, that is, if a layer in the list
        has a parent or is enveloping, then the parent or enveloped layer
        must also be in this list.
        If None (default), all layers are kept
    trim_overlapping: bool
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.

    Returns
    -------
    List[Union['Text', 'BaseText']]
        list containing a `Text` object for every discontinuous section in `sections`.
    """
    if layers_to_keep:
        for layer in layers_to_keep:
            parent = text[layer].parent
            enveloping = text[layer].enveloping
            if parent:
                assert parent in layers_to_keep, 'parent of '+layer+' missing in layers_to keep: '+parent
            if enveloping:
                assert enveloping in layers_to_keep, 'enveloping of '+layer+' missing in layers_to keep: '+enveloping
    result = []
    for subsections in sections:
        # Construct text str based on discontinuous list of spans
        text_str = ''.join( [ text.text[start:end] for start, end in subsections ] )
        new_text = create_text_object( text_str )
        # Construct Layers
        map_spans = {}
        for layer in text.sorted_layers():
            layer_name = layer.name
            if layers_to_keep is not None:
                if layer_name not in layers_to_keep:
                    continue
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
                if ambiguous:
                    for span in layer:
                        span_parent = map_spans.get((span.parent.base_span, span.parent.layer.name))
                        if span_parent:
                            new_span = Span(base_span=span_parent.base_span, layer=new_layer)
                            map_spans[(span.base_span, span.layer.name)] = new_span
                            for annotation in span.annotations:
                                new_layer.add_annotation(new_span, **annotation)
                else:
                    raise NotImplementedError('not ambiguous layer with parent: ' + layer_name)
            elif enveloping:
                if ambiguous:
                    raise NotImplementedError('ambiguous enveloping layer: '+ layer_name)
                else:
                    for start, end in subsections:
                        for span in layer.spans:
                            if (span.base_span, span.layer.name) in map_spans:
                                # Skip a base_span that has already been added
                                # ( no need to add it twice )
                                continue
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
                            # If the subsection is in a gap between two discontinuous 
                            # spans, then it should be skipped ...
                            subsection_inside_gap = False
                            for sid, s in enumerate( span ):
                                if sid+1 < len( span ):
                                    next_s = span[sid+1]
                                    if s.end <= start and end <= next_s.start:
                                        subsection_inside_gap = True
                                        break
                            if subsection_inside_gap:
                                continue
                            # Collect spans for the enveloping span
                            for s in span:
                                parent = map_spans.get((s.base_span, s.layer.name))
                                if parent:
                                    spans.append(parent)
                            attributes = {attr: getattr(span, attr) for attr in attribute_names}
                            new_annotation = new_layer.add_annotation(spans, **attributes)
                            map_spans[(span.base_span, span.layer.name)] = new_annotation.span
            else:
                section_size = 0  # cumulative section size
                for start, end in subsections:
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

                        base_span = ElementaryBaseSpan(section_size + span_start - start, 
                                                       section_size + span_end - start)
                        new_annotation = None
                        for annotation in span.annotations:
                            new_annotation = new_layer.add_annotation(base_span, **annotation)

                        assert new_annotation is not None
                        map_spans[(span.base_span, span.layer.name)] = new_annotation.span
                    section_size += end-start

        result.append(new_text)
    return result



def layers_to_keep_default(text, layer):
    dependency_layers = find_layer_dependencies(text, layer, 
                                        include_enveloping=True,
                                        include_parents=True,
                                        add_bidirectional_parents=True)
    return set(dependency_layers) | {layer}



def group_consecutive_spans( text_str, spans, reduce_spans=True, correct_left_boundary=True ):
    """Groups consecutive spans while taking account of the whitespace between the spans.

    Uses the following logic for grouping the spans:

    * consecutive spans that are separated by whitespaces strings will be joined into one group. For instance::

       text: 'Mees oli tuttav' ->
       spans: ['Mees', 'oli', 'tuttav'] ->
       return one group: [['Mees', 'oli', 'tuttav']]

    * consecutive spans that are separated by empty strings will be joined into one group. For instance::

       text: 'kohtasime,' ->
       spans: ['kohtasime', ','] ->
       return one group: [['kohtasime', ',']]

    * in case of a discontinuity of spans, different groups are formed. For instance::

       text: 'Mees, keda kohtasime, oli tuttav' ->
       spans: ['Mees', 'oli', 'tuttav'] ->
       return two groups: [['Mees'], ['oli', 'tuttav']]

    Returns a grouping of spans: a list of list of span locations (start, end).

    Parameters
    ----------
    text_str: str
        raw text covered by the spans (a string)
    spans:
        a list of `Span` objects that need to be grouped
    reduce_spans: bool
        If `True` (default), then groups of continuous spans are reduced to
        (start, end) of the whole group, e.g. if [(s1, e1), ... , (sN, eN)]
        is a list of continuous spans, then it is reduced to [(s1, eN)].
        If `False`, groups of continuous spans will remain as they are.
    correct_left_boundary: bool
        If `True` (default), then before adding a new group after a group of
        discontinuous spans, the beginning of the new group is checked for
        a preceding whitespace and if the whitespace precedes, it is added
        at the beginning of the new group. For instance::

             old text: 'Mees, keda kohtasime, oli tuttav' ->
             spans: ['Mees', 'oli', 'tuttav'] ->
             return two groups: [['Mees'], [' oli', 'tuttav']]
               ( note whitespace added before 'oli' )
             new_text: 'Mees oli tuttav'.

        If `False`, then no whitespace corrections will be made. As a result,
        you may stumble upon a problem::

             old text: 'Mees, keda kohtasime, oli tuttav' ->
             spans: ['Mees', 'oli', 'tuttav'] ->
             return two groups: [['Mees'], ['oli', 'tuttav']]
             new_text: 'Meesoli tuttav'
           ( because of missing whitespace corrections,
             'Mees' and 'oli' will be joined mistakenly )

    Returns
    -------
    List[List[Tuple(int, int)]]
       list of list of span locations (start, end). start, end indexes of input spans
       grouped in a way that all consecutive spans are grouped together, and discontinuous
       spans are in separate groups.
    """
    i = 0
    consecutive_span_locs = []
    whitespace_corrections = dict()
    while i < len(spans):
        spanA = spans[i]
        locA = (spanA.start, spanA.end)
        if locA in whitespace_corrections:
            locA = whitespace_corrections[locA]
        if not consecutive_span_locs:
            # Add the first group
            consecutive_span_locs.append( [locA] )
        if i + 1 < len(spans):
            spanB = spans[i+1]
            locB = (spanB.start, spanB.end)
            gap = text_str[spanA.end:spanB.start]
            # If spanB comes right after spanA, or there 
            # is only whitespace between A and B, then join
            # A and B into one group
            if spanA.end == spanB.start or gap.isspace():
                # Extend an existing group with B
                assert consecutive_span_locs[-1][-1] == locA 
                consecutive_span_locs[-1].append( locB )
            else:
                if correct_left_boundary:
                    # If there is a whitespace before
                    # start of locB, then include it 
                    # in the span B
                    if spanB.start-1 > -1 and \
                       text_str[spanB.start-1].isspace():
                       whitespace_corrections[locB] = \
                            (spanB.start-1, spanB.end)
                       locB = whitespace_corrections[locB]
                # Start a new group with B
                consecutive_span_locs.append( [locB] )
        i += 1
    if reduce_spans:
        # Reduce (s1, e1), ... , (sN, eN) to (s1, eN)
        new_consecutive_span_locs = []
        for subspans in consecutive_span_locs:
            new_consecutive_span_locs.append( (subspans[0][0], subspans[-1][-1]) )
        consecutive_span_locs = new_consecutive_span_locs
    return consecutive_span_locs



def _split_by_discontinuous_layer(text: Union['Text', 'BaseText'], layer: str, layers_to_keep: Sequence[str]=None, 
                                  trim_overlapping: bool=False, _post_chk: bool=False ) -> List[Union['Text', 'BaseText']]:
    """Split text into a list of texts by a discontinuous layer.

    This splitting method should handle correctly layers with
    discontinuous annotation spans, such as the clauses
    layer, and the verb chains layer.

    Parameters
    ----------
    text: Union['Text', 'BaseText']
        text object which will be split
    layer: str
        name of the discontinuous layer to split by
    layers_to_keep: List[str]
        list of layers to be kept while splitting.
        The dependencies must be included, that is, if a layer in the list
        has a parent or is enveloping, then the parent or enveloped layer
        must also be in this list.
        If None (default), all layers are kept
    trim_overlapping: bool
        If `False` (default), overlapping spans are not kept.
        If `True`, overlapping spans are trimmed to fit the boundaries.
    _post_chk: bool
        If `False` (default), then no post-checking will be done.
        If `True`, then applies post-checking to make sure that there
        are no conflicts/intersections between extracted discontinuous
        sections.

    Returns
    -------
    List[Union['Text', 'BaseText']]
        list containing a `Text` object for every span in the `layer`.
    """
    if layers_to_keep is None:
        raise ValueError('(!) Unexpected None value for layers_to_keep. '+
                         'Please specify layers you need to keep while splitting.')
    all_discontinuous_sections = []
    for disc_layer_spans in text[layer]:
        # Group spans of the layer into discontinuous_sections
        discontinuous_sections = group_consecutive_spans(text.text, disc_layer_spans)
        all_discontinuous_sections.append( discontinuous_sections )
    if _post_chk:
        # Sanity check: there should be no overlap between discontinuous sections
        _flat_spans = []
        for group_list in all_discontinuous_sections:
            for span in group_list:
                _flat_spans.append( span )
        for sid, spanA in enumerate(_flat_spans):
            for sid2 in range(sid+1, len(_flat_spans)):
                spanB = _flat_spans[sid2]
                a_start = spanA[0]
                a_end   = spanA[1]
                b_start = spanB[0]
                b_end   = spanB[1]
                assert a_start <= a_end, '(!) Unexpected span {!r}'.format(spanA)
                assert b_start <= b_end, '(!) Unexpected span {!r}'.format(spanB)
                assert a_end <= b_start or b_end <= a_start, \
                   '(!) Conflicting spans {!r} and {!r}'.format(spanA, spanB)
    # Extract discontinuous sections
    return extract_discontinuous_sections(text, all_discontinuous_sections, \
                                          layers_to_keep, trim_overlapping)



def split_by_clauses(text, layers_to_keep=None, trim_overlapping=False, 
                           input_clauses_layer='clauses' ):
    """Split text into a list of texts by clauses layer.
       This is proper way of splitting text into clauses,
       considering all the discontinuous spans in the 
       clauses layer.
       Note: the implementation needs further testing
    """
    if layers_to_keep is None:
        layers_to_keep = layers_to_keep_default(text, input_clauses_layer)
    return _split_by_discontinuous_layer(text, input_clauses_layer, layers_to_keep, 
                                               trim_overlapping=trim_overlapping )

