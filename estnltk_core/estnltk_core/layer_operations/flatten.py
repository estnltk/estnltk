from typing import Sequence, Union
from itertools import pairwise
from estnltk_core.layer.base_span import ElementaryBaseSpan
from estnltk_core.layer.base_span import EnvelopingBaseSpan


def flatten(input_layer: Union['BaseLayer', 'Layer'], output_layer: str, output_attributes: Sequence[str] = None,
            attribute_mapping: Sequence = None, default_values: dict = None,
            disambiguation_strategy:str = None, gaps_strategy:str = None, 
            gaps_pattern:str = r'\s*\S.*\s*') -> Union['BaseLayer', 'Layer']:
    r"""Reduces enveloping layer or layer with parent to a detached ambiguous layer of simple text spans.
    
       Note: By default, the output layer will be ambiguous. However, if you set 
       disambiguation_strategy = 'pick_first', then only the first annotation of 
       every span will be preserved and an unambiguous layer will be returned. 
       If you need to customize the disambiguation strategy, use a 
       Disambiguator. 

       Note: If the input layer is enveloping and contains discontinuous text 
       spans, the output layer will still have continuous text spans, covering 
       all the gaps inside spans. 
       However, if you set gaps_strategy = 'cut_out', then gaps inside spans 
       (signalled by a non-whitspace string between two sub-spans) will be cut 
       out, splitting spans correspondingly. 
       
       Parameters
       ----------
       input_layer: Union['BaseLayer', 'Layer']
           The layer to be turned into the flat layer.
       output_layer: str
           Name of the output layer.
       output_attributes: Sequence[str]
           Set of attribute names for the output layer.
           Defaults to all attributes of the input layer.
       attribute_mapping: Sequence
           A sequence of tuples (old_attr, new_attr) specifying how attributes 
           should be renamed in the output layer. 
           By default, attribute names will be fully preserved, so the new layer
           will have the same attribute names as the old layer.
       default_values: dict
           Dictionary containing default values for attributes of the output 
           layer. Defaults to None.
       disambiguation_strategy: str
           Specifies disambiguation strategy. By default, there is no strategy and 
           the output layer will be ambiguous.
           If set to 'pick_first', then the first annotation of every span will be 
           preserved.
       gaps_strategy: str
           Specifies strategy for handling gaps inside an enveloping span of an 
           enveloping layer. 
           By default, there is no strategy and even if there is a gap between 
           two consecutive sub-spans of an enveloping span, the new flat span 
           will cover the gap entirely. For instance, in case of clauses layer 
           with an embedded clause ("[Mees, [keda seal kohtasime,] oli tuttav.]"), 
           the flat clauses will be: ['Mees, keda seal kohtasime, oli tuttav.', 
           ', keda seal kohtasime,'], so the first flat clause covers entirely 
           the embedded clause.
           If set to 'cut_out', then all consecutive sub-spans that have a gap 
           between them will be split into two spans. the existence of the gap 
           is checked with the gaps_pattern.
           For instance, in case of clauses layer with an embedded clause 
           ("[Mees, [keda seal kohtasime,] oli tuttav.]"), the flat clauses will 
           be: ['Mees', ', keda seal kohtasime,', 'oli tuttav.'].
       gaps_pattern :str
           String with regular expression pattern that can be used for detecting 
           gaps between two sub-spans of an enveloping span. 
           Defaults to string '\s*\S.*\s*'.
       Returns
       -------
       Union['BaseLayer', 'Layer']
            flattened version of the input_layer
    """
    # Prepare gaps_strategy [Optional]
    gaps_regex = None
    if gaps_strategy is not None and \
       gaps_strategy.lower() == 'cut_out':
           # Sanity check
           if input_layer.enveloping is None:
               raise Exception(f'(!) Cannot use gaps_strategy="cut_out": the input layer {input_layer.name!r} is not enveloping layer.')
           if input_layer.text_object is None:
               raise Exception(f'(!) Cannot use gaps_strategy="cut_out": the input layer {input_layer.name!r} is not attached to a Text object.')
           # Compile the regex for detecting gaps
           import regex as re
           if isinstance(gaps_pattern, str):
               gaps_regex = re.compile( gaps_pattern )
           elif isinstance(gaps_pattern, re.regex.Pattern):
               gaps_regex = gaps_pattern
           if gaps_regex is None:
               raise Exception(f'(!) Cannot use gaps_strategy="cut_out": please provide a valid gaps_pattern for detecting gaps in text.')
           assert isinstance(gaps_regex, re.regex.Pattern)
    # Prepare layer
    layer_attributes = input_layer.attributes
    output_attributes = output_attributes or layer_attributes
    # Create new BaseLayer or Layer
    new_layer = input_layer.__class__(name=output_layer,
                                      attributes=output_attributes,
                                      secondary_attributes=input_layer.secondary_attributes,
                                      text_object=input_layer.text_object,
                                      parent=None,
                                      enveloping=None,
                                      ambiguous=True,
                                      default_values=default_values)

    if attribute_mapping is None:
        attribute_mapping = tuple((attr, attr) for attr in output_attributes)
    else:
        assert {attr for attr, _ in attribute_mapping} <= set(layer_attributes)
        assert {attr for _, attr in attribute_mapping} <= set(output_attributes)

    for span in input_layer:
        base_spans = [ElementaryBaseSpan(span.start, span.end)]
        if gaps_strategy is not None and \
           gaps_strategy.lower() == 'cut_out':
            # Split enveloping spans into chunks of continuous spans [Optional]
            new_base_spans = []
            assert isinstance(span.base_span, EnvelopingBaseSpan)
            last_start = span.base_span[0].start
            for (sub_span_1, sub_span_2) in pairwise( span.base_span ):
                gap_str = input_layer.text_object.text[sub_span_1.end:sub_span_2.start]
                if gaps_regex.match(gap_str):
                    new_base_spans.append( ElementaryBaseSpan(last_start, sub_span_1.end) )
                    last_start = sub_span_2.start
            if len(new_base_spans) > 0:
                # gaps detected: add the last base span
                new_base_spans.append( ElementaryBaseSpan(last_start, span.base_span[-1].end) )
                assert new_base_spans[0].start == base_spans[0].start
                assert new_base_spans[-1].end == base_spans[-1].end
                base_spans = new_base_spans
        # Add annotations
        for base_span in base_spans:
            for annotation_id, annotation in enumerate( span.annotations ):
                attrs = {new_attr: getattr(annotation, old_attr) for old_attr, new_attr, in attribute_mapping}
                new_layer.add_annotation(base_span, **attrs)
                if annotation_id == 0 and \
                   disambiguation_strategy is not None and \
                   disambiguation_strategy.lower() == 'pick_first':
                    # Cancel after the first annotation has been added
                    break

    if disambiguation_strategy is not None and \
       disambiguation_strategy.lower() == 'pick_first':
        new_layer.ambiguous = False

    return new_layer
