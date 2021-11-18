from typing import Container
from collections import Counter

from pandas import DataFrame

from estnltk_core.layer.layer import Layer, SpanList

#
#  Legacy layer operation, relocated from:
#  https://github.com/estnltk/estnltk/blob/217b0071829ec18f0769aa6b3228daab14bbfbe3/estnltk_core/estnltk_core/layer_operations/layer_filtering.py
# 

def apply_filter(layer: Layer, function: callable, preserve_spans: bool = False, drop_immediately: bool = False):
    '''Applies a filtering function on layer: all annotations not passing the function will be deleted.
    
       The function parameter is a callable that takes three parameters: Layer, span index and annotation index. 
       
       Setting preserve_spans=True forces to keep at least one annotation for every span.
       Setting drop_immediately=True causes the annotation to be immediately removed after the check-up with 
       the function ( TODO: probably we should to remove this option, as a non-recommended one? ).
    '''
    if drop_immediately:
        i = 0
        while i < len(layer):
            j = 0
            while j < len(layer[i].annotations):
                if preserve_spans and len(layer[i].annotations) == 1:
                    break
                if function(layer, i, j):
                    j += 1
                    continue
                if len(layer[i].annotations) == 1:
                    del layer[i].annotations[j]
                    i -= 1
                    break
                else:
                    del layer[i].annotations[j]
            i += 1
    else:
        to_remove = []
        for i, span in enumerate(layer):
            for j, annotation in enumerate(span.annotations):
                if not function(layer, i, j):
                    to_remove.append((i, j))
        for i, j in reversed(to_remove):
            if not preserve_spans or len(layer[i].annotations) > 1:
                del layer[i].annotations[j]


def drop_annotations(layer: Layer, attribute: str, values: Container, preserve_spans: bool=False):
    '''Drops only those annotations from the layer that have certain attribute values.
       Setting preserve_spans=True forces to keep at least one annotation for every span.'''
    to_remove = []

    for i, span in enumerate(layer):
        for j, annotation in enumerate(span.annotations):
            if getattr(annotation, attribute) in values:
                to_remove.append((i, j))
    for i, j in reversed(to_remove):
        if not preserve_spans or len(layer[i].annotations) > 1:
            del layer[i].annotations[j]


def keep_annotations(layer: Layer, attribute: str, values: Container, preserve_spans: bool=False):
    '''Keeps only those annotations in the layer that have certain attribute values.
       Setting preserve_spans=True forces to keep at least one annotation for every span.'''
    to_remove = []

    for i, span in enumerate(layer):
        for j, annotation in enumerate(span.annotations):
            if getattr(annotation, attribute) not in values:
                to_remove.append((i, j))
    for i, j in reversed(to_remove):
        if not preserve_spans or len(layer[i].annotations) > 1:
            del layer[i].annotations[j]

#
#  Legacy layer operation, relocated from:
#  https://github.com/estnltk/estnltk/blob/93310cbda16dc71f56a7d5b06124d093040fe684/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L11-L36
# 

def unique_texts(layer: Layer, order=None):
    """Retrive unique texts of layer optionally ordered.
    Parameters
    ----------
    layer: Text Layer
    order: {None, 'asc', 'desc'} (default: None)
        If 'asc', then the texts are returned in ascending order by unicode lowercase.
        If 'desc', then the texts are returned in descending order by unicode lowercase.
        The ordering is nondeterministic if the lowercase versions of words are equal. 
        For example the list ['On', 'on'] is both in ascending and descending order. 
        Else, the texts returned have no particular order.
    Returns
    -------
    list of str
        List of unique texts of given layer.
    """
    texts = layer.text
    if order == None:
        return list(set(texts))
    if order == 'asc':
        return sorted(set(texts), reverse=False, key=str.lower)
    if order == 'desc':
        return sorted(set(texts), reverse=True, key=str.lower)
    raise ValueError('Incorrect order type.')


