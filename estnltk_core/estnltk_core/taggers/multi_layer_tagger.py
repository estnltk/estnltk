from typing import MutableMapping, Sequence, Set, Union

from estnltk_core.layer.layer import Layer
from estnltk_core.layer.to_html import to_str


class MultiLayerTaggerChecker(type):
    def __call__(cls, *args, **kwargs):
        tagger = type.__call__(cls, *args, **kwargs)

        assert isinstance(tagger.conf_param, Sequence), "'conf_param' not defined in {!r}".format(cls.__name__)
        assert not isinstance(tagger.conf_param, str)
        assert all(isinstance(k, str) for k in tagger.conf_param), tagger.conf_param
        tagger.conf_param = tuple(tagger.conf_param)

        assert isinstance(tagger.output_layers, list), "'output_layers' not defined in {!r}".format(cls.__name__)

        assert isinstance(tagger.output_layers_to_attributes, MutableMapping), "'output_layers_to_attributes' not defined in {!r}".format(
            cls.__name__)
        assert isinstance(tagger.output_layers_to_attributes, MutableMapping)
        assert all(isinstance(attr, str) for attr in tagger.output_layers_to_attributes), tagger.output_layers_to_attributes

        tagger._initialized = True

        if tagger.__doc__ is None:
            raise ValueError('{!r} class must have a docstring'.format(cls.__name__))

        return tagger


class MultiLayerTagger(metaclass=MultiLayerTaggerChecker):
    """
    multilayertagger
    """
    __slots__ = ['_initialized', 'conf_param', 'output_layers', 'output_layers_to_attributes']

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
        assert key in {'conf_param', 'output_layers', 'output_layers_to_attributes', '_initialized'} or \
               key in self.conf_param, \
            'attribute {!r} not listed in {}.conf_param'.format(key, self.__class__.__name__)
        super().__setattr__(key, value)

    def _make_layers(self, text: Union['BaseText', 'Text'], layers: MutableMapping[str, Layer], status: dict) -> MutableMapping[str,Layer]:
        """
        analog to tagger._make_layer
        """
        raise NotImplementedError('make_layer method not implemented in ' + self.__class__.__name__)

    def make_layers(self, text: Union['BaseText', 'Text'], layers: Union[MutableMapping[str, Layer], Set[str]] = None,
                   status: dict = None) -> MutableMapping[str,Layer]:
        """
        analog to tagger.make_layer
        """
        assert status is None or isinstance(status, dict), 'status should be None or dict, not {!r}'.format(
            type(status))
        if status is None:
            status = {}

        layers = layers or {}

        # Quick fix for refactoring problem (does not propagate changes out of the function)
        if type(layers) == set and (not layers or set(map(type, layers)) == {str}):
            layers = {layer: text[layer] for layer in layers}
        # End of fix

        try:
            layers = self._make_layers(text=text, layers=layers, status=status)
        except Exception as e:
            e.args += ('in the {!r}'.format(self.__class__.__name__),)
            raise

        assert isinstance(layers, MutableMapping), '{}._make_layers did not return a dict object, but {!r}'.format(
            self.__class__.__name__, type(layers))
        for layer in layers.values():
            assert layer.text_object is text, '{}._make_layers returned a layer with incorrect Text object'.format(
                self.__class__.__name__)
        for layername, layer in layers.items():
            assert layer.attributes == tuple(self.output_layers_to_attributes[layername]), \
                '{}._make_layer returned layer with unexpected attributes: {} != {}'.format(
                    self.__class__.__name__, layer.attributes, tuple(self.output_layers_to_attributes[layername]))
        for layer in layers.values():
            assert isinstance(layer, Layer), self.__class__.__name__ + '._make_layer must return Layer'
        for layer in layers.values():
            assert layer.name in self.output_layers, \
                '{}._make_layer returned a layer with incorrect name: {} != {}'.format(
                    self.__class__.__name__, layer.name, self.output_layers)

        return layers

    def tag(self, text: Union['BaseText', 'Text'], status: dict = None) -> Union['BaseText', 'Text']:
        """Annotates Text object with these taggers.
        """
        layer_mapping = self.make_layers(text=text,layers=text.layers,status=status)
        for layer_name, layer in layer_mapping.items():
            text.add_layer(layer)
        return text

    def __call__(self, text: Union['BaseText', 'Text'], status: dict = None) -> Union['BaseText', 'Text']:
        return self.tag(text, status)

    def _repr_html_(self):
        assert self.__doc__ is not None, 'No docstring.'
        description = self.__doc__.strip().split('\n', 1)[0]

        return self._repr_html('Tagger', description)

    def _repr_html(self, heading: str, description: str):
        import pandas
        parameters = {'name': self.__class__.__name__,
                      'output layers': self.output_layers,
                      'output mapping': str(self.output_layers_to_attributes)}
        table = pandas.DataFrame(data=parameters,
                                 columns=['name', 'output layers', 'output mapping'],
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
            params = ['output_layers', 'output_layers_to_attributes'] + list(self.conf_param)
            try:
                conf = [attr + '=' + to_str(getattr(self, attr)) for attr in params if not attr.startswith('_')]
            except AttributeError as e:
                e.args = e.args[0] + ", but it is listed in 'conf_param'",
                raise
            conf_str = ', '.join(conf)
        return self.__class__.__name__ + '(' + conf_str + ')'

    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.output_layers_to_attributes) + ')'

