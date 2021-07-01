from typing import Iterable, Sequence, List

from estnltk.layer.span import Span
from estnltk.layer.span_list import SpanList
from estnltk.layer.annotation import Annotation
from estnltk.layer.layer import Layer, to_base_span
from estnltk.layer.base_span import EnvelopingBaseSpan, ElementaryBaseSpan
from estnltk.layer.enveloping_span import EnvelopingSpan

from estnltk.text import Text


def shift_span( span, layer: Layer, positions: int ):
    '''Shifts span's start and end indices by the given amount of positions.
       The positions can be both negative (shift backward) and positive 
       (shift forward). 
       Returns a new Span or EnvelopingSpan that copies all annotations of 
       the given span, but has start and end positions shifted.
    '''
    if type( span ) == Span:
        new_start = span.start+positions
        new_end   = span.end+positions
        new_span = Span( base_span=to_base_span((new_start, new_end)), layer=layer )
        for annotation in span.annotations:
            new_span.add_annotation( Annotation(new_span, **{k: v for k, v in annotation.items()}) )
        return new_span
    elif type( span ) == EnvelopingSpan:
        env_base_span_shifted = \
            EnvelopingBaseSpan( [ to_base_span(( s.start+positions, s.end+positions )) for s in span.base_span] )
        new_span = EnvelopingSpan( env_base_span_shifted, layer=layer )
        for annotation in span.annotations:
            new_span.add_annotation( Annotation(new_span, **{k: v for k, v in annotation.items()}) )
        return new_span
    else:
        raise TypeError('(!) Unexpected type of the input span {}. Expected Span or EnvelopingSpan.'.format(type(span)))


def join_layers( layers: Sequence[Layer], separators: Sequence[str] ):
    '''Joins given list of layers into one layer. All layers must have
       same names, parents, enveloped layers and attributes. 
       
       Upon joining layers, separators (strings) are used to determine
       the distance/space between two consecutive texts. Therefore,
       len(separators) must be len(layers) - 1.
       
       The list of layers must contain at least one layer, otherwise an 
       exception will be thrown. 
       
       Returns a new Layer, which contains all spans from given layers 
       in the order of the layers in the input. The new Layer is not 
       attached to any Text object. 
    '''
    if len(layers) == 0:
        raise ValueError('(!) Cannot join layers on an empty list. ')
    elif len(layers) == 1:
        new_layer = layers[0].copy()
        new_layer.text_object = None
        return new_layer
    else:
        # 0) Validate input layers
        assert len(layers) == len(separators)+1, \
               ('(!) The number of layers ({}) does not match the number of separators ({}).'+
                ' Expecting {} separators.').format( len(layers), len(separators), len(layers)-1 )
        name = layers[0].name
        parent = layers[0].parent
        enveloping = layers[0].enveloping
        attributes = layers[0].attributes
        for layer in layers:
            if layer.name != name:
                raise Exception( "Not all layers have the same name: " + str([l.name for l in layers] ) )
            if layer.parent != parent:
                raise Exception( "Not all layers have the same parent: " + str([l.parent for l in layers]) )
            if layer.enveloping != enveloping:
                raise Exception( "Not all layers are enveloping the same layer: " + str([l.enveloping for l in layers]) )
            if layer.attributes != attributes:
                raise Exception( "Not all layers have the same attributes: " + str([l.attributes for l in layers]) )
        # 1) Make a new layer which is not attached to any Text
        new_layer = layers[0].copy()
        new_layer.text_object = None
        # 2) Find shifts (cumulatively)
        shifts = []
        for i, layer in enumerate(layers):
            if i < len(layers) - 1:
                assert layer.text_object is not None
                layer_text = layer.text_object.text
                last_shift = 0 if not shifts else shifts[-1]
                shifts.append( last_shift + len(layer_text) + len(separators[i]) )
        # 3) Compose joined layer's spanlist
        joined_spanlist = SpanList()
        for i, layer in enumerate( layers ):
            shift = 0 if i == 0 else shifts[i-1]
            for span in layer._span_list.spans:
                shifted_span = shift_span( span, new_layer, shift )
                joined_spanlist.add_span( shifted_span )
        # 4) Attach joined spanlist to the new layer
        new_layer._span_list = joined_spanlist
        return new_layer

