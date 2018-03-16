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
    make_layer(...)
    """

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def __setattr__(self, key, value):
        assert key in {'conf_param', 'output_layer', 'output_attributes', 'input_layers'} or\
               key in self.conf_param,\
               'attribute must be listed in conf_param: ' + key
        super.__setattr__(self, key, value)

    def make_layer(self, raw_text: str, layers: dict, status: dict) -> Layer:
        raise NotImplementedError('make_layer method not implemented in ' + self.__class__.__name__)

    def _make_layer(self, text: Text, status: dict = None) -> Layer:
        if status is None:
            status = {}
        layer = self.make_layer(text.text, text.layers, status)
        assert isinstance(layer, Layer), 'make_layer must return Layer'
        assert layer.name == self.output_layer, 'incorrect layer name: {} != {}'.format(layer.name, self.output_layer)
        return layer

    def tag(self, text: Text, status: dict = None) -> Text:
        """
        text: Text object to be tagged
        status: dict, default {}
            This can be used to store metadata on layer creation.
        """
        # input_layers = {name: text.layers[name] for name in self.input_layers}
        text[self.output_layer] = self._make_layer(text, status)
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
        table = pandas.DataFrame(parameters, columns=['name', 'output layer', 'output attributes', 'input layers'], index=[0])
        table = table.to_html(index=False)
        assert self.__class__.__doc__ is not None, 'No docstring.'
        description = self.__class__.__doc__.strip().split('\n')[0]
        table = ['<h4>TaggerOld</h4>', description, table]

        def to_str(value):
            value_str = str(value)
            if len(value_str) < 100:
                return value_str
            value_str = value_str[:80] + ' ..., type: ' + str(type(value))
            if hasattr(value, '__len__'):
                value_str += ', length: ' + str(len(value))
            return value_str

        if self.conf_param:
            public_param = [p for p in self.conf_param if not p.startswith('_')]
            conf_vals = [to_str(getattr(self, attr)) for attr in public_param]
            conf_table = pandas.DataFrame(conf_vals, index=public_param)
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
