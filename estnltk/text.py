import networkx as nx

from copy import copy, deepcopy
from collections import defaultdict
from typing import List, Sequence, Set, Union, Any, Mapping
from typing import DefaultDict

from estnltk.layer.layer import Layer


class Text:
    # All methods for Text object
    # methods: Set[str]
    methods = {
        'add_layer',
        'analyse',
        'attributes',
        'pop_layer',
        'diff',
        'layers',
        'list_layers',
        'tag_layer',
        'topological_sort',
    } | {method for method in dir(object) if callable(getattr(object, method, None))}

    # attribute_mapping_for_elementary_layers: Mapping[str, str]
    attribute_mapping_for_elementary_layers = {
        'lemma': 'morph_analysis',
        'root': 'morph_analysis',
        'root_tokens': 'morph_analysis',
        'ending': 'morph_analysis',
        'clitic': 'morph_analysis',
        'form': 'morph_analysis',
        'partofspeech': 'morph_analysis'
    }

    attribute_mapping_for_enveloping_layers = attribute_mapping_for_elementary_layers

    __slots__ = ['text', 'meta', '__dict__', '_shadowed_layers']

    def __init__(self, text: str = None) -> None:
        # self.text: str
        super().__setattr__('text', text)
        # self._shadowed_layers: Mapping[str, Layer]
        super().__setattr__('_shadowed_layers', {})
        # self.meta: MutableMapping
        super().__setattr__('meta', {})

    def __copy__(self):
        result = Text(self.text)
        result.meta = self.meta
        for layer_name in self.layers:
            layer = copy(self[layer_name])
            layer.text_object = None
            result.add_layer(layer)
        return result

    def __deepcopy__(self, memo={}):
        print(memo)
        text = copy(self.text)
        result = Text(text)
        memo[id(self)] = result
        memo[id(text)] = text
        result.meta = deepcopy(self.meta, memo)
        # Layers must be created in the topological order
        # TODO: test this in tests
        for original_layer in self.list_layers():
            layer = deepcopy(original_layer, memo)
            memo[id(layer)] = layer
            result.add_layer(layer)
        return result

    def __getstate__(self):
        # No copying is allowed or we cannot properly restore text object with recursive references.
        return dict(text=self.text, meta=self.meta, layers=[layer for layer in self.list_layers()])

    def __setstate__(self, state):
        # Initialisation is not guaranteed! Bypass the text protection mechanism
        assert type(state['text']) == str, '\'field \'text\' must be of type str'
        super().__setattr__('text', state['text'])
        super().__setattr__('_shadowed_layers', {})
        self.meta = state['meta']
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
                raise TypeError('expecting a string as rvalue')
            return super().__setattr__('text', value)

        # Deny access to all other attributes (layer names)
        raise AttributeError('layers cannot be assigned directly, use add_layer(...) function instead')

    def __getattr__(self, item):
        # Function __getattr__ is never called on items in __dict__

        # Resolve slots
        if item in Text.__slots__:
            return self.__getattribute__(item)

        # Resolve all function calls
        if item in Text.methods:
            return self.__getattribute__(item)

        # Resolve attributes that uniquely determine a layer, e.g. Text.lemmas ==> Text.morph_layer.lemmas
        attributes = self.__getattribute__('attributes')

        if len(attributes[item]) == 1:
            return getattr(self.__dict__[attributes[item][0]], item)

        # Nothing else to resolve
        raise AttributeError("'Text' object has no layer {!r}".format(item))

    def __setitem__(self, key, value):
        raise TypeError('layers cannot be assigned directly, use add_layer(...) function instead')

    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            return self._shadowed_layers[item]

    def __delattr__(self, item):
        raise TypeError("'Text' object does not support attribute deletion, use pop_layer(...) function instead")

    def __delitem__(self, key):
        raise TypeError("'Text' object does not support item deletion, use pop_layer(...) function instead")

    def __eq__(self, other):
        return self.diff(other) is None

    def __str__(self):
        if self.text is None:
            return 'Text()'
        return 'Text(text={self.text!r})'.format(self=self)

    def __repr__(self):
        return str(self)

    @property
    def layers(self) -> Set[str]:
        """
        Returns the names of all layers in the text object in alphabetical order.
        """
        return self.__dict__.keys() | self._shadowed_layers.keys()

    @property
    def attributes(self) -> DefaultDict[str, List[str]]:
        """
        Returns all attributes together with layer names hosting them.

        # TODO: Reduce defaultdict to dict
        # TODO: Rename to layer_attributes
        # TODO: remove infinite recursion
        """
        result = defaultdict(list)

        # Collect attributes from standard layers
        for name, layer in self.__dict__.items():
            for attrib in layer.attributes:
                result[attrib].append(name)

        # Collect attributes from shadowed layers
        for name, layer in self._shadowed_layers.items():
            for attrib in layer.attributes:
                result[attrib].append(name)

        return result

    def add_layer(self, layer: Layer):
        """
        Adds a layer to the text object

        # TODO: Make it work with shadowed layers
        # TODO: write down what layer must satisfy
        """
        assert isinstance(layer, Layer), 'Layer expected, got {!r}'.format(type(layer))

        name = layer.name

        assert name not in self.__dict__, 'this Text object already has a layer with name {!r}'.format(name)

        if layer.text_object is None:
            layer.text_object = self
        else:
            assert layer.text_object is self, \
                "can't add layer {!r}, this layer is already bound to another Text object".format(name)

        if layer.parent:
            assert layer.parent in self.__dict__, 'Cant add a layer "{layer}" before adding its parent "{parent}"'.format(
                parent=layer.parent, layer=layer.name)

        if layer.enveloping:
            assert layer.enveloping in self.__dict__, "can't add an enveloping layer before adding the layer it envelops"

        if name in Text.methods:
            self._shadowed_layers[name] = layer
        else:
            self.__dict__[name] = layer

    def pop_layer(self, name: str,  cascading: bool = True, default=Ellipsis) -> Union[Layer, Any]:
        """
        Removes a layer from the text object together with the layers that are computed from it by default.

        If the flag cascading is set all descendant layers are computed first and removed together with the layer.
        If the flag is false only the layer is removed. This does not corrupt derivative layers, as spans of each
        layer are independent form other layers.

        Returns popped layer if the layer is present in the text object. If the layer is not found default is
        returned if given, otherwise KeyError is raised.
        """
        if name not in self.layers and default is Ellipsis:
            raise KeyError('{layer!r} is not a valid layer in this Text object'.format(layer=name))

        if not cascading:
            result = self.__dict__.pop(name, None)
            return result if result else self._shadowed_layers.pop(name, None)

        # Find all dependencies between layers. The implementations is complete overkill.
        # However, further optimisation is not worth the time.
        relations = set()
        for layer_name, layer in self.__dict__.items():
            relations.update((b, a) for a, b in [
                (layer_name, layer.parent),
                (layer_name, layer.enveloping)] if b is not None and a != b
                             )

        g = nx.DiGraph()
        g.add_edges_from(relations)
        g.add_nodes_from(self.__dict__.keys())

        to_delete = nx.descendants(g, name)

        result = self.__dict__.pop(name, None)
        result = result if result else self._shadowed_layers.pop(name, None)
        for name in to_delete:
            if not self.__dict__.pop(name):
                self._shadowed_layers.pop(name, None)

        return result

    def tag_layer(self, layer_names: Union[str, Sequence[str]] = ('morph_analysis', 'sentences'), resolver=None) -> 'Text':
        raise NotImplementedError('(!) The NLP pipeline is not available in estnltk-light. Please use the full EstNLTK package for the pipeline.')

    def analyse(self, t: str, resolver=None) -> 'Text':
        raise NotImplementedError('(!) The NLP pipeline is not available in estnltk-light. Please use the full EstNLTK package for the pipeline.')

    @staticmethod
    def topological_sort(layers: Mapping[str, Layer]) -> List[Layer]:
        """
        Returns a list of all layers of the given dict of layers in order of dependencies and layer names.
        The order is uniquely determined.

        layers: Mapping[str, Layer]
            maps layer name to layer
        """
        layer_list = sorted(layers.values(), key=lambda l: l.name)
        layer_name_set = set([l.name for l in layer_list])
        sorted_layers = []
        sorted_layer_names = set()
        while layer_list:
            success = False
            for layer in layer_list:
                if (layer.parent is None or layer.parent in sorted_layer_names) and \
                        (layer.enveloping is None or layer.enveloping in sorted_layer_names):
                    sorted_layers.append(layer)
                    sorted_layer_names.add(layer.name)
                    layer_list.remove(layer)
                    success = True
                    break
            if layer_list and not success:
                # If we could not remove any layer from layer_list, then the data 
                # is malformed: contains unknown dependencies. 
                # Add layers with unknown dependencies to the end of the sorted list.
                for layer in layer_list:
                    if (layer.parent is not None and layer.parent not in layer_name_set) or \
                         (layer.enveloping is not None and layer.enveloping not in layer_name_set):
                        sorted_layers.append(layer)
                        sorted_layer_names.add(layer.name)
                        layer_list.remove(layer)
                        break
        return sorted_layers

    def list_layers(self) -> List[Layer]:
        """
        Returns a list of all layers of this text object in order of dependencies and layer names.
        The order is uniquely determined.
        """
        return self.topological_sort(self.__dict__)

    def diff(self, other):
        """
        Returns a brief diagnostic message that explains why two Text objects are different.

        # TODO: Make it nicer for the Jupyter environment
        # TODO: Use memo dict to break infinite loops
        # TODO: Think what is the right reasoning to give out for various occasions

        # BUGS:
          - Loops with recursive self-references.
          - Layer comparison ignores shadowed layers.
        """
        if self is other:
            return None
        if not isinstance(other, Text):
            return 'Not a Text object.'
        if self.text != other.text:
            return 'The raw text is different.'
        if set(self.__dict__) != set(other.layers):
            return 'Different layer names: {} != {}'.format(set(self.__dict__), set(other.layers))
        if self.meta != other.meta:
            return 'Different metadata.'
        for layer_name in self.__dict__:
            difference = self.__dict__[layer_name].diff(other[layer_name])
            if difference:
                return difference
        return None


