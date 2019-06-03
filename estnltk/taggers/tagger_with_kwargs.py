from typing import MutableMapping, Sequence

from estnltk.text import Layer, Text
from estnltk.taggers import Tagger

from typing import MutableMapping


class TaggerWithKwargs(Tagger):
    """
    Base class for taggers that allow to pass kwargs to the tag() method.

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

    # TODO: rename layers -> detached_layers ?
    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict, **kwargs) -> Layer:
        raise NotImplementedError('make_layer method not implemented in ' + self.__class__.__name__)

    # TODO: rename layers -> detached_layers ?
    def make_layer(self, text: Text, layers: MutableMapping[str, Layer] = None, status: dict = None, **kwargs) -> Layer:
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
            layer = self._make_layer(text=text, layers=layers, status=status, **kwargs)
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

    def tag(self, text: Text, status: dict = None, **kwargs) -> Text:
        """
        text: Text object to be tagged
        status: dict, default {}
            This can be used to store layer creation metadata.
        """
        text[self.output_layer] = self.make_layer(text=text, layers=text.layers, status=status, **kwargs)
        return text

    def __call__(self, text: Text, status: dict = None, **kwargs) -> Text:
        return self.tag(text, status, **kwargs)

