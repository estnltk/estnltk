import bisect
import collections
import keyword
from collections import defaultdict
from typing import MutableMapping, Tuple,  Any, Union, List, Sequence
import pandas
import itertools
import networkx as nx


class Span:
    def __init__(self, start: int = None, end: int = None, parent=None,  *, layer=None, legal_attributes=None, **attributes) -> None:

        #this is set up first, because attribute access depends on knowing attribute names as earley as possible
        self._legal_attribute_names = legal_attributes
        self.is_dependant = parent is None

        # Placeholder, set when span added to spanlist
        self.layer = layer #type:Layer
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

            # The _base of a root-layer Span is the span itself.
            # So, if the parent is a root-layer the following must hold (self._base == self.parent == self.parent._base)
            # If the parent is not a root-layer Span, (self._base == self.parent._base)
            self._base = parent._base #type: Span

        else:
            assert 0, 'What?'


        if not self.is_dependant:
            self._base = self # type:Span

        for k, v in attributes.items():
            if k in legal_attributes:
                self.__setattr__(k, v)


    @property
    def legal_attribute_names(self) -> List[str]:
        if self.__getattribute__('_legal_attribute_names') is not None:
            return self.__getattribute__('_legal_attribute_names')
        else:
            return self.__getattribute__('layer').__getattribute__('attributes')

    def to_record(self, with_text=False) -> MutableMapping[str, Any]:
        return {**{k:self.__getattribute__(k) for k in list(self.legal_attribute_names) + (['text'] if with_text else [])},
                **{'start':self.start, 'end':self.end}}


    def mark(self, mark_layer: str) -> 'Span':
        base_layer = self.text_object.layers[mark_layer] #type: Layer
        parent = base_layer.parent

        assert  parent == self.layer.name, "Expected '{self.layer.name}' got '{parent}'".format(self=self, parent=parent)
        res = base_layer.add_span(
            Span(
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

    @start.setter
    def start(self, value: int):
        assert not self.is_bound, 'setting start is allowed on special occasions only'
        self._start = value


    @property
    def end(self) -> int:
        if not self.is_dependant:
            return self._end
        else:
            return self.parent.end

    @end.setter
    def end(self, value:int):
        assert not self.is_bound, 'setting end is allowed on special occasions only'
        self._end = value


    @property
    def text(self):
        return self.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        return self.layer.text_object


    def __getattr__(self, item):
        if item == 'text':
            return self.text

        if item in self.__getattribute__('legal_attribute_names'):
            try:
                return self.__getattribute__(item)
            except AttributeError:
                return None

        elif item == getattr(self.layer, 'parent', None):
            return self.parent

        elif self.layer is not None and self.layer.text_object is not None and  self.layer.text_object._path_exists(self.layer.name, item):
            #there exists an unambiguous path from this span to the target (attribute)


            looking_for_layer = False
            if item in self.layer.text_object.layers.keys():
                looking_for_layer = True
                target_layer_name = self.text_object._get_path(self.layer.name, item)[-1]
            else:
                target_layer_name = self.text_object._get_path(self.layer.name, item)[-2]



            for i in self.text_object.layers[target_layer_name].spans:
                if i.__getattribute__('parent') == self or self.__getattribute__('parent') == i:
                    if looking_for_layer:
                        return i
                    else:
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

    def __hash__(self):
        return hash((self.start, self.end, tuple(self.__getattribute__(i) for i in self.legal_attribute_names)))

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
            self.classes = {} # type: MutableMapping[Tuple[int, int], SpanList]
        else:
            self.spans = []  #type: Union[List[Span], SpanList]

        self._layer = layer
        self.ambiguous = ambiguous

        # placeholder for ambiguous layer
        self.parent = None # type:Union[Span, None]

        # placeholder for dependant layer
        self._base = None  # type:Union[Span, None]



    def get_equivalence(self, span):
        return self.classes.get((span.start, span.end), None)


    def get_attributes(self, items):
        r = []
        for x in zip(*[[i
                        if isinstance(i, (list, tuple))
                        else itertools.cycle([i]) for i in getattr(self, item)] for item in items]

                     ):

            quickbreak = all(isinstance(i, itertools.cycle) for i in x)

            tmp = []
            for pair in zip(*x):
                tmp.append(pair)
                if quickbreak:
                    break

            r.append(tmp)
        return r

    def to_record(self, with_text=False):
        return [i.to_record(with_text) for i in self.spans]

    def add_span(self, span:Span) -> Span:
        #the assumption is that this method is called by Layer.add_span
        if self.ambiguous:
            span.layer = self.layer
            target = self.get_equivalence(span)
            if target is not None:
                target.spans.append(span)
            else:
                new = SpanList(layer=self.layer)
                new.add_span(span)
                self.classes[(span.start, span.end)] = new

                bisect.insort(self.spans.spans, new)
                new.parent = span.parent

        else:
            span.layer = self.layer
            bisect.insort(self.spans, span)

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
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError
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


    def __getitem__(self, idx: int) -> Union[Span, 'SpanList']:

        wrapped = self.spans.__getitem__(idx)
        if isinstance(idx, int):
            return wrapped
        res = SpanList()
        res.layer = self.layer

        res.spans = wrapped
        res.ambiguous = self.ambiguous
        res.parent = self.parent

        return res

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)
        try:
            return (self.start, self.end) == (other.start, other.end)
        except AttributeError:
            return False

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __hash__(self):
        return hash((tuple(self.spans), self.ambiguous, self.parent))

    def __str__(self):
        return 'SL[{spans}]'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)


