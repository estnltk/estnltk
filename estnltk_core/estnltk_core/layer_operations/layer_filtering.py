from typing import Container

from collections import Counter, defaultdict

from estnltk_core.layer.layer import Layer

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

