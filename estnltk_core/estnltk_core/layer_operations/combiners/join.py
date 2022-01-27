#
#  join -- horizontal joining of layers (aka concatenation)
#
from typing import Sequence, List, Union

from estnltk_core.layer.span import Span
from estnltk_core.layer.span_list import SpanList
from estnltk_core.layer.annotation import Annotation
from estnltk_core.layer.base_layer import to_base_span
from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer.base_span import ElementaryBaseSpan
from estnltk_core.layer.base_span import EnvelopingBaseSpan
from estnltk_core.layer.enveloping_span import EnvelopingSpan

from estnltk_core.common import create_text_object

#
# Remark: semantics of join_layers, join_layers_while_reusing_spans & join_texts are up 
# for a debation, and the corresponding functionalities may change in the future
#

def shift_span( span, layer: Union[BaseLayer, 'Layer'], positions: int ):
    '''Shifts span's start and end indices by the given amount of positions.
       The positions can be negative (shift backward) or positive (shift 
       forward). 
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


def join_layers( layers: Sequence[Union[BaseLayer, 'Layer']], separators: Sequence[str] ):
    '''Joins (concatenates) given list of layers into one layer. 
       This function creates new spans for the new layer, thus input 
       layers (and their corresponding texts) will not be affected
       by joining.
       
       All layers must have same names, parents, enveloping layers and 
       attributes. 
       
       Upon joining layers, it is assumed that their respective Text
       objects are joined by string separators -- a separator placed 
       between each two Texts. Therefore, separators are used to 
       determine the distance/space between two consecutive layers, 
       and len(separators) must be len(layers) - 1.
       
       The list of layers must contain at least one layer, otherwise an 
       exception will be thrown. 
       
       Returns a new Layer, which contains all spans from given layers 
       in the order of the layers in the input. The new Layer is not 
       attached to any Text object. 
       
       Note: this function does not attempt to join or merge layer 
       metadata. It responsibility of the user to carry metadata from
       input layers to the new Layer (if required).
    '''
    if len(layers) == 0:
        raise ValueError('(!) Cannot join layers on an empty list of layers. ')
    elif len(layers) == 1:
        # copy the layer
        new_layer = layers[0].__class__(name=layers[0].name,
                                        attributes=layers[0].attributes,
                                        secondary_attributes=layers[0].secondary_attributes,
                                        text_object=None,
                                        parent=layers[0].parent,
                                        enveloping=layers[0].enveloping,
                                        ambiguous=layers[0].ambiguous,
                                        default_values=layers[0].default_values.copy())
        for span in layers[0]:
            for annotation in span.annotations:
                new_layer.add_annotation(span.base_span, **annotation)
        return new_layer
    else:
        # 0) Validate input layers
        if len(layers) != len(separators) + 1:
             raise ValueError('(!) The number of layers ({}) does not meet the number of separators ({}).'+
                              ' Expecting {} separators.').format( len(layers), len(separators), len(layers)-1 )
        name = layers[0].name
        parent = layers[0].parent
        enveloping = layers[0].enveloping
        attributes = layers[0].attributes
        secondary_attributes = layers[0].secondary_attributes
        ambiguous = layers[0].ambiguous
        for layer in layers:
            if layer.name != name:
                raise Exception( "Not all layers have the same name: " + str([l.name for l in layers] ) )
            if layer.parent != parent:
                raise Exception( "Not all layers have the same parent: " + str([l.parent for l in layers]) )
            if layer.enveloping != enveloping:
                raise Exception( "Not all layers are enveloping the same layer: " + str([l.enveloping for l in layers]) )
            if layer.attributes != attributes:
                raise Exception( "Not all layers have the same attributes: " + str([l.attributes for l in layers]) )
            if layer.secondary_attributes != secondary_attributes:
                raise Exception( "Not all layers have the same secondary_attributes: " + str([l.secondary_attributes for l in layers]) )
            if layer.ambiguous != ambiguous:
                raise Exception( "Not all layers have the same state of ambiguity: " + str([l.ambiguous for l in layers]) )
        # 1) Make a new detached layer
        new_layer = layers[0].__class__( name=name,
                                         attributes=attributes,
                                         secondary_attributes=secondary_attributes,
                                         text_object=None,
                                         parent=parent,
                                         enveloping=enveloping,
                                         ambiguous=ambiguous,
                                         default_values=layers[0].default_values.copy(),
                                         serialisation_module=layers[0].serialisation_module )
        # 2) Compose joined layer's spanlist
        last_shift = 0
        joined_spanlist = SpanList()
        for i, layer in enumerate(layers):
            layer_original_text = layer.text_object.text
            # Make new (shifted) versions from the spans
            for span in layer._span_list.spans:
                shifted_span = shift_span( span, new_layer, last_shift )
                joined_spanlist.add_span( shifted_span )
            if i < len(layers) - 1:
                # Calculate new shift
                last_shift += len(layer_original_text) + len(separators[i])
        # 3) Attach joined spanlist to the new layer
        new_layer._span_list = joined_spanlist
        return new_layer


def join_layers_while_reusing_spans( layers: Sequence[Union[BaseLayer, 'Layer']], separators: Sequence[str] ):
    '''Joins (concatenates) given list of layers into one layer. 
       This function reuses spans of input layers in the new layer, 
       and thus is more efficient than join_layers(). 
       (!) Warning: this joining is also destructive to input layers
       (and their Text objects), as their content will be broken.
       
       All layers must have same names, parents, enveloping layers and 
       attributes. 
       
       Upon joining layers, it is assumed that their respective Text
       objects are joinable by string separators -- a separator placed 
       between each two Texts. Therefore, separators are used to 
       determine the distance/space between two consecutive layers, 
       and len(separators) must be len(layers) - 1.
       
       The list of layers must contain at least one layer, otherwise an 
       exception will be thrown. 
       
       Returns a new Layer, which contains all spans from given layers 
       in the order of the layers in the input. The new Layer is not 
       attached to any Text object. 
       
       Note: this function does not attempt to join or merge layer 
       metadata. It responsibility of the user to carry metadata from
       input layers to the new Layer (if required).
    '''
    if len(layers) == 0:
        raise ValueError('(!) Cannot join layers on an empty list of layers. ')
    if len(layers) == 1:
        new_layer = layers[0]
        new_layer.text_object = None
        return new_layer
    else:
        # 0) Validate input layers
        if len(layers) != len(separators) + 1:
             raise ValueError('(!) The number of layers ({}) does not meet the number of separators ({}).'+
                              ' Expecting {} separators.').format( len(layers), len(separators), len(layers)-1 )
        name = layers[0].name
        parent = layers[0].parent
        enveloping = layers[0].enveloping
        attributes = layers[0].attributes
        secondary_attributes = layers[0].secondary_attributes
        ambiguous = layers[0].ambiguous
        for layer in layers:
            if layer.name != name:
                raise Exception( "Not all layers have the same name: " + str([l.name for l in layers] ) )
            if layer.parent != parent:
                raise Exception( "Not all layers have the same parent: " + str([l.parent for l in layers]) )
            if layer.enveloping != enveloping:
                raise Exception( "Not all layers are enveloping the same layer: " + str([l.enveloping for l in layers]) )
            if layer.attributes != attributes:
                raise Exception( "Not all layers have the same attributes: " + str([l.attributes for l in layers]) )
            if layer.secondary_attributes != secondary_attributes:
                raise Exception( "Not all layers have the same secondary_attributes: " + str([l.secondary_attributes for l in layers]) )
            if layer.ambiguous != ambiguous:
                raise Exception( "Not all layers have the same state of ambiguity: " + str([l.ambiguous for l in layers]) )
        # 1) Make a new detached layer
        new_layer = layers[0].__class__( name=name,
                                         attributes=attributes,
                                         secondary_attributes=secondary_attributes,
                                         text_object=None,
                                         parent=parent,
                                         enveloping=enveloping,
                                         ambiguous=ambiguous,
                                         default_values=layers[0].default_values.copy(),
                                         serialisation_module=layers[0].serialisation_module )
        # 2) Add spans from the old list of layers to the new layer.
        #    Texts of the old layers will be broken (hence destructivity of the approach)
        last_shift = 0
        for i, layer in enumerate(layers):
            layer_original_text = layer.text_object.text
            for span in layer:
                # Set new layer
                span._layer = new_layer
                # Create new base spans
                if type( span._base_span ) == ElementaryBaseSpan:
                    span._base_span = ElementaryBaseSpan( span.start + last_shift, \
                                                          span.end   + last_shift )
                elif type( span._base_span ) == EnvelopingBaseSpan:
                    new_base_spans = \
                        [ElementaryBaseSpan(bs.start+last_shift, bs.end+last_shift) for bs in span._base_span ]
                    span._base_span = EnvelopingBaseSpan( new_base_spans )
                # Add span to the new layer
                new_layer.add_span( span )
            # Calculate new shift
            if i < len(layers) - 1:
                last_shift += len(layer_original_text) + len(separators[i])
        return new_layer


def join_texts( texts: Sequence[Union['Text', 'BaseText']], separators: Sequence[str] = None ):
    '''Joins (concatenates) list of Text objects into a single Text object. 
       All Texts must have the same layers. 
       
       Upon joining Texts, string separators are used to connect 
       consecutive texts -- a separator is placed between each two 
       Texts. Therefore, len(separators) must be len(texts) - 1.
       If separators are not provided (separators=None), then a 
       single whitespace is placed between each two texts upon
       joining. 
       
       The input list of Texts must contain at least one Text object, 
       otherwise an exception will be thrown. 
       
       Returns a new Text, which is a concatenation of input texts and 
       their respective layers.
       
       Note: this function does not attempt to join or merge Text 
       metadata. It responsibility of the user to carry metadata from
       input texts to the new Text (if required).
    '''
    if len(texts) == 0:
        raise ValueError('(!) Cannot join Text objects on an empty list of Text objects. ')
    elif len(texts) == 1:
        # Nothing to do here: return the input Text
        return texts[0]
    else:
        # 0) Initialize default separators list (if required)
        if separators is None:
            if isinstance(texts, Sequence):
                separators = [' ' for i in range(len(texts)-1)]
        # 1) Validate input texts
        assert len(texts) == len(separators)+1, \
               ('(!) The number of separators ({}) does not meet the number of texts ({}).'+
                ' Expecting {} separators.').format( len(separators), len(texts), len(texts)-1 )
        layers = texts[0].layers
        text_strings = []
        for i, text_obj in enumerate( texts ):
            if text_obj.layers != layers:
                raise Exception( "Not all text objects have the same layers: " + str([t.layers for t in texts]) )
            if i > 0:
                sep = separators[i-1]
                if not isinstance( sep, str ):
                    raise ValueError('(!) Separator should be a string, not {!r} ({})'.format(sep,str(type(sep))))
                text_strings.append( sep )
            text_strings.append( text_obj.text )
        # 2) Construct new Text object
        new_text = create_text_object( ''.join(text_strings) )
        # 3) Join layers and add to the new Text
        first_text_layers = { layer:texts[0][layer] for layer in layers }
        for layer in new_text.topological_sort( first_text_layers ):
            all_layers = [ text_obj[layer.name] for text_obj in texts ]
            joined_layer = join_layers( all_layers, separators )
            joined_layer.text_object = new_text
            new_text.add_layer( joined_layer )
        return new_text