def whitelist_record(record, source_attributes):
    #the goal is to only keep the keys explicitly listed in source_attributes

    #record might be a dict:
    if isinstance(record, dict):
        res = {}
        for k in source_attributes:
            res[k] = record.get(k, None)
        return res

    else:
    #record might be nested
        return [whitelist_record(i, source_attributes) for i in record]


class Layer:
    def __init__(self,
                 name:str=None,
                 attributes:Union[Tuple, List]=tuple(),
                 parent:str=None,
                 enveloping:str=None,
                 ambiguous:bool=False
                 ) -> None:
        assert not ((parent is not None) and (enveloping is not None)), 'Cant be derived AND enveloping'

        assert name is not None, 'Layer must have a name'

        #name of the layer
        self.name = name

        #list of legal attribute names for the layer
        self.attributes = attributes

        #the name of the parent layer.
        self.parent = parent


        #has this layer been added to a text object
        self._bound = False

        #marker for creating a lazy layer
        #used in Text._add_layer to check if additional work needs to be done
        self._is_lazy = False

        self._base = name if (not enveloping) and (not parent) else None #This is a placeholder for the base layer.
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
        # and so on...
        self.enveloping = enveloping

        #Container for spans
        self.spans = SpanList(layer=self, ambiguous=ambiguous)

        #boolean for if this is an ambiguous layer
        #if True, add_span will behave differently and add a SpanList instead.
        self.ambiguous = ambiguous #type: bool

        #placeholder. is set when `_add_layer` is called on text object
        self.text_object = None # type:Text

    def from_records(self, records, rewriting=False) -> 'Layer':
        if self.parent is not None and not self._bound:
            self._is_lazy = True

        if self.ambiguous:
            if rewriting:
                self.spans = SpanList(ambiguous=True, layer=self)
                tmpspans = []
                for record_line in records:
                    if record_line is not None:
                        spns = SpanList(layer=self, ambiguous=False)
                        spns.spans = [Span(**{**record, **{'layer':self}}, legal_attributes=self.attributes) 
                                      for record in record_line]
                        tmpspans.append(spns)
                        self.spans.classes[(spns.spans[0].start, spns.spans[0].end)] = spns
                self.spans.spans = tmpspans
            else:
                for record_line in records:
                    self._add_spans([Span(**record, legal_attributes=self.attributes) for record in record_line])
        else:
            if rewriting:
                spns = SpanList(layer=self, ambiguous=False)
                spns.spans = [Span(**{**record, **{'layer': self}}, legal_attributes=self.attributes) for record in records if record is not None]

                self.spans = spns
            else:
                for record in records:
                    self.add_span(Span(
                        **record,
                        legal_attributes=self.attributes
                    ))
        return self

    def to_records(self, with_text=False):
        records = []

        for item in self.spans:
            records.append(item.to_record(with_text))

        return records


    def add_span(self, span: Span) -> Span:
        return self.spans.add_span(span)


    def rewrite(self, source_attributes: List[str], target_attributes: List[str], rules, **kwargs):
        assert 'name' in kwargs.keys(), '"name" must currently be an argument to layer'

        res = [whitelist_record(record, source_attributes + ['start', 'end']) for record in self.to_records(with_text='text' in source_attributes)]
        rewritten = [rules.rewrite(j) for j in res]
        resulting_layer = Layer(
            **kwargs,
            attributes=target_attributes,
            parent=self.name

        ).from_records(
            rewritten, rewriting=True
        )

        return resulting_layer

    def _add_spans_to_enveloping(self, spans):
        spanlist = SpanList(
            layer=self
        )
        spanlist.spans = spans
        bisect.insort(self.spans.spans, spanlist)
        return spanlist

    def _add_spans(self, spans:List[Span]) -> List[Span]:
        assert self.ambiguous or self.enveloping
        res = []
        for span in spans:
            res.append(self.add_span(span))
        return res


    def _resolve(self, target):
        if target in self.attributes:
            raise AssertionError('This path should not be taken')
        else:
            return self.text_object._resolve(self.name, target)

    def __getattr__(self, item):
        if item in {'_ipython_canary_method_should_not_exist_', '__getstate__'}:
            raise AttributeError
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

    def metadata(self):
        """
        Return DataFrame with layer metadata.
        """
        rec = [{'layer': self.name,
                'attributes': ', '.join(self.attributes),
                'parent': str(self.parent),
                'enveloping': str(self.enveloping),
                'ambiguous': str(self.ambiguous),
                'span count': str(len(self.spans.spans))}]
        return pandas.DataFrame.from_records(rec,
                                             columns=['layer', 'attributes',
                                                      'parent', 'enveloping',
                                                      'ambiguous', 'span count'])

    def _repr_html_(self):
        res = []
        if self.enveloping:
            if self.ambiguous:
                # TODO: _repr_html_ for enveloping ambiguous layers
                return repr(self)
            else:
                self.attributes
                for span in self.spans:
                    # html.escape(span[i].text) TODO?
                    t = ['<b>', self.text_object.text[span[0].start:span[0].end], '</b>']
                    for i in range(1, len(span)):
                        t.extend([self.text_object.text[span[i-1].end: span[i].start], '<b>', self.text_object.text[span[i].start:span[i].end], '</b>'])
                    t = ''.join(t)
                    res.append({'text': t, **{k:span.__getattribute__(k) for k in self.attributes}})
        else:
            if self.ambiguous:
                for record in self.to_records(True):
                    first = True
                    for rec in record:
                        if not first:
                            rec['text'] = ''
                        res.append(rec)
                        first = False
            else:
                res = self.to_records(True)
        df = pandas.DataFrame.from_records(res, columns=('text',)+tuple(self.attributes))
        pandas.set_option('display.max_colwidth', -1)
        table1 = self.metadata().to_html(index = False, escape=False)
        table2 = df.to_html(index = False, escape=False)
        return '\n'.join((table1, table2))

    def __eq__(self, other):
        if not isinstance(other, Layer):
            return False
        if self.name != other.name:
            return False
        if self.attributes != other.attributes:
            return False
        if self.ambiguous != other.ambiguous:
            return False
        if self.parent != other.parent:
            return False
        if self.enveloping != other.enveloping:
            return False
        if self.spans != other.spans:
            return False
        return True


