from reprlib import recursive_repr
from typing import Any, Sequence

from estnltk.layer.base_span import BaseSpan, ElementaryBaseSpan
from estnltk.layer.annotation import Annotation
from estnltk.layer import AttributeList, AttributeTupleList

from .to_html import html_table


class Span:
    """Basic element of an EstNLTK layer.

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

    def to_records(self, with_text=False):
        if self._layer.ambiguous:
            return [i.to_record(with_text) for i in self._annotations]
        annotation = self.annotations[0]
        record = {k: annotation[k] for k in self._layer.attributes}
        if with_text:
            record['text'] = self.text
        record['start'] = self.start
        record['end'] = self.end
        return record

    def __setattr__(self, key, value):
        if key in {'_base_span', '_layer', '_annotations', '_parent'}:
            super().__setattr__(key, value)
        elif key in self.legal_attribute_names:
            for annotation in self._annotations:
                setattr(annotation, key, value)
        else:
            raise AttributeError(key)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__', '__deepcopy__'}:
            raise AttributeError

        if item in self._layer.attributes:
            return self[item]

        elif self._layer.text_object is not None and self._layer.text_object._path_exists(self._layer.name, item):
            # there exists an unambiguous path from this span to the target (attribute)

            looking_for_layer = False
            if item in self._layer.text_object.layers.keys():
                looking_for_layer = True
                target_layer_name = self.text_object._get_path(self._layer.name, item)[-1]
            else:
                target_layer_name = self.text_object._get_path(self._layer.name, item)[-2]

            for i in self.text_object.layers[target_layer_name]:
                if i.__getattribute__('parent') == self or self.__getattribute__('parent') == i:
                    if looking_for_layer:
                        return i
                    else:
                        return getattr(i, item)
        else:
            return getattr(self.__class__, item)

    def __lt__(self, other: Any) -> bool:
        return self.base_span < other.base_span

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Span) \
               and self.base_span == other.base_span \
               and len(self.annotations) == len(other.annotations) \
               and all(s in other.annotations for s in self.annotations)

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

    def _repr_html_(self):
        return self._to_html()
