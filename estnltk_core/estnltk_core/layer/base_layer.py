import keyword
from typing import Union, List, Sequence
import pandas
import collections
import warnings
import pkgutil

from copy import deepcopy

from estnltk_core import BaseSpan, ElementaryBaseSpan, EnvelopingBaseSpan
from estnltk_core import Span, EnvelopingSpan, Annotation, SpanList
from estnltk_core.layer import AmbiguousAttributeTupleList, AmbiguousAttributeList, AttributeTupleList, AttributeList


def to_base_span(x) -> BaseSpan:
    """Reduces estnltk's annotation structure (BaseLayer, Span or Annotation) 
       to ElementaryBaseSpan or EnvelopingBaseSpan or creates ElementaryBaseSpan 
       or EnvelopingBaseSpan from given sequence of span locations. 
       
       If param x is BaseLayer, returns EnvelopingBaseSpan enveloping all 
       spans of the layer. 
       A sequence of span locations will converted into appropriate base span: 
       *) (start, end) -> ElementaryBaseSpan 
       *) [(s1, e1), ... (sN, eN)] -> EnvelopingBaseSpan 
    """
    if isinstance(x, BaseSpan):
        return x
    if isinstance(x, Span):
        return x.base_span
    if isinstance(x, Annotation):
        return x.span.base_span
    if isinstance(x, (List, tuple, BaseLayer)):
        if len(x) == 2 and isinstance(x[0], int) and isinstance(x[1], int):
            return ElementaryBaseSpan(*x)
        return EnvelopingBaseSpan(to_base_span(y) for y in x)
    raise TypeError('{} ({}) cannot be converted to base span'.format(type(x), x))


