from typing import MutableMapping, Any, Sequence
from html import escape

from estnltk.layer.base_span import BaseSpan
from estnltk.layer.annotation import Annotation


class Span:
    """Basic element of an EstNLTK layer.

    """
    # __slots__ = ['_annotations', 'is_dependant', 'layer', 'parent', '_start', '_end', '_base', '_base_span']

    def __init__(self, base_span: BaseSpan, layer=None, parent=None):
        assert isinstance(base_span, BaseSpan)

        self._base_span = base_span
        self.layer = layer  # type: Layer
        self.parent = parent  # type: Span

        self._base = self  # type:Span

        self.is_dependant = False

        self._annotations = [Annotation(span=self)]

    def __len__(self):
        return len(self._annotations)

    def __getitem__(self, item):
        return self.annotations[item]

    def add_annotation(self, **attributes) -> Annotation:
        # TODO: try and remove if-s

        annotation = Annotation(self)
        if self.layer:
            for attr in self.layer.attributes:
                if attr in attributes:
                    setattr(annotation, attr, attributes[attr])
        else:
            for attr, value in attributes.items():
                if attr == 'text':
                    continue
                setattr(annotation, attr, value)

        self._annotations[0] = annotation

        return annotation

    @property
    def annotations(self):
        return self._annotations

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        if self.layer is not None:
            return self.layer.attributes
        return ()

    def to_records(self, with_text=False) -> MutableMapping[str, Any]:
        attributes = self.annotations[0].attributes
        record = {k: attributes[k] for k in self.layer.attributes}
        if with_text:
            record['text'] = self.text
        record['start'] = self.start
        record['end'] = self.end
        return record

    # TODO: remove
    def mark(self, mark_layer: str) -> 'Span':
        base_layer = self.text_object.layers[mark_layer]  # type: Layer
        base = base_layer._base

        assert base == self.layer._base, "Expected '{self.layer._base}' got '{base}'".format(self=self, base=base)
        res = base_layer.add_span(
            Span(base_span=self._base.base_span,
                 parent=self._base  # this is the base span
            )
        )
        return res

    @property
    def start(self) -> int:
        return self.base_span.start

    @property
    def end(self) -> int:
        return self.base_span.end

    @property
    def base_span(self):
        return self._base_span

    @property
    def base_spans(self):
        return [(self.start, self.end)]

    @property
    def text(self):
        if self.text_object:
            return self.text_object.text[self.start:self.end]

    @property
    def enclosing_text(self):
        return self.layer.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        if self.layer is not None:
            return self.layer.text_object

    def add_layer(self, layer):
        if self.layer is None:
            self.layer = layer
        assert self.layer is layer

    @property
    def raw_text(self):
        return self.text_object.text

    def html_text(self, margin: int = 0):
        t = self.raw_text
        s = self.start
        e = self.end
        left = escape(t[max(0, s - margin):s])
        middle = escape(t[s:e])
        right = escape(t[e:e + margin])
        return ''.join(('<span style="font-family: monospace; white-space: pre-wrap;">',
                        left,
                        '<span style="text-decoration: underline;">', middle, '</span>',
                        right, '</span>'))

    def __setattr__(self, key, value):
        if key not in {'is_dependant', 'layer', 'parent', '_base', '_base_span', '_annotations'}:
            # assert 0, key
            for annotation in self._annotations:
                setattr(annotation, key, value)
        else:
            pass
        super().__setattr__(key, value)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        if item in self.layer.attributes:
            return getattr(self.annotations[0], item)

        elif self.layer is not None and self.layer.text_object is not None and self.layer.text_object._path_exists(
                self.layer.name, item):
            # there exists an unambiguous path from this span to the target (attribute)

            looking_for_layer = False
            if item in self.layer.text_object.layers.keys():
                looking_for_layer = True
                target_layer_name = self.text_object._get_path(self.layer.name, item)[-1]
            else:
                target_layer_name = self.text_object._get_path(self.layer.name, item)[-2]

            for i in self.text_object.layers[target_layer_name].span_list:
                if i.__getattribute__('parent') == self or self.__getattribute__('parent') == i:
                    if looking_for_layer:
                        return i
                    else:
                        return getattr(i, item)

        else:
            return self.__getattribute__('__class__').__getattribute__(self, item)

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Span):
            return False
        if self.base_span != other.base_span:
            return False
        return self.annotations == other.annotations

    def __hash__(self):
        return hash((self.start, self.end))

    def __str__(self):
        if self.text_object is not None:
            return 'Span(start={self.start}, end={self.end}, text={self.text!r})'.format(self=self)
        if self.layer is None:
            return 'Span(start={self.start}, end={self.end}, layer={self.layer})'.format(self=self)
        if self.layer.text_object is None:
            return 'Span(start={self.start}, end={self.end}, layer: {self.layer.name!r})'.format(self=self)

        # Output key-value pairs in a sorted way
        # (to assure a consistent output, e.g. for automated testing)
        mapping_sorted = []

        for k in sorted(self.layer.attributes):
            key_value_str = "{key_val}".format(key_val = {k:self.__getattribute__(k)})
            # Hack: Remove surrounding '{' and '}'
            key_value_str = key_value_str[1:-1]
            mapping_sorted.append(key_value_str)

        # Hack: Put back surrounding '{' and '}' (mimic dict's representation)
        mapping_sorted_str = '{'+ (', '.join(mapping_sorted)) + '}'
        return 'Span({text}, {attributes})'.format(text=self.text, attributes=mapping_sorted_str)

    def __repr__(self):
        return str(self)
