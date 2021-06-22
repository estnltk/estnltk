from typing import Iterable, Sequence, List
from estnltk.layer.span import Span
from estnltk.layer.span_list import SpanList
from estnltk.layer.annotation import Annotation
from estnltk.layer.layer import Layer, to_base_span
from estnltk.layer.base_span import EnvelopingBaseSpan
from estnltk.layer.enveloping_span import EnvelopingSpan

from estnltk.text import Text


def shift_span( span, layer: Layer, positions: int ):
    '''Shifts span's start and end indices by the given amount of positions.
       The positions can be both negative (shift backward) and positive 
       (shift forward). 
       Returns new Span or EnvelopingSpan that is copies all annotations of 
       the given span, but has the positions shifted.
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
            EnvelopingBaseSpan( [ to_base_span(( s.start+positions, s.end+positions )) for s in span] )
        new_span = EnvelopingSpan( env_base_span_shifted, layer=layer )
        for annotation in span.annotations:
            new_span.add_annotation( Annotation(new_span, **{k: v for k, v in annotation.items()}) )
        return new_span
    else:
        raise TypeError('(!) Unexpected type of the input span {}. Expected Span or EnvelopingSpan.'.format(type(span)))

