import bisect
import keyword
from typing import *

import ipywidgets
import collections
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

        self._attributes = {}

        for k, v in attributes.items():
            if k in legal_attributes:
                self._attributes[k] = v



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
            return self.__getattribute__('_attributes').get(item, None)
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
        return 'Span({self.text})'.format(self=self)

    def __repr__(self):
        return str(self)


class SpanList(collections.Sequence):
    def __init__(self,
                 layer=None) -> None:
        self.spans = []  # type: List[AbstractSpan]
        self.layer = layer

    def add_span(self, span) -> None:
        span.layer = self.layer
        bisect.insort(self.spans, span)
        return span

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
        return len(self.spans)

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __getattr__(self, item):
        layer = self.__getattribute__('layer') #type: Layer
        if item in layer.attributes:
            return [getattr(span, item) for span in self.spans]
        else:
            target = layer.text_object._resolve(
                layer.name, item, sofar = self
            )
            return target


    def __getitem__(self, idx: int) -> Span:

        res = SpanList()
        res.layer = self.layer
        wrapped = self.spans.__getitem__(idx)
        if isinstance(wrapped, Span):
            return wrapped
        res.spans = wrapped

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
                 name=None,
                 attributes=tuple(),
                 parent=None,
                 enveloping=None
                 ):
        assert not ((parent is not None) and (enveloping is not None)), 'Cant be derived AND enveloping'
        assert name is not None, 'Layer must have a name'
        self.name = name
        self.attributes = attributes
        self.parent = parent
        self.enveloping = enveloping

        self.spans = SpanList(layer=self)

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

    # def from_span_dict(self, dict):
    #     self.from_dict(dict)

    def add_span(self, span):
        return self.spans.add_span(span)

    def add_spans(self, spans):
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



        GENERAL_KEYS = ['text']
        path_exists = False
        if (self._path_exists(frm, to) or (to in GENERAL_KEYS)) and to in self.layers.keys():
            path_exists = True

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
        elif self._path_exists(frm, to):

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

            #attributes of a (direct) parent
            if to in self.layers[self.layers[frm].parent].attributes:
                if sofar:
                    print('asdasd')
                else:
                    print('123124')


        raise NotImplementedError('{} -> {} not implemented'.format(frm, to) +
                                  (' but path exists' if path_exists else ' - path does not exist')
                                  )


    def _path_exists(self, frm, to):
        attributes = []
        for i in self.layers_to_attributes.values():
            attributes.extend(i)
        try:
            # should never happen
            assert len(list(nx.all_simple_paths(self._g, frm, to))) == 1, 'ambiguous path'
        except nx.NetworkXError:
            pass
            # print('nxerror')

        tos = []
        if to in attributes:
            for k, v in self.layers_to_attributes.items():
                for i in v:
                    if i == to:
                        tos.append(k + '.' + i)
        paths = []
        for to_ in tos:
            paths.extend(list(nx.all_simple_paths(self._g, frm, to_)))
        assert len(paths) in (0, 1), 'ambiguous path to attribute {}'.format(to)

        try:
            res = len(paths) == 1 or nx.has_path(self._g, frm, to)
        except nx.NetworkXError:
            raise KeyError

        return res

    def _get_path(self, frm, to):
        if self._path_exists(frm, to):
            attributes = []

            for i in self.layers_to_attributes.values():
                attributes.extend(i)

            tos = []
            if to in attributes:
                for k, v in self.layers_to_attributes.items():
                    for i in v:
                        if i == to:
                            tos.append(k + '.' + i)
            paths = []
            for to_ in tos:
                paths.extend(list(nx.all_simple_paths(self._g, frm, to_)))

            return paths[0]

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
# ttt = 'Minu nimi on Uku, mis sinu nimi on?'
# t = Text(ttt)
# l = Layer(name='words')
#
# old = OldText(ttt)
# old.words
# l.from_dict(old.words)
# t.add_layer(l)
#
# print(t.words.name)
#
# l2 = Layer(parent='words', attributes=['test'], name='testlayer')
# t.add_layer(l2)
# print(t)
#
# for i in t.words:
#     i.mark('testlayer').test = 'asd'
#
# for i in t.testlayer:
#     print(i)

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
                attributes=morf_attributes)
    new.add_layer(dep)

    for word, analysises in zip(new.words, old.analysis):
        for analysis in analysises:
            m = word.mark('morf_analysis')
            for attr in morf_attributes:
                setattr(m, attr, analysis[attr])
            break #no ambiguous stuff yet
    return new


