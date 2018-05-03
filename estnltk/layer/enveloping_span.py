import collections
from typing import Any, Union
import itertools

from estnltk import Span


class EnvelopingSpan(collections.Sequence):
    def __init__(self,
                 spans,
                 layer=None
                 ) -> None:
        self.spans = spans

        self._layer = layer

        self.parent = None  # type:Union[Span, None]

        # placeholder for dependant layer
        self._base = None  # type:Union[Span, None]

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
        result = []
        for span in self.spans:
            if isinstance(span, EnvelopingSpan):
                result.extend(span.text)
            else:
                result.append(span.text)
        return result

    @property
    def enclosing_text(self):
        return self.layer.text_object.text[self.start:self.end]

    @property
    def raw_text(self):
        return self.text_object.text

    @property
    def html_text(self):
        rt = self.raw_text
        result = []
        for a, b in zip(self.spans, self.spans[1:]):
            result.extend(('<b>', rt[a.start:a.end], '</b>', rt[a.end:b.start]))
        result.extend(('<b>', rt[self.spans[-1].start:self.spans[-1].end], '</b>'))
        return ''.join(result)

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

        return layer.text_object._resolve(layer.name, item, sofar=self)

    def __getitem__(self, idx: int) -> Union[Span, 'EnvelopingSpan']:
        wrapped = self.spans.__getitem__(idx)
        if isinstance(idx, int):
            return wrapped
        res = EnvelopingSpan(spans=wrapped)
        res.layer = self.layer

        res.parent = self.parent

        return res

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, EnvelopingSpan) and self.spans == other.spans

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __hash__(self):
        return hash((tuple(self.spans), self.parent))

    def __str__(self):
        return 'ES[{spans}]'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        if self.layer and self is self.layer.spans:
            return self.layer.to_html(header='SpanList', start_end=True)
        return str(self)
