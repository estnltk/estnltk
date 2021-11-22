from copy import copy

from estnltk_core import Annotation

from estnltk_core.layer.annotation import Annotation
from estnltk_core.taggers import Retagger


class SpanAnnotationsRewriter(Retagger):
    """Applies a modifying function on each span's annotations.
    
       The function takes span's annotations (a list of Annotation 
       objects) as an input and is allowed to change, delete and 
       add new annotations to the list. Added new annotations can 
       also be dictionaries, as long as they have keys corresponding
       to layer's attributes. The function must return a list with 
       modified annotations. 
       Returning an empty list or None (deleting all annotations)
       is not allowed and causes an exception.
       
       The parameter attr_change determines how retagger's 
       output_attributes change/affect layer's attributes:
       * None (default) -- the function does not change 
         layer's attributes, only changes their values;
       * 'SET' -- layer's attributes will be completely 
         overwritten by retagger's output_attributes;
       * 'ADD' -- retagger's output_attributes will be 
         appended to layer's attributes;
       * 'REMOVE' -- retagger's output_attributes will 
         be removed from layer's attributes;
       
       Usage note: this retagger should be used if you 
       need to rewrite all annotations of a span at once  
       (e.g. if you have an ambiguous layer, and you need 
             to consider other annotations while rewriting).
       Use AnnotationRewriter if your layer is unambiguous: 
       you can rewrite annotations one-by-one, and it'll 
       likely be faster.
       
    """
    conf_param = ['function', 'attr_change']

    def __init__(self, layer_name, output_attributes, function, attr_change=None):
        self.output_layer = layer_name
        self.input_layers = [layer_name]
        self.output_attributes = output_attributes
        self.function = function
        if attr_change is not None:
            if not isinstance(attr_change, str) or attr_change.upper() not in ['SET', 'ADD', 'REMOVE']:
                raise ValueError('(!) attr_change must be one of the following: None, "SET", "ADD" or "REMOVE".')
            attr_change = attr_change.upper()
        else:
            self.output_attributes = ()
        self.attr_change = attr_change

    def _change_layer(self, text, layers, status):
        layer = layers[self.output_layer]
        # Change output attributes
        if self.attr_change is None:
            # Nothing to change here, move along
            pass
        elif self.attr_change == 'SET':
            layer.attributes = self.output_attributes
        elif self.attr_change == 'ADD':
            layer.attributes += self.output_attributes
        elif self.attr_change == 'REMOVE':
            layer.attributes = (attr for attr in layer.attributes if attr not in self.output_attributes)
        
        for span in layer:
            results = self.function( copy(span.annotations) )
            if results is None:
                raise Exception('(!) The modifying function should return the list of changed Annotations or equivalent dicts, not None.')
            if len(results) == 0:
                raise Exception('(!) The modifying function cannot return an empty list: '+\
                                'at least one Annotation object or dict must remain.')
            # Check that all required attributes are present on each annotation
            for aid, annotation in enumerate(results):
                # check type
                if not isinstance(annotation, (Annotation, dict)):
                    TypeError('(!) Expected an Annotation object or equivalent dict, not {!r}'.format(type(annotation)))
                if isinstance(annotation, dict):
                    # convert dict into annotation
                    results[aid] = Annotation(span, **annotation)
            # Remove old annotations completely and insert new ones
            span.clear_annotations()
            for annotation in results:
                # Note span.add_annotation(...) checks that:
                #  * annotation has correct span;
                #  * annotation has correct attributes;
                #  * the span can take multiple annotations (in case it is ambiguous)
                span.add_annotation( annotation )

