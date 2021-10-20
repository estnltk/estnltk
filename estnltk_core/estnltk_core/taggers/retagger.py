from estnltk_core.layer.layer import Layer
from estnltk_core.taggers import Tagger

from typing import MutableMapping, Union, Set


class Retagger(Tagger):
    """Base class for retaggers. A retagger modifies existing layer. 
    Use this class as a superclass in creating concrete 
    implementations of retaggers.
    
    Layer is modified inside the _change_layer() method, 
    which always returns None, indicating that the method does 
    not produce a new layer, but changes the target layer.
    
    Retagger is a subclass of Tagger and inherits its parameters 
    and methods. 
    Retagger's derived class needs to implement the following: 
    
    conf_param
    input_layers
    output_layer
    output_attributes
    __init__(...)
    _change_layer(...)

    The target layer that will be changed is the output_layer, 
    which should be accessed as layers[self.output_layer] inside 
    the _change_layer(...) method.
    
    Retagger can add or remove spans inside the target layer, or 
    change annotations of the spans. In addition, it can also modify 
    attributes of the layer: add new attributes, delete old ones,
    or change attributes. 
    
    Changing annotations 
    ==================== 
    
    This is the most common and simplest layer modification operation. 
    Basically, you can iterate over spans of the layer, remove old 
    annotations and add new ones: 
    
        from estnltk_core import Annotation 

        for span in layers[self.output_layer]: 
            span.clear_annotations()
            span.add_annotation( Annotation(span, ...) )
    
    Note, however, that the new Annotation must have the same 
    attributes as the old annotation(s) had.
    Consult the tutorial "low_level_layer_operations.ipynb" for 
    more information about creating Annotation objects. 
    
    Adding spans 
    ============ 
    
    You can use layer's methods add_annotation(...) and add_span(...) 
    to add new spans. The add_annotation(...) method is the most straight-
    forward one. It takes two inputs: the location of the span (start,end), 
    and the dictionary of an annotation (attributes-values), and adds 
    annotations to the layer at the specified location:
    
        assert isinstance(annotations, dict)
        
        layers[self.output_layer].add_annotation( (start,end),**annotations )
    
    In case of an ambiguous layer, you can also add multiple annotations 
    to the same location via layer.add_annotation(...).
    
    The add_span(...) method adds a new Span or EnvelopingSpan to the 
    layer:
    
        from estnltk_core import Span

        layers[self.output_layer].add_span( Span(...) )
    
    Initializing a new Span or EnvelopingSpan is a nuanced operation, 
    please consult the tutorial "low_level_layer_operations.ipynb" for 
    more information about that.
    
    Note that you cannot add two Spans (or EnvelopingSpan-s) that have 
    exactly the same text location, however, partially overlapping spans
    are allowed.
    
    Removing spans 
    ============== 
    
    You can delete spans directly via the method remove_span( ... ), 
    which takes the deletable Span or EnvelopingSpan as an input 
    parameter. 
    Be warned, however, that you should not delete spans while iterating 
    over the layer, as this results in inconsistent deleting behaviour. 
    Instead, you can first iterate over the layer and gather the deletable 
    elements into a separate list, and then apply the deletion on the 
    elements of that list:
    
        to_delete = []
        for span in layers[self.output_layer]:
            if must_be_deleted(span):
                to_delete.append(span)
        
        for span in to_delete:
            layers[self.output_layer].remove_span( span )
    
    Alaternatively, you can also delete spans by their index in the 
    layer, using the del function. Example:
    
        to_delete = []
        for span_id, span in enumerate( layers[self.output_layer] ):
            if must_be_deleted(span):
                to_delete.append( span_id )
        
        for span_id in to_delete:
            del layers[self.output_layer][ span_id ]


    Adding attributes 
    ================= 
    
    New attributes can be added in the following way. First, update
    layer's attributes tuple:
    
        layers[self.output_layer].attributes += ('new_attr_1', 'new_attr_2')
    
    Note that after this step the old annotations of the layer become 
    partially broken (e.g. you cannot display them) until you've set all 
    the missing attributes, but you can still read and change their 
    data.
    Second, update all annotations by adding new attributes:
    
        for span in layers[self.output_layer]: 
            for annotation in span.annotations:
                annotation['new_attr_1'] = ...
                annotation['new_attr_2'] = ...
    
    Removing attributes 
    =================== 
    
    First, update layer's attributes tuple by leaving deletable attributes
    out:
    
        # leave out attributes ('old_attr_1', 'old_attr_2')
        new_attribs = tuple( a for a in layers[self.output_layer].attributes if a not in ('old_attr_1', 'old_attr_2') )
        # update layer's attributes
        layers[self.output_layer].attributes = new_attribs
    
    Second, remove attributes from the annotations of the layer with the 
    help of the delattr function:
    
        for span in layers[self.output_layer]: 
            for annotation in span.annotations:
                delattr(annotation, 'old_attr_1')
                delattr(annotation, 'old_attr_2')
    
    
    Varia
    =====

    # TODO: text.layers will be Set[str]. Make sure that this does not cause problems
    
    """
    # check_output_consistency:
    #    If set, then applies layer's method check_span_consistency()
    #    after modification of the layer.
    check_output_consistency=True,

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def _change_layer(self, text: Union['BaseText', 'Text'], layers: MutableMapping[str, Layer], status: dict) -> None:
        raise NotImplementedError('_change_layer method not implemented in ' + self.__class__.__name__)

    def change_layer(self, text: Union['BaseText', 'Text'], layers: Union[MutableMapping[str, Layer], Set[str]], status: dict = None) -> None:
        """
        # QUICK FIXES:
        layers should be a dictionary of layers but due to the changes in the Text object signature, it is actually a
        list of layer names which will cause a lot of problems in refactoring. Hence, we convert list of layer names
        to dictionary of layers.

        # REFLECTION:
        Adding layers as a separate argument is justified only if the layer is not present in the text object but
        then these layers become undocumented input which make the dependency graph useless.

        The only useful place where layers as separate argument is useful is in text collectons where we cn work with
        detached layers directly.

        Hence, it makes sense to rename layers parameter as detached_layers and check that these are indeed detached
        Also fix some resolving order for the case text[layer] != layers[layer]
        """
        # Quick fix for refactoring problem (does not propagate changes out of the function)
        if type(layers) == set and (not layers or set(map(type, layers)) == {str}):
            layers = {layer: text[layer] for layer in layers}
        # End of fix

        # In order to change the layer, the layer must already exist
        assert self.output_layer in layers, \
          "output_layer {!r} missing from layers {}".format(
                                                 self.output_layer,
                                                 list(layers.keys()))

        target_layers = {name: layers[name] for name in self.input_layers}
        # TODO: check that layer is not frozen

        # Used _change_layer to get the retagged variant of the layer
        self._change_layer(text, target_layers, status)
        # Check that the layer exists
        assert self.output_layer in target_layers, \
               "output_layer {!r} missing from layers {}".format(
                                                 self.output_layer,
                                                 list(layers.keys()))
        if self.check_output_consistency:
            # Validate changed layer: check span consistency
            target_layers[self.output_layer].check_span_consistency()

    def retag(self, text: Union['BaseText', 'Text'], status: dict = None ) -> Union['BaseText', 'Text']:
        """
        Modifies output_layer of given Text object.
        
        Parameters
        ----------
        text: 
            Text object to be retagged
        status: dict, default {}
            This can be used to store metadata on layer modification.
        """
        # Used change_layer to get the retagged variant of the layer
        self.change_layer(text, text.layers, status)
        return text

    def __call__(self, text: Union['BaseText', 'Text'], status: dict = None) -> Union['BaseText', 'Text']:
        return self.retag(text, status)

    def _repr_html_(self):
        import pandas
        parameters = {'name': self.__class__.__name__,
                      'output layer': self.output_layer,
                      'output attributes': str(self.output_attributes),
                      'input layers': str(self.input_layers)}
        table = pandas.DataFrame(parameters, columns=['name', 'output layer', 'output attributes', 'input layers'], index=[0])
        table = table.to_html(index=False)
        assert self.__class__.__doc__ is not None, 'No docstring.'
        description = self.__class__.__doc__.strip().split('\n')[0]
        table = ['<h4>{self.__class__.__name__}({self.__class__.__base__.__name__})</h4>'.format(self=self),
                 description, table]

        def to_str(value):
            value_str = str(value)
            if len(value_str) < 100:
                return value_str
            value_str = value_str[:80] + ' ..., type: ' + str(type(value))
            if hasattr(value, '__len__'):
                value_str += ', length: ' + str(len(value))
            return value_str

        if self.conf_param:
            conf_vals = [to_str(getattr(self, attr)) for attr in self.conf_param if not attr.startswith('_')]
            conf_table = pandas.DataFrame(conf_vals, index=[attr for attr in self.conf_param if not attr.startswith('_')])
            conf_table = conf_table.to_html(header=False)
            conf_table = ('<h4>Configuration</h4>', conf_table)
        else:
            conf_table = ('No configuration parameters.',)

        table.extend(conf_table)
        return '\n'.join(table)

    def __repr__(self):
        conf_str = ''
        if self.conf_param:
            conf = [attr+'='+str(getattr(self, attr)) for attr in self.conf_param if not attr.startswith('_')]
            conf_str = ', '.join(conf)
        return self.__class__.__name__+'('+conf_str+')'

    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.input_layers) + '->' + self.output_layer + ')'
