import html
from collections import defaultdict
from typing import MutableMapping, List, Sequence
import pandas
import networkx as nx

from estnltk.layer.layer import Layer


class Text:
    __slots__ = ['_text', '__dict__', 'meta']

    def __init__(self, text: str = None) -> None:
        self._text = text  # type: str
        self.meta = {}  # type: MutableMapping

    attribute_mapping_for_elementary_layers = {'lemma': 'morph_analysis',
                                               'root': 'morph_analysis',
                                               'root_tokens': 'morph_analysis',
                                               'ending': 'morph_analysis',
                                               'clitic': 'morph_analysis',
                                               'form': 'morph_analysis',
                                               'partofspeech': 'morph_analysis'}
    attribute_mapping_for_enveloping_layers = attribute_mapping_for_elementary_layers

    @property
    def layers(self):
        return dict(self.__dict__)

    def set_text(self, text: str):
        assert self._text is None, "raw text has already been set"
        self._text = text

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
            del self.tokens
        return self

    def list_layers(self) -> List[Layer]:
        """
        Returns a list of all layers of this text object in order of dependences and layer names.
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

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        if self._text is not None:
            raise AttributeError('raw text has already been set')
        if not isinstance(t, str):
            raise TypeError('')
        self._text = t

    @property
    def attributes(self):
        res = defaultdict(list)
        for k, layer in self.__dict__.items():
            for attrib in layer.attributes:
                res[attrib].append(k)

        return res

    def __setattr__(self, name, value):
        if name == 'meta' and not isinstance(value, dict):
            raise ValueError('meta must be of type dict')
        super.__setattr__(self, name, value)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        attributes = self.__getattribute__('attributes')
        if len(attributes[item]) == 1:
            return getattr(self.__dict__[attributes[item][0]], item)

        return self.__getattribute__(item)

    def add_layer(self, layer: Layer):
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

        self.__dict__[name] = layer

    def __getitem__(self, item):
        # always returns layer
        return self.__dict__[item]

    def _delete_layer(self, name):
        assert name in self.__dict__, '{item} is not a valid layer in this Text object'.format(item=name)

        # find all dependencies between layers
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
        to_delete.add(name)

        for name in to_delete:
            self.__dict__.pop(name)

    def __delattr__(self, item):
        self._delete_layer(item)

    def __delitem__(self, key):
        self._delete_layer(key)

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
            difference = self.__dict__[layer_name].diff(other.layers[layer_name])
            if difference:
                return difference
        return None

    def __eq__(self, other):
        return self.diff(other) is None

    def __str__(self):
        if self._text is None:
            return 'Text()'
        return 'Text(text={self.text!r})'.format(self=self)

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        pandas.set_option('display.max_colwidth', -1)

        if self._text is None:
            table = '<h4>Empty Text object</h4>'
        else:
            text = self.text
            if len(text) > 10000:
                text = '{}\n\n<skipping {} characters>\n\n{}'.format(text[:8000],
                                                                     len(text)-9000,
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
