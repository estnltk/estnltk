import bisect
from typing import Union, List, Sequence, MutableMapping, Tuple, Any
import pandas

from estnltk import Span, EnvelopingSpan

import collections
import itertools

from estnltk import AmbiguousSpan


class SpanList(collections.Sequence):
    def __init__(self,
                 layer=None,  # type: Layer
                 ambiguous: bool=False) -> None:
        # TODO:
        # assert layer is not None
        self.classes = {}  # type: MutableMapping[Tuple[int, int], AmbiguousSpan]

        self.spans = []  # type: List

        self._layer = layer
        self.ambiguous = ambiguous

        # placeholder for ambiguous layer
        self.parent = None  # type:Union[Span, None]

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

    def add_span(self, span: Union[Span, EnvelopingSpan]) -> Span:
        # the assumption is that this method is called by Layer.add_span
        assert isinstance(span, (EnvelopingSpan, Span))
        span.layer = self.layer
        target = self.get_equivalence(span)
        if self.ambiguous:
            if target is None:
                new = AmbiguousSpan(layer=self.layer)
                new.add_span(span)
                self.classes[(span.start, span.end)] = new
                bisect.insort(self.spans, new)
                new.parent = span.parent
            else:
                assert isinstance(target, AmbiguousSpan)
                target.add_span(span)
        else:
            if target is None:
                bisect.insort(self.spans, span)
                self.classes[(span.start, span.end)] = span
            else:
                raise ValueError('span is already in spanlist: ' + str(span))
        return span

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        # assert isinstance(value, Layer) or value is None
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

    @property
    def enclosing_text(self):
        return self.layer.text_object.text[self.start:self.end]

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
        if item == '_ipython_canary_method_should_not_exist_' and self.layer is not None and self is self.layer.spans:
            raise AttributeError

        layer = self.__getattribute__('layer')  # type: Layer
        if item in layer.attributes:
            return [getattr(span, item) for span in self.spans]
        if item in self.__dict__.keys():
            return self.__dict__[item]
        if item == getattr(self.layer, 'parent', None):
            return self.parent
        if item in self.__dict__:
            return self.__dict__[item]

        target = layer.text_object._resolve(layer.name, item, sofar=self)
        return target

    def __getitem__(self, idx: int) -> Union[Span, 'SpanList', list]:
        if isinstance(idx, str) or isinstance(idx, tuple) and all(isinstance(s, str) for s in idx):
            return self.get_attributes(idx)

        wrapped = self.spans.__getitem__(idx)
        if isinstance(idx, int):
            return wrapped

        res = SpanList(layer=self.layer, ambiguous=self.ambiguous)
        res.spans = wrapped
        res.ambiguous = self.ambiguous
        res.parent = self.parent
        return res

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)
        # try:
        #    return (self.start, self.end) == (other.start, other.end)
        # except AttributeError:
        #    return False

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __hash__(self):
        return hash((tuple(self.spans), self.ambiguous, self.parent))

    def __str__(self):
        return 'SL[{spans}]'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        if self.layer and self is self.layer.spans:
            return self.layer.to_html(header='SpanList', start_end=True)
        return str(self)



def whitelist_record(record, source_attributes):
    # the goal is to only keep the keys explicitly listed in source_attributes

    # record might be a dict:
    if isinstance(record, dict):
        res = {}
        for k in source_attributes:
            res[k] = record.get(k, None)
        return res

    else:
        # record might be nested
        return [whitelist_record(i, source_attributes) for i in record]