#
#  Legacy layer operation, relocated from:
#  https://github.com/estnltk/estnltk/blob/93310cbda16dc71f56a7d5b06124d093040fe684/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L107-L114
#

def get_enclosing_spans(layer: Layer, span):
    '''Yields layer's spans enclosing around the given span.
       Note: this is inefficient. Instead of using this function,
       use a regular iteration over spans of the enveloping layer 
       and over subspans of each (enveloping) span.
    '''
    base_span = span.base_span
    end = span.end
    for sp in layer:
        if base_span in sp.base_span:
            yield sp
        if end < sp.start:
            break

#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/08aee4213e1fe1132c12b3393b545613a24940d0/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L41-L78
#

def count_by(layer: Layer, attributes, counter=None):
    """Create table of counts for every *layer* *attributes* value combination.
    
    Note: this functionality is already covered by layer_operations.GroupBy.
    
    Parameters
    ----------
    layer: Layer
        The layer which elements have the keys listed in *attributes*.
    attributes: list of str or str
        Name of *layer*'s key or list of *layer*'s key names.
        If *attributes* contains 'text', then the *layer*'s text is found using spans.
    table: collections.Counter, None, default: None
        If table==None, then new 
        If table!=None, then the table is updated and returned.
    
    Returns
    -------
    collections.Counter
        The keys are tuples of values of attributes. 
        The values are corresponding counts.
    """
    if isinstance(attributes, str):
        attributes = [attributes]

    if counter is None:
        counter = Counter()

    for span in layer:
        key = []
        for a in attributes:
            if a == 'text':
                key.append(span.text)
            else:
                for annotation in span.annotations:
                    key.append(getattr(annotation, a))
        key = tuple(key)
        counter[key] += 1

    return counter

#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/65b26140df807a0b0d0f76ddf22f274dc8049fed/estnltk_core/estnltk_core/layer_operations/aggregators/groupby.py#L84-L100
#

def group_by_layer(layer: Layer, by: Layer):
    """Groups layer's spans by an enveloping layer.
    
    :param layer: Layer
        Layer which spans will be grouped;
    :param by: Layer
        Layer that envelopes the groupable layer.
    :return:
        iterator of SpanList
    """
    for enveloping_span in by:
        span_list = SpanList()
        for span in enveloping_span.spans:
            sp = layer.get(span)
            if sp is not None:
                span_list.add_span(sp)
        yield span_list

#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/535654dca55f0cc8067599c9da49f025e46e3554/estnltk_core/estnltk_core/layer_operations/merge.py#L71-L76
#

def iterate_spans(layer: 'Layer'):
    if layer.ambiguous:
        for ambiguous_span in layer:
            yield from ambiguous_span
    else:
        yield from layer

#
#  Legacy layer operations, relocated from:
#   https://github.com/estnltk/estnltk/blob/21a0d68f72ae714abab14fe2f730bf9c3df1e49e/estnltk_core/estnltk_core/layer_operations/layer_operations.py#L66-L74
#

def apply_to_annotations(layer: 'Layer', function: callable):
    for span in layer:
        for annotation in span:
            function(annotation)


def apply_to_spans(layer: 'Layer', function: callable):
    for span in layer:
        function(span)


#
#  Legacy layer operation, relocated from:
#   https://github.com/estnltk/estnltk/blob/051d0c3ff1931a50a799dae2916f7202a62ab46c/estnltk_core/estnltk_core/layer_operations/conflict_resolver.py#L13-L29
#

def iterate_conflicting_spans( layer: 'Layer' ):
    """Yields all pairs `(a, b)` of spans in the layer such that
       `a.start <= b.start` and `b.start < a.end`.
       
       Note: this function duplicates the functionality of 
       layer_operations.iterate_intersecting_spans(...) and 
       therefore was moved into legacy.
       
       :param layer: Layer
          input layer
       :returns generator
    """
    len_layer = len(layer)
    for i, a in enumerate(layer):
        a_end = a.end
        for j in range(i + 1, len_layer):
            b = layer[j]
            if a_end <= b.start:
                break
            yield a, b
