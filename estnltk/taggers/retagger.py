from estnltk.text import Text


class Retagger:
    """
    Base class for retaggers. Retagger modifies existing layer.

    The following needs to be implemented in a derived class:
    conf_param
    depends_on
    layer_name
    attributes
    __init__(...)
    change_layer(...)
    """

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def __setattr__(self, key, value):
        assert key in {'conf_param', 'description', 'output_layer', 'output_attributes', 'input_layers'} or\
               key in self.conf_param,\
               'attribute must be listed in conf_param: ' + key
        super.__setattr__(self, key, value)

    def change_layer(self, raw_text: str, input_layers: dict, status: dict) -> None:
        raise NotImplementedError('change_layer method not implemented in ' + self.__class__.__name__)

    def _change_layer(self, text: Text, status: dict) -> None:
        layers = {name: text.layers[name] for name in self.input_layers}
        # TODO: check that layer is not frozen
        self.change_layer(text.text, layers, status)

    def change(self, text: Text, status: dict = None) -> Text:
        if status is None:
            status = {}
        self._change_layer(text, status)
        return text

    def retag(self, text: Text, status: dict = None) -> Text:
        """
        text: Text object to be retagged
        status: dict, default {}
            This can be used to store metadata on layer creation.
        """
        self._change_layer(text, status)
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
            conf_vals = [to_str(getattr(self, attr)) for attr in self.conf_param]
            conf_table = pandas.DataFrame(conf_vals, index=self.conf_param)
            conf_table = conf_table.to_html(header=False)
            conf_table = ('<h4>Configuration</h4>', conf_table)
        else:
            conf_table = ('No configuration parameters.',)

        table.extend(conf_table)
        return '\n'.join(table)

    def __repr__(self):
        conf_str = ''
        if self.conf_param:
            conf = [attr+'='+str(getattr(self, attr)) for attr in self.conf_param]
            conf_str = ', '.join(conf)
        return self.__class__.__name__+'('+conf_str+')'
