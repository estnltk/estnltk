from estnltk.layer import Layer


class TaggerNew:
    """
    Base class for taggers. Proposed new version.

    The following needs to be implemented in a derived class:
    conf_param
    description
    depends_on
    layer_name
    attributes
    __init__(...)
    _change_layer(...) or _make_layer(...)
    """

    def __init__(self):
        raise NotImplementedError('__init__ method not implemented in ' + self.__class__.__name__)

    def __setattr__(self, key, value):
        assert key in {'conf_param', 'description', 'layer_name', 'attributes', 'depends_on'} or\
               key in self.conf_param,\
               'attribute must be listed in conf_param: ' + key
        super.__setattr__(self, key, value)

    def _change_layer(self, raw_text: str, input_layers: dict, status: dict) -> None:
        raise NotImplementedError('_change_layer method not implemented in ' + self.__class__.__name__)

    def change_layer(self, raw_text: str, input_layers=None, status: dict = None) -> None:
        assert set(input_layers) == set(self.depends_on)
        # TODO: check that layer is not frozen
        if input_layers is None:
            input_layers = {}
        if status is None:
            status = {}
        self._change_layer(raw_text, input_layers, status)

    def _make_layer(self, raw_text: str, input_layers: dict, status: dict) -> Layer:
        raise NotImplementedError('_make_layer method not implemented in ' + self.__class__.__name__)

    def make_layer(self, raw_text: str, input_layers=None, status: dict = None) -> Layer:
        if input_layers is None:
            input_layers = {}
        assert set(input_layers) == set(self.depends_on)
        if status is None:
            status = {}
        layer = self._make_layer(raw_text, input_layers, status)
        assert isinstance(layer, Layer), '_make_layer must return Layer'
        assert layer.name == self.layer_name, 'incorrect layer name: {} != {}'.format(layer.name, self.layer_name)
        return layer

    def tag(self, text: 'Text', status: dict = None) -> 'Text':
        """
        text: Text object to be tagged
        status: dict, default {}
            This can be used to store metadata on layer creation.
        """
        input_layers = {name: text.layers[name] for name in self.depends_on}
        text[self.layer_name] = self.make_layer(text.text, input_layers, status)
        return text

    def __call__(self, text: 'Text', status: dict = None) -> 'Text':
        return self.tag(text, status)

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        parameters = {'name': self.__class__.__name__,
                      'layer': self.layer_name,
                      'attributes': str(self.attributes),
                      'depends_on': str(self.depends_on)}
        table = pandas.DataFrame(parameters, columns=['name', 'layer', 'attributes', 'depends_on'], index=[0])
        table = table.to_html(index=False)
        table = ['<h4>Tagger</h4>', self.description, table]

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
