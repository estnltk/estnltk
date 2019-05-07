import bisect
from typing import Union, Any
import collections
import itertools

from estnltk import Span
from estnltk.layer import AmbiguousAttributeTupleList, AttributeTupleList, AttributeList, AmbiguousAttributeList


class SpanList(collections.Sequence):
    def __init__(self,
                 layer,  # type: Layer
                 spans: list = None):
        self._layer = layer
        self._hash_to_span = {}
        self.spans = []
        # TODO: remove next lines
        for span in spans or ():
            self.add_span(span)

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

    def add_layer(self, layer):
        self._layer = layer

    def add_span(self, span):
        # assert span.layer is self.layer  # TODO
        assert hash(span) not in self._hash_to_span
        bisect.insort(self.spans, span)
        self._hash_to_span[hash(span)] = span

    def get(self, span):
        result = self._hash_to_span.get(hash(span))
        if result is not None and result.start == span.start and result.end == span.end:
            return result

    def remove_span(self, span):
        del self._hash_to_span[hash(span)]
        self.spans.remove(span)

    def attribute_list(self, attributes):
        assert isinstance(attributes, (str, list, tuple)), str(type(attributes))
        if not attributes:
            raise IndexError('no attributes: ' + str(attributes))

        if self._layer.ambiguous:
            if isinstance(attributes, (list, tuple)):
                return AmbiguousAttributeTupleList((((getattr(sp, name) for name in attributes) for sp in asp)
                                                    for asp in self.spans), attributes)
            else:
                return AmbiguousAttributeList(((getattr(sp, attributes) for sp in asp)
                                               for asp in self.spans), attributes)
        else:
            if isinstance(attributes, (list, tuple)):
                return AttributeTupleList([[getattr(sp, attr) for attr in attributes] for sp in self.spans], attributes)
            else:
                return AttributeList([getattr(sp, attributes) for sp in self.spans], attributes)

    def to_records(self, with_text=False):
        return [i.to_records(with_text) for i in self.spans]

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
        # return AttributeList([span.text for span in self.spans], 'text')

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
        if item in self._hash_to_span:
            return True
        if hash(item) not in self._hash_to_span:
            return False
        return self._hash_to_span[hash(item)] == item

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError
        if item == '_ipython_canary_method_should_not_exist_' and self.layer is not None and self is self.layer.span_list:
            raise AttributeError

        layer = self.layer  # type: Layer
        if item in layer.attributes:
            return self.attribute_list(item)
        if item in self.__dict__:
            return self.__dict__[item]

        target = layer.text_object._resolve(layer.name, item, sofar=self)
        return target

    def __getitem__(self, idx) -> Union[Span, 'SpanList', list, AmbiguousAttributeTupleList]:
        if isinstance(idx, str) or isinstance(idx, (list, tuple)) and all(isinstance(s, str) for s in idx):
            return self.attribute_list(idx)

        wrapped = self.spans.__getitem__(idx)
        if isinstance(idx, int):
            return wrapped

        res = SpanList(layer=self.layer, spans=wrapped)
        return res

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, SpanList) and self.spans == other.spans

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __str__(self):
        return 'SL[{spans}]'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        if self.layer is None:
            return

        attributes = []
        if self.layer.text_object is None:
            text_object = 'No Text object.'
        else:
            attributes.append('text')
            text_object = ''
        if self.layer.print_start_end:
            attributes.extend(['start', 'end'])
        attributes.extend(self.layer.attributes)
        if not attributes:
            attributes = ['start', 'end']
        table_2 = ''
        if attributes:
            table_2 = self.attribute_list(attributes).to_html(index='text')
        return '<h4>{self.__class__.__name__}</h4>\n<b>Layer</b>: {self.layer.name!r}\n{}\n{}'.format(
                          text_object, table_2, self=self)
