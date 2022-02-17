from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Sequence, Union, Dict

from estnltk_core.common import _create_attr_val_repr

from estnltk_core.layer.base_span import BaseSpan, ElementaryBaseSpan
from estnltk_core.layer.annotation import Annotation
from estnltk_core.layer import AttributeList, AttributeTupleList

from .to_html import html_table

class Span:
    """Basic element of an EstNLTK layer.

    A span is a container for a fragment of text that is meaningful in the analyzed context.
    There can be several spans in one layer and each span can have many annotations which contain the
    information about the span. However, if the layer is not ambiguous, a span can have only one
    annotation.

    When creating a span, it must be given two arguments: BaseSpan which defines the mandatory attributes
    for a span (the exact attributes depend which kind of BaseSpan is given but minimally these are
    start and end of the span) and the layer that the span is attached to.

    Each annotation can have only one span.

    Span can exist without annotations. It is the responsibility of a programmer to remove such spans.

    """
    __slots__ = ['_base_span', '_layer', '_annotations', '_parent']

    def __init__(self, base_span: BaseSpan, layer):
        assert isinstance(base_span, BaseSpan), base_span

        self._base_span = base_span
        self._layer = layer  # type: Layer

        self._annotations = []

        self._parent = None  # type: Span

    def __deepcopy__(self, memo=None):
        """
        Makes a deep copy from the span.
        Loosely based on: 
          https://github.com/estnltk/estnltk/blob/5bacff50072f9415814aee4f369c28db0e8d7789/estnltk/layer/span.py#L60
        """
        memo = memo or {}
        # Create new valid instance
        # _base_span: Immutable
        result = self.__class__(base_span=self.base_span, \
                                layer=None)
        # Add self to memo
        memo[id(self)] = result
        # _annotations: List[Mutable]
        for annotation in self._annotations:
            deepcopy_annotation = deepcopy(annotation, memo)
            deepcopy_annotation.span = result
            result._annotations.append( deepcopy_annotation )
        # _parent: Mutable
        result._parent = deepcopy(self._parent, memo)
        # _layer: Mutable
        result._layer = deepcopy(self._layer, memo)
        return result

    def add_annotation(self, annotation: Union[Dict[str, Any], Annotation]={}, **annotation_kwargs) -> Annotation:
        """Adds new annotation (from `annotation` / `annotation_kwargs`) to this span.

        `annotation` can be either an Annotation object initiated with this span. For example::

            span.add_annotation(Annotation(span, {'attr1': ..., 'attr2': ...}))
           
        Or it can be a dictionary of attributes and values::

            span.add_annotation( {'attr1': ..., 'attr2': ...} )
           
        Missing attributes will be filled in with span layer's default_values
        (None values, if defaults have not been explicitly set).
        Redundant attributes (attributes not in `span.layer.attributes`)
        will be discarded.
        Optionally, you can leave `annotation` unspecified and pass keyword
        arguments to the method via `annotation_kwargs`, for example::
           
            span.add_annotation( attr1=..., attr2=... )
           
        Note that keyword arguments can only be valid Python keywords
        (excluding the keyword 'annotation'), and using `annotation`
        dictionary enables to bypass these restrictions.
           
        Note that you cannot pass Annotation object and keyword arguments
        simultaneously, this will result in TypeError.
        However, you can pass annotation dictionary and keyword arguments
        simultaneously. In that case, keyword arguments override annotation
        dictionary in case of an overlap in attributes. Overall, the
        priority order in setting value of an attribute is:
        `annotation_kwargs` > `annotation(dict)` > `default attributes`.
            
        The method returns added Annotation object.
           
        Note: you can add two or more annotations to this span only if
        the layer is ambiguous.
        """
        if isinstance(annotation, Annotation):
            # Annotation object
            if annotation.span is not self:
                raise ValueError('the annotation has a different span {}'.format(annotation.span))
            if set(annotation) != set(self.layer.attributes):
                raise ValueError('the annotation has unexpected or missing attributes {}!={}'.format(
                        set(annotation), set(self.layer.attributes)))
            if len(annotation_kwargs.items()) > 0:
                # If Annotation object is already provided, cannot add additional keywords
                raise TypeError(('cannot add keyword arguments {!r} to an existing Annotation object.'+\
                                 'please pass keywords as a dict instead of Annotation object.').format(annotation_kwargs))
        elif isinstance(annotation, dict):
            # annotation dict
            annotation_dict = {**self.layer.default_values, \
                               **{k: v for k, v in annotation.items() if k in self.layer.attributes}, \
                               **{k: v for k, v in annotation_kwargs.items() if k in self.layer.attributes}}
            annotation = Annotation(self, annotation_dict)
        else:
            raise TypeError('expected Annotation object or dict, but got {}'.format(type(annotation)))

        if annotation not in self._annotations:
            if self.layer.ambiguous or len(self._annotations) == 0:
                self._annotations.append(annotation)
                return annotation

            raise ValueError('The layer is not ambiguous and this span already has a different annotation.')

    def del_annotation(self, idx):
        """Deletes annotation by index `idx`.
        """
        del self._annotations[idx]

    def clear_annotations(self):
        """Removes all annotations from this span.
        Warning: Span without any annotations is dysfunctional.
        It is the responsibility of a programmer to either add new annotations
        to span after clearing it, or to remove the span from the layer
        altogether.
        """
        self._annotations.clear()

    @property
    def annotations(self):
        return self._annotations

    def __getitem__(self, item):
        if isinstance(item, str):
            if self._layer.ambiguous:
                return AttributeList(self, item, index_type='annotations')
            return self._annotations[0][item]
        if isinstance(item, tuple):
            if self._layer.ambiguous:
                return AttributeTupleList(self, item, index_type='annotations')
            return self._annotations[0][item]

        raise KeyError(item)

    @property
    def parent(self):
        if self._parent is None:
            if self._layer is None or self._layer.parent is None:
                return self._parent
            
            text_obj = self._layer.text_object
            if text_obj is None or self._layer.parent not in text_obj.layers:
                return self._parent
            
            self._parent = self._layer.text_object[self._layer.parent].get(self.base_span)
        return self._parent

    @property
    def layer(self):
        return self._layer

    @property
    def legal_attribute_names(self) -> Sequence[str]:
        return self._layer.attributes

    @property
    def start(self) -> int:
        return self._base_span.start

    @property
    def end(self) -> int:
        return self._base_span.end

    @property
    def base_span(self):
        return self._base_span

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
        if self.text_object is None:
            return
        return self._layer.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        if self._layer is not None:
            return self._layer.text_object

    @property
    def raw_text(self):
        return self.text_object.text

    def __setattr__(self, key, value):
        if key in {'_base_span', '_layer', '_annotations', '_parent'}:
            super().__setattr__(key, value)
        elif key in self.legal_attribute_names:
            for annotation in self._annotations:
                setattr(annotation, key, value)
        else:
            raise AttributeError(key)

    def resolve_attribute(self, item):
        """Resolves and returns values of foreign attribute `item`, 
           or resolves and returns a foreign span from layer `item`.
           
           More specifically:
           1) If `item` is a name of a foreign attribute which 
              is listed in the mapping from attribute names to 
              foreign layer names 
              (`attribute_mapping_for_elementary_layers`),
              attempts to find foreign span with the same base 
              span as this span from the foreign layer & returns 
              value(s) of the attribute `item` from that foreign 
              span. 
              (raises KeyError if base span is missing in the 
               foreign layer);
              Note: this is only available when this span belongs to 
              estnltk's `Text` object. The step will be skipped if 
              the span belongs to `BaseText`;

           2) If `item` is a layer attached to span's the text_object,
              attempts to get & return span with the same base span 
              from that layer (raises KeyError if base span is missing);
        """
        if self.text_object is not None:
            if hasattr(self.text_object, 'attribute_mapping_for_elementary_layers'):
                # Attempt to get the foreign attribute of 
                # the same base span of a different attached 
                # layer, based on the mapping of attributes-layers
                # (only available if we have estnltk.text.Text object)
                attribute_mapping = self.text_object.attribute_mapping_for_elementary_layers
                if item in attribute_mapping:
                    return self._layer.text_object[attribute_mapping[item]].get(self.base_span)[item]
            if item in self.text_object.layers:
                # Attempt to get the same base span from 
                # a different attached layer 
                # (e.g parent or child span)
                return self.text_object[item].get(self.base_span)
        else:
            raise AttributeError(("Unable to resolve foreign attribute {!r}: "+\
                                  "the layer is not attached to Text object.").format(item) )
        raise AttributeError("Unable to resolve foreign attribute {!r}.".format(item))

    def __getattr__(self, item):
        if item in self.__getattribute__('_layer').attributes:
            return self[item]
        try:
            return self.resolve_attribute(item)
        except KeyError as key_error:
            raise AttributeError(key_error.args[0]) from key_error

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
            attribute_names = self._layer.attributes
            annotation_strings = []
            for annotation in self._annotations:
                attr_val_repr = _create_attr_val_repr( [(attr, annotation[attr]) for attr in attribute_names] )
                annotation_strings.append( attr_val_repr )
            annotations = '[{}]'.format(', '.join(annotation_strings))
        except:
            annotations = None

        return '{class_name}({text!r}, {annotations})'.format(class_name=self.__class__.__name__, text=text,
                                                              annotations=annotations)

    def _to_html(self, margin=0) -> str:
        return '<b>{}</b>\n{}'.format(
                self.__class__.__name__,
                html_table(spans=[self], attributes=self._layer.attributes, margin=margin, index=False))

    def _repr_html_(self):
        return self._to_html()
