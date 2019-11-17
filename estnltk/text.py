import html
from copy import copy, deepcopy
from collections import defaultdict
from typing import MutableMapping, List, Sequence, Mapping, Set, Union, Any
from typing import DefaultDict
import pandas
import networkx as nx

from estnltk.layer.layer import Layer


class Text:
    # List of all methods for Text object
    methods: Set[str] = {
                            '_repr_html_',
                            'add_layer',
                            'analyse',
                            'attributes',
                            'pop_layer',
                            'diff',
                            'layers',
                            'list_layers',
                            'set_text',
                            'tag_layer'
                        } | {method for method in dir(object) if callable(getattr(object, method, None))}

    attribute_mapping_for_elementary_layers: Mapping[str, str] = {
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
        self.text: str
        super().__setattr__('text', text)
        self._shadowed_layers: Mapping[str, Layer]
        super().__setattr__('_shadowed_layers', {})
        self.meta: MutableMapping
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
        # Shallow copy of layers is enough for serialisation
        # But layers must be detached from text otherwise assembly fails
        state = {
            'text': self.text,
            'meta': self.meta,
            # Layers must be created in the topological order
            # TODO: test this in tests
            'layers': [copy(layer) for layer in self.list_layers()]
        }
        for layer in state['layers']:
            layer.text_object = None
        return state

    def __setstate__(self, state):
        # Initialisation is not guaranteed!
        # Bypass the text protection mechanism
        assert type(state['text']) == str, "'field 'text' must be of type str"
        super().__setattr__('text', state['text'])
        super().__setattr__('_shadowed_layers', {})
        self.meta = state['meta']
        for layer in state['layers']:
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
    def layers(self):
        """
        Returns the names of all layers of the text object

        # TODO: Currently, it returns a dict for backward compatibility
                Make it to the list of strings instead
        """
        return self.__dict__.keys() | self._shadowed_layers.keys()
        # return {**self.__dict__, **self._shadowed_layers}

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

    def set_text(self, text: str):
        """
        Deprecated duplicated functionality. Use text property!
        # TODO: To be removed
        """
        assert self.text is None, "raw text has already been set"
        self.text = text

    def tag_layer(self, layer_names: Sequence[str] = ('morph_analysis', 'sentences'), resolver=None) -> 'Text':
        if resolver is None:
            resolver = DEFAULT_RESOLVER
        for layer_name in layer_names:
            resolver.apply(self, layer_name)
        return self

    def analyse(self, t: str, resolver=None) -> 'Text':
        if resolver is None:
            resolver = DEFAULT_RESOLVER
        if t == 'segmentation':
            self.tag_layer(['paragraphs'], resolver)
        elif t == 'morphology':
            self.tag_layer(['morph_analysis'], resolver)
        elif t == 'syntax_preprocessing':
            self.tag_layer(['sentences', 'morph_extended'], resolver)
        elif t == 'all':
            self.tag_layer(['paragraphs', 'morph_extended'], resolver)
        else:
            raise ValueError("invalid argument: '" + str(t) +
                             "', use 'segmentation', 'morphology' or 'syntax' instead")
        if 'tokens' in self.__dict__ and t != 'all':
            self.pop_layer('tokens')
        return self

    def list_layers(self) -> List[Layer]:
        """
        Returns a list of all layers of this text object in order of dependencies and layer names.
        The order is uniquely determined.
        """
        layer_list = sorted(self.__dict__.values(), key=lambda l: l.name)
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

    def diff(self, other):
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

    def _repr_html_(self):
        pandas.set_option('display.max_colwidth', -1)

        if self.text is None:
            table = '<h4>Empty Text object</h4>'
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
        if self.__dict__:
            # create a list of layers preserving the order of registered layers
            # can be optimized
            layers = []
            presort = (
                'paragraphs',
                'sentences',
                'tokens',
                'compound_tokens',
                'normalized_words',
                'words',
                'morph_analysis',
                'morph_extended')
            for layer_name in presort:
                layer = self.__dict__.get(layer_name)
                if layer is not None:
                    layers.append(layer)
            for layer_name in sorted(self.__dict__):
                if layer_name not in presort:
                    layers.append(self.__dict__[layer_name])

            layer_table = pandas.DataFrame()
            for layer in layers:
                layer_table = layer_table.append(layer.metadata())
            layer_table = layer_table.to_html(index=False, escape=False)
            return '\n'.join((table, layer_table))
        return table


from .resolve_layer_dag import DEFAULT_RESOLVER