def _get_span_by_start_and_end(spans:SpanList, start:int, end:int) -> Union[Span, None]:
    for span in spans:
        if span.start == start and span.end == end:
            return span
    return None


class Text:

    def __init__(self, text:str) -> None:

        self._text = text #type: str
        self.layers = {} # type: MutableMapping[str, Layer]
        self.layers_to_attributes = collections.defaultdict(list)  # type: MutableMapping[str, List[str]]
        self.base_to_dependant = collections.defaultdict(list) # type: MutableMapping[str, List[str]]
        self.enveloping_to_enveloped = collections.defaultdict(list)  # type: MutableMapping[str, List[str]]

        self._setup_structure()


    def tag_layer(self, layer_names:Sequence[str] = ('morph_analysis', 'sentences'), resolver=None) -> 'Text':
        if resolver is None:
            resolver = DEFAULT_RESOLVER
        for layer_name in layer_names:
            resolver.apply(self, layer_name)
        return self

    def analyse(self, t, resolver=None):
        if resolver is None:
            resolver = DEFAULT_RESOLVER
        if t == 'segmentation':
            self.tag_layer(['paragraphs'], resolver)
        elif t == 'morphology':
            self.tag_layer(['morph_analysis'], resolver)
        elif t == 'syntax_preprocessing':
            self.tag_layer(['sentences','morph_extended'], resolver)
        else:
            raise ValueError("invalid argument: '"+str(t)+
                             "', use 'segmentation', 'morphology' or 'syntax' instead")
        if 'tokens' in self.layers:
            del self.tokens
        return self

    def list_registered_layers(self):
        return DEFAULT_RESOLVER.list_layers()

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

    def _add_layer(self, layer:Layer):
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
            assert layer.parent in self.layers.keys(), 'Cant add a layer "{layer}" before adding its parent "{parent}"'.format(parent = layer.parent, layer= layer.name)

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

    def _resolve(self, frm, to, sofar:SpanList = None) -> Union[SpanList, List[None]]:
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

                    #path taken by text.sentences[0].lemma
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

                #through an enveloped layer (enveloping-enveloping-target)
                elif to == self.layers[self.layers[frm].enveloping].enveloping:
                    return self._resolve(frm = self.layers[frm].enveloping,
                                         to = to,
                                         sofar=sofar
                                         )


        #attribute access
        elif path_exists:
            to_layer_name = self.attributes[to][0]
            path = self._get_path(frm, to_layer_name) + ['{}.{}'.format(to_layer_name, to)]

            to_layer = self.layers[to_layer_name]
            assert  to_layer_name in self.layers.keys()


            if self.layers[frm] == to_layer:
                raise NotImplementedError('Seda ei tohiks juhtuda.')


            #attributes of a (direct) dependant
            if to_layer.parent == frm:
                res = []
                if sofar:
                    for i in to_layer.spans:
                        if i.parent in sofar.spans:
                            res.append(getattr(i, to))
                    return res


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


    def __setitem__(self, key, value):
        #always sets layer
        assert key not in self.layers.keys(), 'Re-adding a layer not implemented yet'
        assert value.name == key, 'Name mismatch between layer name and value'
        return self._add_layer(
            value
        )

    def __getitem__(self, item):
        #always returns layer
        return self.layers[item]



    def __delattr__(self, item):
        assert item in self.layers.keys(), '{item} is not a valid layer in this Text object'.format(item=item)

        #find all dependencies between layers
        relations = set()
        for layer_name, layer in self.layers.items():
            relations.update((b, a) for a,b in [
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

    def __str__(self):
        return 'Text(text="{self.text}")'.format(self=self)

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        pandas.set_option('display.max_colwidth', -1)

        rec = [{'text': self.text.replace('\n', '<br/>')}]
        table1 = pandas.DataFrame.from_records(rec)
        table1 = table1.to_html(index=False, escape=False)
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

            rec = [{'layer': layer.name,
                    'attributes': ', '.join(layer.attributes),
                    'parent': str(layer.parent),
                    'enveloping': str(layer.enveloping),
                    'ambiguous': str(layer.ambiguous),
                    'span count': str(len(layer.spans.spans))}
                   for layer in layers]

            layer_table = pandas.DataFrame()
            for layer in layers:
                layer_table = layer_table.append(layer.metadata())
            layer_table = layer_table.to_html(index=False, escape=False)
            return '\n'.join((table1, layer_table))
        return table1

    def __eq__(self, other):
        if not isinstance(other, Text):
            return False
        if self.text != other.text:
            return False
        return self.layers == other.layers


from .resolve_layer_dag import DEFAULT_RESOLVER
