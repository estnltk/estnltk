from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Mapping, Sequence


class Annotation(Mapping):
    """Mapping for Span attribute values.

    TODO: Find out whether it should derive from Mapping or from MutableMapping

    TODO: Resolve the problem with shadowed annotation keys. It is irrelevant but still necessary
    TODO: Get rid of _span slot. Use span slot instead and protect memory with __getattr__

    """
    __slots__ = ['__dict__', '_span', 'mapping']

    def __init__(self, span, **attributes):
        self._span = span
        self.__dict__ = attributes

    def __copy__(self):
        """
        Makes a copy of all annotation attributes but detaches span from annotation.
        RATIONALE: One copies an annotation only to attach the copy to a different span.
        """
        return Annotation(span=None, **self.__dict__)

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
        result.__dict__ = deepcopy(self.__dict__, memo)
        return result

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
        record = self.__dict__.copy()
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
            self.__dict__[key] = value

    def __contains__(self, item):
        return item in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.__dict__[item]
        if isinstance(item, tuple):
            return tuple(self.__dict__[i] for i in item)
        raise TypeError(item)

    def __iter__(self):
        yield from self.__dict__

    def __delitem__(self, key):
        del self.__dict__[key]

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError as key_error:
            raise AttributeError(key_error.args[0]) from key_error

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Annotation) and self.__dict__ == other.__dict__

    @recursive_repr()
    def __str__(self):
        # Output key-value pairs in an ordered way
        # (to assure a consistent output, e.g. for automated testing)

        if self.legal_attribute_names is None:
            attribute_names = sorted(self.__dict__)
        else:
            attribute_names = self.legal_attribute_names

        key_value_strings = ['{!r}: {!r}'.format(k, self.__dict__[k]) for k in attribute_names]

        return '{class_name}({text!r}, {{{attributes}}})'.format(class_name=self.__class__.__name__, text=self.text,
                                                                 attributes=', '.join(key_value_strings))

    def __repr__(self):
        return str(self)
