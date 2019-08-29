import html
from collections import defaultdict
from typing import MutableMapping, List, Sequence
import pandas
import networkx as nx

from estnltk.layer.layer import Layer


class Text:
    def __init__(self, text: str = None) -> None:
        self._text = text  # type: str
        self._layers = {}  # type: MutableMapping[str, Layer]
        self.meta = {}  # type: MutableMapping
        self.layers_to_attributes = defaultdict(list)  # type: MutableMapping[str, List[str]]
        self.base_to_dependant = defaultdict(list)  # type: MutableMapping[str, List[str]]
        self.enveloping_to_enveloped = defaultdict(list)  # type: MutableMapping[str, List[str]]
        self._setup_structure()

    attribute_mapping_for_spans = {'lemma': 'morph_analysis',
                                   'root': 'morph_analysis',
                                   'root_tokens': 'morph_analysis',
                                   'ending': 'morph_analysis',
                                   'clitic': 'morph_analysis',
                                   'form': 'morph_analysis',
                                   'partofspeech': 'morph_analysis'}
    attribute_mapping_for_enveloping_spans = attribute_mapping_for_spans

    @property
    def layers(self):
        return dict(self._layers)

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
        if 'tokens' in self._layers and t != 'all':
            del self.tokens
        return self

    @staticmethod
    def list_registered_layers():
        return DEFAULT_RESOLVER.list_layers()

    def list_layers(self) -> List[Layer]:
        """
        Returns a list of all layers of this text object in order of dependences and layer names.
        The order is uniquely determined.
        """
        layer_list = sorted(self._layers.values(), key=lambda l: l.name)
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

    def setup_structure(self):
        return self._setup_structure()

    def _setup_structure(self):
        pairs = []
        attributes = []

        # we can go from enveloping to enveloped
        for frm, tos in self.enveloping_to_enveloped.items():
            for to in tos:
                pairs.append((frm, to))

        # we can go from base to dependant and back
        for frm, tos in self.base_to_dependant.items():
            for to in tos:
                pairs.append((frm, to))
                pairs.append((to, frm))

        self.layers_to_attributes = defaultdict(list)
        for name, layer in self._layers.items():
            self.layers_to_attributes[name] = layer.attributes

        # we can go from layer to attribute
        for frm, tos in self.layers_to_attributes.items():
            for to in tos:
                attributes.append((frm, frm + '.' + to))

        self.pairs = pairs
        g = nx.DiGraph()
        g.add_edges_from(pairs)
        g.add_edges_from(attributes)
        g.add_nodes_from(self._layers.keys())

        self._g = g

    @property
    def attributes(self):
        res = defaultdict(list)
        for k, layer in self._layers.items():
            for attrib in layer.__getattribute__('attributes'):
                res[attrib].append(k)

        return res

    def __setattr__(self, name, value):
        if name == 'meta' and not isinstance(value, dict):
            raise ValueError('meta must be of type dict')
        super.__setattr__(self, name, value)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError
        if item in self._layers.keys():
            return self._layers[item]  # .spans

        attributes = self.__getattribute__('attributes')
        if len(attributes[item]) == 1:
            return getattr(self._layers[attributes[item][0]], item)

        return self.__getattribute__(item)

    def add_layer(self, layer: Layer):
        assert isinstance(layer, Layer), 'Layer expected, got {!r}'.format(type(layer))

        name = layer.name

        assert name not in self._layers, 'this Text object already has a layer with name {!r}'.format(name)

        if layer.text_object is None:
            layer.text_object = self
        else:
            assert layer.text_object is self, \
                "can't add layer {!r}, this layer is already bound to another Text object".format(name)

        if layer.parent:
            assert layer.parent in self._layers.keys(), 'Cant add a layer "{layer}" before adding its parent "{parent}"'.format(
                parent=layer.parent, layer=layer.name)

        if layer.enveloping:
            assert layer.enveloping in self._layers.keys(), "can't add an enveloping layer before adding the layer it envelops"

        #
        # ASSERTS DONE,
        # Let's feel free to change the layer we have been handed.
        #

        if layer.parent:
            layer._base = self._layers[layer.parent]._base

        if layer.parent:
            # This is a change to accommodate pruning of the layer tree.
            # self.base_to_dependant[layer.parent].append(name)
            self.base_to_dependant[layer._base].append(name)

        if layer.enveloping:
            self.enveloping_to_enveloped[name].append(layer.enveloping)

        self._layers[name] = layer

        setattr(self, layer.name, layer)

        self._setup_structure()

    def _path_exists(self, frm, to):
        paths = self._get_all_paths(frm, to)
        assert len(paths) in (0, 1), 'ambiguous path to attribute {}'.format(to)

        try:
            res = len(paths) == 1 or nx.has_path(self._g, frm, to)
        except nx.NodeNotFound:
            res = False
            # raise KeyError('No path found {} {}'.format(frm, to))
        return res

    def _get_all_paths(self, frm, to):
        attributes = self._get_relevant_attributes()
        tos = self._get_attribute_node_names(attributes, to)
        paths = self._get_relevant_paths(frm, tos)
        return paths

    def _get_path(self, frm, to):
        if self._path_exists(frm, to):
            paths = self._get_all_paths(frm, to)
            try:
                return paths[0]
            except IndexError:
                res = nx.shortest_path(self._g, frm, to)
                return res

    def _get_relevant_paths(self, frm, tos):
        paths = []
        for to_ in tos:
            paths.extend(list(nx.all_simple_paths(self._g, frm, to_)))
        return paths

    def _get_relevant_attributes(self):
        attributes = []
        for i in self.layers_to_attributes.values():
            attributes.extend(i)
        return attributes

    def _get_attribute_node_names(self, attributes, to):
        tos = []
        if to in attributes:
            for k, v in self.layers_to_attributes.items():
                for i in v:
                    if i == to:
                        tos.append(k + '.' + i)
        return tos

    def __getitem__(self, item):
        # always returns layer
        return self._layers[item]

    def __delattr__(self, item):
        assert item in self._layers, '{item} is not a valid layer in this Text object'.format(item=item)

        # find all dependencies between layers
        relations = set()
        for layer_name, layer in self._layers.items():
            relations.update((b, a) for a, b in [
                (layer_name, layer.parent),
                (layer_name, layer._base),
                (layer_name, layer.enveloping)] if b is not None and a != b
                             )

        g = nx.DiGraph()
        g.add_edges_from(relations)
        g.add_nodes_from(self._layers.keys())

        to_delete = nx.descendants(g, item)
        to_delete.add(item)

        for item in to_delete:
            self._layers.pop(item)
            super().__delattr__(item)

        self._setup_structure()

    def diff(self, other):
        if not isinstance(other, Text):
            return 'Not a Text object.'
        if self.text != other.text:
            return 'The raw text is different.'
        if set(self._layers) != set(other.layers):
            return 'Different layer names: {} != {}'.format(set(self._layers), set(other.layers))
        if self.meta != other.meta:
            return 'Different metadata.'
        for layer_name in self._layers:
            difference = self._layers[layer_name].diff(other.layers[layer_name])
            if difference:
                return difference
        return None

    def __eq__(self, other):
        if self is other:
            return True
        return not self.diff(other)

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
        if self._layers:
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
                layer = self._layers.get(layer_name)
                if layer is not None:
                    layers.append(layer)
            for layer_name in sorted(self._layers):
                if layer_name not in presort:
                    layers.append(self._layers[layer_name])

            layer_table = pandas.DataFrame()
            for layer in layers:
                layer_table = layer_table.append(layer.metadata())
            layer_table = layer_table.to_html(index=False, escape=False)
            return '\n'.join((table, layer_table))
        return table


from .resolve_layer_dag import DEFAULT_RESOLVER
