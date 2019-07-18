from IPython.core.display import display_html
from reprlib import recursive_repr
from typing import Union, Any

from estnltk import Span, BaseSpan
from estnltk import Annotation, ElementaryBaseSpan
from estnltk.layer import AttributeList, AttributeTupleList
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
        if self._parent is None and self._layer.parent:
            self._parent = self._layer.text_object[self._layer.parent].get(self.base_span)

        return self._parent

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

    # TODO: remove __len__
    def __len__(self) -> int:
        return len(self.annotations)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError
        layer = self._layer  # type: Layer
        if item in layer.attributes:
            return self[item]
        if item == layer.parent:
            return self.parent
        if item in self.__dict__:
            return self.__dict__[item]

        return self.__getattribute__(item)

    def __getitem__(self, item) -> Union[Annotation, AttributeList, AttributeTupleList]:
        if isinstance(item, int):
            return self.annotations[item]
        if isinstance(item, str):
            if self._layer.ambiguous:
                return AttributeList((annotation[item] for annotation in self._annotations), item)
            return self._annotations[0][item]
        if isinstance(item, tuple):
            if self._layer.ambiguous:
                return AttributeTupleList((annotation[item] for annotation in self._annotations), item)
            return self._annotations[0][item]

        raise KeyError(item)

    def __lt__(self, other: Any) -> bool:
        return self.base_span < other.base_span

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AmbiguousSpan) \
               and self.base_span == other.base_span \
               and len(self.annotations) == len(other.annotations) \
               and all(s in other.annotations for s in self.annotations)

    def __contains__(self, item: Any):
        return item in self._annotations

    def __hash__(self):
        return hash(self._base_span)

    @recursive_repr()
    def __str__(self):
        try:
            text = self.text
        except:
            text = None

        try:
            attribute_names = self._layer.attributes
            annotation_strings = []
            for annotation in self._annotations:
                key_value_strings = ['{!r}: {!r}'.format(attr, annotation[attr]) for attr in attribute_names]
                annotation_strings.append('{{{}}}'.format(', '.join(key_value_strings)))
            annotations = '[{}]'.format(', '.join(annotation_strings))
        except:
            annotations = None

        return '{class_name}({text!r}, {annotations})'.format(class_name=self.__class__.__name__, text=text,
                                                              annotations=annotations)

    def __repr__(self):
        return str(self)

    def _to_html(self, margin=0) -> str:
        try:
            return '<b>{}</b>\n{}'.format(
                    self.__class__.__name__,
                    html_table(spans=[self], attributes=self._layer.attributes, margin=margin, index=False))
        except:
            return str(self)

    def display(self, margin: int = 0):
        display_html(self._to_html(margin), raw=True)

    def _repr_html_(self):
        return self._to_html()
