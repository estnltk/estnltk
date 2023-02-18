from estnltk_core.layer.layer import Layer
from estnltk_core.layer.relation_layer import RelationLayer
from estnltk_core.taggers.tagger import TaggerChecker
from estnltk_core.taggers.tagger import Tagger

from typing import MutableMapping, Union, Set, Sequence

class RelationTaggerChecker(TaggerChecker):
    def __call__(cls, *args, **kwargs):
        # Basics: check for existence of 'conf_param', 'input_layers', 'output_layer' and 'output_attributes'
        tagger = TaggerChecker.__call__(cls, *args, **kwargs)

        object.__setattr__(tagger, '_initialized', False)

        # RelationTagger specific: check for existence of 'output_span_names'
        assert isinstance(tagger.output_span_names, Sequence), "'output_span_names' not defined in {!r}".format(cls.__name__)
        assert not isinstance(tagger.output_span_names, str)
        assert len(tagger.output_span_names) > 0, "'output_span_names' must contain at least 1 span name in {!r}".format(cls.__name__)
        assert all(isinstance(attr, str) for attr in tagger.output_span_names), tagger.output_span_names
        tagger.output_span_names = tuple(tagger.output_span_names)
        tagger._initialized = True

        return tagger


class RelationTagger(Tagger, metaclass=RelationTaggerChecker):
    """Base class for relation taggers. A relation tagger creates 
    new RelationLayer (not to be confused with Layer, a.k.a span 
    layer). Use this class as a superclass in creating concrete 
    implementations of relation taggers.

    RelationTagger's derived class needs to set the instance variables:
    conf_param
    output_layer
    output_span_names
    output_attributes
    input_layers

    ... and implement the following methods:
    __init__(...)
    _make_layer(...)

    Optionally, you may also add implementations of: 
    _make_layer_template
    __copy__
    __deepcopy__

    API of RelationTagger is almost the same as that of Tagger, with 
    exceptions that one additional instance variable must be defined 
    (output_span_names) and that all layer creation methods (_make_layer(...), 
    _make_layer_template()) must return RelationLayer instead of Layer. 
    """
    __slots__ = ['_initialized', 'conf_param', 'output_layer', 'output_span_names', 'output_attributes', 'input_layers']

    def __setattr__(self, key, value):
        if self._initialized:
            raise AttributeError('changing of the tagger attributes is not allowed: {!r}, {!r}'.format(
                    self.__class__.__name__, key))
        assert key in {'conf_param', 'output_layer', 'output_span_names', 'output_attributes', 'input_layers', 
                       '_initialized'} or\
               key in self.conf_param,\
               'attribute {!r} not listed in {}.conf_param'.format(key, self.__class__.__name__)
        object.__setattr__(self, key, value)

    def _make_layer(self, text: Union['BaseText', 'Text'], 
                          layers: Union[MutableMapping[str, Union[Layer, RelationLayer]], Set[str]], 
                          status: dict) -> RelationLayer:
        """Creates and returns a new relation layer, based on the given `text` and its `layers`.

        **This method needs to be implemented in a derived class.**

        Parameters
        ----------
        text: Union['BaseText', 'Text']
            Text object to be annotated.
        layers: MutableMapping[str, Union[Layer, RelationLayer]]
            A mapping from layer names to corresponding Layer or RelationLayer 
            objects. Layers in the mapping can be detached from the Text object.
            It can be assumed that all tagger's `input_layers` are in the 
            mapping.
            IMPORTANT: input_layers should always be accessed via the layers 
            parameter, and NOT VIA THE TEXT OBJECT, because the Text object 
            is not guaranteed to have the input layers as attached layers at 
            this processing stage.
        status: dict
            Dictionary for recording status messages about tagging.
            Note: the status parameter is **deprecated**.
            To store any metadata, use ``layer.meta`` instead.

        Returns
        ----------
        RelationLayer
            Created RelationLayer object, which is detached from the Text object.
        """
        raise NotImplementedError('make_layer method not implemented in ' + self.__class__.__name__)

    def make_layer(self, text: Union['BaseText', 'Text'], 
                         layers: Union[MutableMapping[str, Union[Layer, RelationLayer]], Set[str]] = None, 
                         status: dict = None) -> RelationLayer:
        """Creates and returns a new relation layer, based on the given `text` and its `layers`.

        Note: derived classes **should not override** this method.

        Parameters
        ----------
        text: Union['BaseText', 'Text']
            Text object to be annotated.
        layers: MutableMapping[str, Union[Layer, RelationLayer]]
            A mapping from layer names to corresponding Layer or RelationLayer 
            objects. 
            Layers in the mapping can be detached from the Text object.
            It is assumed that all tagger's `input_layers` are in the
            mapping.
            IMPORTANT: the new layer is created based on input_layers
            in the mapping, and not based on layers attached to the
            Text object.
        status: dict
            Dictionary with status messages about tagging.
            Note: the status parameter is **deprecated**.
            To store/access metadata, use ``layer.meta`` instead.

        Returns
        ----------
        RelationLayer
            Created RelationLayer object, which is detached from the Text object.
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

        assert isinstance(layer, RelationLayer), '{}._make_layer did not return a RelationLayer object, but {!r}'.format(
                                                 self.__class__.__name__, type(layer))
        assert layer.text_object is text, '{}._make_layer returned a layer with incorrect Text object'.format(
                                           self.__class__.__name__)
        assert layer.span_names == self.output_span_names,\
            '{}._make_layer returned layer with unexpected span_names: {} != {}'.format(
                    self.__class__.__name__, layer.span_names, self.output_span_names)
        assert layer.attributes == self.output_attributes,\
            '{}._make_layer returned layer with unexpected attributes: {} != {}'.format(
                    self.__class__.__name__, layer.attributes, self.output_attributes)
        assert isinstance(layer, RelationLayer), self.__class__.__name__ + '._make_layer must return Layer'
        assert layer.name == self.output_layer,\
            '{}._make_layer returned a layer with incorrect name: {} != {}'.format(
                    self.__class__.__name__, layer.name, self.output_layer)

        return layer

    def _make_layer_template(self) -> RelationLayer:
        """ Returns an empty detached relation layer that contains all parameters of 
            the output layer.
            This method needs to be implemented in a derived class.
        """
        raise NotImplementedError('_make_layer_template method not implemented in ' + self.__class__.__name__)

    def get_layer_template(self) -> RelationLayer:
        """
        Returns an empty detached relation layer that contains all parameters 
        of the output layer.
        """
        return self._make_layer_template()

    def _repr_html_(self):
        assert self.__doc__ is not None, 'No docstring.'
        description = self.__doc__.strip().split('\n', 1)[0]

        return self._repr_html('RelationTagger', description)

    def _repr_html(self, heading: str, description: str):
        import pandas
        parameters = {'name': self.__class__.__name__,
                      'output layer': self.output_layer,
                      'output span names': str(self.output_span_names),
                      'output attributes': str(self.output_attributes),
                      'input layers': str(self.input_layers)}
        table = pandas.DataFrame(data=parameters,
                                 columns=['name', 'output layer', 'output span names', 'output attributes', 'input layers'],
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
            params = ['input_layers', 'output_layer', 'output_span_names', 'output_attributes'] + list(self.conf_param)
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
                  'span_names': self.output_span_names,
                  'attributes': self.output_attributes,
                  'depends_on': self.input_layers,
                  'configuration': [p+'='+str(getattr(self, p)) for p in self.conf_param if not p.startswith('_')]
                  }
        return record