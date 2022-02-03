#
#  Helper for creating (Ambiguous)Attribute(Tuple)List objects from raw attribute 
#  value and name listings 
# 
from typing import Union

from estnltk_core.layer.base_span import ElementaryBaseSpan
from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer import AmbiguousAttributeTupleList, AmbiguousAttributeList
from estnltk_core.layer import AttributeTupleList, AttributeList
from estnltk_core import Span, Annotation


def _add_attributes_to_mock_span( span, attributes, attribute_values ) -> Span:
    assert len(attributes) == len(attribute_values)
    attribs_dict = { attr: val for attr, val in zip(attributes, attribute_values) }
    if '__id' in span.layer.attributes:
        attribs_dict['__id'] = len(span.annotations)
    span.add_annotation( Annotation(span, attribs_dict) )
    return span

def _create_mock_layer( attributes, ambiguous, add_id_attrib=True ) -> BaseLayer:
    if add_id_attrib:
        # '__id' attribute is required for handling duplicate 
        # attribute values: if we have selected only 1 attribute, 
        # a span cannot have two annotations with exactly the 
        # same attribute values unless we add an extra attribute 
        # to distinguish them 
        attributes = ('__id',) + tuple(attributes)
    return BaseLayer('mock_layer', attributes=attributes, ambiguous=ambiguous )

def _create_mock_span( x, attributes, attribute_values, layer ) -> Span:
    span = Span( ElementaryBaseSpan(x, x+1), layer=layer )
    return _add_attributes_to_mock_span( span, attributes, attribute_values)

def _nested_list_depth( nested_list ) -> int:
    if isinstance( nested_list, (list, tuple) ):
        return 1 + _nested_list_depth( nested_list[0] ) if len(nested_list) > 0 else 0
    else:
        return 0

def create_amb_attribute_list( in_attr_tuple_list, attributes ) -> \
        Union[AmbiguousAttributeTupleList, AmbiguousAttributeList, AttributeTupleList, AttributeList]:
    """Creates (Ambiguous)Attribute(Tuple)List from the given structure of attribute values 
       (in_attr_tuple_list) and attribute names.
       
       Examples of inputs and returned objects:
       *) [0, 3], 'attr_1' --> AttributeList
       *) [[1, 11], [2, 12], [None, None]], ('attr_1', 'attr_2') --> AttributeTupleList
       *) [['J'], ['P', 'P'], ['V'], ['D'], ['Z']], ('attr_1',)  --> AmbiguousAttributeList
       *) [ [['L1-0', 'B']], [['L1-1', 'C'], ['L1-2', 'D']] ], ('attr_1', 'attr_2') --> AmbiguousAttributeTupleList
       
       Only to be used for testing purposes.
       
       Limitations: 
       1) cannot mock 'text' attribute;
       2) cannot mock recursive structures, such as:
          AttributeList([AmbiguousAttributeList(...), AmbiguousAttributeList(...)], ...)
    """
    if isinstance( attributes, str ):
        attributes = (attributes, )
    assert isinstance( attributes, (list, tuple) )
    assert _nested_list_depth( attributes ) == 1
    # determine possible ambiguity based on depth of the nested list
    ambiguous = False
    depth = _nested_list_depth( in_attr_tuple_list )
    if depth == 3 or (depth == 2 and len(attributes) == 1):
        ambiguous = True
    mock_layer = _create_mock_layer( attributes, ambiguous )
    if len(attributes) == 1 and not ambiguous:
        #
        # AttributeList 
        #    Example:  AttributeList([0, 3], 'attr_1')
        #
        if len(in_attr_tuple_list) > 0:
            assert not isinstance( in_attr_tuple_list[0], (list, tuple) )
            spanlist = []
            for x, val in enumerate( in_attr_tuple_list ):
                spanlist.append( _create_mock_span( x, attributes, [val], mock_layer ) )
            return AttributeList( spanlist, attributes[0] )
        elif len(in_attr_tuple_list) == 0:
            return AttributeList( [], attributes[0] )
    elif len(attributes) > 1 and not ambiguous:
        #
        # AttributeTupleList
        #    Example:  AttributeTupleList( [[1, 11], [2, 12], [None, None]], ('attr_1', 'attr_2') )
        #
        if len(in_attr_tuple_list) > 0:
            assert isinstance( in_attr_tuple_list[0], (list, tuple) )
            spanlist = []
            for x, values in enumerate( in_attr_tuple_list ):
                all_values = [val for val in values]
                spanlist.append( _create_mock_span( x, attributes, all_values, mock_layer ) )
            return AttributeTupleList( spanlist, attributes )
        elif len(in_attr_tuple_list) == 0:
            return AttributeTupleList( [], attributes )
    elif len(attributes) == 1 and ambiguous:
        #
        # AmbiguousAttributeList
        #    Example:  AmbiguousAttributeList( [['J'], ['P', 'P'], ['V'], ['D'], ['Z']], ('attr_1',) )
        #
        if len(in_attr_tuple_list) > 0:
            assert isinstance( in_attr_tuple_list[0], (list, tuple) )
            spanlist = []
            for x, values in enumerate( in_attr_tuple_list ):
                assert len(values) > 0
                span = _create_mock_span( x, attributes, [values[0]], mock_layer )
                if len(values) > 1:
                    for val in values[1:]:
                        _add_attributes_to_mock_span( span, attributes, [val] )
                spanlist.append( span )
            return AmbiguousAttributeList( spanlist, attributes[0] )
        elif len(in_attr_tuple_list) == 0:
            return AmbiguousAttributeList( [], attributes[0] )
    elif len(attributes) > 1 and ambiguous:
        #     
        # AmbiguousAttributeTupleList
        #     Example:  AmbiguousAttributeTupleList([ [['L1-0', 'B']], [['L1-1', 'C'], ['L1-2', 'D']] ], ('attr_1', 'attr_2'))
        # 
        if len(in_attr_tuple_list) > 0:
            assert isinstance( in_attr_tuple_list[0], (list, tuple) )
            assert isinstance( in_attr_tuple_list[0][0], (list, tuple) )
            spanlist = []
            for x, attr_values in enumerate( in_attr_tuple_list ):
                assert len(attr_values) > 0
                span = _create_mock_span( x, attributes, attr_values[0], mock_layer )
                if len(attr_values) > 1:
                    for next_attr_values in attr_values[1:]:
                        _add_attributes_to_mock_span( span, attributes, next_attr_values )
                spanlist.append( span )
            return AmbiguousAttributeTupleList( spanlist, attributes )
        elif len(in_attr_tuple_list) == 0:
            return AmbiguousAttributeTupleList( [], attributes )
