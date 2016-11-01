import bisect
import collections
import keyword
from typing import *

import ipywidgets
import networkx as nx


def draw_graph(g):
    p = nx.drawing.nx_pydot.to_pydot(g)
    return ipywidgets.HTML(p.create_svg())



class Span:
    # __slots__ = ['_start', '_end', 'layer', '_attributes']

    def __init__(self, start: int = None, end: int = None, parent=None,  *, legal_attributes=None, **attributes) -> None:
        # Placeholder, set when span added to spanlist
        self.layer = None #type:Layer

        self.parent = parent

        if isinstance(start, int) and isinstance(end, int):
            assert start < end

            self._start = start
            self._end = end
            self.is_dependant = False


        #parent is a Span of dependant Layer
        elif parent is not None:
            assert isinstance(parent, Span)
            assert start is None
            assert end is None
            self.is_dependant = True

        # self._attributes = {}

        for k, v in attributes.items():
            if k in legal_attributes:
                self.__setattr__(k, v)
                # self._attributes[k] = v



    def mark(self, mark_layer):
        assert self.text_object.layers[mark_layer].parent == self.layer.name
        res = self.text_object.layers[mark_layer].add_span(
            Span(
                parent=self
            )
        )
        return res

    @property
    def start(self) -> int:
        if not self.is_dependant:
            return self._start
        else:
            return self.parent.start

    @property
    def end(self) -> int:
        if not self.is_dependant:
            return self._end
        else:
            return self.parent.end

    @property
    def text(self):
        return self.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        return self.layer.text_object



    def __getattr__(self, item):
        legal_attribute_names = self.__getattribute__('layer').__getattribute__('attributes')

        if item in legal_attribute_names:
            try:
                return self.__getattribute__(item)#get(item, None)
            except AttributeError:
                return None

        elif self.layer.text_object._path_exists(self.layer.name, item):
            #there exists an unambiguous path from this span to the target (attribute)
            target_layer_name  = self.text_object._get_path(self.layer.name, item)[-2]
            #siin on kala
            for i in self.text_object.layers[target_layer_name].spans:
                if i.__getattribute__('parent') == self:
                    return getattr(i, item)
                elif self.__getattribute__('parent')  == i:
                    return getattr(i, item)


        else:
            return self.__getattribute__('__class__').__getattribute__(self, item)


    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        try:
            return (self.start, self.end) == (other.start, other.end)
        except AttributeError:
            return False

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __str__(self):
        return 'Span({text})'.format(text=self.text)

    def __repr__(self):
        return str(self)


class AmbiguousSpan(Span):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class SpanList(collections.Sequence):
    def __init__(self,
                 layer=None,
                 ambiguous:bool=False) -> None:
        if ambiguous:
            self.spans = SpanList(layer=layer, ambiguous=False)
        else:
            self.spans = []  # type: List[AbstractSpan]

        self.layer = layer
        self.ambiguous = ambiguous
        self.parent = None #placeholder for ambiguous layer


    def add_span(self, span) -> None:



        if not self.ambiguous:
            span.layer = self.layer
            bisect.insort(self.spans, span)
            return span
        else:
            span.layer = self.layer

            # we should keep stuff in spanlists
            if span.parent:
                equality_check = lambda span1, span2: span1.parent == span2.parent
            elif isinstance(span.start, int) and isinstance(span.end, int):
                equality_check = lambda span1, span2: span1.start == span2.start and span1.end == span2.end
            else:
                raise NotImplementedError

            for spn_lst in self.spans:
                if equality_check(span, spn_lst[0]):
                    spn_lst.spans.append(span)
                    return spn_lst

            new = SpanList(layer=self.layer)
            new.add_span(span)
            self.spans.spans.append(new)
            new.parent = span.parent
            return new

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        assert isinstance(value, Layer) or value == None
        self._layer = value


    @property
    def start(self):
        return self.spans[0].start

    @property
    def end(self):
        return self.spans[-1].end

    @property
    def text(self):
        return [span.text for span in self.spans]

    def __iter__(self):
        yield from self.spans

    def __len__(self) -> int:
        return len(self.__getattribute__(
            'spans'
        ))

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __getattr__(self, item):
        layer = self.__getattribute__('layer') #type: Layer
        if item in layer.attributes:
            return [getattr(span, item) for span in self.spans]
        else:
            if item in self.__dict__:
                return self.__dict__[item]

            target = layer.text_object._resolve(
                layer.name, item, sofar = self
            )
            return target


    def __getitem__(self, idx: int) -> Span:

        res = SpanList()
        res.layer = self.layer
        wrapped = self.spans.__getitem__(idx)
        if isinstance(idx, int):
            return wrapped

        res.spans = wrapped
        res.ambiguous = self.ambiguous
        res.parent = self.parent

        return res

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        try:
            return (self.start, self.end) == (other.start, other.end)
        except AttributeError:
            return False

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __str__(self):
        return 'SpanList({spans})'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)


