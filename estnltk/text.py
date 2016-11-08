import bisect
import keyword
# noinspection PyUnresolvedReferences
import collections
from typing import *

# noinspection PyPackageRequirements
import ipywidgets
# noinspection PyPackageRequirements
import networkx as nx


def draw_graph(g):
    p = nx.drawing.nx_pydot.to_pydot(g)
    return ipywidgets.HTML(p.create_svg())


class Span:
    # __slots__ = ['_start', '_end', 'layer', '_attributes']

    def __init__(self, start: int = None, end: int = None, parent=None,  *, legal_attributes=None, **attributes) -> None:
        # Placeholder, set when span added to spanlist
        self.layer = None #type:Layer

        self.parent = parent #type: Span

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
            self._base = parent._base

        if not self.is_dependant:
            self._base = self

        for k, v in attributes.items():
            if k in legal_attributes:
                self.__setattr__(k, v)



    def mark(self, mark_layer: str) -> 'Span':
        base_layer = self.text_object.layers[mark_layer] #type: Layer
        parent = base_layer.parent

        assert  parent == self.layer.name, "Expected '{self.layer.name}' got '{parent}'".format(self=self, parent=parent)
        res = base_layer.add_span(
            Span(
                # parent=self
                parent = self._base #this is the base span
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
                return self.__getattribute__(item)
            except AttributeError:
                return None

        elif item == getattr(self.layer, 'parent', None):
            return self.parent

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
        legal_attribute_names = self.__getattribute__('layer').__getattribute__('attributes')

        mapping = {}

        for k in legal_attribute_names:
            mapping[k] = self.__getattribute__(k)


        return 'Span({text}, {attributes})'.format(text=self.text, attributes=mapping)

    def __repr__(self):
        return str(self)

class SpanList(collections.Sequence):
    def __init__(self,
                 layer=None,
                 ambiguous:bool=False) -> None:
        if ambiguous:
            self.spans = SpanList(layer=layer, ambiguous=False)  #type: Union[List[Span], SpanList]
        else:
            self.spans = []  #type: Union[List[Span], SpanList]

        self._layer = layer
        self.ambiguous = ambiguous
        self.parent = None #placeholder for ambiguous layer
        self._base = None  #placeholder for dependant layer


    def add_span(self, span:Span) -> Span:
        #the assumption is that this method is called by Layer.add_span
        if not self.ambiguous:
            span.layer = self.layer
            bisect.insort(self.spans, span)
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
                    break
            else:
                new = SpanList(layer=self.layer)
                new.add_span(span)
                bisect.insort(self.spans.spans, new)
                new.parent = span.parent


        return span

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        assert isinstance(value, Layer) or value is None
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
        elif item in self.__dict__.keys():
            return self.__dict__[item]

        elif item == getattr(self.layer, 'parent', None):
            return self.parent

        else:
            if item in self.__dict__:
                return self.__dict__[item]

            target = layer.text_object._resolve(layer.name, item, sofar = self)
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
        return 'SL[{spans}]'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)


class Layer:
    def __init__(self,
                 name:str=None,
                 attributes:Union[Tuple, List]=tuple(),
                 parent:str=None,
                 enveloping:str=None,
                 ambiguous:bool=None
                 ):
        assert not ((parent is not None) and (enveloping is not None)), 'Cant be derived AND enveloping'
        assert name is not None, 'Layer must have a name'

        #name of the layer
        self.name = name

        #list of legal attribute names for the layer
        self.attributes = attributes

        #the name of the parent layer.
        self.parent = parent


        #has this layer been added to a text object?
        self._bound = False

        #marker for creating a lazy layer
        #used in Text.add_layer to check if additional work needs to be done
        self._is_lazy = False

        self._base = name if ((not enveloping) and (not parent)) else None #This is a placeholder for the base layer.
        #_base is None if parent is None
        #_base is self.name if ((not self.enveloping) and (not self.parent))
        #_base is parent._base otherwise
        #We can't assign the value yet, because we have no access to the parent layer
        #The goal is to swap the use of the "parent" attribute to the new "_base" attribute for all
        #layer inheritance purposes. As the idea about new-style text objects has evolved, it has been decided that
        #it is more sensible to keep the tree short and pruned. I'm hoping to avoid a rewrite though.

        #the name of the layer this class envelops
        #sentences envelop words
        #paragraphs envelop sentences
        #...
        self.enveloping = enveloping

        #Container for spans
        self.spans = SpanList(layer=self, ambiguous=ambiguous)

        #boolean for if this is an ambiguous layer
        #if True, add_span will behave differently and add a SpanList instead.
        self.ambiguous = ambiguous #type: bool

        #placeholder. is set when `add_layer` is called on text object
        self.text_object = None # type:Text

    def from_dict(self, records):
        if self.parent is not None and not self._bound:
            self._is_lazy = True
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

    def add_span(self, span: Span) -> Span:
        return self.spans.add_span(span)

    def add_spans_to_enveloping(self, spans):
        spanlist = SpanList(
            layer=self
        )
        spanlist.spans = spans
        bisect.insort(self.spans.spans, spanlist)

    def add_spans(self, spans:List[Span]) -> List[Span]:
        assert self.ambiguous or self.enveloping
        res = []
        for span in spans:
            res.append(self.add_span(span))
        return res


    def _resolve(self, target):
        if target in self.attributes:
            print('return attribute ', target)
        else:
            return self.text_object._resolve(self.name, target)

    def __getattr__(self, item):
        if item in self.__getattribute__('__dict__').keys():
            return self.__getattribute__('__dict__')[item]
        elif item in self.__getattribute__('attributes'):
            return self.spans.__getattr__(item)
        else:
            return self.__getattribute__('_resolve')(item)

    def __getitem__(self, idx):
        res = self.spans.__getitem__(idx)
        return res

    def __str__(self):
        return 'Layer(name={self.name}, spans={self.spans})'.format(self=self)


def _get_span_by_start_and_end(spans:SpanList, start:int, end:int) -> Span:
    for span in spans:
        if span.start == start and span.end == end:
            return span
    return None


class Text:
    def __init__(self, text:str):

        self._text = text
        self.layers = {} # type: MutableMapping[str, Layer]
        self.layers_to_attributes = collections.defaultdict(list)  # type: MutableMapping[str, List[str]]
        self.base_to_dependant = collections.defaultdict(list) # type: MutableMapping[str, List[str]]
        self.enveloping_to_enveloped = collections.defaultdict(list)  # type: MutableMapping[str, List[str]]

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

    def add_layer(self, layer:Layer):
        name = layer.name
        attributes = layer.attributes


        ##
        ## ASSERTS
        ##

        assert not layer._bound
        assert name not in ['text'], 'Restricted for layer name'
        assert name.isidentifier() and not keyword.iskeyword(name), 'Layer name must be a valid python identifier'
        assert name not in self.layers.keys(), 'Layer with name {name} already exists'.format(name=name)


        if layer.parent:
            assert layer.parent in self.layers.keys(), 'Cant add a layer before adding its parent'

        if layer.enveloping:
            assert layer.enveloping in self.layers.keys(), 'Cant add an enveloping layer before adding the layer it envelops'

        ##
        ## ASSERTS DONE,
        ## Let's feel free to change the layer we have been handed.
        ##


        if layer.parent:
            layer._base = self.layers[layer.parent]._base

        self.layers_to_attributes[name] = attributes


        if layer.parent:
            ## This is a change to accommodate pruning of the layer tree.
            # self.base_to_dependant[layer.parent].append(name)
            self.base_to_dependant[layer._base].append(name)


        if layer.enveloping:
            self.enveloping_to_enveloped[name].append(layer.enveloping)


        if layer._is_lazy:
            #this means the layer might already have spans, and the spans might need to have their parents reset
            if layer.parent is not None:
                for span in layer:
                    span.parent = _get_span_by_start_and_end(
                        self.layers[layer._base].spans,
                        span.start,
                        span.end
                    )
                    span._base = span.parent

        self.layers[name] = layer
        layer.text_object = self
        layer._bound = True


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
        if path_exists and to in self.layers.keys():
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
                elif frm == self.layers[to]._base:

                    # if sofar is None:
                    sofar = self.layers[to].spans

                    spans = []
                    for i in sofar:
                        spans.append(i.parent)
                    res = SpanList(layer=self.layers[to])
                    res.spans = spans
                    return res

                # #from layer to direct parent layer
                # elif to == self.layers[frm].parent:
                #     if sofar is None:
                #         sofar = self.layers[frm].spans
                #
                #     spans = []
                #     for i in sofar:
                #         spans.append(i.parent)
                #     res = SpanList(layer=self.layers[to])
                #     res.spans = spans
                #     return res
                #


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

            if to_layer.parent == from_layer.enveloping:
                if sofar:
                    res = []
                    for i in sofar.spans:
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

        raise NotImplementedError('{} -> {} not implemented'.format(frm, to) +
                                  (' but path exists' if path_exists else ' - path does not exist')
                                  )


    def _path_exists(self, frm, to):
        paths = self._get_all_paths(frm, to)
        assert len(paths) in (0, 1), 'ambiguous path to attribute {}'.format(to)

        try:
            res = len(paths) == 1 or nx.has_path(self._g, frm, to)
        except nx.NetworkXError:
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

    def _draw_graph(self):
        return draw_graph(self._g)

    def __delattr__(self, item):
        raise NotImplementedError('deleting not implemented')

        # if item in self.layers.keys():
        #
        #     layer = self.layers[item]
        #
        #     if layer.parent or layer.enveloping:
        #         raise NotImplementedError('deleting base or envleoping layers not implemented')
        #
        #     del self.layers[item]
        #     del self.layers_to_attributes[item]
        #     self._setup_structure()
        # else:
        #     raise NotImplementedError('deleting attributes not implemented')



    def __str__(self):
        return 'Text(text="{self.text}")'.format(self=self)


from estnltk.legacy.text import Text as OldText
#

def words_sentences(text):
    old = OldText(text)

    # noinspection PyStatementEffect
    old.sentences
    # noinspection PyStatementEffect
    old.words
    # noinspection PyStatementEffect
    old.paragraphs


    new = Text(text)
    words = Layer(name='words').from_dict([{
        'start':start,
        'end':end
                                           } for start, end in old.spans('words')])

    new.add_layer(words)


    old_sentences = old.split_by('sentences')
    sentences = Layer(enveloping='words', name='sentences')
    new.add_layer(sentences)

    #TODO fix dumb manual loop
    i = 0
    new_sentences = []
    for sentence in old_sentences:
        sent = []
        for _ in sentence.words:
            sent.append(words[i])
            i += 1
        new_sentences.append(sent)



    for sentence in new_sentences:
        sentences.add_spans_to_enveloping(sentence)


    morf_attributes = ['form', 'root_tokens', 'clitic', 'partofspeech', 'ending', 'root', 'lemma']

    dep = Layer(name='morf_analysis',
                parent='words',
                ambiguous=True,
                attributes=morf_attributes
                )
    new.add_layer(dep)

    for word, analysises in zip(new.words, old.analysis):
        assert isinstance(word, Span)
        for analysis in analysises:
            m = word.mark('morf_analysis')
            assert isinstance(m, Span), 'Was hoping for Span, found {}'.format(type(m).__name__)


            for attr in morf_attributes:
                setattr(m, attr, analysis[attr])
    return new


