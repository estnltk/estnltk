from IPython.core.display import display_html
from reprlib import recursive_repr
from typing import Union

from estnltk import Span, BaseSpan
from estnltk.layer import AttributeList, AttributeTupleList
from .to_html import html_table


class AmbiguousSpan(Span):
    __slots__ = ['_base_span', '_layer', '_annotations', '_parent']

    def __init__(self, base_span: BaseSpan, layer) -> None:
        assert isinstance(base_span, BaseSpan), base_span

        self._base_span = base_span
        self._layer = layer  # type: Layer

        self._annotations = []

        self._parent = None  # type: Union[Span, None]

    @property
    def annotations(self):
        return self._annotations

    @annotations.setter
    def annotations(self, value):
        self._annotations = value

    def to_records(self, with_text=False):
        return [i.to_record(with_text) for i in self._annotations]

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError
        layer = self._layer  # type: Layer
        if item in layer.attributes:
            return self[item]
        if item == layer.parent:
            return self.parent

        return self.__getattribute__(item)

    def __getitem__(self, item) -> Union[AttributeList, AttributeTupleList]:
        if isinstance(item, str):
            if self._layer.ambiguous:
                return AttributeList((annotation[item] for annotation in self._annotations), item)
            return self._annotations[0][item]
        if isinstance(item, tuple):
            if self._layer.ambiguous:
                return AttributeTupleList((annotation[item] for annotation in self._annotations), item)
            return self._annotations[0][item]

        raise KeyError(item)

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

    def _to_html(self, margin=0) -> str:
        try:
            return '<b>{}</b>\n{}'.format(
                    self.__class__.__name__,
                    html_table(spans=[self], attributes=self._layer.attributes, margin=margin, index=False))
        except:
            return str(self)

    def display(self, margin: int = 0):
        display_html(self._to_html(margin), raw=True)
