from typing import MutableMapping, Any, Sequence


class Annotation:
    def __init__(self, ambiguous_span) -> None:

        self._ambiguous_span = ambiguous_span

        self.layer = ambiguous_span.layer
        self.spans = []

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        return self.layer.attributes

    def to_record(self, with_text=False) -> MutableMapping[str, Any]:
        return {
        **{k: self.__getattribute__(k) for k in list(self.legal_attribute_names) + (['text'] if with_text else [])},
            **{'start': self.start, 'end': self.end}}

    def attributes(self):
        return {attr: self.__getattribute__(attr) for attr in self.legal_attribute_names}

    @property
    def parent(self):
        return self._ambiguous_span.parent

    @property
    def start(self) -> int:
        return self._ambiguous_span.start

    @property
    def end(self) -> int:
        return self._ambiguous_span.end

    @property
    def text(self):
        return self.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        return self.layer.text_object

    def __getattr__(self, item):
        if item in {'start', 'end', 'layer', 'text', 'spans'}:
            return self.__getattribute__(item)

        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError

        if item in self.__getattribute__('legal_attribute_names'):
            try:
                return self.__getattribute__(item)
            except AttributeError:
                return None

        return self.__getattribute__('__class__').__getattribute__(self, item)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Annotation):
            return False
        if self.legal_attribute_names != other.legal_attribute_names:
            return False
        return all(self.__getattribute__(i) == other.__getattribute__(i) for i in self.legal_attribute_names)

    def __hash__(self):
        return hash((self.start, self.end))

    def __str__(self):
        if self.layer is None:
            return 'Annotation(start={self.start}, end={self.end}, layer={self.layer}, parent={self.parent})'.\
                format(self=self)
        if self.layer.text_object is None:
            return 'Annotation(start={self.start}, end={self.end}, layer_name={self.layer.name}, parent={self.parent})'.\
                format(self=self)
        legal_attribute_names = self.__getattribute__('layer').__getattribute__('attributes')

        # Output key-value pairs in a sorted way
        # (to assure a consistent output, e.g. for automated testing)
        mapping_sorted = []

        for k in sorted(legal_attribute_names):
            key_value_str = "{key_val}".format(key_val = {k:self.__getattribute__(k)})
            # Hack: Remove surrounding '{' and '}'
            key_value_str = key_value_str[:-1]
            key_value_str = key_value_str[1:]
            mapping_sorted.append(key_value_str)

        # Hack: Put back surrounding '{' and '}' (mimic dict's representation)
        mapping_sorted_str = '{'+ (', '.join(mapping_sorted)) + '}'
        return 'Annotation({text}, {attributes})'.format(text=self.text, attributes=mapping_sorted_str)

    def __repr__(self):
        return str(self)
