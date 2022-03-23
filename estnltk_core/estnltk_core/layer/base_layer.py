import keyword
from typing import Union, List, Sequence, Dict, Any, Optional
import pandas
import collections
import warnings
import pkgutil

from copy import copy, deepcopy

from estnltk_core import BaseSpan, ElementaryBaseSpan, EnvelopingBaseSpan
from estnltk_core import Span, EnvelopingSpan, Annotation, SpanList
from estnltk_core.layer import AmbiguousAttributeTupleList, AmbiguousAttributeList, AttributeTupleList, AttributeList


def to_base_span(x) -> BaseSpan:
    """Reduces estnltk's annotation structure to BaseSpan or creates BaseSpan from raw location.

       If parameter `x` is estnltk's structure, returns corresponding base span:

       * BaseSpan -> BaseSpan (returns input);
       * Span -> ElementaryBaseSpan;
       * EnvelopingSpan -> EnvelopingBaseSpan;
       
       If parameter `x` is BaseLayer, returns EnvelopingBaseSpan enveloping all
       spans of the layer. 
       
       If parameter `x` is a raw location, creates and returns appropriate base span:

       * (start, end) -> ElementaryBaseSpan;
       * [(start_1, end_1), ... (start_N, end_N)] -> EnvelopingBaseSpan;
    """
    if isinstance(x, BaseSpan):
        return x
    if isinstance(x, Span):
        return x.base_span
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
    Annotation consists of attributes which can have arbitrary names. 
    However, attribute names that are layer or span attributes (e.g. meta, start, end) are 
    accessible only with indexing operator as the attribute access is not possible.

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
                 'text_object', 'serialisation_module', 'secondary_attributes', 'meta']

    def __init__(self,
                 name: str,
                 attributes: Sequence[str] = (),
                 secondary_attributes: Sequence[str] = (),
                 text_object: Union['BaseText','Text']=None,
                 parent: str = None,
                 enveloping: str = None,
                 ambiguous: bool = False,
                 default_values: dict = None,
                 serialisation_module=None
                 ) -> None:
        """
        Initializes a new BaseLayer object based on given configuration.
        
        Parameter `name` is mandatory and should be a descriptive name of the layer.
        It is advisable to use layer names that are legitimate Pyhton attribute names 
        (e.g. 'morphology', 'syntax_layer') and are not attributes of text objects. 
        Otherwise, the layer is accessible only with indexing operator.
        
        Parameter `attributes` lists legal attribute names for the layer. 
        If an annotation is added to the layer, only values of legal attributes will 
        be added, and values of illegal attributes will be ignored. 

        Parameter `secondary_attributes` lists names of layer's attributes which 
        will be skipped while comparing two layers. Usually this means that these 
        attributes contain redundant information. Another reason for marking attribute 
        as secondary is avoiding (infinite) recursion in comparison. For instance, 
        attributes referring to parent and children spans in the syntax layer are 
        marked as secondary, because they are recursive and comparing recursive spans 
        is not supported. 
        All secondary attributes must also be present in `attributes`.

        Parameter `text_object` specifies the Text object of this layer. 
        Note that the Text object becomes fully connected with the layer only 
        after text.add_layer( layer ) has been called.
        
        Parameter `parent` is used to specify the name of the parent layer, declaring that 
        each span of this layer has a parent span on the parent layer.
        For instance, 'morph_analysis' layer takes 'words' layer as a parent, because 
        morphological properties can be described on each word.
        
        Parameter `enveloping` specifies the name of the layer this layer envelops, meaning 
        that each span of this layer envelops (wraps around) multiple spans of that layer. 
        For instance, 'sentences' layer is enveloping around 'words' layer, and 'paragraphs' 
        layer is enveloping around 'sentences' layer. 
        
        Note that `parent` and `enveloping` cannot be set simultaneously -- one of them 
        must be None.
        
        If ambiguous is set, then this layer can have multiple annotations on the same 
        location (same span).
        
        Parameter `default_values` can be used to specify default values for `attributes`
        in case they are missing from the annotation. If not specified, missing attributes 
        will obtain None values.
        
        Parameter `serialisation_module` specifies name of the serialisation module. 
        If left unspecified, then default serialisation module is used.
        """
        default_values = default_values or {}
        assert isinstance(default_values, dict)
        self.default_values = default_values

        self.attributes = attributes
        self.secondary_attributes = secondary_attributes

        # name of the layer
        assert name is not None and len(name) > 0 and not name.isspace(), \
            'layer name cannot be empty or consist of only whitespaces {!r}'.format(name)
        self.name = name

        assert parent is None or enveloping is None, "can't be derived AND enveloping"
        self.parent = parent
        self.enveloping = enveloping

        self._span_list = SpanList()

        self.ambiguous = ambiguous

        self.text_object = text_object

        self.serialisation_module = serialisation_module

        self.meta = {}

    def __copy__(self):
        """
        Creates a new Layer object with the same content.

        TODO: this functionality will be deprecated in the future. 
        Normally, you won't need to copy the layer. If you want to 
        use copying for safely deleting spans, copy layer.spans 
        instead:
        
            for span in copy(layer.spans):
                layer.remove_span(span)
        """
        result = self.__class__(
            name=self.name,
            attributes=self.attributes,
            secondary_attributes=self.secondary_attributes,
            text_object=self.text_object,
            parent=self.parent,
            enveloping=self.enveloping,
            ambiguous=self.ambiguous,
            default_values=self.default_values,
            serialisation_module=self.serialisation_module)
        result.meta = copy(self.meta)
        result._span_list = copy(self._span_list)
        # TODO: fix the span level ?
        return result
    
    def __deepcopy__(self, memo=None):
        """
        Makes a deep copy from the layer. Essential for deep copying of Text objects.
        
        Layer's inner components -- spans and annotations -- are also deep-copied,
        along with the Text object of the layer.
        """
        memo = memo or {}
        result = self.__class__( name=self.name,
                                 attributes=deepcopy(self.attributes, memo),
                                 secondary_attributes=deepcopy(self.secondary_attributes, memo),
                                 text_object=None,
                                 parent=self.parent,
                                 enveloping=self.enveloping,
                                 ambiguous=self.ambiguous,
                                 default_values=deepcopy(self.default_values, memo),
                                 serialisation_module=self.serialisation_module )
        memo[id(self)] = result
        result.meta = deepcopy(self.meta, memo)
        for span in self:
            deepcopy_span = deepcopy( span, memo )
            deepcopy_span._layer = result
            result._span_list.add_span( deepcopy_span )
        result.text_object = deepcopy( self.text_object, memo )
        return result

    def __setattr__(self, key, value):
        if key == 'attributes':
            # check attributes
            attributes = value
            assert not isinstance(attributes, str), \
                'attributes must be a list or tuple of strings, not a single string {!r}'.format(attributes)
            attributes = tuple(attributes)
            assert len(attributes) == len(set(attributes)), 'repetitive attribute name: ' + str(attributes)
            # set attributes
            super().__setattr__('attributes', attributes)
            # (re)set default values
            self.default_values = {attr: self.default_values.get(attr) for attr in attributes}
            # TODO: secondary_attributes should also be updated, but this can be done only
            # after secondary_attributes have been initialized
            return
        if key == 'secondary_attributes':
            # check secondary_attributes
            assert not isinstance(value, str), \
                'secondary_attributes must be a list or tuple of strings, not a single string {!r}'.format(value)
            secondary_attributes = value or ()
            for sec_attrib in secondary_attributes:
                if sec_attrib not in self.attributes:
                    raise ValueError( \
                        'secondary attribute {!r} not listed in attributes {!r}'.format(sec_attrib, self.attributes))
            # set secondary_attributes
            secondary_attributes = tuple(secondary_attributes)
            super().__setattr__('secondary_attributes', secondary_attributes)
            return
        super().__setattr__(key, value)

    def __setitem__(self, key: int, value: Span):
        self._span_list[key] = value

    def __getattr__(self, item):
        # Deny access to other attributes
        raise AttributeError('attribute {} cannot be accessed directly in {}'.format(item, self.__class__.__name__))

    def __getitem__(self, item) -> Union[Span, 'BaseLayer', 'Layer', AmbiguousAttributeTupleList]:
        if isinstance(item, int):
            # Expected call: layer[index]
            # Returns Span
            return self._span_list[item]

        if isinstance(item, BaseSpan):
            # Example call: layer[ parent_layer[0].base_span ]
            # Returns Span
            return self._span_list.get(item)

        if item == [] or item == ():
            # Unexpected call: layer[[]]
            raise IndexError('no attributes: ' + str(item))

        if isinstance(item, str) or isinstance(item, (list, tuple)) and all(isinstance(s, str) for s in item):
            # Expected call: layer[attribute] or layer[attributes]
            # Returns AmbiguousAttributeTupleList
            if isinstance(item, (list, tuple)):
                # Separate regular attributes from index attributes
                attributes = \
                    [attr for attr in item if attr not in ['start', 'end'] or attr in self.attributes]
                index_attributes = \
                    [attr for attr in item if attr in ['start', 'end'] and attr not in self.attributes]
                return self.attribute_values(attributes, index_attributes=index_attributes)
            return self.attribute_values(item)

        if isinstance(item, tuple) and len(item) == 2:
            # Expected call: layer[indexes, attributes]
            # Check that the first item specifies an index or a range indexes
            # Can also be a callable function validating suitable spans
            first_ok = callable(item[0]) or \
                       isinstance(item[0], (int, slice)) or \
                       (isinstance(item[0], (tuple, list)) and all(isinstance(i, int) for i in item[0]))
            # Check that the second item specifies an attribute or a list of attributes
            second_ok = isinstance(item[1], str) or \
                        isinstance(item[1], (list, tuple)) and all(isinstance(i, str) for i in item[1])
            if first_ok and second_ok:
                if isinstance(item[0], int):
                    # Select attribute(s) of a single span
                    # Example: text.morph_analysis[0, ['partofspeech', 'lemma']]
                    # Returns Span -> List
                    return self[item[1]][item[0]]
                # Select attribute(s) over multiple spans
                # Example: text.morph_analysis[0:5, ['partofspeech', 'lemma']]
                # Returns AmbiguousAttributeTupleList
                return self[item[0]][item[1]]

            # If not first_ok or not second_ok, then we need to check 
            # if this could be a list call with 2-element list, see below 
            # for details

        layer = self.__class__(name=self.name,
                               attributes=self.attributes,
                               secondary_attributes=self.secondary_attributes,
                               text_object=self.text_object,
                               parent=self.parent,
                               enveloping=self.enveloping,
                               ambiguous=self.ambiguous,
                               default_values=self.default_values)
        # keep the span level same
        layer._span_list = SpanList(span_level=self.span_level)
        if isinstance(item, slice):
            # Expected call: layer[start:end]
            # Returns Layer
            wrapped = self._span_list.spans.__getitem__(item)
            layer._span_list.spans = wrapped
            return layer
        if isinstance(item, (list, tuple)):
            if all(isinstance(i, bool) for i in item):
                # Expected call: layer[list_of_bools]
                # Returns Layer
                if len(item) != len(self):
                    warnings.warn('Index boolean list not equal to length of layer: {}!={}'.format(len(item), len(self)))
                wrapped = [s for s, i in zip(self._span_list.spans, item) if i]
                layer._span_list.spans = wrapped
                return layer
            if all(isinstance(i, int) and not isinstance(i, bool) for i in item):
                # Expected call: layer[list_of_indexes]
                # Returns Layer
                wrapped = [self._span_list.spans.__getitem__(i) for i in item]
                layer._span_list.spans = wrapped
                return layer
            if all(isinstance(i, BaseSpan) for i in item):
                # Expected call: layer[list_of_base_span]
                # Returns Layer
                wrapped = [self._span_list.get(i) for i in item]
                layer._span_list.spans = wrapped
                return layer
        if callable(item):
            # Expected call: layer[selector_function]
            # Returns Layer
            wrapped = [span for span in self._span_list.spans if item(span)]
            layer._span_list.spans = wrapped
            return layer

        raise TypeError('index not supported: ' + str(item))

    def get(self, item):
        """ Finds and returns Span (or EnvelopingSpan) corresponding to the given (Base)Span item(s).
            If this layer is empty, returns None.
            If the parameter item is a sequence of BaseSpans, then returns a new Layer populated
            with specified spans and bearing the same configuration as this layer. For instance, 
            if you pass a span of the enveloping layer as item, then you'll get a snapshot layer 
            with all the spans of this layer wrapped by the enveloping span:
           
                # get a snapshot words-layer bearing all words of the first sentence
                text['words'].get( text['sentences'][0] )
        """
        if len(self._span_list) == 0:
            return
        if isinstance(item, Span):
            item = item.base_span
        if isinstance(item, BaseSpan):
            if self.span_level == item.level:
                return self._span_list.get(item)
            item = item.reduce(self.span_level)

        if isinstance(item, (list, tuple)):
            layer = self.__class__(name=self.name,
                                   attributes=self.attributes,
                                   secondary_attributes=self.secondary_attributes,
                                   text_object=self.text_object,
                                   parent=self.parent,
                                   enveloping=self.enveloping,
                                   ambiguous=self.ambiguous,
                                   default_values=self.default_values)
            # keep the span level same
            layer._span_list = SpanList(span_level=self.span_level)
            wrapped = [self._span_list.get(i) for i in item]
            assert all(s is not None for s in wrapped)
            layer._span_list.spans = wrapped
            return layer

        raise ValueError(item)

    def index(self, x, *args) -> int:
        '''Returns the index of the given span in this layer.
           Use this to find the location of the span.
           
           TODO: this is only used in legacy serialization, 
           so it can also be deprecated/removed if there are 
           no other usages.
        '''
        return self._span_list.index(x, *args)

    def __delitem__(self, key):
        self._span_list.remove_span(self[key])

    def __iter__(self):
        return iter(self._span_list.spans)

    def __len__(self):
        return len(self._span_list)

    def __eq__(self, other):
        return self.diff(other) is None

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
    def span_level(self):
        """Returns an integer conveying depth of enveloping 
           structure of this layer, or None if the structure 
           has not been initiated yet (no spans have been 
           added to this layer).
           
           span_level=0 indicates that spans of the layer 
           mark raw text positions (start, end), and 
           span_level > 0 indicates that spans of the 
           layer envelop around smaller level spans 
           (for details, see the BaseSpan docstring from
           estnltk_core).
           
           Note: if this layer has a parent layer, then this 
           layer has the same span_level as the parent layer.
        """
        return self._span_list.span_level

    @property
    def text(self):
        """Returns a list of text fragments corresponding to 
           spans/annotations of this layer.
           Normally, this is a list of strings, but in case 
           of an enveloping layer, a list of lists of strings
           will be returned, as each enveloping span is made 
           of a list of spans of the enveloped layer.
        """
        result = []
        for span in self._span_list.spans:
            if isinstance(span, EnvelopingSpan):
                result.extend(span.text)
            else:
                result.append(span.text)
        return result

    @property
    def enclosing_text(self):
        """Returns a whole text region covered by this layer.
        The region starts from the first span of the layer
        and extends to the end of the farthest span of the layer."""
        return self.text_object.text[self.start:self.end]

    def attribute_values(self, attributes, index_attributes=[]):
        """Returns a matrix-like data structure containing all annotations of this layer with the selected attributes.

        Usage examples:

        >>> from estnltk import Text
        >>> text = Text('Kirjule kassile').tag_layer('morph_analysis')
        >>> # select 'partofspeech' attributes from the 'morph_analysis' layer
        >>> text['morph_analysis'].attribute_values('partofspeech')
        [['A'], ['S']]

        >>> text = Text('Kirjule kassile').tag_layer('morph_analysis')
        >>> # select 'lemma' & 'partofspeech' attributes from the 'morph_analysis' layer
        >>> text['morph_analysis'].attribute_values(['lemma', 'partofspeech'])
        [[['kirju', 'A']], [['kass', 'S']]]

        Optional parameter `index_attributes` can be a list of span's indexing
        attributes ('start', 'end', 'text'), which will be prepended to attributes:
        Example:

        >>> text = Text('Kirjule kassile').tag_layer('morph_analysis')
        >>> # select 'partofspeech' from the 'morph_analysis' layer and prepend surface text strings
        >>> text['morph_analysis'].attribute_values('partofspeech', index_attributes=['text'])
        [[['Kirjule', 'A']], [['kassile', 'S']]]

        Note: for a successful selection, you should provide at least one regular or index
        attribute; a selection without any attributes raises IndexError.

        Parameters
        ----------
        attributes: Union[str, List[str]]
            layer's attribute or attributes which values will be selected
        index_attributes: Union[str, List[str]]
            layer's indexing attributes ('start', 'end' or 'text') which values will be selected

        Returns
        --------
        AmbiguousAttributeTupleList
            * AttributeList -- if the layer is not ambiguous and only one attribute was selected;
            * AttributeTupleList -- if the layer is not ambiguous and more than one attributes were selected;
            * AmbiguousAttributeList -- if the layer is ambiguous and only one attribute was selected;
            * AmbiguousAttributeTupleList -- if the layer is ambiguous and more than one attributes were selected;
        """
        if not isinstance(attributes, (str, list, tuple)):
            raise TypeError( 'Unexpected type for attributes:'.format( str(type(attributes)) ) )
        if not isinstance(index_attributes, (str, list, tuple)):
            raise TypeError( 'Unexpected type for index_attributes:'.format( str(type(index_attributes)) ) )
        number_of_layer_attrs = \
            len(attributes) if isinstance(attributes, (list, tuple)) else (0 if not attributes else 1)
        number_of_index_attrs = \
            len(index_attributes) if isinstance(index_attributes, (list, tuple)) else (0 if not index_attributes else 1)
        if number_of_layer_attrs + number_of_index_attrs == 0:
            raise IndexError('no attributes: ' + str(attributes))
        if self.ambiguous:
            if (number_of_layer_attrs + number_of_index_attrs) > 1 or \
                isinstance(attributes, (list, tuple)):
                # selected: more than 1 attributes at total or 
                # at least 1 layer attribute in a list (for backwards compatibility)
                result = AmbiguousAttributeTupleList(self.spans, attributes,
                                                     span_index_attributes=index_attributes)
            elif number_of_layer_attrs + number_of_index_attrs == 1:
                # only attribute
                index_attr = index_attributes if len(index_attributes) > 0 else None
                result = AmbiguousAttributeList(self.spans, attributes, index_attribute_name=index_attr)
        else:
            if (number_of_layer_attrs + number_of_index_attrs) > 1 or \
                isinstance(attributes, (list, tuple)):
                # selected: more than 1 attributes at total or 
                # at least 1 layer attribute in a list (for backwards compatibility)
                result = AttributeTupleList(self.spans, attributes,
                                            span_index_attributes=index_attributes)
            elif number_of_layer_attrs + number_of_index_attrs == 1:
                # only attribute
                index_attr = index_attributes if len(index_attributes) > 0 else None
                result = AttributeList(self.spans, attributes, index_attribute_name=index_attr)
        return result

    def add_span(self, span: Span) -> Span:
        """Adds new Span (or EnvelopingSpan) to this layer.
           Before adding, span will be validated:
           * the span must have at least one annotation;
           * the span must have exactly one annotation (if the layer is not ambiguous);
           * the span belongs to this layer;
           * the base_span of the new span matches the span level of this layer;

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

        if self.span_level is not None:
            # Check that level of the new (base)span matches the span level of this layer
            # ( all basespans in the layer should be at the same level )
            if self.span_level != span.base_span.level:
                raise ValueError( ('(!) Mismatching base_span levels: span level of this layer is {}, '+\
                   'while level of the new span is {}').format( self.span_level, span.base_span.level ) )
        
        self._span_list.add_span(span)

        return span

    def add_annotation(self, base_span, attribute_dict: Dict[str, Any]={}, **attribute_kwargs) -> Annotation:
        """Adds new annotation (from `attribute_dict` / `attribute_kwargs`) to given text location `base_span`.
        
           For non-enveloping layer, the location `base_span` can be:

           * (start, end) -- integer tuple;
           * ElementaryBaseSpan;
           * Span;
           
           For enveloping layer, the `base_span` can be:

           * [(start_1, end_1), ... (start_N, end_N)] -- list of integer tuples;
           * EnvelopingBaseSpan;
           * EnvelopingSpan;
           * BaseLayer if the layer is enveloping;
           
           `attribute_dict` should contain attribute assignments for the annotation. Example:

               layer.add_annotation( base_span, {'attr1': ..., 'attr2': ...} )
               
           Missing attributes will be filled in with layer's default_values 
           (None values, if defaults have not been explicitly set).
           Optionally, you can leave `attribute_dict` unspecified and pass keyword 
           arguments to the method via `attribute_kwargs`, for example: 
           
               layer.add_annotation( base_span, attr1=..., attr2=... )
           
           While keyword arguments can only be valid Python keywords 
           (excluding the keyword 'base_span'), `attribute_dict` enables to 
           bypass these restrictions while giving the attribute assignments.
           
           The priority order in setting value of an attribute is:
           `attribute_kwargs` > `attribute_dict` > `default attributes`
           (e.g. if the attribute has a default value, and it is set 
            both in `attribute_dict` and in `attribute_kwargs`, then 
            `attribute_kwargs` will override other assignments).
            
           The method returns added annotation.
           
           Note 1: you can add two or more annotations to exactly the 
           same `base_span` location only if the layer is ambiguous. 
           however, partially overlapping locations are always allowed. 
           
           Note 2: in case of an enveloping layer, all basespans must be 
           at the same level. For instance, if you add an enveloping span 
           [(1,2), (2,3)], which corresponds to level 1, you cannot add 
           level 2 span [ [(1,2), (2,3)], [(4,5)]].
        """
        base_span = to_base_span(base_span)
        # Make it clear, if we got non-enveloping or enveloping span properly
        # (otherwise we may run into obscure error messages later)
        if self.enveloping is not None and not isinstance(base_span, EnvelopingBaseSpan):
            raise TypeError('Cannot add {!r} to enveloping layer. Enveloping span is required.'.format(base_span))
        elif self.enveloping is None and isinstance(base_span, EnvelopingBaseSpan):
            # TODO: A tricky situation is when the parent is enveloping -- should allow EnvelopingBaseSpan then?
            # And how can we get the parent layer if it is not attached to the Text object?
            raise TypeError('Cannot add {!r} to non-enveloping layer. Elementary span is required.'.format(base_span))
        
        if not isinstance(attribute_dict, dict):
            raise ValueError('(!) attribute_dict should be an instance of dict, not {}'.format(type(attribute_dict)))
        attributes = {**self.default_values, \
                      **{k: v for k, v in attribute_dict.items() if k in self.attributes}, \
                      **{k: v for k, v in attribute_kwargs.items() if k in self.attributes}}

        span = self.get(base_span)

        if self.enveloping is not None:
            if span is None:
                # add to new span
                span = EnvelopingSpan(base_span=base_span, layer=self)
                annotation = span.add_annotation(Annotation(span, attributes))
                self.add_span(span)
            else:
                # add to existing span
                if isinstance(span, EnvelopingSpan):
                    annotation = span.add_annotation(Annotation(span, attributes))
                else:
                    # Normally, self.get(base_span) should return EnvelopingSpan for the 
                    # enveloping layer. If it returned BaseLayer instead, then we are most 
                    # likely in a situation where the level of the base_span mismatches 
                    # the level of the layer.
                    assert self.span_level is not None
                    if self.span_level != base_span.level:
                        raise ValueError( ('(!) Mismatching base_span levels: span level of this layer is {}, '+\
                             'while level of the new span is {}').format( self.span_level, base_span.level ) )
                    raise ValueError(('(!) Unexpected base_span {!r}.'+\
                                     ' Unable to find layer span corresponding to this base_span.').format(base_span))
            return annotation

        if self.ambiguous:
            if span is None:
                # add to new span
                span = Span(base_span, self)
                annotation = span.add_annotation(Annotation(span, attributes))
                self.add_span(span)
            else:
                # add to existing span
                assert isinstance(span, Span), span
                annotation = span.add_annotation(Annotation(span, attributes))
            return annotation

        if span is not None:
            raise ValueError('the layer is not ambiguous and already contains this span')

        # add to new span
        span = Span(base_span=base_span, layer=self)
        annotation = span.add_annotation(Annotation(span, attributes))
        self.add_span(span)
        return annotation

    def remove_span(self, span):
        """Removes given span from the layer.
        """
        self._span_list.remove_span(span)

    def clear_spans(self):
        """Removes all spans (and annotations) from this layer.
           Note: Clearing preserves the span level of the layer.
        """
        self._span_list = SpanList(span_level=self.span_level)

    def check_span_consistency(self) -> Optional[str]:
        """Checks for layer's span consistency.
           Checks that:
           * all spans are attached to this layer;
           * spans of the layer are sorted;
           * each span has at least one annotation;
           * each span has at exactly one annotation if the layer is not ambiguous;
           * all annotations have exactly the same attributes as the layer;

           Returns None if no inconsistencies were detected; 
           otherwise, returns a string message describing the problem.
           
           This method is mainly used by Retagger to validate that 
           changes made in the layer do not break the span consistency.
        """
        attribute_names = set(self.attributes)

        last_span = None
        for span in self:
            if span.layer is not self:
                return '{} is not attached to this layer'.format(span)
            
            if last_span is not None and not last_span < span:
                if last_span.base_span == span.base_span:
                    return 'duplicate spans: {!r} and {!r} (both have basespan {})'.format( \
                                    last_span, span, last_span.base_span )
                return 'ordering problem: {!r} should precede {!r}'.format(last_span, span)
            last_span = span

            annotations = span.annotations

            if len(annotations) == 0:
                return '{} has no annotations'.format(span)
            if not self.ambiguous and len(annotations) > 1:
                return 'the layer is not ambiguous but {} has {} annotations'.format(span, len(annotations))

            for annotation in annotations:
                if set(annotation) != attribute_names:
                    return '{!r} has redundant annotation attributes: {}, missing annotation attributes: {}'.format( \
                                span, 
                                set(annotation) - attribute_names, 
                                attribute_names - set(annotation) )
        return None

    def diff(self, other) -> Optional[str]:
        """Finds differences between this layer and the other layer.
           Checks that both layers:
            * are instances of BaseLayer;
            * have same names and attributes;
            * have same parent and enveloping layers;
            * are correspondingly ambiguous or unambiguous;
            * have same serialisation_module;
            * have same spans (and annotations);
           Returns None if no differences were detected (both layers are the 
           same or one is exact copy of another), or a message string describing 
           the difference.
        """
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

    def __repr__(self):
        return '{classname}(name={self.name!r}, attributes={self.attributes}, spans={self._span_list})'.format(classname=self.__class__.__name__, self=self)

    def get_overview_dataframe(self):
        """
        Returns DataFrame giving an overview about layer's configuration (name, attributes, parent etc) and status (span count).
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

        index_attributes = []
        if self.text_object is None:
            text_object = 'No Text object.'
        else:
            index_attributes.append('text')
            text_object = ''
        if self.print_start_end:
            index_attributes.extend(['start', 'end'])
        attributes = self.attributes[:]
        if not attributes and not index_attributes:
            index_attributes = ['start', 'end']
        table_1 = self.get_overview_dataframe().to_html(index=False, escape=False)
        table_2 = ''
        if attributes or index_attributes:
            table_2 = self.attribute_values(attributes, index_attributes=index_attributes).to_html(index='text')
        return '\n'.join(('<h4>{}</h4>'.format(self.__class__.__name__), meta, text_object, table_1, table_2))
