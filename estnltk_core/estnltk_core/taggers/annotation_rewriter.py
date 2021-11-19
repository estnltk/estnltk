from estnltk_core.taggers import Retagger


class AnnotationRewriter(Retagger):
    """Applies a modifying function for every annotation.
    
       The function takes an Annotation object as an input 
       and is allowed to change it (including add new 
       attributes or remove old ones), but not allowed 
       to delete or add any Annotations.
       
       The parameter attribute_change_op determines how
       output_attributes should be interpreted:
       * None (default) -- the function does not change 
         attributes, only changes their values;
       * 'SET' -- layer's attributes will be completely 
         overwritten by output_attributes;
       * 'ADD' -- output_attributes will be appended to 
         layer's attributes;
       * 'REMOVE' -- output_attributes will be removed 
         from layer's attributes;
       
       Usage note: this function should be reasonably fast 
       if you can rewrite annotations one-by-one. 
       Use SpanAnnotationsRewriter (TODO) instead if you 
       need to rewrite all annotations of a span at once 
       (e.g. you need to consider other annotations
        while rewriting).
    """
    conf_param = ['check_output_consistency', 'function', 'attribute_change_op']

    def __init__(self, layer_name, output_attributes, function, attribute_change_op=None, check_output_consistency=True):
        self.output_layer = layer_name
        self.input_layers = [layer_name]
        self.output_attributes = output_attributes
        self.function = function
        if attribute_change_op is not None:
            if not isinstance(attribute_change_op, str) or attribute_change_op.upper() not in ['SET', 'ADD', 'REMOVE']:
                raise ValueError('(!) attribute_change_op must be one of the following: None, "SET", "ADD" or "REMOVE".')
            attribute_change_op = attribute_change_op.upper()
        else:
            self.output_attributes = ()
        self.attribute_change_op = attribute_change_op
        self.check_output_consistency = check_output_consistency

    def _change_layer(self, text, layers, status):
        layer = layers[self.output_layer]
        layer_attributes = layer.attributes
        # Change output attributes
        if self.attribute_change_op is None:
            # Nothing to change here, move along
            pass
        elif self.attribute_change_op == 'SET':
            layer.attributes = self.output_attributes
        elif self.attribute_change_op == 'ADD':
            layer.attributes += self.output_attributes
        elif self.attribute_change_op == 'REMOVE':
            layer.attributes = (attr for attr in layer.attributes if attr not in self.output_attributes)

        for span in layer:
            initial_annotations_length = len(span.annotations)
            for annotation in span.annotations:
                # Apply the function on annotation
                self.function(annotation)
                if self.check_output_consistency:
                    # check that all required attributes are present
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

