import html
import regex as re
from typing import MutableMapping, Sequence
from estnltk.text import Layer, Text


class Tagger:
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
    conf_param = None  # type: Sequence[str]
    output_layer = None  # type: str
    output_attributes = None  # type: Sequence[str]
    input_layers = None  # type: Sequence[str]

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def __setattr__(self, key, value):
        assert key in {'conf_param', 'output_layer', 'output_attributes', 'input_layers'} or\
               key in self.conf_param,\
               'attribute must be listed in conf_param: ' + key
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


def to_str(value, escape_html=False):
    if callable(value) and hasattr(value, '__name__') and hasattr(value, '__module__'):
        value_str = '<function {}.{}>'.format(value.__module__, value.__name__)
    elif isinstance(value, re.Pattern):
        value_str = '<Regex {}>'.format(value.pattern)
    else:
        value_str = str(value)

    if len(value_str) >= 100:
        value_str = value_str[:80] + ' ..., type: ' + str(type(value))
        if hasattr(value, '__len__'):
            value_str += ', length: ' + str(len(value))

    if escape_html:
        value_str = html.escape(value_str)
    return value_str
