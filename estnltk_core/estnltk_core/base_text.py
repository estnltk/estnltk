import html
import pandas

from copy import copy, deepcopy
from typing import List, Sequence, Set, Union, Any, Mapping

from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies

class BaseText:
    """
    Base class for EstNLTK's Text. BaseText stores raw text along with annotation layers and metadata.

    Raw text can simply be accessed via attribute ``.text``.

    BaseText allows to add and remove annotation layers, and checks for layer dependencies.
    A layer can be added to text only if its dependency layers already exist, and removing a layer results
    in removing its descendant layers.

    BaseText provides access to annotation layers via indexing, where index value should be the
    name of the layer, e.g. text['words'] or text['sentences'].

    It is possible to add meta-information about text as a whole by specifying text.meta,
    which is a dictionary of type MutableMapping[str, Any]. However we strongly advise to
    use the following value types:
        str
        int
        float
        DateTime
    as database serialisation does not work for other types. See [estnltk.storage.postgres] for further documentation.

    Note: BaseText does not provide any linguistic analysis / NLP pipeline. Use the Text class from the full EstNLTK
    package for NLP.
    """
    __slots__ = ['text', 'meta', '_layers']

    def __init__(self, text: str = None) -> None:
        assert text is None or isinstance(text, str), "{} takes string as an argument!".format( self.__class__.__name__ )
        # self.text: str
        super().__setattr__('text', text)
        # self.meta: MutableMapping
        super().__setattr__('meta', {})
        # self._layers: MutableMapping
        object.__setattr__(self, '_layers', {})

    def __copy__(self):
        raise Exception('Shallow copying of {} object is not allowed. Use deepcopy instead.'.format( self.__class__.__name__ ) )

    def __deepcopy__(self, memo={}):
        #print(memo)
        text = copy(self.text)
        result = self.__class__( text )
        memo[id(self)] = result
        memo[id(text)] = text
        result.meta = deepcopy(self.meta, memo)
        # Layers must be created in the topological order
        for original_layer in self.sorted_layers():
            layer = deepcopy(original_layer, memo)
            layer.text_object = None
            memo[id(layer)] = layer
            result.add_layer(layer)
        return result

    def __getstate__(self):
        # No copying is allowed or we cannot properly restore text object with recursive references.
        return dict(text=self.text, meta=self.meta, layers=[layer for layer in self.sorted_layers()])

    def __setstate__(self, state):
        # Initialisation is not guaranteed! Bypass the text protection mechanism
        assert type(state['text']) == str, '\'field \'text\' must be of type str'
        super().__setattr__('text', state['text'])
        super().__setattr__('meta', state['meta'])
        super().__setattr__('_layers', {})
        # Layer.text_object is already set! Bypass the add_layer protection mechanism
        # By wonders of pickling this resolves all recursive references including references to the text object itself
        for layer in state['layers']:
            assert id(layer.text_object) == id(self), '\'layer.text_object\' must reference caller'
            layer.text_object = None
            self.add_layer(layer)

    def __setattr__(self, name, value):
        # Resolve meta attribute
        if name == 'meta':
            if not isinstance(value, dict):
                raise ValueError('meta must be of type dict')
            if value and set(map(type, value)) != {str}:
                raise ValueError('meta must be of type dict with keys of type str')
            return super().__setattr__(name, value)

        # Resolve text attribute
        if name == 'text':
            if self.__getattribute__('text') is not None:
                raise AttributeError('raw text has already been set')
            if not isinstance(value, str):
                raise TypeError('expecting a string as value')
            return super().__setattr__('text', value)

        # Deny access to all other attributes (layer names)
        raise AttributeError('layers cannot be assigned directly, use add_layer(...) function instead')

    def __setitem__(self, key, value):
        raise TypeError('layers cannot be assigned directly, use add_layer(...) function instead')

    def __getitem__(self, item):
        if item in self._layers:
            return self._layers[item]
        else:
            raise KeyError("'{}' object has no layer {!r}".format( self.__class__.__name__, item ))

    def __delattr__(self, item):
        raise TypeError("'{}' object does not support attribute deletion".format( self.__class__.__name__ ))

    def __delitem__(self, key):
        raise TypeError("'{}' object does not support item deletion, use pop_layer(...) function instead".format( self.__class__.__name__ ))

    def __eq__(self, other):
        return self.diff(other) is None

    def __repr__(self):
        if self.text is None:
            return '{}()'.format( self.__class__.__name__ )
        text_string = self.text
        if len(text_string) > 10000:
            text_string = '{}\n\n<skipping {} characters>\n\n{}'.format(text_string[:8000],
                                                                        len(text_string) - 9000,
                                                                        text_string[-1000:])
        return '{classname}(text={text_string!r})'.format(classname=self.__class__.__name__, text_string=text_string)

    @property
    def layers(self) -> Set[str]:
        """
        Returns the names of all layers in the text object in alphabetical order.
        """
        return set( self._layers.keys() )

    def add_layer(self, layer: Union[BaseLayer, 'Layer']):
        """
        Adds a layer to the text object.
        
        An addable layer must satisfy the following conditions:
        * layer.name is unique among names of existing layers of this 
          Text object;
        * layer.text_object is either None or points to this Text object;
          if layer has already been associated with another Text object, 
          throws an AssertionError;
        * if the layer has parent, then its parent layer must already exist 
          among the layers of this Text object;
        * if the layer is enveloping, then the layer it envelops must already 
          exist among the layers of this Text object;
        """
        assert isinstance(layer, BaseLayer), 'Layer expected, got {!r}'.format(type(layer))

        name = layer.name

        assert name not in self._layers, 'this {} object already has a layer with name {!r}'.format(self.__class__.__name__, name)

        if layer.text_object is None:
            layer.text_object = self
        else:
            assert layer.text_object is self, \
                "can't add layer {!r}, this layer is already bound to another {} object".format(name, self.__class__.__name__)

        if layer.parent:
            assert layer.parent in self._layers, 'Cant add a layer "{layer}" before adding its parent "{parent}"'.format(
                parent=layer.parent, layer=layer.name)

        if layer.enveloping:
            assert layer.enveloping in self._layers, "can't add an enveloping layer before adding the layer it envelops"

        self._layers[name] = layer

    def pop_layer(self, name: str,  cascading: bool = True, default=Ellipsis) -> Union[BaseLayer, 'Layer', Any]:
        """
        Removes a layer from the text object together with the layers that are computed from it by default.

        If the flag cascading is set all descendant layers are computed first and removed together with the layer.
        If the flag is false only the layer is removed. This does not corrupt derivative layers, as spans of each
        layer are independent form other layers.

        Returns popped layer if the layer is present in the text object. If the layer is not found default is
        returned if given, otherwise KeyError is raised.
        """
        if name not in self.layers and default is Ellipsis:
            raise KeyError('{layer!r} is not a valid layer in this {classname} object'.format(layer=name,classname=self.__class__.__name__))

        if not cascading:
            return self._layers.pop(name, None)

        # Find layer's descendant layers
        to_delete = sorted(find_layer_dependencies(self, name, reverse=True))
        
        result = self._layers.pop(name, None)
        for name in to_delete:
            self._layers.pop(name, None)

        return result

    def tag_layer(self, layer_names: Union[str, Sequence[str]]=None, resolver=None) -> 'Text':
        raise NotImplementedError('(!) The NLP pipeline is not available in estnltk-core. Please use the full EstNLTK package for the pipeline.')

    def analyse(self, t: str, resolver=None) -> 'Text':
        raise NotImplementedError('(!) The NLP pipeline is not available in estnltk-core. Please use the full EstNLTK package for the pipeline.')

    @staticmethod
    def topological_sort(layers: Mapping[str, Union[BaseLayer, 'Layer']]) -> List[Union[BaseLayer, 'Layer']]:
        """
        Returns a list of all layers of the given dict of layers in order of dependencies and layer names.
        The order is uniquely determined.

        layers: Mapping[str, Union[BaseLayer, Layer]]
            maps layer name to layer
        """
        layer_list = sorted(layers.values(), key=lambda l: l.name)
        sorted_layers = []
        sorted_layer_names = set()
        while layer_list:
            for layer in layer_list:
                if (layer.parent is None or layer.parent in sorted_layer_names) and \
                        (layer.enveloping is None or layer.enveloping in sorted_layer_names):
                    sorted_layers.append(layer)
                    sorted_layer_names.add(layer.name)
                    layer_list.remove(layer)
                    break
        return sorted_layers

    def sorted_layers(self) -> List[Union[BaseLayer, 'Layer']]:
        """
        Returns a list of all layers of this text object in order of dependencies and layer names.
        The order is uniquely determined.
        """
        return self.topological_sort(self._layers)

    def diff(self, other):
        """
        Returns a brief diagnostic message that explains why two BaseText/Text objects are different.

        # BUGS:
          - Inf loops with recursive self-references in meta dictionary.
        """
        if self is other:
            return None
        if not isinstance(other, self.__class__):
            return 'Not a {} object.'.format( self.__class__.__name__ )
        if self.text != other.text:
            return 'The raw text is different.'
        if set(self._layers) != set(other.layers):
            return 'Different layer names: {} != {}'.format(set(self._layers), set(other.layers))
        if self.meta != other.meta:
            return 'Different metadata.'
        for layer_name in self._layers:
            difference = self._layers[layer_name].diff(other[layer_name])
            if difference:
                return difference
        return None

    def _repr_html_(self):
        if self.text is None:
            table = '<h4>Empty {} object</h4>'.format( self.__class__.__name__ )
        else:
            text = self.text
            if len(text) > 10000:
                text = '{}\n\n<skipping {} characters>\n\n{}'.format(text[:8000],
                                                                     len(text) - 9000,
                                                                     text[-1000:])
            text_html = '<div align = "left">' + html.escape(text).replace('\n', '</br>') + '</div>'
            df = pandas.DataFrame(columns=['text'], data=[text_html])
            table = df.to_html(index=False, escape=False)

        if self.meta:
            data = {'key': sorted(self.meta), 'value': [self.meta[k] for k in sorted(self.meta)]}
            table_meta = pandas.DataFrame(data, columns=['key', 'value'])
            table_meta = table_meta.to_html(header=False, index=False)
            table = '\n'.join((table, '<h4>Metadata</h4>', table_meta))
        if self._layers:
            layers = []
            # Try to fetch presorted layers (only available in Text)
            presorted_layers = getattr(self, 'presorted_layers', ())
            for layer_name in presorted_layers:
                assert isinstance(layer_name, str)
                layer = self._layers.get(layer_name)
                if layer is not None:
                    layers.append(layer)
            # Assuming self._layers is always ordered (requires Python 3.7+)
            for layer_name in self._layers:
                if layer_name not in presorted_layers:
                    layers.append(self._layers[layer_name])

            layer_table = pandas.DataFrame()
            layer_table = pandas.concat([layer.get_overview_dataframe() for layer in layers])
            layer_table = layer_table.to_html(index=False, escape=False)
            return '\n'.join((table, layer_table))
        return table

