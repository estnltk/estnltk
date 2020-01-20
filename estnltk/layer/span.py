from copy import deepcopy
from reprlib import recursive_repr
from typing import Any, Sequence, List, Tuple, Optional, Union

from estnltk.layer.base_span import BaseSpan, ElementaryBaseSpan, EnvelopingBaseSpan
from estnltk.layer.annotation import Annotation
from estnltk.layer import AttributeList, AttributeTupleList

from .to_html import html_table


class Span:
    """Basic element of an EstNLTK layer.

    Span can exist without annotations. It is the responsibility of a programmer to remove such spans.

    """
    __slots__ = ['base_span', 'layer', 'annotations', '_parent', '_spans']

    # List of protected attribute names
    constant_attributes = frozenset([
        '__doc__', '__hash__','__module__', '__slots__', 'methods', 'constant_attributes',
        'start', 'end', 'text_object', 'text', 'enclosing_text',
        '_ipython_canary_method_should_not_exist_',
        'legal_attribute_names', 'base_spans', 'raw_text'])
    methods = frozenset([
        '__copy__', '__deepcopy__', '__getstate__', '__setstate__',
        '__getattr__', '__setattr__', '__delattr__', '__getitem__', '__settitem__', '__delitem__',
        '__lt__', '__eq__', '__iter__', '__len__', '__contains__', '__repr__',
        'add_annotation', 'del_annotation', 'clear_annotations', 'get',
        'to_records', 'resolve_attribute', '_to_html', '_repr_html_'] + \
        [method for method in dir(object) if callable(getattr(object, method, None)) and method != '__hash__'])

    def __init__(self, base_span: BaseSpan, layer):
        assert isinstance(base_span, BaseSpan), base_span
        # We cannot import Layer without creating circular imports
        # TODO: Make None invalid argument as soon as possible
        assert type(layer).__name__ in {'NoneType', 'Layer'}, layer

        self_setattr = super().__setattr__
        # self.layer: Layer = layer
        self_setattr('layer', layer)
        # self.base_span: BaseSpan = base_span
        self_setattr('base_span', base_span)
        # self.annotations: List[Annotation] = []
        self_setattr('annotations', [])
        # self._parent: Span = None
        self_setattr('_parent', None)
        # self._spans: List[Span] = None
        self_setattr('_spans', None)

    def __copy__(self):
        result = Span(base_span=self.base_span, layer=self.layer)
        result_setattr = super(Span, result).__setattr__
        result_setattr('annotations', self.annotations)
        result_setattr('_parent', self._parent)
        result_setattr('_spans', self._spans)
        return result

    def __deepcopy__(self, memo=None):
        memo = memo or {}
        # Create invalid instance
        cls = self.__class__
        result = cls.__new__(cls)
        # Process span without sub-spans
        if self._spans is None:
            # Add all fields to the instance to make it valid
            # All assignments are safe as self is consistent
            annotations = list()
            result_setattr = super(Span, result).__setattr__
            result_setattr('layer',  None)                         # Mutable
            result_setattr('base_span', self.base_span)            # Immutable
            result_setattr('annotations', annotations)             # List[Mutable]
            result_setattr('_parent', None)                        # Mutable
            result_setattr('_spans', None)                         # Mutable
            # Add newly created valid mutable objects to memo
            memo[id(self)] = result
            memo[id(self.annotations)] = annotations
            # Perform deep copy with a valid memo dict
            result_setattr('layer', deepcopy(self.layer, memo))
            result_setattr('_parent', deepcopy(self._parent, memo))
            annotations.extend(deepcopy(annotation, memo) for annotation in self.annotations)
        else:
            # Add all fields to the instance to make it valid
            # All assignments are safe as self is consistent
            spans = list()
            annotations = list()
            result_setattr = super(Span, result).__setattr__
            result_setattr('layer',  None)                         # Mutable
            result_setattr('base_span', self.base_span)            # Immutable
            result_setattr('annotations', annotations)             # List[Mutable]
            result_setattr('_parent', None)                        # Mutable
            result_setattr('_spans', spans)                        # Mutable
            # Add newly created valid mutable objects to memo
            memo[id(self)] = result
            memo[id(self.annotations)] = annotations
            memo[id(self._spans)] = spans
            # Perform deep copy with a valid memo dict
            result_setattr('layer', deepcopy(self.layer, memo))
            result_setattr('_parent', deepcopy(self._parent, memo))
            spans.extend(deepcopy(self._spans))
            annotations.extend(deepcopy(annotation, memo) for annotation in self.annotations)
        return result

    def __getstate__(self):
        return dict(layer=self.layer, base_span=self.base_span, annotations=self.annotations,
                    parent=self._parent, spans=self._spans)

    def __setstate__(self, state):
        self.__init__(base_span=state['base_span'], layer=state['layer'])
        self_setattr = super().__setattr__
        self_setattr('annotations', state['annotations'])
        self_setattr('_parent', state['parent'])
        self_setattr('_spans', state['spans'])

    def __getattr__(self, item):
        """
        Gives access to all layer attributes that are not shadowed by methods, properties or slots.
        All layer attributes are accessible by index operator regardless of the attribute name.
        RATIONALE: This is the best trade-off between convenience and safety.

        1) layer attributes
        2) layer names
        3) special construction

        None has many meanings here!

        TODO: There are some other attributes that become accessible
        """
        # Python resolves property vs layer attribute name conflict: item is not a method, a slot or a property.

        # TODO: Remove this check when layer cannot be None
        if self.layer is None:
            raise AttributeError(
                "unable to resolve attribute {!r} as the span is not attached a layer.".format(item))

        # Start resolving from legitimate layer attributes
        if item in self.__getattribute__('layer').attributes:
            return self.get(item, None)

        # Abort if text object is not available
        text = self.layer.text_object
        if text is None:
            raise AttributeError(
                "unable to resolve attribute {!r} as the layer is not attached to a text.".format(item))

        # Return span if the attribute is legitimate layer name.
        if item in text.layers:
            # TODO: there are some additional checks

            return text[item].get(self.base_span)

            # if len(target_layer) == 0:
            #     return
            #
            # if target_layer[0].base_span.level >= self.base_span.level:
            #     raise AttributeError('target layer level {} should be lower than {}'.format(
            #         target_layer[0].base_span.level, self.base_span.level))
            #
            # return target_layer.get(self.base_span)

        # Choose the correct lookup table according to the base span level
        if self.base_span.level == 0:
            target_layer = text.attribute_mapping_for_elementary_layers[item]
        else:
            target_layer = text.attribute_mapping_for_enveloping_layers[item]

        # Abort if the target layer is not part of the text
        if target_layer not in text.layers:
            raise AttributeError("???")

        return text[target_layer].get(self.base_span)

        try:
            return self.resolve_attribute(item)
                # if item not in self.text_object.layers:
                #     attribute_mapping = self.text_object.attribute_mapping_for_elementary_layers
                #     return self.layer.text_object[attribute_mapping[item]].get(self.base_span)[item]