class Layer:
    def __init__(self,
                 name: str = None,
                 attributes: Sequence[str] = (),
                 parent: str = None,
                 enveloping: str = None,
                 ambiguous: bool = False
                 ) -> None:
        assert parent is None or enveloping is None, "Can't be derived AND enveloping"

        assert name is not None, 'Layer must have a name'

        # name of the layer
        self.name = name

        # list of legal attribute names for the layer
        self.attributes = attributes
        assert len(attributes) == len(set(attributes)), 'repetitive attribute name'

        # the name of the parent layer.
        self.parent = parent

        # has this layer been added to a text object
        self._bound = False

        self._is_frozen = False

        # marker for creating a lazy layer
        # used in Text._add_layer to check if additional work needs to be done
        self._is_lazy = False

        self._base = name if enveloping or not parent else None  # This is a placeholder for the base layer.
        # _base is self.name if self.enveloping or not self.parent
        # _base is parent._base otherwise, but we can't assign the value yet,
        # because we have no access to the parent layer
        # The goal is to swap the use of the "parent" attribute to the new "_base" attribute for all
        # layer inheritance purposes. As the idea about new-style text objects has evolved, it has been decided that
        # it is more sensible to keep the tree short and pruned. I'm hoping to avoid a rewrite though.

        # the name of the layer this class envelops
        # sentences envelop words
        # paragraphs envelop sentences
        # and so on...
        self.enveloping = enveloping

        # Container for spans
        self.spans = SpanList(layer=self, ambiguous=ambiguous)

        # boolean for if this is an ambiguous layer
        # if True, add_span will behave differently and add a SpanList instead.
        self.ambiguous = ambiguous  # type: bool

        # placeholder. is set when `_add_layer` is called on text object
        self.text_object = None  # type: Text

    def freeze(self):
        self._is_frozen = True

    def unfreeze(self):
        if self.text_object is None:
            self._is_frozen = False
            return
        for layer in self.text_object.layers.values():
            assert not layer.enveloping == self.name, "can't unfreeze. This layer is enveloped by " + layer.name
            assert not layer.parent == self.name, "can't unfreeze. This layer is parent of " + layer.name
        self._is_frozen = False

    @property
    def is_frozen(self):
        return self._is_frozen

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
                        spns.spans = [Span(**{**record, **{'layer': self}}, legal_attributes=self.attributes)
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
                spns.spans = [Span(**{**record, **{'layer': self}}, legal_attributes=self.attributes) for record in
                              records if record is not None]

                self.spans = spns
            else:
                for record in records:
                    self.add_span(Span(
                        **record,
                        legal_attributes=self.attributes
                    ))
        return self

    def get_attributes(self, items):
        return self.__getattribute__('spans').get_attributes(items)

    # TODO: remove this
    def to_record(self, with_text=False):
        return self.spans.to_record(with_text)

    def to_records(self, with_text=False):
        records = []

        for item in self.spans:
            records.append(item.to_record(with_text))

        return records

    def add_span(self, span: Union[Span, EnvelopingSpan]) -> Span:
        assert not self.is_frozen, "can't add spans to frozen layer"
        return self.spans.add_span(span)

    def rewrite(self, source_attributes: List[str], target_attributes: List[str], rules, **kwargs):
        assert 'name' in kwargs.keys(), '"name" must currently be an argument to layer'
        res = [whitelist_record(record, source_attributes + ('start', 'end')) for record in
               self.to_records(with_text='text' in source_attributes)]
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
        assert not self.is_frozen, "can't add spans to frozen layer"
        spanlist = SpanList(
            layer=self
        )
        spanlist.spans = spans
        bisect.insort(self.spans.spans, spanlist)
        return spanlist

    def _add_spans(self, spans: List['Span']) -> List['Span']:
        assert not self.is_frozen, "can't add spans to frozen layer"
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
        if item in self.__getattribute__('attributes'):
            return self.__getattribute__('spans').__getattr__(item)

        return self.__getattribute__('text_object')._resolve(self.name, item, sofar=self.__getattribute__('spans'))

    def __getitem__(self, idx):
        res = self.spans.__getitem__(idx)
        return res

    def __len__(self):
        return len(self.spans)

    def __str__(self):
        return 'Layer(name={self.name}, spans={self.spans})'.format(self=self)

    def metadata(self):
        """
        Return DataFrame with layer metadata.
        """
        rec = [{'layer name': self.name,
                'attributes': ', '.join(self.attributes),
                'parent': str(self.parent),
                'enveloping': str(self.enveloping),
                'ambiguous': str(self.ambiguous),
                'span count': str(len(self.spans.spans))}]
        return pandas.DataFrame.from_records(rec,
                                             columns=['layer name', 'attributes',
                                                      'parent', 'enveloping',
                                                      'ambiguous', 'span count'])

    def to_html(self, header='Layer', start_end=False):
        res = []
        base_layer = self
        if self._base:
            base_layer = self.text_object[self._base]
        if base_layer.enveloping:
            if self.ambiguous:
                # TODO: _repr_html_ for enveloping ambiguous layers
                return repr(self)
            else:
                for span in base_layer.spans:
                    # html.escape(span[i].text) TODO?
                    t = ['<b>', self.text_object.text[span[0].start:span[0].end], '</b>']
                    for i in range(1, len(span)):
                        t.extend([self.text_object.text[span[i - 1].end: span[i].start], '<b>',
                                  self.text_object.text[span[i].start:span[i].end], '</b>'])
                    t = ''.join(t)
                    res.append({'text': t, 'start': span.start, 'end': span.end,
                                **{k: span.__getattribute__(k) for k in self.attributes}})
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
        if start_end:
            columns = ('text', 'start', 'end') + tuple(self.attributes)
        else:
            columns = ('text',) + tuple(self.attributes)
        df = pandas.DataFrame.from_records(res, columns=columns)
        pandas.set_option('display.max_colwidth', -1)
        table1 = self.metadata().to_html(index=False, escape=False)
        table2 = df.to_html(index=False, escape=False)
        if header:
            return '\n'.join(('<h4>' + header + '</h4>', table1, table2))
        return '\n'.join((table1, table2))

    def _repr_html_(self):
        return self.to_html()

    def __repr__(self):
        return str(self)

    def diff(self, other):
        if not isinstance(other, Layer):
            return 'Other is not a Layer.'
        if self.name != other.name:
            return "Layer names are different: {self.name}!={other.name}".format(self=self, other=other)
        if tuple(self.attributes) != tuple(other.attributes):
            return "{self.name} layer attributes differ: {self.attributes} != {other.attributes}".format(self=self,
                                                                                                         other=other)
        if self.ambiguous != other.ambiguous:
            return "{self.name} layer ambiguous differs: {self.ambiguous} != {other.ambiguous}".format(self=self,
                                                                                                       other=other)
        if self.parent != other.parent:
            return "{self.name} layer parent differs: {self.parent} != {other.parent}".format(self=self, other=other)
        if self._base != other._base:
            return "{self.name} layer _base differs: {self._base} != {other._base}".format(self=self, other=other)
        if self.enveloping != other.enveloping:
            return "{self.name} layer enveloping differs: {self.enveloping}!={other.enveloping}".format(self=self,
                                                                                                        other=other)
        if self.spans != other.spans:
            return "{self.name} layer spans differ".format(self=self, other=other)
        return None

    def __eq__(self, other):
        return not self.diff(other)
