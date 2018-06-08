import collections
import itertools
from typing import Union, Any

from estnltk import Span
from .annotation import Annotation


class AmbiguousSpan(collections.Sequence):
    def __init__(self,
                 layer) -> None:
        self._spans = []

        self._span = None
        self._annotations = []

        self._layer = layer

        # placeholder for ambiguous layer
        self.parent = None  # type:Union[Span, None]

        # placeholder for dependant layer
        self._base = None  # type:Union[Span, None]

    @property
    def annotations(self):
        return self._annotations

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
        return [i.to_record(with_text) for i in self._annotations]

    def add_span(self, span: Span) -> Span:
        self._span = span
        if span not in self._spans:
            self._spans.append(span)
            annotation = Annotation(start=span.start,
                                    end=span.end,
                                    parent=span.parent,
                                    layer=self._layer,
                                    legal_attributes=self._layer.attributes
                                    )
            for attr in span.legal_attribute_names:
                setattr(annotation, attr, getattr(span, attr))
            if not isinstance(span, Span):
                # EnvelopingSpan
                annotation._attributes = span._attributes
                annotation.spans = span.spans
            self._annotations.append(annotation)
            return span

    @property
    def spans(self):
        return self._annotations

    @spans.setter
    def spans(self, spans):
        self._spans = []
        self._annotations = []
        for span in spans:
            self.add_span(span)

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        self._layer = value

    @property
    def span(self):
        return self._span

    @property
    def start(self):
        return self._span.start

    @property
    def end(self):
        return self._span.end

    @property
    def text(self):
        return self._span.text

    @property
    def enclosing_text(self):
        return self.layer.text_object.text[self.start:self.end]

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
            return [getattr(span, item) for span in self._annotations]
        if item in self.__dict__.keys():
            return self.__dict__[item]
        if item == getattr(self.layer, 'parent', None):
            return self.parent
        if item in self.__dict__:
            return self.__dict__[item]

        target = layer.text_object._resolve(layer.name, item, sofar=self)
        return target

    def __getitem__(self, idx: int) -> Union[Span, 'SpanList']:
        wrapped = self._annotations.__getitem__(idx)
        if isinstance(idx, int):
            return wrapped
        raise NotImplementedError('slicing of ambiguous span not yet implemented')

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AmbiguousSpan) \
               and len(self._annotations) == len(other._annotations) \
               and all(s in other._annotations for s in self._annotations)

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