#        return self.text_object[item].get(self.base_span)


        except KeyError as key_error:
            raise AttributeError("unresolvable attribute {!r}".format(key))
            raise AttributeError(key_error.args[0]) from key_error

    def __setattr__(self, key, value):
        """
        Gives access to all layer attributes that are not shadowed by methods, properties or slots.
        All layer attributes are accessible by index operator regardless of the attribute name.
        RATIONALE: This is the best trade-off between convenience and safety.
        """
        # Assignable properties
        if key in {'parent', 'spans'}:
            return super().__setattr__(key, value)

        # Constant slots
        elif key in {'annotations', 'base_span', 'layer'}:
            raise AttributeError(
                'an attempt to redefine a constant slot {!r} of Span. Define a new instance.'.format(key))
        # Prohibited slots
        elif key in {'_parent', '_spans'}:
            raise AttributeError('an attempt to assign a private slot {!r} of Span'.format(key))
        # Constant properties and attributes
        elif key in super().__getattribute__('constant_attributes'):
            raise AttributeError('an attempt to redefine a constant property or attribute {!r} of Span.'.format(key))
        # Protected methods
        if key in super().__getattribute__('methods'):
            raise AttributeError('attempt to set an attribute that shadows a method {!r} of Span.'.format(key))

        # Dynamic attributes resolving for layer attributes
        if self.layer is None or key not in self.layer.attributes:
            raise AttributeError('an attempt to set an attribute {!r} that is not a layer attribute.'.format(key))
        # Update the attribute value for all annotations. This may lead to two or more identical annotations
        # TODO: Resolve this issue when it is clear what is the right way to address this issue
        # There are three options:
        # 1) omit assignment altogether
        # 2) allow assignment only for spans with a single annotation
        # 3) restore the invariant after assignment
        for annotation in self.annotations:
            setattr(annotation, key, value)

    def __dir__(self):
        # TODO: To be completed to get all hints in Jupyter
        return super().__dir__()

    def __getitem__(self, item):
        # TODO: define non-failing get version as well!
        # We need to resolve non-slot and non-properties and non-methods
        if isinstance(item, str):
            if self.layer.ambiguous:
                return AttributeList((annotation[item] for annotation in self.annotations), item)
            return self.annotations[0][item]
        if isinstance(item, tuple):
            if self.layer.ambiguous:
                return AttributeTupleList((annotation[item] for annotation in self.annotations), item)
            return self.annotations[0][item]

        raise KeyError(item)

    # Quick hack to get going
    # No annotations is filled with default for non-ambiquous layer
    # This is exception safe
    def get(self, key, default=None):
        if isinstance(key, str):
            if self.layer.ambiguous:
                return AttributeList((annotation.get(key, default) for annotation in self.annotations), key)
            if len(self.annotations) == 0:
                return default
            return self.annotations[0].get(key, default)
        if isinstance(key, tuple):
            raise NotImplementedError('Indeed. Probably not need as well')
            if self.layer.ambiguous:
                return AttributeTupleList((annotation[key] for annotation in self.annotations), key)
            return self.annotations[0][key]

    def __lt__(self, other: Any) -> bool:
        return self.base_span < other.base_span

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Span) \
               and self.base_span == other.base_span \
               and len(self.annotations) == len(other.annotations) \
               and all(s in other.annotations for s in self.annotations)

    # TODO: Correct and test
    # def __iter__(self):
    #     yield from self.spans
    #
    # def __len__(self) -> int:
    #     return len(self.base_span)
    #
    # def __contains__(self, item: Any) -> bool:
    #     return item in self.spans
    # # -----------------------

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
    def start(self) -> int:
        """
        Returns the location of the first character (start) in the span.
        """
        return self.base_span.start

    @property
    def end(self) -> int:
        """
        Returns the location of the character next to the last character (end) in the span.
        RATIONALE: This is in line with the convention how substrings are indexed in Pyhton.
        """
        return self.base_span.end

    @property
    def text_object(self) -> Optional['Text']:
        """
        Returns the text object to which the span belongs or none if the layer is not attached to text.
        """
        # TODO: Drop this check as soon as layer is guaranteed to be not None
        if self.layer is not None:
            return self.layer.text_object


    @property
    def text(self) -> Union[None, str, List[str]]:
        """
        Returns the underlying text fragment associated with the span or none the layer is not attached to text.
        The output type None indicates that the span is not attached to a text. If span is consists of a single text
        fragment a string is returned. Otherwise, the list of strings corresponding to the smallest fragments are
        returned. Note that these fragments may be adjacent or even cover a continuous chunk of text.

        It is theoretically possible that the base span contains fragments that are partially outside of the text.
        These fragments are truncated to be inside the text. No fragments are dropped even if they are completely
        outside of the text. However, you are doing something fundamentally wrong if you have this issue.

        RATIONALE: It is impossible to test whether base_span fits text during initialisation as the layer might be
        detached from text. Omission of empty text fragments would invalidate invariant len(base_span) == len(text)
        for enveloping spans. The alternative output types are for convenience: the natural output for elementary spans
        is string and not one element list of strings.
        """
        if self.text_object is None:
            return None

        text = self.text_object.text
        base_span = self.base_span

        if isinstance(base_span, ElementaryBaseSpan):
            return text[base_span.start:base_span.end]

        return [text[start:end] for start, end in base_span.flatten()]

    @property
    def enclosing_text(self) -> Optional[str]:
        """
        Returns a minimal chunk of text that contains all text fragments in the span or none the layer is not attached
        to text. The output type None indicates that the span is not attached to a text.

        It is theoretically possible that the base span contains fragments that are partially outside of the text.
        Then the enclosing text fragment is truncated to be inside the text.

        RATIONALE: It is impossible to test whether base_span fits text during initialisation as the layer might be
        detached from text. The truncation is the only reasonable option.
        """
        text_object = self.text_object
        if text_object is None:
            return None

        return text_object.text[self.start:self.end]

    @property
    def parent(self) -> Optional['Span']:
        """
        Returns parent span if it is defined or can be computed. The attribute value can be set only once.
        A parent span is a span with the same base span from which the span is derived by adding additional attributes.

        By default the parent span is taken form the parent layer from which the current layer is derived.
        However, it is possible to take the parent span from other layers if it makes sense. For that one must
        explicitly define the value and take responsibility for potential confusion it might create.

        RATIONALE: This property is defined for efficiency and convenience. One often needs to combine matching spans
        from different layers. Existing parent attribute allows to omit search for a matching spans. As such it is
        useful only if one frequently uses its value in computations.
        """
        parent = self._parent
        if parent is None:
            # Lets try to compute parent
            layer = self.__getattribute__('layer')
            # Be explicit: bool conversion can fail sometimes
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

    @property
    def spans(self) -> Optional[List['Span']]:
        """
        Returns a list of sub-spans from which the current span is composed. The attribute value can be set only once
        but there is a default algorithm to compute its value when the attribute value is undefined.
        A span is a sub-span if its base span is a direct sub-span of a base span of the compound span.

        By default sub-spans are taken form the layer from which the current layer is derived. The algorithm uses all
        or nothing tactic -- it some sub-spans cannot be resolved the algorithm returns none.

        However, it is possible to take a sub-span from other layers if it makes sense. For that one must explicitly
        define the list of spans and take responsibility for potential confusion it might create.

        RATIONALE: This property is defined for efficiency and convenience. One often needs to combine matching spans
        from different layers. Existing spans attribute allows to omit search for a sub-spans. As such it is
        useful only if one frequently uses sub-span values in computations.
        """
        spans = self._spans
        if spans is None:
            # Lets try to compute parent
            layer = self.__getattribute__('layer')
            # Be explicit: bool conversion can fail sometimes
            if layer is None or layer.enveloping is None:
                return spans
            text = layer.text_object
            # Be explicit bool conversion can fail sometimes
            if text is None or layer.enveloping not in text.layers:
                return spans
            # We can search for individual sub-spans
            resolve_base_span = self.layer.text_object[self.layer.enveloping].get
            spans = tuple(resolve_base_span(base) for base in self.base_span)
            # Make sure that all sub-spans are resolved
            if any(span is None for span in spans):
                return None
            # We have it. Lets cache the result
            super().__setattr__('_spans', spans)
        return spans

    @spans.setter
    def spans(self, value):
        # Validity checks
        if self._spans is not None:
            raise AttributeError("value of 'spans' property is already fixed. Define a new instance.")
        elif not isinstance(self.base_span, EnvelopingBaseSpan):
            raise AttributeError("'spans' property cannot be set as the span contains no sub-spans.")
        elif not isinstance(value, (list, tuple)) or any(not isinstance(span, Span) for span in value):
            raise TypeError("'spans' must be a list or tuple of Span objects.")
        elif len(self.base_span) != len(value):
            raise ValueError("an invalid 'spans' value: the number of spans must match the sub-span count.")
        # Validity check for individual elements
        for span, base_span in zip(value, self.base_span._spans):
            if span.base_span != base_span:
                raise ValueError("an invalid 'spans' value: 'base_span' attribute must match a sub-span location.")
        # Assignment
        return super().__setattr__('_spans', value)

    def add_annotation(self, annotation: Annotation) -> Annotation:
        # TODO: Allow less attributes than required!
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

    # TODO: To be pushed into the layer as layer does the resolving
    def resolve_attribute(self, item):
        if item not in self.text_object.layers:
            attribute_mapping = self.text_object.attribute_mapping_for_elementary_layers
            return self.layer.text_object[attribute_mapping[item]].get(self.base_span)[item]

        return self.text_object[item].get(self.base_span)

    # TODO: To be inlined
    # Why do we need to change margin!?
    def _to_html(self, margin=0) -> str:
        try:
            return '<b>{}</b>\n{}'.format(
                    self.__class__.__name__,
                    html_table(spans=[self], attributes=self.layer.attributes, margin=margin, index=False))
        except:
            return str(self)

    # We can add kwargs fror conf through display
    def _repr_html_(self):
        return self._to_html()

    @property
    def legal_attribute_names(self) -> Optional[Sequence[str]]:
        """
        Deprecated property. Do not use it. Will be removed as soon as possible.
        TODO: Remove references in morph_common.py to achieve this
        """
        # TODO: Drop this check as soon as layer is guaranteed to be not None
        if self.layer is not None:
            return self.layer.attributes

    @property
    def base_spans(self) -> List[Tuple[int, int]]:
        """
        Deprecated property. Do not use it. Will be removed as soon as possible.
        TODO: Remove references in texta_exporter.py to achieve this
        """
        return [(self.start, self.end)]

    @property
    def raw_text(self) -> str:
        """
        Deprecated property. Do not use it. Will be removed as soon as possible.
        TODO: Remove references in enveloping_span.py to achieve this
        """
        if self.text_object is not None:
            return self.text_object.text
        else:
            return ""
