from typing import MutableMapping, Sequence, Set, Union

from estnltk_core.layer.layer import Layer
from estnltk_core.layer.ambiguous_attribute_tuple_list import to_str


class TaggerChecker(type):
    def __call__(cls, *args, **kwargs):
        tagger = type.__call__(cls, *args, **kwargs)

        assert isinstance(tagger.conf_param, Sequence), "'conf_param' not defined in {!r}".format(cls.__name__)
        assert not isinstance(tagger.conf_param, str)
        assert all(isinstance(k, str) for k in tagger.conf_param), tagger.conf_param
        tagger.conf_param = tuple(tagger.conf_param)

        assert isinstance(tagger.input_layers, Sequence), "'input_layers' not defined in {!r}".format(cls.__name__)
        assert not isinstance(tagger.input_layers, str)
        assert all(isinstance(k, str) for k in tagger.input_layers), tagger.input_layers
        tagger.input_layers = tuple(tagger.input_layers)

        assert isinstance(tagger.output_layer, str), "'output_layer' not defined in {!r}".format(cls.__name__)

        assert isinstance(tagger.output_attributes, Sequence), "'output_attributes' not defined in {!r}".format(cls.__name__)
        assert not isinstance(tagger.output_attributes, str)
        assert all(isinstance(attr, str) for attr in tagger.output_attributes), tagger.output_attributes
        tagger.output_attributes = tuple(tagger.output_attributes)

        tagger._initialized = True

        if tagger.__doc__ is None:
            raise ValueError('{!r} class must have a docstring'.format(cls.__name__))

        return tagger


