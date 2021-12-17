from reprlib import recursive_repr
from typing import Any, Sequence

from estnltk_core.common import _create_attr_val_repr

from estnltk_core.layer.base_span import BaseSpan, ElementaryBaseSpan
from estnltk_core.layer.annotation import Annotation
from estnltk_core.layer import AttributeList, AttributeTupleList

from .to_html import html_table

class Span:
    """Basic element of an EstNLTK layer.

    A span is a container for a fragment of text that is meaningful in the analyzed context.
    There can be several spans in one layer and each span can have many annotations which contain the
    information about the span. However, if the layer is not ambiguous, a span can have only one
    annotation.

    When creating a span, it must be given two arguments: BaseSpan which defines the mandatory attributes
    for a span (the exact attributes depend which kind of BaseSpan is given but minimally these are
    start and end of the span) and the layer that the span is attached to.

    Each annotation can have only one span.

    Span can exist without annotations. It is the responsibility of a programmer to remove such spans.

    """
    __slots__ = ['_base_span', '_layer', '_annotations', '_parent']

    def __init__(self, base_span: BaseSpan, layer):
        assert isinstance(base_span, BaseSpan), base_span

        self._base_span = base_span
        self._layer = layer  # type: Layer

        self._annotations = []

        self._parent = None  # type: Span

    def add_annotation(self, annotation: Annotation) -> Annotation:
        if not isinstance(annotation, Annotation):
            raise TypeError('expected Annotation, got {}'.format(type(annotation)))
        if annotation.span is not self:
            raise ValueError('the annotation has a different span {}'.format(annotation.span))
        if set(annotation) != set(self.layer.attributes):
            raise ValueError('the annotation has unexpected or missing attributes {}!={}'.format(
                    set(annotation), set(self.layer.attributes)))

        if annotation not in self._annotations:
            if self.layer.ambiguous or len(self._annotations) == 0:
                self._annotations.append(annotation)
                return annotation

            raise ValueError('The layer is not ambiguous and this span already has a different annotation.')

    def del_annotation(self, idx):
        del self._annotations[idx]

    def clear_annotations(self):
        self._annotations.clear()

    @property
    def annotations(self):
        return self._annotations

    def __getitem__(self, item):
        if isinstance(item, str):
            if self._layer.ambiguous:
                return AttributeList((annotation[item] for annotation in self._annotations), item)
            return self._annotations[0][item]
        if isinstance(item, tuple):
            if self._layer.ambiguous:
                return AttributeTupleList((annotation[item] for annotation in self._annotations), item)
            return self._annotations[0][item]

        raise KeyError(item)

    @property
    def parent(self):
        if self._parent is None and self._layer.parent:
            self._parent = self._layer.text_object[self._layer.parent].get(self.base_span)

        return self._parent

    @property
    def layer(self):
        return self._layer

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        return self._layer.attributes

    @property
    def start(self) -> int:
        return self._base_span.start

    @property
    def end(self) -> int:
        return self._base_span.end

    @property
    def base_span(self):
        return self._base_span

    @property
    def base_spans(self):
        return [(self.start, self.end)]

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
        return self.text_object.text

    def __setattr__(self, key, value):
        if key in {'_base_span', '_layer', '_annotations', '_parent'}:
            super().__setattr__(key, value)
        elif key in self.legal_attribute_names:
            for annotation in self._annotations:
                setattr(annotation, key, value)
        else:
            raise AttributeError(key)

    def resolve_attribute(self, item):
        if item not in self.text_object.layers:
            attribute_mapping = self.text_object.attribute_mapping_for_elementary_layers
            return self._layer.text_object[attribute_mapping[item]].get(self.base_span)[item]

        return self.text_object[item].get(self.base_span)

    def __getattr__(self, item):
        if item in self.__getattribute__('_layer').attributes:
            return self[item]
        try:
            return self.resolve_attribute(item)
        except KeyError as key_error:
            raise AttributeError(key_error.args[0]) from key_error

    def __lt__(self, other: Any) -> bool:
        return self.base_span < other.base_span

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Span) \
               and self.base_span == other.base_span \
               and len(self.annotations) == len(other.annotations) \
               and all(s in other.annotations for s in self.annotations)

    @recursive_repr()
    def __repr__(self):
        try:
            text = self.text
        except:
            text = None

        try:
            attribute_names = self._layer.attributes
            annotation_strings = []
            for annotation in self._annotations:
                attr_val_repr = _create_attr_val_repr( [(attr, annotation[attr]) for attr in attribute_names] )
                annotation_strings.append( attr_val_repr )
            annotations = '[{}]'.format(', '.join(annotation_strings))
        except:
            annotations = None

        return '{class_name}({text!r}, {annotations})'.format(class_name=self.__class__.__name__, text=text,
                                                              annotations=annotations)

    def _to_html(self, margin=0) -> str:
        try:
            return '<b>{}</b>\n{}'.format(
                    self.__class__.__name__,
                    html_table(spans=[self], attributes=self._layer.attributes, margin=margin, index=False))
        except:
            return str(self)

    def _repr_html_(self):
        return self._to_html()
