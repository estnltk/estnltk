from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Mapping, Sequence, Optional

from estnltk.helpers.attrdict import AttrDict


class Annotation(AttrDict):
    """
    Dictionary for Span attribute values that provides attribute access for most keys.
    It is possible to access all keys that are not shadowed by the methods and properties of Annotation.
    A fool-proof way to to assign, delete or access keys is through indexing.
    Attribute access is meant mostly for convenience and has performance penalties.
    Use only indexing in time-critical code as there is a faster implementation Annotation without attribute access.

    The dictionary is fully mutable. Elements can be added and deleted.
    The annotation does not keep track which are valid attribute names for a layer.
    This is task of a low-lever system programmer who uses a raw access to Annotation.
    Normally, inconsistencies will be caught by Layer level operations.
    In particular, if you write a Tagger or a ReTagger such errors will be caught automatically.
    """

    __slots__ = ['span']

    # List of prohibited attribute names
    methods = AttrDict.methods | {
        'end', 'layer', 'legal_attribute_names', 'start', 'text', 'text_object', 'to_record',
        '_repr_html_', '__copy__', '__deepcopy__', '__getstate__', '__setstate__', '__getattr__'}

    def __init__(self, span: 'Span', **attributes):
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

    def __getstate__(self):
        """
        Serialises the state of the object to a dictionary with fields span and mapping.
        RATIONALE: This is minimal amount of information needed to recreate the state.
        """
        return dict(span=self.span, mapping=self.mapping)

    def __setstate__(self, state):
        """
        Reconstructs object form a dictionary with the fields span and mapping. Does not check correctness.
        RATIONALE: This function is mostly used in pickling and thus the input is guaranteed to be correct.
        """
        self.__init__(span=state['span'])
        self.update(state['mapping'])

    def __setattr__(self, key, value):
        """
        Gives access to all annotation attributes that are not shadowed by methods, properties or slots.
        All attributes are accessible by index operator regardless of the attribute name.
        RATIONALE: This is the best trade-off between convenience and safety.
        """
        if key == 'span':
            if self.span is None:
                # We cannot import Span without creating circular imports
                if type(value).__name__ not in ['Span', 'EnvelopingSpan']:
                    raise TypeError("span must be an instance of 'Span'")
            elif value is None:
                raise AttributeError('an attempt to detach Annotation form its span')
            else:
                raise AttributeError('an attempt to re-attach Annotation to a different span')
        super().__setattr__(key, value)

    def __setitem__(self, key, value):
        """
        Gives access to an annotation attribute regardless of the attribute name.
        Multi-indexing is not supported in assignment statements.
        RATIONALE: As layers do not support multi-indexing in assignments nor should annotations do.
        """
        if not isinstance(key, str):
            raise TypeError('index must be a string. Multi-indexing is not supported')
        super().__setitem__(key, value)

    def __getitem__(self, item):
        """
        Gives access to (multiple) annotation attributes regardless of the attribute names.
        Multiple attributes can be specified by providing a tuple of keys as an index.
        RATIONALE: Multi-indexing is just to preserve an indexing invariant layer[i, attrs] == layer[i][attrs].
        """
        if isinstance(item, str):
            return self.mapping[item]
        if isinstance(item, tuple) and all(isinstance(i, str) for i in item):
            return tuple(self.mapping[i] for i in item)
        raise TypeError(item, 'index must be a string or a tuple of strings')

    def __eq__(self, other):
        """
        Checks if key-value pairs are same and completely ignores the span slot.
        RATIONALE: One often needs to check if annotations of two different spans are equal or not.
        """
        return isinstance(other, Annotation) and self.mapping == other.mapping

    @recursive_repr()
    def __repr__(self):
        """
        Outputs a recursion safe representation of an annotation where key-value pairs in alphabetical order.
        The result is not a printable representation of an object as the span is replaced by the underlying text.
        RATIONALE: Alphabetical order guarantees a consistent output that is essential in automated testing.
        Ability to depict recursive objects is needed in debugging. Normal annotations have simple value types.
        TODO: Get rid of unnecessary curly brackets in the representation when we can change all tests.
        """
        if self.layer is None or self.layer.attributes is None:
            attribute_names = sorted(self.mapping)
        else:
            layer_attributes = self.layer.attributes
            # Remove attribute names layer spec that are not present in the annotation
            attribute_names = [attr for attr in layer_attributes if attr in self.mapping]
            # Add attribute names that are not present in the layer spec
            if len(attribute_names) < len(self.mapping):
                attribute_names.extend(sorted(attr for attr in self.mapping if attr not in layer_attributes))

        key_value_strings = ['{!r}: {!r}'.format(k, self.mapping[k]) for k in attribute_names]

        return '{class_name}({text!r}, {{{attributes}}})'.format(class_name=self.__class__.__name__, text=self.text,
                                                                 attributes=', '.join(key_value_strings))

    # add _html_repr

    @property
    def start(self) -> Optional[int]:
        """
        Convenience function that returns the start of the span associated with the annotation.
        Use it only for interactive explorations and not in time-critical applications.
        """
        if self.span:
            return self.span.start

    @property
    def end(self) -> Optional[int]:
        """
        Convenience function that returns the end of the span associated with the annotation.
        Use it only for interactive explorations and not in time-critical applications.
        """
        if self.span:
            return self.span.end

    @property
    def layer(self) -> Optional['Layer']:
        """
        Convenience function that returns the layer to which the span associated with the annotation belongs.
        Use it only for interactive exploration when you do not know to which layer the annotation belongs.
        """
        if self.span:
            return self.span.layer

    @property
    def legal_attribute_names(self) -> Optional[Sequence[str]]:
        """
        Deprecated property. Do not use it. Will be removed as soon as possible
        TODO: Remove references in morph_common.py to achieve this
        """
        if self.layer is not None:
            return self.layer.attributes

    @property
    def text_object(self) -> Optional['Text']:
        """
        Convenience function that returns the text object to which the annotation belongs.
        Use it only for interactive exploration when you do not know which text object is annotated.
        """
        if self.span is not None:
            return self.span.text_object

    @property
    def text(self) -> Optional[str]:
        """
        Convenience function that returns the underlying text fragment associated with the annotation.
        Use it only for interactive explorations and not in time-critical applications.
        """
        if self.span:
            return self.span.text

    def to_record(self, with_text: bool = False) -> Mapping[str, Any]:
        """
        Deprecated function.  Do not use it. Will be removed as soon as possible.
        This function not work correctly and is unnecessary reimplementation of __getstate__.
        TODO: Remove references in span.py to achieve this
        """
        record = self.mapping.copy()
        if with_text:
            record['text'] = getattr(self, 'text')
        record['start'] = self.start
        record['end'] = self.end
        return record
