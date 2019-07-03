from typing import Union, Any
from IPython.core.display import display_html

from estnltk import Span, BaseSpan
from estnltk import Annotation, ElementaryBaseSpan
from estnltk.layer import AttributeList
from .to_html import html_table


class AmbiguousSpan:
    def __init__(self, base_span: BaseSpan, layer) -> None:
        assert isinstance(base_span, BaseSpan), base_span

        self._base_span = base_span
        self._layer = layer  # type: Layer

        self._annotations = []

        self._parent = None  # type: Union[Span, None]

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

    @annotations.setter
    def annotations(self, value):
        self._annotations = value

    def to_records(self, with_text=False):
        return [i.to_record(with_text) for i in self._annotations]

    def __delitem__(self, key):
        del self._annotations[key]
        if not self._annotations:
            self._layer.remove_span(self)

    # TODO: remove span
    @property
    def span(self):
        return Span(self._base_span, self._layer)

    @property
    def parent(self):
        if self._parent is None:
            if self._layer.parent:
                self._parent = self._layer.text_object[self._layer.parent].get(self.base_span)

        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def layer(self):
        return self._layer

    @property
    def start(self):
        return self._base_span.start

    @property
    def end(self):
        return self._base_span.end

    @property
    def base_span(self):
        return self._base_span

    @property
    def text(self):
        if self.text_object is None:
            return
        text = self.text_object.text
        base_span = self.base_span

        if isinstance(base_span, ElementaryBaseSpan):
            return text[base_span.start:base_span.end]

        return [text[start:end] for start, end in base_span.flatten()]

    @property
    def enclosing_text(self):
        return self._layer.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        if self._layer is not None:
            return self._layer.text_object

    @property
    def raw_text(self):
        if self.text_object is not None:
            return self.text_object.text

    def __len__(self) -> int:
        return len(self.annotations)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError
        layer = self.__getattribute__('layer')  # type: Layer
        if item in layer.attributes:
            if layer.ambiguous:
                return AttributeList((getattr(span, item) for span in self._annotations), item)
            return getattr(self._annotations[0], item)
        if item == layer.parent:
            return self.parent
        if item in self.__dict__:
            return self.__dict__[item]

        return self.__getattribute__(item)

    def __getitem__(self, idx: int) -> Union[Annotation, AttributeList]:
        if isinstance(idx, int):
            return self._annotations[idx]

        if isinstance(idx, str):
            return getattr(self, idx)

        raise KeyError(idx)

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AmbiguousSpan) \
               and self.base_span == other.base_span \
               and len(self.annotations) == len(other.annotations) \
               and all(s in other.annotations for s in self.annotations)

    def __contains__(self, item: Any):
        return item in self._annotations

    def __hash__(self):
        return hash(self._base_span)

    def __str__(self):
        if self.text_object is not None:
            return 'AS(start={self.start}, end={self.end}, text:{self.text!r})'.format(self=self)
        return 'AS[{spans}]'.format(spans=', '.join(str(i) for i in self.annotations))

    def __repr__(self):
        return str(self)

    def _to_html(self, margin=0) -> str:
        return '<b>{}</b>\n{}'.format(
                self.__class__.__name__,
                html_table(spans=[self], attributes=self._layer.attributes, margin=margin, index=False))

    def display(self, margin: int = 0):
        display_html(self._to_html(margin), raw=True)

    def _repr_html_(self):
        return self._to_html()