class BaseLayer:
    """Basic container for text annotations.

    BaseLayer is used to give annotations to text fragments. Each annotation consists of:
        selected text fragment
        corresponding annotations
    Annotation consists of attributes which can have arbitrary names except reserved words:
        meta - meta information
        start
        end

    It is possible to add meta-information about layer as a whole by specifying layer.meta,
    which is a dictionary of type MutableMapping[str, Any]. However we strongly advise to use
    the following list of attribute types:
        str
        int
        float
        DateTime
    as database serialisation does not work for other types. See [estnltk.storage.postgres] for further documentation.

    """
    __slots__ = ['name', 'default_values', 'attributes', 'parent', 'enveloping', '_span_list', 'ambiguous',
                 'text_object', 'serialisation_module', 'meta']

    def __init__(self,
                 name: str,
                 attributes: Sequence[str] = (),
                 text_object=None,
                 parent: str = None,
                 enveloping: str = None,
                 ambiguous: bool = False,
                 default_values: dict = None,
                 serialisation_module=None
                 ) -> None:
        assert parent is None or enveloping is None, "can't be derived AND enveloping"

        self.default_values = default_values or {}
        assert isinstance(self.default_values, dict)

        # list of legal attribute names for the layer
        self.attributes = attributes

        # name of the layer
        assert name.isidentifier() and not \
            keyword.iskeyword(name), 'layer name must be a valid python identifier, {!r}'.format(name)

        self.name = name

        # the name of the parent layer.
        self.parent = parent

        # the name of the layer this class envelops
        # sentences envelop words
        # paragraphs envelop sentences
        # and so on...
        self.enveloping = enveloping

        # Container for spans
        self._span_list = SpanList()

        # boolean for if this is an ambiguous layer
        # if True, add_span will behave differently and add a SpanList instead.
        self.ambiguous = ambiguous  # type: bool

        # placeholder. is set when `_add_layer` is called on text object
        self.text_object = text_object  # type: Text

        self.serialisation_module = serialisation_module

        self.meta = {}

    def __copy__(self):
        """
        Creates a new layer object with the same content.

        New object is needed as a same layer object cannot be part of another text object.
        """
        result = self.__class__(
            name=self.name,
            attributes=self.attributes,
            text_object=self.text_object,
            parent=self.parent,
            enveloping=self.enveloping,
            ambiguous=self.ambiguous,
            default_values=self.default_values,
            serialisation_module=self.serialisation_module)
        result._span_list = self._span_list
        return result

    def __deepcopy__(self, memo={}):
        result = self.__class__( name=self.name,
                                 attributes=deepcopy(self.attributes, memo),
                                 text_object=self.text_object,
                                 parent=self.parent,
                                 enveloping=self.enveloping,
                                 ambiguous=self.ambiguous,
                                 default_values=deepcopy(self.default_values, memo),
                                 serialisation_module=self.serialisation_module )
        memo[id(self)] = result
        result.meta = deepcopy(self.meta, memo)
        for span in self:
            for annotation in span.annotations:
                result.add_annotation(span.base_span, **annotation)
        return result

    @property
    def layer(self):
        return self

    @property
    def start(self):
        return self._span_list.spans[0].start

    @property
    def end(self):
        # Important: SpanList is sorted only by start indexes, 
        # so we have to seek the farthest span ending
        return max( sp.end for sp in self._span_list.spans )

    @property
    def spans(self):
        return self._span_list.spans

    @property
    def text(self):
        result = []
        for span in self._span_list.spans:
            if isinstance(span, EnvelopingSpan):
                result.extend(span.text)
            else:
                result.append(span.text)
        return result

    @property
    def enclosing_text(self):
        return self.text_object.text[self.start:self.end]

    def attribute_list(self, attributes):
        """ Returns all annotations of this layer with selected `attributes` (snapshot of attributes).
            Returns:
                AttributeList -- if the layer is not ambiguous and only one attribute was selected;
                AttributeTupleList -- if the layer is not ambiguous and more than one attributes were selected;
                AmbiguousAttributeList -- if the layer is ambiguous and only one attribute was selected;
                AmbiguousAttributeTupleList -- if the layer is ambiguous and more than one attributes were selected;
        """
        assert isinstance(attributes, (str, list, tuple)), str(type(attributes))
        if not attributes:
            raise IndexError('no attributes: ' + str(attributes))
        if self.ambiguous:
            if isinstance(attributes, (list, tuple)):
                result = AmbiguousAttributeTupleList(
                        (((getattr(a, attr) for attr in attributes) for a in sp.annotations)
                         for sp in self.spans), attributes)
            else:
                result = AmbiguousAttributeList(((getattr(a, attributes) for a in sp.annotations)
                                                 for sp in self.spans), attributes)
        else:
            if isinstance(attributes, (list, tuple)):
                result = AttributeTupleList([[getattr(sp, attr) for attr in attributes] for sp in self.spans],
                                            attributes)
            else:
                result = AttributeList([getattr(sp, attributes) for sp in self.spans], attributes)
        return result

    def add_span(self, span: Span) -> Span:
        """Adds new Span (or EnvelopingSpan) to this layer.
           Before adding, span will be validated:
           * the span must have at least one annotation;
           * the span must have exactly one annotation (if the layer is not ambiguous);
           * the span belongs to this layer;
           
           Note that you cannot add two Spans (EnvelopingSpans) that 
           have exactly the same text location (base span); however, 
           partially overlapping spans are allowed.
        """
        assert isinstance(span, Span), str(type(span))
        assert len(span.annotations) > 0, span
        assert self.ambiguous or len(span.annotations) == 1, span
        assert span.layer is self, span.layer

        if self.get(span) is not None:
            raise ValueError('this layer already has a span with the same base span')

        self._span_list.add_span(span)

        return span

    def remove_span(self, span):
        """Removes given span from the layer.
        """
        self._span_list.remove_span(span)

    def add_annotation(self, base_span, **attributes) -> Annotation:
        """Adds new annotation (from dict `attributes`) to given text location `base_span`.
        
           Location `base_span` can be:
           * (start, end) or ElementaryBaseSpan or Span;
           * [(s1, e1), ... (sN, eN)] or EnvelopingBaseSpan or EnvelopingSpan or BaseLayer if the layer is enveloping;
           * Annotation if it is attached to Span (appropriately non-enveloping or enveloping);
           
           `attributes` should contain attribute assignments for the annotation. 
           Missing attributes will be filled in with layer's default_values 
           (None values, if defaults have not been explicitly set).
           
           Note that you can add two or more annotations to exactly the 
           same `base_span` location only if the layer is ambiguous. 
           however, partially overlapping locations are always allowed. 
        """
        base_span = to_base_span(base_span)
        # Make it clear, if we got non-enveloping or enveloping span properly
        # (otherwise we may run into obscure error messages later)
        if self.enveloping is not None and not isinstance(base_span, EnvelopingBaseSpan):
            raise TypeError('Cannot add {!r} to enveloping layer. Enveloping span is required.'.format(base_span))
        elif self.enveloping is None and isinstance(base_span, EnvelopingBaseSpan):
            raise TypeError('Cannot add {!r} to non-enveloping layer. Elementary span is required.'.format(base_span))
        
        attributes = {**self.default_values, **{k: v for k, v in attributes.items() if k in self.attributes}}
        span = self.get(base_span)

        if self.enveloping is not None:
            if span is None:
                span = EnvelopingSpan(base_span=base_span, layer=self)
                annotation = span.add_annotation(Annotation(span, **attributes))
                self._span_list.add_span(span)
            else:
                annotation = span.add_annotation(Annotation(span, **attributes))

            return annotation

        if self.ambiguous:
            if span is None:
                span = Span(base_span, self)
                self._span_list.add_span(span)
            assert isinstance(span, Span), span
            return span.add_annotation(Annotation(span, **attributes))

        if span is not None:
            raise ValueError('the layer is not ambiguous and already contains this span')

        span = Span(base_span=base_span, layer=self)
        annotation = span.add_annotation(Annotation(span, **attributes))
        self._span_list.add_span(span)
        return annotation

    def check_span_consistency(self) -> None:
        """Checks for layer's span consistency.
           Checks that:
           * spans of the layer are sorted;
           * each span has at least one annotation;
           * each span has at exactly one annotation if the layer is not ambiguous;
           * all annotations have exactly the same attributes as the layer;
        """
        attribute_names = set(self.attributes)

        last_span = None
        for span in self:
            assert last_span is None or last_span < span
            last_span = span

            annotations = span.annotations

            assert len(annotations) > 0, 'the span {} has no annotations'.format(span)
            assert self.ambiguous or len(annotations) == 1, \
                'the layer is not ambiguous but the span {} has {} annotations'.format(span, len(annotations))

            for annotation in annotations:
                assert set(annotation) == attribute_names, \
                    'extra annotation attributes: {}, missing annotation attributes: {} in layer {!r}'.format(
                            set(annotation) - attribute_names,
                            attribute_names - set(annotation),
                            self.name)

    def __getattr__(self, item):
        # Deny access to other attributes
        raise AttributeError('attributes cannot be accessed directly in {}'.format(self.__class__.__name__))

    def _set_attributes(self, attributes: Sequence[str]):
        assert not isinstance(attributes, str), attributes
        attributes = tuple(attributes)
        assert all(attr.isidentifier() for attr in attributes), attributes
        assert len(attributes) == len(set(attributes)), 'repetitive attribute name: ' + str(attributes)
        super().__setattr__('attributes', attributes)

        try:
            # due to unordered __slots__ in case of Python <= 3.5
            # 'default_values' might not be set by __deepcopy__ before setting 'attributes'
            #  which would lead to nasty errors
            self.__getattribute__('default_values')
        except AttributeError:
            self.default_values = {}

        for attr in set(self.default_values) - set(attributes):
            del self.default_values[attr]

        self.default_values = {attr: self.default_values.get(attr) for attr in attributes}

    def __setattr__(self, key, value):
        if key == 'attributes':
            return self._set_attributes(value)
        super().__setattr__(key, value)

    def __iter__(self):
        return iter(self._span_list.spans)

    def __setitem__(self, key: int, value: Span):
        self._span_list[key] = value

    def index(self, x, *args) -> int:
        return self._span_list.index(x, *args)

    def __getitem__(self, item) -> Union[Span, 'BaseLayer', 'Layer', AmbiguousAttributeTupleList]:
        if isinstance(item, int):
            return self._span_list[item]

        if isinstance(item, BaseSpan):
            return self._span_list.get(item)

        if item == [] or item == ():
            raise IndexError('no attributes: ' + str(item))

        if isinstance(item, str) or isinstance(item, (list, tuple)) and all(isinstance(s, str) for s in item):
            return self.attribute_list(item)

        if isinstance(item, tuple) and len(item) == 2 \
           and (callable(item[0])
                or isinstance(item[0], (int, slice))
                or (isinstance(item[0], (tuple, list)) and all(isinstance(i, int) for i in item[0])))\
           and (isinstance(item[1], str)
                or isinstance(item[1], (list, tuple)) and all(isinstance(i, str) for i in item[1])):
            if isinstance(item[0], int):
                return self[item[1]][item[0]]
            return self[item[0]][item[1]]

        layer = self.__class__(name=self.name,
                               attributes=self.attributes,
                               text_object=self.text_object,
                               parent=self.parent,
                               enveloping=self.enveloping,
                               ambiguous=self.ambiguous,
                               default_values=self.default_values)

        if isinstance(item, slice):
            wrapped = self._span_list.spans.__getitem__(item)
            layer._span_list.spans = wrapped
            return layer
        if isinstance(item, (list, tuple)):
            if all(isinstance(i, bool) for i in item):
                if len(item) != len(self):
                    warnings.warn('Index boolean list not equal to length of layer: {}!={}'.format(len(item), len(self)))
                wrapped = [s for s, i in zip(self._span_list.spans, item) if i]
                layer._span_list.spans = wrapped
                return layer
            if all(isinstance(i, int) for i in item):
                wrapped = [self._span_list.spans.__getitem__(i) for i in item]
                layer._span_list.spans = wrapped
                return layer
            if all(isinstance(i, BaseSpan) for i in item):
                wrapped = [self._span_list.get(i) for i in item]
                layer._span_list.spans = wrapped
                return layer
        if callable(item):
            wrapped = [span for span in self._span_list.spans if item(span)]
            layer._span_list.spans = wrapped
            return layer

        raise TypeError('index not supported: ' + str(item))

    def __delitem__(self, key):
        self._span_list.remove_span(self[key])

    def get(self, item):
        if len(self._span_list) == 0:
            return
        if isinstance(item, Span):
            item = item.base_span
        if isinstance(item, BaseSpan):
            level = self._span_list[0].base_span.level
            if level == item.level:
                return self._span_list.get(item)
            item = item.reduce(level)

        if isinstance(item, (list, tuple)):
            layer = self.__class__(name=self.name,
                                   attributes=self.attributes,
                                   text_object=self.text_object,
                                   parent=self.parent,
                                   enveloping=self.enveloping,
                                   ambiguous=self.ambiguous,
                                   default_values=self.default_values)

            wrapped = [self._span_list.get(i) for i in item]
            assert all(s is not None for s in wrapped)
            layer._span_list.spans = wrapped
            return layer

        raise ValueError(item)

    def __len__(self):
        return len(self._span_list)

    def __repr__(self):
        return '{classname}(name={self.name!r}, attributes={self.attributes}, spans={self._span_list})'.format(classname=self.__class__.__name__, self=self)

    def metadata(self):
        """
        Return DataFrame with layer metadata.
        """
        rec = [{'layer name': self.name,
                'attributes': ', '.join(self.attributes),
                'parent': str(self.parent),
                'enveloping': str(self.enveloping),
                'ambiguous': str(self.ambiguous),
                'span count': str(len(self._span_list.spans))}]
        return pandas.DataFrame.from_records(rec,
                                             columns=['layer name', 'attributes',
                                                      'parent', 'enveloping',
                                                      'ambiguous', 'span count'])

    print_start_end = False

    def _repr_html_(self):
        if self.meta:
            data = {'key': sorted(self.meta), 'value': [self.meta[k] for k in sorted(self.meta)]}
            meta_table = pandas.DataFrame(data, columns=['key', 'value'])
            meta_table = meta_table.to_html(header=False, index=False)
            meta = '\n'.join(('<h4>Metadata</h4>', meta_table))
        else:
            meta = ''

        attributes = []
        if self.text_object is None:
            text_object = 'No Text object.'
        else:
            attributes.append('text')
            text_object = ''
        if self.print_start_end:
            attributes.extend(['start', 'end'])
        attributes.extend(self.attributes)
        if not attributes:
            attributes = ['start', 'end']
        table_1 = self.metadata().to_html(index=False, escape=False)
        table_2 = ''
        if attributes:
            table_2 = self.attribute_list(attributes).to_html(index='text')
        return '\n'.join(('<h4>{}</h4>'.format(self.__class__.__name__), meta, text_object, table_1, table_2))

    def diff(self, other):
        if self is other:
            return None
        if not isinstance(other, BaseLayer):
            return 'Other is not a Layer.'
        if self.name != other.name:
            return "Layer names are different: {self.name}!={other.name}".format(self=self, other=other)
        if tuple(self.attributes) != tuple(other.attributes):
            return "{self.name} layer attributes differ: {self.attributes} != {other.attributes}".format(self=self,
                                                                                                         other=other)
        if self.ambiguous != other.ambiguous:
            return "{self.name} layer ambiguous differs: {self.ambiguous} != {other.ambiguous}".format(self=self,
                                                                                                       other=other)
        if self.parent != other.parent:
            return "{self.name} layer parent differs: {self.parent} != {other.parent}".format(self=self, other=other)
        if self.enveloping != other.enveloping:
            return "{self.name} layer enveloping differs: {self.enveloping}!={other.enveloping}".format(self=self,
                                                                                                        other=other)
        if self.serialisation_module != other.serialisation_module:
            return "{self.name!r} layer dict converter modules are different: " \
                   "{self.dict_converter_module!r}!={other.dict_converter_module!r}".format(self=self, other=other)
        if self._span_list != other._span_list:
            return "{self.name} layer spans differ".format(self=self)
        return None

    def __eq__(self, other):
        return self.diff(other) is None