class Tagger(metaclass=TaggerChecker):
    """Base class for taggers. Tagger creates a new layer. 
    The new layer is created inside the _make_layer() method, 
    which returns Layer object. Optionally, you can also 
    implement _make_layer_template() method, which returns an 
    empty layer that contains all the proper attribute 
    initializations, but is not associated with any text 
    object (this is required if you want to use EstNLTK's 
    Postgres interface). 

    Tagger's derived class needs to implement the following: 
    conf_param
    output_layer
    output_attributes
    input_layers
    __init__(...)
    _make_layer(...)

    Optionally, you may also add implementations of: 
    _make_layer_template
    __copy__
    __deepcopy__
    
    The name of the creatable layer is the output_layer, 
    and the layers required for its creation are listed in 
    input_layers. 
    Note, inside the _make_layer(...) method, you should 
    access input_layers via the layers parameter, e.g. 
    layers[self.input_layers[0]], layers[self.input_layers[1]] 
    etc., and NOT VIA THE INPUT TEXT OBJECT, because 
    the input Text object is not guaranteed to have 
    the input layers as attached layers. 
    
    The attributes of the creatable layer should be listed 
    in self.output_attributes.

    Creating a layer 
    ================ 
    
    You can create a new layer in the following way:
    
        from estnltk_core import Layer
        
        new_layer = Layer(name=self.output_layer,
                          text_object=text,
                          attributes=self.output_attributes,
                          parent=...,
                          enveloping=...,
                          ambiguous=...)
    
    If you have the _make_layer_template() method 
    implemented, it is recommended to create a new 
    layer only inside that method, and then call for 
    the method inside the _make_layer(...):
    
        new_layer = self._make_layer_template()
        new_layer.text_object = text
    
    Layer types 
    =========== 
    
    Simple layer -- a layer that is not ambiguous, nor dependent 
      of any other layer (is not enveloping and does not have a 
      parent layer).
    
    Ambiguous layer -- a layer that can have multiple annotations 
      on same location (same span).
    
    Enveloping layer -- a layer which spans envelop (wrap) around
      spans of some other layer. E.g. 'sentences' layer can be 
      defined as enveloping around 'words' layer.
    
    Child layer -- a layer that has a parent layer and its spans 
      can only be at the same locations as spans of the parent 
      layer. 
    
    A layer can be either enveloping or child, but not both at 
    the same time. 
    
    For more information about layer types, and how to create and 
    and populate different types of layers, see the tutorial 
    "low_level_layer_operations.ipynb"
    
    Adding spans 
    ============ 
    
    Once you've created the layer, you can populate it with data:
    spans and corresponding annotations. 
    
    You can use layer's methods add_annotation(...) and add_span(...) 
    to add new spans. The add_annotation(...) method is the most straight-
    forward one. It takes two inputs: the location of the span (start,end), 
    and the dictionary of an annotation (attributes-values), and adds 
    annotations to the layer at the specified location:
    
        assert isinstance(annotations, dict)
        
        new_layer.add_annotation( (start,end),**annotations )
    
    In case of an ambiguous layer, you can also add multiple annotations 
    to the same location via layer.add_annotation(...).
    
    The add_span(...) method adds a new Span or EnvelopingSpan to the 
    layer:
    
        from estnltk_core import Span

        new_layer.add_span( Span(...) )
    
    Initializing a new Span or EnvelopingSpan is a nuanced operation, 
    please consult the tutorial "low_level_layer_operations.ipynb" for 
    more information about that.
    
    Note that you cannot add two Spans (or EnvelopingSpan-s) that have 
    exactly the same text location, however, partially overlapping spans
    are allowed.

    """
    __slots__ = ['_initialized', 'conf_param', 'output_layer', 'output_attributes', 'input_layers']

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        object.__setattr__(instance, '_initialized', False)
        return instance

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def __copy__(self):
        raise NotImplementedError('__copy__ method not implemented in ' + self.__class__.__name__)

    def __deepcopy__(self, memo={}):
        raise NotImplementedError('__deepcopy__ method not implemented in ' + self.__class__.__name__)

    def __setattr__(self, key, value):
        if self._initialized:
            raise AttributeError('changing of the tagger attributes is not allowed: {!r}, {!r}'.format(
                    self.__class__.__name__, key))
        assert key in {'conf_param', 'output_layer', 'output_attributes', 'input_layers', '_initialized'} or\
               key in self.conf_param,\
               'attribute {!r} not listed in {}.conf_param'.format(key, self.__class__.__name__)
        super().__setattr__(key, value)

    # TODO: rename layers -> detached_layers ?
    # TODO: remove status parameter, use Layer.meta instead
    def _make_layer(self, text: Union['BaseText', 'Text'], layers: MutableMapping[str, Layer], status: dict) -> Layer:
        raise NotImplementedError('make_layer method not implemented in ' + self.__class__.__name__)

    # TODO: rename layers -> detached_layers ?
    # TODO: change argument type layers: Set[str]
    def make_layer(self, text: Union['BaseText', 'Text'], layers: Union[MutableMapping[str, Layer], Set[str]] = None, status: dict = None) -> Layer:
        """
        # TODO: Add documentation
        :param text:
        :param layers:
        :param status:
        :return:

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

        BUG: The function alters layers if it is specified as variable. This can lead to unexpected results
        """
        assert status is None or isinstance(status, dict), 'status should be None or dict, not {!r}'.format(type(status))
        if status is None:
            status = {}

        layers = layers or {}

        # Quick fix for refactoring problem (does not propagate changes out of the function)
        if type(layers) == set and (not layers or set(map(type, layers)) == {str}):
            layers = {layer: text[layer] for layer in layers}
        # End of fix

        for layer in self.input_layers:
            if layer in layers:
                continue
            if layer in text.layers:
                layers[layer] = text[layer]
            else:
                raise ValueError('missing input layer: {!r}'.format(layer))

        try:
            layer = self._make_layer(text=text, layers=layers, status=status)
        except Exception as e:
            e.args += ('in the {!r}'.format(self.__class__.__name__),)
            raise

        assert isinstance(layer, Layer), '{}._make_layer did not return a Layer object, but {!r}'.format(
                                           self.__class__.__name__, type(layer))
        assert layer.text_object is text, '{}._make_layer returned a layer with incorrect Text object'.format(
                                           self.__class__.__name__)
        assert layer.attributes == self.output_attributes,\
            '{}._make_layer returned layer with unexpected attributes: {} != {}'.format(
                    self.__class__.__name__, layer.attributes, self.output_attributes)
        assert isinstance(layer, Layer), self.__class__.__name__ + '._make_layer must return Layer'
        assert layer.name == self.output_layer,\
            '{}._make_layer returned a layer with incorrect name: {} != {}'.format(
                    self.__class__.__name__, layer.name, self.output_layer)

        return layer

    def tag(self, text: Union['BaseText', 'Text'], status: dict = None) -> Union['BaseText', 'Text']:
        """
        text: Text object to be tagged
        status: dict, default {}
            This can be used to store layer creation metadata.
        """
        text.add_layer(self.make_layer(text=text, layers=text.layers, status=status))
        return text

    def _make_layer_template(self) -> Layer:
        """ Returns an empty detached layer that contains all parameters of 
            the output layer.
            This method needs to be implemented in a derived class.
        """
        raise NotImplementedError('_make_layer_template method not implemented in ' + self.__class__.__name__)

    def get_layer_template(self) -> Layer:
        """
        Returns an empty detached layer that contains all parameters 
        of the output layer.
        """
        return self._make_layer_template()

    def __call__(self, text: Union['BaseText', 'Text'], status: dict = None) -> Union['BaseText', 'Text']:
        return self.tag(text, status)

    def _repr_html_(self):
        assert self.__doc__ is not None, 'No docstring.'
        description = self.__doc__.strip().split('\n', 1)[0]

        return self._repr_html('Tagger', description)

    def _repr_html(self, heading: str, description: str):
        import pandas
        parameters = {'name': self.__class__.__name__,
                      'output layer': self.output_layer,
                      'output attributes': str(self.output_attributes),
                      'input layers': str(self.input_layers)}
        table = pandas.DataFrame(data=parameters,
                                 columns=['name', 'output layer', 'output attributes', 'input layers'],
                                 index=[0])
        table = table.to_html(index=False)

        table = ['<h4>{}</h4>'.format(heading), description, table]

        if self.conf_param:
            public_param = [p for p in self.conf_param if not p.startswith('_')]
            conf_values = [to_str(getattr(self, attr)) for attr in public_param]
            conf_table = pandas.DataFrame(conf_values, index=public_param)
            conf_table = conf_table.to_html(header=False)
            conf_table = ('<h4>Configuration</h4>', conf_table)
        else:
            conf_table = ('No configuration parameters.',)

        table.extend(conf_table)
        return '\n'.join(table)

    def __repr__(self):
        conf_str = ''
        if self.conf_param:
            params = ['input_layers', 'output_layer', 'output_attributes'] + list(self.conf_param)
            try:
                conf = [attr+'='+to_str(getattr(self, attr)) for attr in params if not attr.startswith('_')]
            except AttributeError as e:
                e.args = e.args[0] + ", but it is listed in 'conf_param'",
                raise
            conf_str = ', '.join(conf)
        return self.__class__.__name__ + '(' + conf_str + ')'

    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.input_layers) + '->' + self.output_layer + ')'

    # for compatibility with Taggers in resolve_layer_tag
    def parameters(self):
        record = {'name': self.__class__.__name__,
                  'layer': self.output_layer,
                  'attributes': self.output_attributes,
                  'depends_on': self.input_layers,
                  'configuration': [p+'='+str(getattr(self, p)) for p in self.conf_param if not p.startswith('_')]
                  }
        return record
