from estnltk_core.layer.layer import Layer
from estnltk_core.taggers import Tagger

from typing import MutableMapping, Union, Set


class Retagger(Tagger):
    """Base class for retaggers. A retagger modifies existing layer. 
    Use this class as a superclass in creating concrete 
    implementations of retaggers.
    
    Retagger's derived class needs to set the instance variables:
    conf_param
    input_layers
    output_layer
    output_attributes

    ... and implement the following methods:
    __init__(...)
    _change_layer(...)
    
    Optionally, you can also add implementations of: 
    __copy__
    __deepcopy__

    Constructor
    =============
    Every subclass of Retagger should have __init__(...) constructor,
    in which retagger's configuration and instance variables are set.
    The following instance variables should be set:

    * input_layers: Sequence[str] -- names of all layers that are needed
    by the retagger for input;
    * output_layer: str -- name of the layer modified by the retagger;
    * output_attributes: Sequence[str] -- (final) attributes of the output_layer;
    * conf_param: Sequence[str] -- names of all additional attributes of
    the retagger object, which are set in the constructor. If retagger tries
    to set an attribute not declared in conf_param, an exception will be
    raised.

    Note that instance variables (the configuration of the retagger) can only
    be set inside the constructor. After the retagger has been initialized,
    changing values of instance variables is no longer allowed.

    _change_layer(...) method
    ==========================

    The layer is modified inside the _change_layer(...) method, 
    which always returns None, indicating that the method does 
    not produce a new layer, but only changes the target layer.
    
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
    
        for span in layers[self.output_layer]:
            # remove old annotations
            span.clear_annotations()
            # create a dictionary of new annotation
            new_annotation = ...
            assert isinstance(new_annotation, dict)
            # add new annotation
            span.add_annotation( new_annotation )
    
    Note, however, that the new annotation (a dictionary of attributes
    and values) should have the same attributes as the layer has.
    Any attributes of the new annotation that are not present in
    the layer will be discarded. And if the new annotation misses
    some of the layer's attributes, these will be replaced by default
    values (None values, if the layer does not define default values).

    Adding annotations
    ==================
    
    You can use layer's add_annotation(...) method to add new annotations
    to the specific (text) locations. The method takes two inputs: the
    location of the span (start,end), and the dictionary of an annotation
    (attributes-values), and adds annotations to the layer at the specified
    location:
    
        assert isinstance(annotations, dict)
        layers[self.output_layer].add_annotation( (start,end), annotations )
    
    If all attribute names are valid Python identifiers, you can also pass
    annotation as keyword assignments, e.g.:

        layers[self.output_layer].add_annotation( (start,end), attr1=..., attr2=... )

    In case of an ambiguous layer, you can add multiple annotations to the
    same location via layer.add_annotation(...), but this is not allowed
    for unambiguous layers.
    
    Note #1: if the layer does not define any attributes, you can use
    layers[self.output_layer].add_annotation( (start,end) ) to create a
    markup without attributes-values (an empty annotation).

    Note #2: location of the span can be given as (start,end) only if the
    output layer is not enveloping. In case of an enveloping layer, a more
    complex structure should be used, please consult the documentation of
    BaseSpan (from estnltk_core) for details.

    Note #3: you cannot add two Spans (or EnvelopingSpan-s) that have exactly the
    same text location, however, partially overlapping spans are allowed.
    
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

    check_output_consistency=True,
    """
    check_output_consistency: if ``True`` (default), then applies layer's method `check_span_consistency()`
    after the modification to validate the layer. 
    Do not turn this off unless you know what you are doing! 
    """

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def _change_layer(self, text: Union['BaseText', 'Text'], layers: MutableMapping[str, Layer], status: dict) -> None:
        """Changes `output_layer` in the given `text`.

        **This method needs to be implemented in a derived class.**

        Parameters
        ----------
        text: Union['BaseText', 'Text']
            Text object which layer is changed
        layers: MutableMapping[str, Layer]
            A mapping from layer names to Layer objects.
            Layers in the mapping can be detached from the Text object.
            It can be assumed that `output_layer` is in the mapping and
            all tagger's `input_layers` are also in the mapping.
            IMPORTANT: input_layers and output_layer should always be
            accessed via the layers parameter, and NOT VIA THE TEXT
            OBJECT, because the Text object is not guaranteed to have
            them as attached layers at this processing stage.
        status: dict
            Dictionary for recording status messages about tagging.
            Note: the status parameter is **deprecated**.
            To store any metadata, use ``layer.meta`` instead.

        Returns
        ----------
        NoneType
            None
        """
        raise NotImplementedError('_change_layer method not implemented in ' + self.__class__.__name__)

    def change_layer(self, text: Union['BaseText', 'Text'], layers: Union[MutableMapping[str, Layer], Set[str]], status: dict = None) -> None:
        """Changes `output_layer` in the given `text`.

        Note: derived classes **should not override** this method.

        Parameters
        ----------
        text: Union['BaseText', 'Text']
            Text object which layer is changed
        layers: MutableMapping[str, Layer]
            A mapping from layer names to Layer objects.
            Layers in the mapping can be detached from the Text object.
            It can be assumed that `output_layer` is in the mapping and
            all tagger's `input_layers` are also in the mapping.
            IMPORTANT: the output_layer is changed based on input_layers
            and output_layer in the mapping, and not based on the layers
            attached to the Text object.
        status: dict
            Dictionary with status messages about retagging.
            Note: the status parameter is **deprecated**.
            To store/access metadata, use ``layer.meta`` instead.

        Returns
        ----------
        NoneType
            None

        =============================================================================

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
            error_msg = target_layers[self.output_layer].check_span_consistency()
            if error_msg is not None:
                # TODO: should we use ValueErrors (here and elsewere) instead of AssertionError ?
                raise AssertionError( error_msg )

    def retag(self, text: Union['BaseText', 'Text'], status: dict = None ) -> Union['BaseText', 'Text']:
        """
        Modifies output_layer of given Text object.

        Note: derived classes **should not override** this method.

        Parameters
        ----------
        text: 
            Text object to be retagged
        status: dict, default {}
            This can be used to store metadata on layer modification.

        Returns
        -------
        Union['BaseText', 'Text']
            Input Text object which has a output_layer changed by this retagger.
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
