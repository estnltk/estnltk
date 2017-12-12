import keyword
from bisect import bisect_left
from collections import defaultdict
from typing import MutableMapping, Union, List, Sequence
import pandas
import networkx as nx

from .layer import Layer
from .spans import Span, SpanList


def _get_span_by_start_and_end(spans: SpanList, start: int=None, end: int=None, span: Span=None) -> Union[Span, None]:
    if span:
        i = bisect_left(spans, span)
    else:
        i = bisect_left(spans, Span(start=start, end=end))
    if i != len(spans):
        return spans[i]
    return None


class Text:
    def __init__(self, text: str) -> None:
        self._text = text  # type: str
        self.layers = {}  # type: MutableMapping[str, Layer]
        self.meta = {}  # type: MutableMapping
        self.layers_to_attributes = defaultdict(list)  # type: MutableMapping[str, List[str]]
        self.base_to_dependant = defaultdict(list)  # type: MutableMapping[str, List[str]]
        self.enveloping_to_enveloped = defaultdict(list)  # type: MutableMapping[str, List[str]]
        self._setup_structure()

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
        if 'tokens' in self.layers and t != 'all':
            del self.tokens
        return self

    @staticmethod
    def list_registered_layers():
        return DEFAULT_RESOLVER.list_layers()

    def list_layers(self) -> List[Layer]:
        """
        Returns a list of all layers of this text object in order of dependences.
        The order is not uniquely determined.
        """
        graph = nx.DiGraph()
        graph.add_nodes_from(self.layers)
        for layer_name, layer in self.layers.items():
            if layer.enveloping:
                graph.add_edge(layer.enveloping, layer_name)
            elif layer.parent:
                graph.add_edge(layer.parent, layer_name)
        names = nx.topological_sort(graph)
        return [self.layers[name] for name in names]

    @property
    def text(self):
        return self._text

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

        # we can go from layer to attribute
        for frm, tos in self.layers_to_attributes.items():
            for to in tos:
                attributes.append((frm, frm + '.' + to))

        self.pairs = pairs
        g = nx.DiGraph()
        g.add_edges_from(pairs)
        g.add_edges_from(attributes)
        g.add_nodes_from(self.layers.keys())

        self._g = g

    @property
    def attributes(self):
        res = defaultdict(list)
        for k, layer in self.layers.items():
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
        if item in self.layers.keys():
            return self.layers[item].spans
        else:
            attributes = self.__getattribute__('attributes')
            if len(attributes[item]) == 1:
                return getattr(self.layers[attributes[item][0]], item)

            return self.__getattribute__(item)

    def _add_layer(self, layer: Layer):
        name = layer.name
        attributes = layer.attributes

        #
        # ASSERTS
        #

        assert not layer._bound
        assert name not in ['text'], 'Restricted for layer name'
        assert name.isidentifier() and not keyword.iskeyword(name), 'Layer name must be a valid python identifier'
        assert name not in self.layers.keys(), 'Layer with name {name} already exists'.format(name=name)

        if layer.parent:
            assert layer.parent in self.layers.keys(), 'Cant add a layer "{layer}" before adding its parent "{parent}"'.format(
                parent=layer.parent, layer=layer.name)

        if layer.enveloping:
            assert layer.enveloping in self.layers.keys(), 'Cant add an enveloping layer before adding the layer it envelops'

        #
        # ASSERTS DONE,
        # Let's feel free to change the layer we have been handed.
        #

        if layer.parent:
            layer._base = self.layers[layer.parent]._base

        self.layers_to_attributes[name] = attributes

        if layer.parent:
            # This is a change to accommodate pruning of the layer tree.
            # self.base_to_dependant[layer.parent].append(name)
            self.base_to_dependant[layer._base].append(name)

        if layer.enveloping:
            self.enveloping_to_enveloped[name].append(layer.enveloping)

        if layer._is_lazy:
            # this means the layer might already have spans, and the spans might need to have their parents reset
            if layer.parent is not None:
                for span in layer:
                    span.parent = _get_span_by_start_and_end(
                        self.layers[layer._base].spans,
                        span=span
                    )
                    span._base = span.parent

        self.layers[name] = layer
        layer.text_object = self
        layer._bound = True

        self._setup_structure()

    def _resolve(self, frm, to, sofar: 'SpanList'=None) -> Union['SpanList', List[None]]:
        # must return the correct object
        # this method is supposed to centralize attribute access

        # if sofar is set, it must be a SpanList at point "frm" with a path to "to"
        # going down a level of enveloping layers adds a layer SpanLists

        GENERAL_KEYS = ['text', 'parent']
        if to in GENERAL_KEYS:
            if sofar:
                return sofar.__getattribute__(to)
            else:
                return self.layers[frm].spans.__getattribute__(to)

        path_exists = self._path_exists(frm, to)
        if path_exists and to in self.layers.keys():
            if frm in self.layers.keys():
                # from layer to its attribute
                if to in self.layers[frm].attributes or (to in GENERAL_KEYS):
                    return getattr(self.layers[frm], to)

                # from enveloping layer to its direct descendant
                elif to == self.layers[frm].enveloping:
                    return sofar

                # from an enveloping layer to dependant layer (one step only, skipping base layer)
                elif self.layers[frm].enveloping == self.layers[to].parent:
                    if sofar is None:
                        sofar = self.layers[frm].spans

                    spans = []

                    # path taken by text.sentences.lemma
                    if isinstance(sofar[0], SpanList):
                        for envelop in sofar:
                            enveloped_spans = []
                            for span in self.layers[to]:
                                if span.parent in envelop.spans:
                                    enveloped_spans.append(span)
                            if enveloped_spans:
                                sl = SpanList(layer=self.layers[frm])
                                sl.spans = enveloped_spans
                                spans.append(sl)

                        res = SpanList(layer=self.layers[to])
                        res.spans = spans
                        return res

                    # path taken by text.sentences[0].lemma
                    elif isinstance(sofar[0], Span):
                        enveloped_spans = []
                        for span in self.layers[to]:
                            if span.parent in sofar:
                                enveloped_spans.append(span)
                        if enveloped_spans:
                            sl = SpanList(layer=self.layers[frm])
                            sl.spans = enveloped_spans
                            spans.append(sl)

                        res = SpanList(layer=self.layers[to])
                        res.spans = spans
                        return res[0]

                # from layer to strictly dependant layer
                elif frm == self.layers[to]._base:

                    # if sofar is None:
                    sofar = self.layers[to].spans

                    spans = []
                    for i in sofar:
                        spans.append(i.parent)
                    res = SpanList(layer=self.layers[to])
                    res.spans = spans
                    return res

                # through an enveloped layer (enveloping-enveloping-target)
                elif to == self.layers[self.layers[frm].enveloping].enveloping:
                    return self._resolve(frm=self.layers[frm].enveloping,
                                         to=to,
                                         sofar=sofar
                                         )

        # attribute access
        elif path_exists:
            to_layer_name = self.attributes[to][0]
            path = self._get_path(frm, to_layer_name) + ['{}.{}'.format(to_layer_name, to)]

            to_layer = self.layers[to_layer_name]
            assert to_layer_name in self.layers.keys()

            if self.layers[frm] == to_layer:
                raise NotImplementedError('Seda ei tohiks juhtuda.')

            # attributes of a (direct) dependant
            if to_layer.parent == frm:
                res = []
                if sofar:
                    for i in to_layer.spans:
                        if i.parent in sofar.spans:
                            res.append(getattr(i, to))
                    return res

            # attributes of an (directly) enveloped object
            to_layer_name = path[-2]
            to_layer = self.layers[to_layer_name]
            from_layer_name = path[0]
            from_layer = self.layers[from_layer_name]

            if from_layer.enveloping == to_layer.name:
                if sofar:
                    res = []
                    for i in sofar.spans:
                        res.append(i.__getattr__(to))
                    return res
                else:
                    res = []
                    for i in to_layer.spans:
                        res.append(
                            i.__getattr__(to)
                        )
                    return res

            if to_layer.parent == from_layer.enveloping:
                if sofar:
                    res = []
                    for i in sofar.spans:
                        res.append(i.__getattr__(to))
                    return res
                else:
                    res = []
                    for i in to_layer.spans:
                        res.append(
                            i.__getattr__(to)
                        )
                    return res

        raise AttributeError('{} -> {} not implemented'.format(frm, to) +
                                  (' but path exists' if path_exists else ' - path does not exist')
                                  )

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

    def __setitem__(self, key, value):
        # always sets layer
        assert key not in self.layers.keys(), 'Re-adding a layer not implemented yet'
        assert value.name == key, 'Name mismatch between layer name and value'
        return self._add_layer(
            value
        )

    def __getitem__(self, item):
        # always returns layer
        return self.layers[item]

    def __delattr__(self, item):
        assert item in self.layers.keys(), '{item} is not a valid layer in this Text object'.format(item=item)

        # find all dependencies between layers
        relations = set()
        for layer_name, layer in self.layers.items():
            relations.update((b, a) for a, b in [
                (layer_name, layer.parent),
                (layer_name, layer._base),
                (layer_name, layer.enveloping)] if b is not None and a != b
                             )

        g = nx.DiGraph()
        g.add_edges_from(relations)
        g.add_nodes_from(self.layers.keys())

        to_delete = nx.descendants(g, item)
        to_delete.add(item)

        for item in to_delete:
            self.layers.pop(item)

        self._setup_structure()

    def diff(self, other):
        if not isinstance(other, Text):
            return 'Not a Text object.'
        if self.text != other.text:
            return 'The raw text is different.'
        if set(self.layers) != set(other.layers):
            return 'Different layer names: {} != {}'.format(set(self.layers), set(other.layers))
        if self.meta != other.meta:
            return 'Different metadata.'
        for layer_name in self.layers:
            difference = self.layers[layer_name].diff(other.layers[layer_name])
            if difference:
                return difference
        return None

    def __eq__(self, other):
        return not self.diff(other)

    def __str__(self):
        return 'Text(text="{self.text}")'.format(self=self)

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        pandas.set_option('display.max_colwidth', -1)

        rec = [{'text': self.text.replace('\n', '<br/>')}]
        table = pandas.DataFrame.from_records(rec)
        table = table.to_html(index=False, escape=False)
        if self.meta:
            table_meta = pandas.DataFrame.from_dict(self.meta, orient='index')
            table_meta = table_meta.to_html(header=False)
            table = '\n'.join((table, '<h4>Metadata</h4>', table_meta))
        if self.layers:
            # create a list of layers preserving the order of registered layers
            # can be optimized
            layers = []
            for layer_name in [
                                'paragraphs',
                                'sentences',
                                'tokens',
                                'compound_tokens',
                                'normalized_words',
                                'words',
                                'morph_analysis',
                                'morph_extended']:
                if layer_name in self.layers:
                    layers.append(self.layers[layer_name])
            for _, layer in self.layers.items():
                if layer not in layers:
                    layers.append(layer)

            layer_table = pandas.DataFrame()
            for layer in layers:
                layer_table = layer_table.append(layer.metadata())
            layer_table = layer_table.to_html(index=False, escape=False)
            return '\n'.join((table, layer_table))
        return table


from .resolve_layer_dag import DEFAULT_RESOLVER
