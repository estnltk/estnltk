from typing import MutableMapping, Sequence, Tuple

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.layer.ambiguous_attribute_tuple_list import to_str


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
    """
    Base class for taggers. Proposed new version.

    The following needs to be implemented in a derived class:
    conf_param
    input_layers
    output_layer
    output_attributes
    __init__(...)
    _make_layer(...)
    """
    _initialized = False
    conf_param = None  # type: Sequence[str]
    output_layer = None  # type: str
    output_attributes = None  # type: Sequence[str]
    input_layers = None  # type: Sequence[str]

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def __setattr__(self, key, value):
        if self._initialized:
            raise AttributeError('changing of the tagger attributes is not allowed: {!r}, {!r}'.format(
                    self.__class__.__name__, key))
        assert key in {'conf_param', 'output_layer', 'output_attributes', 'input_layers', '_initialized'} or\
               key in self.conf_param,\
               'attribute {!r} not listed in {}.conf_param'.format(key, self.__class__.__name__)
        super().__setattr__(key, value)

    # TODO: rename layers -> detached_layers ?
    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        raise NotImplementedError('make_layer method not implemented in ' + self.__class__.__name__)

    # TODO: rename layers -> detached_layers ?
    def make_layer(self, text: Text, layers: MutableMapping[str, Layer] = None, status: dict = None) -> Layer:
        assert status is None or isinstance(status, dict), 'status should be None or dict, not {!r}'.format(type(status))
        if status is None:
            status = {}
        layers = layers or {}
        for layer in self.input_layers:
            if layer in layers:
                continue
            if layer in text.layers:
                layers[layer] = text.layers[layer]
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

    def tag(self, text: Text, status: dict = None) -> Text:
        """
        text: Text object to be tagged
        status: dict, default {}
            This can be used to store layer creation metadata.
        """
        text[self.output_layer] = self.make_layer(text=text, layers=text.layers, status=status)
        return text

    def __call__(self, text: Text, status: dict = None) -> Text:
        return self.tag(text, status)

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        parameters = {'name': self.__class__.__name__,
                      'output layer': self.output_layer,
                      'output attributes': str(self.output_attributes),
                      'input layers': str(self.input_layers)}
        table = pandas.DataFrame(data=parameters,
                                 columns=['name', 'output layer', 'output attributes', 'input layers'],
                                 index=[0])
        table = table.to_html(index=False)
        assert self.__class__.__doc__ is not None, 'No docstring.'
        description = self.__class__.__doc__.strip().split('\n')[0]
        table = ['<h4>Tagger</h4>', description, table]

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
