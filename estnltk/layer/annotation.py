from typing import Any, Mapping, Sequence, MutableMapping


class Annotation(Mapping):
    """Span attribute values are stored here.

    """
    __slots__ = ['_attributes', '_span']

    def __init__(self, span, **attributes):
        self._attributes = attributes
        self._span = span

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
        return self._attributes[item]

    def __iter__(self):
        yield from self._attributes

    def __delattr__(self, item):
        attributes = self._attributes
        if item in attributes:
            del attributes[item]
        else:
            raise AttributeError(item)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Annotation):
            return False
        if self.legal_attribute_names is None or other.legal_attribute_names is None:
            if set(self._attributes) == set(other._attributes):
                return all(getattr(self, i) == getattr(other, i) for i in self._attributes)
            return False

        if set(self.legal_attribute_names) == set(other.legal_attribute_names):
            return all(getattr(self, i) == getattr(other, i) for i in self.legal_attribute_names)

        return False

    def __str__(self):
        # Output key-value pairs in a sorted way
        # (to assure a consistent output, e.g. for automated testing)
        if self.legal_attribute_names is None:
            attribute_names = sorted(self._attributes)
        else:
            attribute_names = self.legal_attribute_names

        mapping_sorted = []

        for k in sorted(attribute_names):
            key_value_str = "{key_val}".format(key_val={k: getattr(self, k)})
            # Hack: Remove surrounding '{' and '}'
            key_value_str = key_value_str[1:-1]
            mapping_sorted.append(key_value_str)

        # Hack: Put back surrounding '{' and '}' (mimic dict's representation)
        mapping_sorted_str = '{' + (', '.join(mapping_sorted)) + '}'
        return 'Annotation({text}, {attributes})'.format(text=self.text, attributes=mapping_sorted_str)

    def __repr__(self):
        return str(self)
