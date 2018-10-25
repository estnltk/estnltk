from estnltk.text import Layer, Text
from estnltk.taggers import Tagger

from typing import MutableMapping


class Retagger(Tagger):
    """
    Base class for retaggers. Retagger modifies existing layer.
    For the sake of simplicity, we currently just use Tagger as 
    the super class.

    The following needs to be implemented in a derived class:
    conf_param
    depends_on
    layer_name
    attributes
    __init__(...)
    _change_layer(...)
    """

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict) -> None:
        raise NotImplementedError('_change_layer method not implemented in ' + self.__class__.__name__)

    def retag(self, text: Text, status: dict = None, 
                    check_output_consistency: bool=True ) -> Text:
        """
        Modifies output_layer of given Text object.
        
        Parameters
        ----------
        text: 
            Text object to be retagged
        status: dict, default {}
            This can be used to store metadata on layer modification.
        check_output_consistency: boolean (default: True)
            If set, then applies layer's method check_span_consistency()
            after modification of the layer.
        """
        # In order to change the layer, the layer must already exist
        assert self.output_layer in text.layers, \
          "output_layer '{}' missing from Text's layers {}".format(
                                                 self.output_layer, 
                                                 list(text.layers.keys()))
        layers = {name: text.layers[name] for name in self.input_layers}
        # TODO: check that layer is not frozen

        # Used _change_layer to get the retagged variant of the layer
        self._change_layer(text.text, layers, status)
        # Check that the layer exists
        assert self.output_layer in layers, \
               "output_layer '{}' missing from layers {}".format(
                                                 self.output_layer, 
                                                 list(layers.keys()))
        if check_output_consistency:
            # Validate changed layer: check span consistency
            layers[self.output_layer].check_span_consistency()
        return text

    def __call__(self, text: Text, status: dict = None) -> Text:
        return self.retag(text, status)

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        parameters = {'name': self.__class__.__name__,
                      'output layer': self.output_layer,
                      'output attributes': str(self.output_attributes),
                      'input layers': str(self.input_layers)}
        table = pandas.DataFrame(parameters, columns=['name', 'output layer', 'output attributes', 'input layers'], index=[0])
        table = table.to_html(index=False)
        assert self.__class__.__doc__ is not None, 'No docstring.'
        description = self.__class__.__doc__.strip().split('\n')[0]
        table = ['<h4>Retagger</h4>', description, table]

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
