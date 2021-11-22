from estnltk_core.taggers import Retagger


class AnnotationRewriter(Retagger):
    """Applies a modifying function for every annotation.
    
       The function takes an Annotation object as an input 
       and is allowed to change it (including adding new 
       attributes or removing old ones). But the function 
       cannot delete Annotation, or add new Annotations.
       
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
       
       Usage note: this retagger should be reasonably fast 
       if you can rewrite annotations one-by-one. This 
       is also most suitable for rewriting unambiguous layer. 
       
       Use SpanAnnotationsRewriter instead if you 
       need to rewrite all annotations of a span at once 
       (e.g. if you have an ambiguous layer, and you need 
             to consider other annotations while rewriting).
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
        layer_attributes = layer.attributes
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
            initial_annotations_length = len(span.annotations)
            for annotation in span.annotations:
                # Apply the function on annotation
                self.function(annotation)
                # Check that all required attributes are present
                if set(annotation) != set(layer.attributes):
                    raise ValueError('the annotation has unexpected or missing attributes {}!={}'.format(
                        set(annotation), set(layer.attributes)))
            # Guard: the function should not add or delete annotations
            annotations_length_diff = len(span.annotations) - initial_annotations_length
            if annotations_length_diff < 0:
                raise Exception( \
                       'Cannot delete annotations: {} annotations are missing in {!r}'.format(abs(annotations_length_diff), span) )
            elif annotations_length_diff > 0:
                raise Exception( \
                       'Cannot add annotations: {} annotations redundant in {!r}'.format( annotations_length_diff, span) )

