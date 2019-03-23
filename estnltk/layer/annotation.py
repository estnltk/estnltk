from typing import Any, Sequence, Mapping


class Annotation:
    __slots__ = ['_attributes', '_span']

    def __init__(self, span=None, **attributes):
        self._attributes = attributes
        self._span = span

    def to_record(self, with_text=False) -> Mapping[str, Any]:
        return {**{k: getattr(self, k) for k in list(self.legal_attribute_names) + (['text'] if with_text else [])},
                **{'start': self.start, 'end': self.end}}

    def attributes(self):
        return {attr: getattr(self, attr) for attr in self.legal_attribute_names}

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
        if self._span:
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
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        attributes = self._attributes
        if item in attributes:
            value = attributes[item]
            if isinstance(value, str) and value.startswith('lambda a: '):
                return eval(value)(self)
            return value

        # item == '__deepcopy__'
        return self.__getattribute__('__class__').__getattribute__(self, item)

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

    def __hash__(self):
        return hash((self.start, self.end))

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
