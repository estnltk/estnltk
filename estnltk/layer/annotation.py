from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Mapping, Sequence, Iterable


class Annotation(Mapping):
    """Mapping for Span attribute values.

    TODO: Find out whether it should derive from Mapping or from MutableMapping
    TODO: Find out whether it should be mutable or not?
         - It is not clear how retaggers work? Do they compute new annotations or modify existing

    TODO: Resolve the problem with shadowed annotation keys. It is irrelevant but still necessary
    TODO: Get rid of _span slot. Use span slot instead and protect memory with __getattr__

    """
    __slots__ = ['__dict__', '_span', 'mapping']

    def __init__(self, span, **attributes):
        self._span = span
        self.mapping = attributes

    def __copy__(self):
        """
        Makes a copy of all annotation attributes but detaches span from annotation.
        RATIONALE: One copies an annotation only to attach the copy to a different span.
        """
        return Annotation(span=None, **self.mapping)

    def __deepcopy__(self, memo=None):
        """
        Makes a deep copy of all annotation attributes but detaches span from annotation.
        RATIONALE: One copies an annotation only to attach the copy to a different span.
        """
        memo = memo or {}
        # Create invalid instance
        cls = self.__class__
        result = cls.__new__(cls)
        # Add all fields to the instance to make it valid
        result._span = None
        # Add newly created valid mutable objects to memo
        memo[id(self)] = result
        print('boo', id(result))
        # Perform deep copy with a valid memo dict
        result.mapping = deepcopy(self.mapping, memo)
        return result

    def __getattr__(self, item):
        if item in self.mapping:
            return self.mapping[item]
        raise AttributeError('Annotation object has no attribute {!r}'.format(item))

    def __setattr__(self, key, value):
        if key in self.__slots__:
            super().__setattr__(key, value)
        elif key == 'span':
            if self._span is None:
                super().__setattr__('_span', value)
            else:
                raise AttributeError('this Annotation object already has a span')
        else:
            self.mapping[key] = value

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.mapping[item]
        if isinstance(item, tuple):
            return tuple(self.mapping[i] for i in item)
        raise TypeError(item)

    def __setitem__(self, key, value):
        self.mapping[key] = value

    def __dir__(self) -> Iterable[str]:
        """
        Extends default attribute list with annotation attributes in order to make code completion work.
        """
        return set(super().__dir__()) | set(self.mapping.keys())

    def __delitem__(self, key):
        if key not in self.mapping:
            raise KeyError('Annotation does not contain attribute {!r}'.format(key))
        del self.mapping[key]

    def __delattr__(self, item):
        if item not in self.mapping:
            raise AttributeError('Annotation does not contain attribute {!r}'.format(item))
        del self.mapping[item]

    def __len__(self):
        # Works also on invalid class instances
        return len(self.__getattribute__('mapping'))

    def __contains__(self, item):
        return item in self.mapping

    def __iter__(self):
        yield from self.mapping

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Annotation) and self.mapping == other.mapping

    @recursive_repr()
    def __str__(self):
        # Output key-value pairs in an ordered way
        # (to assure a consistent output, e.g. for automated testing)

        if self.legal_attribute_names is None:
            attribute_names = sorted(self.mapping)
        else:
            attribute_names = self.legal_attribute_names

        key_value_strings = ['{!r}: {!r}'.format(k, self.mapping[k]) for k in attribute_names]

        return '{class_name}({text!r}, {{{attributes}}})'.format(class_name=self.__class__.__name__, text=self.text,
                                                                 attributes=', '.join(key_value_strings))

    def __repr__(self):
        return str(self)


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

    # TODO: get rid of this. This does not work correctly
    def to_record(self, with_text=False) -> Mapping[str, Any]:
        record = self.mapping.copy()
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