class Layer:
    def __init__(self,
                 name:str=None,
                 attributes=tuple(),
                 parent:str=None,
                 enveloping:str=None,
                 ambiguous:bool=None
                 ):
        assert not ((parent is not None) and (enveloping is not None)), 'Cant be derived AND enveloping'
        assert name is not None, 'Layer must have a name'
        self.name = name
        self.attributes = attributes
        self.parent = parent
        self.enveloping = enveloping

        self.spans = SpanList(layer=self, ambiguous=ambiguous)

        self.ambiguous = ambiguous


        #  placeholder, is set when `add_layer` is called on text object
        self.text_object = None # type:Text

    def from_dict(self, records):
        for record in records:
            self.add_span(Span(
                **record, legal_attributes=self.attributes
            ))

        return self

    def from_tuples(self, spans):
        return self.from_dict(
            [{'start':start,
                'end':end} for start,end in spans]
        )

    def add_span(self, span):
        return self.spans.add_span(span)

    def add_spans(self, spans):
        assert self.ambiguous or self.enveloping
        container = SpanList(layer=self)
        container.spans = spans
        return self.spans.add_span(
            container
        )


    def _resolve(self, target):
        if target in self.attributes:
            print('return attribute ', target)
        else:
            return self.text_object._resolve(self.name, target)

    def __getattr__(self, item):
        if item in self.__getattribute__('attributes'):
            return item  # TODO!
        elif item in self.__getattribute__('__dict__').keys():
            return self.__getattribute__('__dict__')[item]
        else:
            return self.__getattribute__('_resolve')(item)

    def __getitem__(self, idx):
        res = self.spans.__getitem__(idx)
        return res

    def __str__(self):
        return 'Layer(name={self.name}, spans={self.spans})'.format(self=self)


