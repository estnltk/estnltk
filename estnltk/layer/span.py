from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Sequence

from estnltk.layer.base_span import BaseSpan, ElementaryBaseSpan
from estnltk.layer.annotation import Annotation
from estnltk.layer import AttributeList, AttributeTupleList

from .to_html import html_table


class Span:
    """Basic element of an EstNLTK layer.

    Span can exist without annotations. It is the responsibility of a programmer to remove such spans.

    """
    __slots__ = ['base_span', 'layer', 'annotations', '_parent']

    def __init__(self, base_span: BaseSpan, layer):
        assert isinstance(base_span, BaseSpan), base_span
        # assert isinstance(layer, Layer), layer

        self_setattr = super().__setattr__
        # self.layer: Layer = layer
        self_setattr('layer', layer)
        # self.base_span: BaseSpan = base_span
        self_setattr('base_span', base_span)
        # self.annotations: List[Annotation] = []
        self_setattr('annotations', [])
        # self._parent: Span = None
        self_setattr('_parent', None)

    def __copy__(self):
        result = Span(base_span=self.base_span, layer=self.layer)
        result_setattr = super(Span, result).__setattr__
        result_setattr('annotations', self.annotations)
        result_setattr('_parent', self._parent)
        return result

    def __deepcopy__(self, memo=None):
        memo = memo or {}
        # Create invalid instance
        cls = self.__class__
        result = cls.__new__(cls)
        # Add all fields to the instance to make it valid
        # All assignments are safe as self is consistent
        result_setattr = super(Span, result).__setattr__
        result_setattr('layer',  None)                         # Mutable
        result_setattr('base_span', self.base_span)            # Immutable
        result_setattr('annotations', list())                  # List[Mutable]
        result_setattr('_parent', None)                        # Mutable
        # Add newly created valid mutable objects to memo
        memo[id(self)] = result
        memo[id(self.annotations)] = result.annotations
        # Perform deep copy with a valid memo dict
        result_setattr('layer', deepcopy(self.layer, memo))
        result_setattr('_parent', deepcopy(self._parent, memo))
        result.annotations.extend(deepcopy(annotation, memo) for annotation in self.annotations)
        return result

    def __getstate__(self):
        return dict(layer=self.layer, base_span=self.base_span, annotations=self.annotations, parent=self._parent)

    def __setstate__(self, state):
        self.__init__(base_span=state['base_span'], layer=state['layer'])
        self_setattr = super().__setattr__
        self_setattr('annotations', state['annotations'])
        self_setattr('_parent', state['parent'])

    def __getattr__(self, item):

        if item in self.__getattribute__('layer').attributes:
            return self[item]
        try:
            return self.resolve_attribute(item)
        except KeyError as key_error:
            raise AttributeError(key_error.args[0]) from key_error

    def __setattr__(self, key, value):
        # Assignable properties
        if key == 'parent':
            return super().__setattr__(key, value)
        # Constant slots
        elif key in {'annotations', 'base_span', 'layer'}:
            raise AttributeError(
                'an attempt to redefine a constant slot {!r} of Span. Define a new instance.'.format(key))
        # Prohibited slots
        elif key == '_parent':
            raise AttributeError('an attempt to assign a private slot {!r} of Span'.format(key))

        # TODO: Resolve property attribute conflict
        # Properties must win and put the corresponding check first

        if key in self.legal_attribute_names:
            for annotation in self.annotations:
                setattr(annotation, key, value)
        else:
            raise AttributeError(key)

    def __getitem__(self, item):
        if isinstance(item, str):
            if self.layer.ambiguous:
                return AttributeList((annotation[item] for annotation in self.annotations), item)
            return self.annotations[0][item]
        if isinstance(item, tuple):
            if self.layer.ambiguous:
                return AttributeTupleList((annotation[item] for annotation in self.annotations), item)
            return self.annotations[0][item]

        raise KeyError(item)

    def __lt__(self, other: Any) -> bool:
        return self.base_span < other.base_span

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Span) \
               and self.base_span == other.base_span \
               and len(self.annotations) == len(other.annotations) \
               and all(s in other.annotations for s in self.annotations)

    @recursive_repr()
    def __repr__(self):
        try:
            text = self.text
        except:
            text = None

        try:
            attribute_names = self.layer.attributes
            annotation_strings = []
            for annotation in self.annotations:
                key_value_strings = ['{!r}: {!r}'.format(attr, annotation[attr]) for attr in attribute_names]
                annotation_strings.append('{{{}}}'.format(', '.join(key_value_strings)))
            annotations = '[{}]'.format(', '.join(annotation_strings))
        except:
            annotations = None

        return '{class_name}({text!r}, {annotations})'.format(class_name=self.__class__.__name__, text=text,
                                                              annotations=annotations)

    @property
    def parent(self):
        parent = self._parent
        if parent is None:
            # Lets try to compute parent
            layer = self.__getattribute__('layer')
            # Be explicit bool conversion can fail sometimes
            if layer is None or layer.parent is None:
                return parent
            text = layer.text_object
            # Be explicit bool conversion can fail sometimes
            if text is None or layer.parent not in text.layers:
                return parent
            # We have it. Lets cache the result
            parent = text[layer.parent].get(self.base_span)
            super().__setattr__('_parent', parent)
        return parent

    @parent.setter
    def parent(self, value):
        # Validity checks
        if self._parent is not None:
            raise AttributeError("value of 'parent' property is already fixed. Define a new instance.")
        elif not isinstance(value, Span):
            raise TypeError("'parent' must be an instance of Span.")
        elif value.base_span != self.base_span:
            raise ValueError("an invalid 'parent' value: 'base_span' attributes must coincide.")
        elif value is self:
            raise ValueError("an invalid 'parent' value: self-loops are not allowed.")
        # Assignment
        return super().__setattr__('_parent', value)


    def add_annotation(self, annotation: Annotation) -> Annotation:
        if not isinstance(annotation, Annotation):
            raise TypeError('expected Annotation, got {}'.format(type(annotation)))
        if annotation.span is not self:
            raise ValueError('the annotation has a different span {}'.format(annotation.span))
        if set(annotation) != set(self.layer.attributes):
            raise ValueError('the annotation has unexpected or missing attributes {}!={}'.format(
                    set(annotation), set(self.layer.attributes)))

        if annotation not in self.annotations:
            if self.layer.ambiguous or len(self.annotations) == 0:
                self.annotations.append(annotation)
                return annotation

            raise ValueError('The layer is not ambiguous and this span already has a different annotation.')

    def del_annotation(self, idx):
        del self.annotations[idx]

    def clear_annotations(self):
        self.annotations.clear()

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        return self.layer.attributes

    @property
    def start(self) -> int:
        return self.base_span.start

    @property
    def end(self) -> int:
        return self.base_span.end

    # TODO: Legacy. To be removed!
    @property
    def base_spans(self):
        return [(self.start, self.end)]

    @property
    def text(self):
        if self.text_object is None:
            return
        text = self.text_object.text
        base_span = self.base_span

        if isinstance(base_span, ElementaryBaseSpan):
            return text[base_span.start:base_span.end]

        return [text[start:end] for start, end in base_span.flatten()]

    @property
    def enclosing_text(self):
        return self.layer.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        if self.layer is not None:
            return self.layer.text_object

    @property
    def raw_text(self):
        return self.text_object.text

    def to_records(self, with_text=False):
        if self.layer.ambiguous:
            return [i.to_record(with_text) for i in self.annotations]
        annotation = self.annotations[0]
        record = {k: annotation[k] for k in self.layer.attributes}
        if with_text:
            record['text'] = self.text
        record['start'] = self.start
        record['end'] = self.end
        return record


    def resolve_attribute(self, item):
        if item not in self.text_object.layers:
            attribute_mapping = self.text_object.attribute_mapping_for_elementary_layers
            return self.layer.text_object[attribute_mapping[item]].get(self.base_span)[item]

        return self.text_object[item].get(self.base_span)


    def _to_html(self, margin=0) -> str:
        try:
            return '<b>{}</b>\n{}'.format(
                    self.__class__.__name__,
                    html_table(spans=[self], attributes=self.layer.attributes, margin=margin, index=False))
        except:
            return str(self)

    def _repr_html_(self):
        return self._to_html()
