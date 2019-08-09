from typing import Union

from estnltk import Span, BaseSpan
from estnltk.layer import AttributeList, AttributeTupleList


class AmbiguousSpan(Span):
    __slots__ = []

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

    def __setattr__(self, key, value):
        if key in {'_base_span', '_layer', '_annotations', '_parent', 'annotations'}:
            object.__setattr__(self, key, value)
        else:
            for annotation in self._annotations:
                setattr(annotation, key, value)
