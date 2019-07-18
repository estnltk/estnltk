from reprlib import recursive_repr
from typing import Any, Mapping, Sequence


class Annotation(Mapping):
    """Mapping for Span attribute values.

    """
    __slots__ = ['_attributes', '_span']

    def __init__(self, span, **attributes):
        self._span = span
        self._attributes = attributes

    @property
    def span(self):
        return self._span

    @property
    def start(self) -> int:
        if self._span:
            return self._span.start

    @property
    def end(self) -> int:
        if self._span:
            return self._span.end

    # TODO: get rid of this
    def to_record(self, with_text=False) -> Mapping[str, Any]:
        record = self._attributes.copy()
        if with_text:
            record['text'] = getattr(self, 'text')
        record['start'] = self.start
        record['end'] = self.end
        return record

    @property
    def layer(self):
        if self._span:
            return self._span.layer

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        if self.layer is not None:
            return self.layer.attributes

    @property
    def text_object(self):
        if self._span is not None:
            return self._span.text_object

    @property
    def text(self):
        if self._span:
            return self._span.text

    def __setattr__(self, key, value):
        if key in self.__slots__:
            super().__setattr__(key, value)
        elif key == 'span':
            if self._span is None:
                super().__setattr__('_span', value)
            else:
                raise AttributeError('this Annotation object already has a span')
        else:
            self._attributes[key] = value

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__', '__deepcopy__'}:
            raise AttributeError(item)

        attributes = self._attributes
        if item in attributes:
            return attributes[item]

        return self.__getattribute__(item)

    def __contains__(self, item):
        return item in self._attributes

    def __len__(self):
        return len(self._attributes)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._attributes[item]
        if isinstance(item, tuple):
            return tuple(self._attributes[i] for i in item)
        raise TypeError(item)

    def __iter__(self):
        yield from self._attributes

    def __delattr__(self, item):
        attributes = self._attributes
        if item in attributes:
            del attributes[item]
        else:
            raise AttributeError(item)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Annotation) and self._attributes == other._attributes

    @recursive_repr()
    def __str__(self):
        # Output key-value pairs in an ordered way
        # (to assure a consistent output, e.g. for automated testing)

        if self.legal_attribute_names is None:
            attribute_names = sorted(self._attributes)
        else:
            attribute_names = self.legal_attribute_names

        key_value_strings = ['{!r}: {!r}'.format(k, self._attributes[k]) for k in attribute_names]

        return '{class_name}({text!r}, {{{attributes}}})'.format(class_name=self.__class__.__name__, text=self.text,
                                                                 attributes=', '.join(key_value_strings))

    def __repr__(self):
        return str(self)
