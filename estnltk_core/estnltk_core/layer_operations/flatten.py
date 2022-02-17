from typing import Sequence, Union
from estnltk_core.layer.base_span import ElementaryBaseSpan


def flatten(input_layer: Union['BaseLayer', 'Layer'], output_layer: str, output_attributes: Sequence[str] = None,
            attribute_mapping: Sequence = None, default_values: dict = None,
            disambiguation_strategy:str = None ) -> Union['BaseLayer', 'Layer']:
    """Reduces enveloping layer or layer with parent to a detached ambiguous layer of simple text spans.
    
       Note: By default, the output layer will be ambiguous. However, if you set 
       disambiguation_strategy = 'pick_first', then only the first annotation of 
       every span will be preserved and an unambiguous layer will be returned. 
       If you need to customize the disambiguation strategy, use a 
       Disambiguator. 
       
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

       Returns
       -------
       Union['BaseLayer', 'Layer']
            flattened version of the input_layer
    """
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
        for annotation_id, annotation in enumerate( span.annotations ):
            attrs = {new_attr: getattr(annotation, old_attr) for old_attr, new_attr, in attribute_mapping}
            new_layer.add_annotation(ElementaryBaseSpan(span.start, span.end), **attrs)
            if annotation_id == 0 and \
               disambiguation_strategy is not None and \
               disambiguation_strategy.lower() == 'pick_first':
                # Cancel after the first annotation has been added
                break

    if disambiguation_strategy is not None and \
       disambiguation_strategy.lower() == 'pick_first':
        new_layer.ambiguous = False

    return new_layer
