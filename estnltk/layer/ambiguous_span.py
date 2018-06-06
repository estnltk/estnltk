import collections
import itertools
from typing import Union, Any

from estnltk import Span


class AmbiguousSpan(collections.Sequence):
    def __init__(self,
                 layer=None) -> None:
        self._spans = []

        self._layer = layer

        # placeholder for ambiguous layer
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

    def add_span(self, span: Span) -> Span:
        if span not in self._spans:
            self._spans.append(span)
            return span

    @property
    def spans(self):
        return self._spans

    @spans.setter
    def spans(self, spans):
        self._spans = []
        for span in spans:
            self.add_span(span)

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
        return self.spans[0].text

    @property
    def enclosing_text(self):
        return self.layer.text_object.text[self.start:self.end]

    @property
    def html_text(self):
        return self.spans[0].html_text

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

    def __getitem__(self, idx: int) -> Union[Span, 'SpanList']:
        wrapped = self.spans.__getitem__(idx)
        if isinstance(idx, int):
            return wrapped
        raise NotImplementedError('slicing of ambiguous span not yet implemented')

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AmbiguousSpan) \
               and len(self.spans) == len(other.spans) \
               and all(s in other.spans for s in self.spans)

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __hash__(self):
        return hash((tuple(self.spans), self.parent))

    def __str__(self):
        return 'AS[{spans}]'.format(spans=', '.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)

    def _repr_html_(self):
        if self.layer and self is self.layer.spans:
            return self.layer.to_html(header='AmbiguousSpan', start_end=True)
        return str(self)