class Text:
    def __init__(self, text):

        self._text = text
        self.layers = {}
        self.layers_to_attributes = collections.defaultdict(list)
        self.base_to_dependant = collections.defaultdict(list)
        self.enveloping_to_enveloped = collections.defaultdict(list)

        self._setup_structure()

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
        res = []
        for i in self.layers.values():
            res.extend(i.attributes)
        return set(res)

    def __getattr__(self, item):
        if item in self.layers.keys():
            return self.layers[item].spans
        else:
            return self.__getattribute__(item)

    def add_layer(self, layer):
        name = layer.name
        attributes = layer.attributes

        assert name not in ['text'], 'Restricted for layer name'
        assert name.isidentifier() and not keyword.iskeyword(name), 'Layer name must be a valid python identifier'

        assert name not in self.layers.keys(), 'Layer with name {name} already exists'.format(name=name)

        if layer.parent:
            assert layer.parent in self.layers.keys(), 'Cant add a layer before adding its parent'

        if layer.enveloping:
            assert layer.enveloping in self.layers.keys(), 'Cant add an enveloping layer before adding the layer it envelops'

        self.layers_to_attributes[name] = attributes
        if layer.parent:
            self.base_to_dependant[layer.parent].append(name)


        if layer.enveloping:
            self.enveloping_to_enveloped[name].append(layer.enveloping)

        self.layers[name] = layer
        layer.text_object = self

        self._setup_structure()

    def _resolve(self, frm, to, sofar:SpanList = None):
        #must return the correct object
        #this method is supposed to centralize attribute access

        #if sofar is set, it must be a SpanList at point "frm" with a path to "to"
        #going down a level of enveloping layers adds a layer SpanLists



        GENERAL_KEYS = ['text', 'parent']
        if to in GENERAL_KEYS:
            if sofar:
                return sofar.__getattribute__(to)
            else:
                return self.layers[frm].spans.__getattribute__(to)


        path_exists = self._path_exists(frm, to)
        if (path_exists) and to in self.layers.keys():
            if frm in self.layers.keys():
                #from layer to its attribute
                if to in self.layers[frm].attributes  or (to in GENERAL_KEYS):
                    return getattr(self.layers[frm], to)


                #from enveloping layer to its direct descendant
                elif to == self.layers[frm].enveloping:
                    return sofar

                #from an enveloping layer to dependant layer (one step only, skipping base layer)
                elif self.layers[frm].enveloping == self.layers[to].parent:
                    if sofar is None:
                        sofar = self.layers[frm].spans

                    spans = []
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

                #from layer to strictly dependant layer
                elif frm == self.layers[to].parent:

                    sofar = self.layers[to].spans

                    spans = []
                    for i in sofar:
                        spans.append(i.parent)
                    res = SpanList(layer=self.layers[to])
                    res.spans = spans
                    return res


        #attribute access
        elif path_exists:

            path = self._get_path(frm, to)
            to_layer_name = path[-2]
            to_layer = self.layers[to_layer_name]
            assert  to_layer_name in self.layers.keys()


            #attributes of a (direct) dependant
            if to_layer.parent == frm:
                res = []
                if sofar:
                    for i in to_layer.spans:
                        if i.parent in sofar.spans:
                            res.append(getattr(i, to))
                    return res
                else:
                    print('nope')


            #attributes of an (directly) enveloped object
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

            if (to_layer.parent == from_layer.enveloping):
                if sofar:
                    res = []
                    for i in sofar.spans:
                        print('iiiii', i, i.layer.name, to, i.__getattr__(to))
                        res.append(i.__getattr__(to))
                    return res
                else:
                    print('asdasdasdasdas')
                    res = []
                    for i in to_layer.spans:
                        res.append(
                            i.__getattr__(to)
                        )
                    return res

                # attributes of a (direct) parent
            # if to in self.layers[self.layers[frm].parent].attributes:
            #     if sofar:
            #         print('asdasd')
            #     else:
            #         print('123124')


        raise NotImplementedError('{} -> {} not implemented'.format(frm, to) +
                                  (' but path exists' if path_exists else ' - path does not exist')
                                  )


    def _path_exists(self, frm, to):
        paths = self._get_all_paths(frm, to)

        try:
            # should never happen
            assert len(list(nx.all_simple_paths(self._g, frm, to))) == 1, 'ambiguous path'
        except nx.NetworkXError:
            pass

        assert len(paths) in (0, 1), 'ambiguous path to attribute {}'.format(to)

        try:
            res = len(paths) == 1 or nx.has_path(self._g, frm, to)
        except nx.NetworkXError:
            raise KeyError
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

    def _draw_graph(self):
        return draw_graph(self._g)

    def __delattr__(self, item):
        if item in self.layers.keys():

            layer = self.layers[item]

            if layer.parent or layer.enveloping:
                raise NotImplementedError('deleting base or envleoping layers not implemented')

            del self.layers[item]
            del self.layers_to_attributes[item]
            self._setup_structure()
        else:
            raise NotImplementedError('deleting attributes not implemented')



    def __str__(self):
        return 'Text(text="{self.text}")'.format(self=self)


from estnltk.legacy.text import Text as OldText
#

def words_sentences(text):
    old = OldText(text)
    old.sentences
    old.words
    old.paragraphs


    new = Text(text)
    words = Layer(name='words').from_dict([{
        'start':start,
        'end':end
                                           } for start, end in old.spans('words')])

    new.add_layer(words)


    old_sentences = old.split_by('sentences')
    sentences = Layer(enveloping='words', name='sentences')
    i = 0
    new_sentences = []
    for sentence in old_sentences:
        sent = []
        for word in sentence.words:
            sent.append(words[i])
            i += 1
        new_sentences.append(sent)


    for sentence in new_sentences:
        sentences.add_spans(sentence)
    new.add_layer(sentences)

    morf_attributes = ['form', 'root_tokens', 'clitic', 'partofspeech', 'ending', 'root', 'lemma']
    #
    dep = Layer(name='morf_analysis',
                parent='words',
                ambiguous=True,
                attributes=morf_attributes
                )
    new.add_layer(dep)

    for word, analysises in zip(new.words, old.analysis):
        for analysis in analysises:
            m = word.mark('morf_analysis')
            for attr in morf_attributes:
                setattr(m, attr, analysis[attr])
    return new


