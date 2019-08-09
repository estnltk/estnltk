import itertools
from typing import Any, Union, Sequence

from estnltk.layer.span import Span, Annotation
from estnltk import BaseSpan, EnvelopingBaseSpan


class EnvelopingSpan(Span):
    __slots__ = ['_spans']

    def __init__(self, base_span: BaseSpan, layer):
        self._spans = None
        super().__init__(base_span, layer)

    @classmethod
    def from_spans(cls, spans, layer, records):
        span = cls(base_span=EnvelopingBaseSpan(s.base_span for s in spans), layer=layer)
        for record in records:
            span.add_annotation(Annotation(span, **record))
        return span

    @property
    def spans(self):
        if self._spans is None:
            get_from_enveloped = self._layer.text_object[self._layer.enveloping].get
            self._spans = tuple(get_from_enveloped(base) for base in self._base_span)

        return self._spans

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

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        return self.layer.attributes

    def to_records(self, with_text=False):
        return [i.to_records(with_text) for i in self.spans]

    @property
    def base_spans(self):
        return tuple(s for span in self.spans for s in span.base_spans)

    @property
    def enclosing_text(self):
        return self.layer.text_object.text[self.start:self.end]

    # TODO
    def html_text(self, margin: int = 0):
        return self.text

    @property
    def _html_text(self):
        rt = self.raw_text
        result = []
        for a, b in zip(self.spans, self.spans[1:]):
            result.extend(('<b>', rt[a.start:a.end], '</b>', rt[a.end:b.start]))
        result.extend(('<b>', rt[self.spans[-1].start:self.spans[-1].end], '</b>'))
        return ''.join(result)

    def __iter__(self):
        yield from self.spans

    def __len__(self) -> int:
        return len(self._base_span)

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __setattr__(self, key, value):
        if key in {'_base_span', '_layer', '_annotations', '_parent', '_spans'}:
            object.__setattr__(self, key, value)
        else:
            for annotation in self._annotations:
                setattr(annotation, key, value)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        if self._annotations and item in self._annotations[0]:
            return self.annotations[0][item]

        layer = self.__getattribute__('layer')  # type: Layer

        return layer.text_object._resolve(layer.name, item, sofar=self)

    def __getitem__(self, idx: int) -> Union[Span, 'EnvelopingSpan']:
        if isinstance(idx, int):
            return self.spans[idx]

        if isinstance(idx, str):
            return getattr(self, idx)

        if isinstance(idx, slice):
            res = EnvelopingSpan(spans=self.spans[idx], layer=self.layer)
            return res

        raise KeyError(idx)
