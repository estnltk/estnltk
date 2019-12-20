from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Mapping, Sequence, Iterable

from estnltk.helpers.attrdict import AttrDict


class Annotation(AttrDict):
    """Mapping for Span attribute values.

    TODO: Find out whether it should derive from Mapping or from MutableMapping
    TODO: Find out whether it should be mutable or not?
         - It is not clear how retaggers work? Do they compute new annotations or modify existing

    TODO: Resolve the problem with shadowed annotation keys. It is irrelevant but still necessary
    TODO: Get rid of _span slot. Use span slot instead and protect memory with __getattr__

    """
    __slots__ = ['span']

    # List of prohibited attribute names
    methods = AttrDict.methods | {
        'end', 'layer', 'legal_attribute_names', 'start', 'text', 'text_object', 'to_record',
        '_repr_html_', '__copy__', '__deepcopy__', '__getattr__'}

    def __init__(self, span, **attributes):
        super().__init__(**attributes)
        super().__setattr__('span', span)

    def __copy__(self):
        """
        Makes a copy of all annotation attributes but detaches span from annotation.
        RATIONALE: One copies an annotation only to attach the copy to a different span.
        """
        result = Annotation(span=None)
        result.update(self)
        return result

    def __deepcopy__(self, memo=None):
        """
        Makes a deep copy of all annotation attributes but detaches span from annotation.
        RATIONALE: One copies an annotation only to attach the copy to a different span.
        """
        memo = memo or {}
        result = Annotation(span=None)
        # Add newly created valid mutable objects to memo
        memo[id(self)] = result
        # Perform deep copy with a valid memo dict
        result.update(deepcopy(self.mapping, memo))
        return result

    def __setattr__(self, key, value):
        """
        Gives access to dict keys as attributes for all keys that are not shadowed by methods, properties or slots.
        RATIONALE: This is the best trade-off between convenience and safety.
        """
        if key == 'span' and self.span is not None:
            if value is None:
                raise AttributeError('an attempt to detach Annotation form its span')
            else:
                raise AttributeError('an attempt to re-attach Annotation to a different span')
        super().__setattr__(key, value)

    def __getitem__(self, item):
        """
        # TODO: remove this function. The tuple exception is dangerous and unintuitive. Why is it here?
        """
        if isinstance(item, str):
            return self.mapping[item]
        if isinstance(item, tuple):
            return tuple(self.mapping[i] for i in item)
        raise TypeError(item)

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
    def start(self) -> int:
        if self.span:
            return self.span.start

    @property
    def end(self) -> int:
        if self.span:
            return self.span.end

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
        if self.span:
            return self.span.layer

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        if self.layer is not None:
            return self.layer.attributes

    @property
    def text_object(self):
        if self.span is not None:
            return self.span.text_object

    @property
    def text(self):
        if self.span:
            return self.span.text
