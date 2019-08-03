import itertools
from IPython.core.display import display_html
from reprlib import recursive_repr
from typing import Any, Union, Sequence

from estnltk.layer.span import Span, Annotation
from estnltk import BaseSpan
from .to_html import html_table


class EnvelopingSpan:
    __slots__ = ['_base_span', '_layer', '_annotations', 'parent', '_spans']

    def __init__(self, base_span: BaseSpan, layer):
        assert isinstance(base_span, BaseSpan)

        self._base_span = base_span
        self._layer = layer

        self._annotations = []
        self.parent = None  # type:Union[Span, None]
        self._spans = None

    @property
    def spans(self):
        if self._spans is None:
            get_from_enveloped = self._layer.text_object[self._layer.enveloping].get
            self._spans = tuple(get_from_enveloped(base) for base in self._base_span)

        return self._spans

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
        return self._base_span.start

    @property
    def end(self):
        return self._base_span.end

    @property
    def base_span(self):
        return self._base_span

    @property
    def base_spans(self):
        return tuple(s for span in self.spans for s in span.base_spans)

    @property
    def text(self):
        raw_text = self.text_object.text
        return [raw_text[start:end] for start, end in self._base_span.flatten()]

    @property
    def text_object(self):
        return self._layer.text_object

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
        return len(self._base_span)

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __setattr__(self, key, value):
        if key in {'_spans', '_attributes', 'parent', '_base', '_base_span', '_layer', '_annotations'}:
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
        return isinstance(other, EnvelopingSpan) and self._base_span < other._base_span

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, EnvelopingSpan) \
               and self._base_span == other._base_span \
               and self.annotations == other.annotations

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
