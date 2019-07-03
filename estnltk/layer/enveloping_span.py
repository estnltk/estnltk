from typing import Any, Union, Sequence
import itertools
from IPython.core.display import display_html

from estnltk.layer.span import Span, Annotation
from estnltk.layer.ambiguous_span import AmbiguousSpan
from estnltk import EnvelopingBaseSpan
from .to_html import html_table


class EnvelopingSpan:
    def __init__(self, spans, layer):
        spans = tuple(spans)
        assert all(isinstance(span, (Span, AmbiguousSpan, EnvelopingSpan, Annotation)) for span in spans), [type(span) for span in spans]
        self.spans = spans

        self._layer = layer

        self.parent = None  # type:Union[Span, None]

        # placeholder for dependant layer
        self._base = None  # type:Union[Span, None]

        self._annotations = []

        # TODO: self._base_span = base_span
        self._base_span = None

    def add_annotation(self, annotation: Annotation) -> Annotation:
        if not isinstance(annotation, Annotation):
            raise TypeError('expected Annotation, got {}'.format(type(annotation)))
        if annotation.span is not self:
            raise ValueError('the annotation has a different span {}'.format(annotation.span))
        if set(annotation) != set(self.layer.attributes):
            raise ValueError('the annotation has unexpected or missing attributes {}'.format(annotation.attributes))

        if annotation not in self._annotations:
            if self.layer.ambiguous or len(self._annotations) == 0:
                self._annotations.append(annotation)
                return annotation

            raise ValueError('The layer is not ambiguous and this span already has a different annotation.')

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

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        return self.layer.attributes

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
    def base_span(self):
        # TODO: return self._base_span
        return EnvelopingBaseSpan([s.base_span for s in self.spans])

    @property
    def base_spans(self):
        return tuple(s for span in self.spans for s in span.base_spans)

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
        return len(self.__getattribute__(
            'spans'
        ))

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __setattr__(self, key, value):
        if key in {'spans', '_attributes', 'parent', '_base', '_base_span', '_layer', '_annotations'}:
            super().__setattr__(key, value)
        else:
            if not self.annotations:
                self.annotations.append(Annotation(self))
            for annotation in self._annotations:
                setattr(annotation, key, value)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        if self._annotations and item in self._annotations[0]:
            return self.annotations[0][item]

        layer = self.__getattribute__('layer')  # type: Layer
        if item == layer.parent:
            return self.parent

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

    def __lt__(self, other: Any) -> bool:
        return isinstance(other, EnvelopingSpan) and \
            (self.start, self.end, self.spans) < (other.start, other.end, other.spans)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, EnvelopingSpan) \
               and self.annotations == other.annotations \
               and self.spans == other.spans

    def __hash__(self):
        return hash(self.base_span)

    def __str__(self):
        return 'ES[{spans}]'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)

    @property
    def raw_text(self):
        return self.layer.text_object.text

    def _to_html(self, margin=0) -> str:
        return '<b>{}</b>\n{}'.format(
                self.__class__.__name__,
                html_table(spans=[self], attributes=self.layer.attributes, margin=margin, index=False))

    def display(self, margin: int = 0):
        display_html(self._to_html(margin), raw=True)

    def _repr_html_(self):
        return self._to_html()
