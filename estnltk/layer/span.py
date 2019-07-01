from typing import MutableMapping, Any, Sequence
from html import escape

from estnltk.layer.base_span import BaseSpan
from estnltk.layer.annotation import Annotation


class Span:
    """Basic element of an EstNLTK layer.

    """
    __slots__ = ['_base_span', '_layer', '_annotations', 'parent', '_base']

    def __init__(self, base_span: BaseSpan, layer=None, parent=None):
        assert isinstance(base_span, BaseSpan)

        self._base_span = base_span
        self._layer = layer  # type: Layer

        self._annotations = []

        self.parent = parent  # type: Span
        self._base = self  # type:Span

    def __getitem__(self, item):
        return self.annotations[item]

    def add_annotation(self, **attributes) -> Annotation:
        # TODO: try and remove if-s

        annotation = Annotation(self)
        if self._layer:
            for attr in self._layer.attributes:
                if attr in attributes:
                    setattr(annotation, attr, attributes[attr])
        else:
            for attr, value in attributes.items():
                if attr == 'text':
                    continue
                setattr(annotation, attr, value)

        if len(self._annotations) == 0:
            self.annotations.append(annotation)
        elif len(self._annotations) == 1:
            if annotation != self._annotations[0]:
                raise Exception('the layer is not ambiguous and this span already has a different annotation')
        else:
            raise Exception('this should be impossible: the layer is not ambiguous but this span already has more than '
                            'one annotations')
        return annotation

    @property
    def annotations(self):
        return self._annotations

    @property
    def layer(self):
        return self._layer

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        return self._layer.attributes

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
        return self._layer.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        if self._layer is not None:
            return self._layer.text_object

    def add_layer(self, layer):
        if self._layer is None:
            self._layer = layer
        assert self._layer is layer

    @property
    def raw_text(self):
        return self.text_object.text

    def to_records(self, with_text=False) -> MutableMapping[str, Any]:
        attributes = self.annotations[0].attributes
        record = {k: attributes[k] for k in self._layer.attributes}
        if with_text:
            record['text'] = self.text
        record['start'] = self.start
        record['end'] = self.end
        return record

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
        if key in self.__slots__:
            super().__setattr__(key, value)
        elif key in self.legal_attribute_names:
            for annotation in self._annotations:
                setattr(annotation, key, value)
        else:
            raise AttributeError(key)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        if item in self._layer.attributes:
            return getattr(self.annotations[0], item)

        elif self._layer is not None and self._layer.text_object is not None and self._layer.text_object._path_exists(
                self._layer.name, item):
            # there exists an unambiguous path from this span to the target (attribute)

            looking_for_layer = False
            if item in self._layer.text_object.layers.keys():
                looking_for_layer = True
                target_layer_name = self.text_object._get_path(self._layer.name, item)[-1]
            else:
                target_layer_name = self.text_object._get_path(self._layer.name, item)[-2]

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
        if self._layer is None:
            return 'Span(start={self.start}, end={self.end}, layer={self._layer})'.format(self=self)
        if self._layer.text_object is None:
            return 'Span(start={self.start}, end={self.end}, layer: {self._layer.name!r})'.format(self=self)

        # Output key-value pairs in a sorted way
        # (to assure a consistent output, e.g. for automated testing)
        mapping_sorted = []

        for k in sorted(self._layer.attributes):
            key_value_str = "{key_val}".format(key_val = {k:self.__getattribute__(k)})
            # Hack: Remove surrounding '{' and '}'
            key_value_str = key_value_str[1:-1]
            mapping_sorted.append(key_value_str)

        # Hack: Put back surrounding '{' and '}' (mimic dict's representation)
        mapping_sorted_str = '{'+ (', '.join(mapping_sorted)) + '}'
        return 'Span({text}, {attributes})'.format(text=self.text, attributes=mapping_sorted_str)

    def __repr__(self):
        return str(self)
