#
#  RelationsLayer is a special layer for holding Relation annotations.
#  Relation consists of named BaseSpans (NamedSpan objects) and a list of RelationAnnotations.
#  
#  (WORK IN PROGESS) 
#

from typing import Any, Mapping, Sequence, Dict, List, Tuple, Union

from reprlib import recursive_repr

import pandas

from estnltk_core import BaseSpan, ElementaryBaseSpan, EnvelopingBaseSpan, Span
from estnltk_core.common import _create_attr_val_repr


def to_relation_base_span(x) -> BaseSpan:
    """Reduces estnltk's relation annotation structure to BaseSpan or creates BaseSpan from raw location.
       If parameter `x` is estnltk's structure, returns corresponding base span:
       * BaseSpan -> BaseSpan (returns input);
       * Span -> ElementaryBaseSpan;
       * EnvelopingSpan -> EnvelopingBaseSpan;
       
       If parameter `x` is a raw location, creates and returns appropriate base span:
       * (start, end) -> ElementaryBaseSpan;
       * [(start_1, end_1), ... (start_N, end_N)] -> EnvelopingBaseSpan;
    """
    if isinstance(x, (List, tuple)):
        # Try to convert list/tuple of integers to base span
        if len(x) == 2 and isinstance(x[0], int) and isinstance(x[1], int):
            base_span = ElementaryBaseSpan(*x)
        else:
            base_span = EnvelopingBaseSpan(to_relation_base_span(y) for y in x)
        return base_span
    if isinstance(x, BaseSpan):
        return x
    if isinstance(x, (NamedSpan, Span)):
        return x.base_span
    raise TypeError('{} ({}) cannot be converted to base span'.format(type(x), x))


class RelationsLayer:
    """
    RelationsLayer is a collection of Relation objects.
    
    Relation consists of named BaseSpans (NamedSpan objects) and a list of RelationAnnotations.
    
    Rules:
    * span names and annotation attribute names cannot overlap;
    * each relation must have at least one NamedSpan, and at least one RelationAnnotation;
    * a relation does not need to have all spans defined by the layer, some spans 
      (but not all) can be empty/unassigned;
    """

    __slots__ = ['name', 'span_names', 'attributes', 'ambiguous', 'text_object', 
                 'serialisation_module', 'meta', '_relation_list']
    
    def __init__(self,
                 name: str,
                 span_names: Sequence[str] = (),
                 attributes: Sequence[str] = (),
                 text_object: Union['BaseText','Text']=None,
                 ambiguous: bool = False,
                 serialisation_module: str="relations_v0"
                 ) -> None:
        """
        Initializes a new RelationsLayer object based on given configuration.
        
        Rules:
        * span_names must contain at least one name;
        * span_names must be valid identifiers;
        * span_names and attributes cannot have overlap;
        """
        # name of the layer
        assert name is not None and len(name) > 0 and not name.isspace(), \
            'layer name cannot be empty or consist of only whitespaces {!r}'.format(name)
        self.name = name
        self.span_names = span_names
        self.attributes = attributes
        # validate that span_names and attributes do not have common keys
        span_names_set = set(self.span_names) if self.span_names is not None else set()
        attributes_set = set(self.attributes) if self.attributes is not None else set()
        common = span_names_set.intersection(attributes_set)
        assert len(common) == 0, \
            'attributes cannot have overlapping values with span_names: {}'.format(list(common))
        self._relation_list = []
        self.ambiguous = ambiguous
        self.text_object = text_object
        self.serialisation_module = serialisation_module
        self.meta = {}

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
        """
        if len(self._relation_list) > 0:
            return self._relation_list[0].span_level

    @property
    def relations(self):
        return self._relation_list

    def add_annotation(self, relation_dict: Dict[str, Any]={}, **relation_kwargs) -> 'RelationAnnotation':
        '''
        Adds new relation annotation based on the dictionary.
        
        Rules:
        * dictionary must contain at least one mapping from span name 
          to a base span, using key from span_names of this layer;
        * if this layer already has relations, then newly added named 
          spans must match with the span level of this layer;
        * only values of keys in self.attributes will be picked from 
          the dictionary for relation annotation; values under keys 
          not in span_names and attributes will be discarded;
        * if relation location (named spans) already exists and 
          the layer is ambiguous, then the annotation is added to 
          existing relation; but if layer is not ambiguous, an 
          exception will be thrown;
        '''
        if not isinstance(relation_dict, dict):
            raise TypeError('(!) Unexpected relation_dict data type: {} ({})'.format( \
                                 type(relation_dict), relation_dict) )
        relation_dict_merged = { **{k: v for k, v in relation_dict.items()}, \
                                 **{k: v for k, v in relation_kwargs.items()} }
        # Get named spans
        spans_list = []
        for span_name in self.span_names:
            span_value = relation_dict_merged.get(span_name, None)
            if span_value is not None:
                base_span = to_relation_base_span(span_value)
                spans_list.append( (span_name, base_span) )
            else:
                spans_list.append( (span_name, None) )
        # Get attributes (only valid ones)
        annotation = \
            { attr:relation_dict_merged.get(attr, None) for attr in self.attributes }
        existing_spans_list = \
            [sp for sp in spans_list if sp[1] is not None]
        # At least one named span must be given
        if len(existing_spans_list) == 0:
            raise ValueError(('Cannot add annotation: no named spans in {}, '+\
                              'at least one of {} must be defined').format(relation_dict_merged, 
                                                                           self.span_names))
        # Try to get existing relation
        relation = self.get( existing_spans_list )
        if relation is None:
            # Relation does not exits. Try to create it
            relation = Relation( existing_spans_list, self )
            # Check that span level matches with the current level
            if len(self._relation_list) > 0:
                cur_span_level = self._relation_list[0].span_level
                if cur_span_level != relation.span_level:
                    raise ValueError( ('Cannot add annotation: this layer has different '+\
                                       'span level ({}) than newly addable spans {}.'+\
                                       '').format(cur_span_level, existing_spans_list) )
            annotation_obj = relation.add_annotation(annotation)
            self._relation_list.append(relation)
        else:
            # Relation exists. Check ambiguity
            if not self.ambiguous and len(relation.annotations)+1 > 1:
                raise Exception(('Cannot add another annotation to {}: '+\
                                 'the layer is not ambiguous').format(relation) )
            # Add annotation to existing relation
            annotation_obj = relation.add_annotation(annotation)
        return annotation_obj

    def get(self, item):
        """ Finds and returns Relation corresponding to the given list of NamedSpan(s).
            Alternatively, list of tuples (span_name, BaseSpan) can be the input parameter. 
            If this layer is empty or Relation was not found, returns None.
        """
        if len(self._relation_list) == 0:
            return None
        if isinstance(item, (list, tuple)):
            # List of NamedSpan-s
            if all(isinstance(i, NamedSpan) for i in item):
                for relation in self._relation_list:
                    if relation.spans == item:
                        return relation
                return None
            # List of Tuples (span_name, BaseSpan)
            if all(isinstance(i, tuple) and len(i)==2 and \
                   isinstance(i[0], str) and isinstance(i[1], BaseSpan) for i in item):
                for relation in self._relation_list:
                    if [r.as_tuple for r in relation.spans] == item:
                        return relation
                return None
        raise ValueError(item)

    def remove_relation(self, relation: 'Relation'):
        """Removes relation from the layer.
        """
        self._relation_list.remove(relation)

    def clear_relations(self):
        """Removes all relations from the given layer.
        """
        self._relation_list = []

    def get_overview_dataframe(self):
        """
        Returns DataFrame giving an overview about layer's configuration (name, attributes etc) and status (relation count).
        This is used for visualization purposes.
        """
        rec = [{'layer name': self.name,
                'span_names': ', '.join(self.span_names),
                'attributes': ', '.join(self.attributes),
                'ambiguous' : str(self.ambiguous),
                'relation count': str(len(self._relation_list))}]
        return pandas.DataFrame.from_records(rec,
                                             columns=['layer name', 'span_names',
                                                      'attributes', 'ambiguous', 
                                                      'relation count'])

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memo=None):
        raise NotImplementedError

    def __setitem__(self, key: int, value: 'Relation'):
        self._relation_list[key] = value

    def __getitem__(self, item) -> Union['Relation', List['Relation']]:
        if isinstance(item, int):
            # Expected call: layer[index]
            # Returns Relation
            return self._relation_list[item]
        
        if isinstance(item, slice):
            # Expected call: layer[start:end]
            # Returns List of Relation-s
            return list(self._relation_list[item])

        if isinstance(item, (list, tuple)) and all(isinstance(i, str) for i in item):
            # Expected call: layer[[span1, span2, attr1, attr2, ...]]
            # Returns named spans & annotation values extracted from all Relations
            results = []
            for relation in self:
                if not self.ambiguous:
                    results.append( relation[item] )
                else:
                    # ambiguous: more than one annotation per selection of spans
                    # need to flatten the results (TODO: does Layer behave the same)
                    for result in relation[item]:
                        results.append( result )
            return results

        raise TypeError('index not supported: ' + str(item))

    def __setattr__(self, key, value):
        if key == 'span_names':
            # check span_names
            span_names = value
            assert not isinstance(span_names, str), \
                'span_names must be a list or tuple of strings, not a single string {!r}'.format(span_names)
            span_names = tuple(span_names)
            assert len(span_names) > 0, 'span_names cannot be empty, at least one span_name must be specified'
            span_names_set = set(span_names)
            assert len(span_names) == len(span_names_set), 'repetitive span name: ' + str(span_names)
            for span_name in span_names:
                if not span_name.isidentifier():
                    raise ValueError('Unexpected span_name: {!r}. span_name should be a valid identifier.'.format(span_name))
            # set span_names
            super().__setattr__('span_names', span_names)
            return
        elif key == 'attributes':
            # check attributes
            attributes = value
            assert not isinstance(attributes, str), \
                'attributes must be a list or tuple of strings, not a single string {!r}'.format(attributes)
            attributes = tuple(attributes)
            attributes_set = set(attributes)
            assert len(attributes) == len(attributes_set), 'repetitive attribute name: ' + str(attributes)
            # set attributes
            super().__setattr__('attributes', attributes)
            return
        super().__setattr__(key, value)

    def __getattr__(self, item):
        # Deny access to other attributes
        raise AttributeError('attribute {} cannot be accessed directly in {}'.format(item, self.__class__.__name__))

    def __delitem__(self, relation: 'Relation'):
        self._relation_list.remove(relation)

    def __iter__(self):
        return iter(self._relation_list)

    def __len__(self):
        return len(self._relation_list)

    def __repr__(self):
        return ('{classname}(name={self.name!r}, span_names={self.span_names}, '+\
                'attributes={self.attributes}, relations={self._relation_list})').format(classname=self.__class__.__name__, \
                                                                                         self=self)

    def _repr_html_(self):
        if self.meta:
            data = {'key': sorted(self.meta), 'value': [self.meta[k] for k in sorted(self.meta)]}
            meta_table = pandas.DataFrame(data, columns=['key', 'value'])
            meta_table = meta_table.to_html(header=False, index=False)
            meta = '\n'.join(('<h4>Metadata</h4>', meta_table))
        else:
            meta = ''

        if self.text_object is None:
            text_object_msg = 'No Text object.'
        else:
            text_object_msg = ''
        table_1 = self.get_overview_dataframe().to_html(index=False, escape=False)
        # Construct layer table
        table_2 = ''
        columns = self.span_names + self.attributes
        layer_table_content = []
        for relation in self:
            spans = []
            for sp in self.span_names:
                span_repr = None
                if relation[sp] is not None:
                    span_repr = relation[sp].text
                    if span_repr is None:
                        # This means that no Text object is attached. 
                        # Then use base_span value instead of text
                        span_repr = str(relation[sp].base_span.raw())
                spans.append( span_repr )
            attrib_values = relation[self.attributes]
            if not self.ambiguous:
                layer_table_content.append(spans + attrib_values)
            else:
                # attrib_values is a list of lists
                empty_spans = ['' for i in range(len(self.span_names))]
                first = True
                for values in attrib_values:
                    if first:
                        layer_table_content.append(spans + values)
                    else:
                        layer_table_content.append(empty_spans + values)
                    first = False
        df = pandas.DataFrame.from_records(layer_table_content, columns=columns)
        table_2 = df.to_html(index=False, escape=True)
        return '\n'.join(('<h4>{}</h4>'.format(self.__class__.__name__), meta, text_object_msg, table_1, table_2))


class Relation:
    """
    Relation consists of named BaseSpan-s (NamedSpan-s) and a list of RelationAnnotations. 
    
    Relation should have at least one NamedSpan, and at least one RelationAnnotation. 
    Note that the constructor of this class allows to create a Relation without annotations. 
    It is responsibility of the programmer to ensure that each Relation will get a 
    RelationAnnotation.
    """
    
    __slots__ = ['_named_spans', '_annotations', '_relations_layer', '_span_level']

    def __init__(self, spans: List[Tuple[str, BaseSpan]], relations_layer: 'RelationsLayer'):
        assert isinstance(spans, list), spans
        self._named_spans = dict()
        self._span_level = None
        self._relations_layer = relations_layer
        self._annotations = []
        # Validate that we have at least one span
        if len(spans) == 0:
            raise ValueError('Error on creating Relation: at least one span must be provided')
        # Add named spans
        for named_span in spans:
            assert isinstance(named_span, (list, tuple)) and len(named_span) == 2
            name, base_span = named_span
            self.set_span( name, base_span )

    @property
    def annotations(self):
        return self._annotations

    @property
    def span_names(self):
        return list(self._named_spans.keys())

    @property
    def spans(self):
        return list(self._named_spans.values())

    @property
    def base_spans(self):
        return [span.base_span for span in self.spans]

    @property
    def span_level(self):
        return self._span_level

    @property
    def text(self):
        return [span.text for span in self.spans]

    @property
    def relations_layer(self):
        return self._relations_layer

    @property
    def text_object(self):
        if self.relations_layer is not None:
            return self.relations_layer.text_object

    @property
    def legal_span_names(self):
        return self.relations_layer.span_names

    @property
    def legal_attribute_names(self):
        return self.relations_layer.attributes

    def set_span(self, name: str, base_span: BaseSpan ):
        assert isinstance(name, str)
        assert isinstance(base_span, BaseSpan) 
        # Check span level
        if self.span_level is not None:
            if base_span.level != self.span_level:
                raise ValueError( ('Cannot set span: this relation has different '+\
                                   'span level ({}) than the input base_span {}.'+\
                                   '').format(self.span_level, base_span) )
        # Check span name 
        if name not in self.legal_span_names:
            raise ValueError(('Cannot set span: relations layer has does not have '+\
                              'span named {!r}. Valid span names are: {}.'+\
                              '').format(name, self.legal_span_names))
        arg_span = NamedSpan(name, base_span, self)
        self._named_spans[name] = arg_span
        # Set span level based on the first span
        if self.span_level is None:
            self._span_level = base_span.level

    def remove_span(self, name: str):
        """
        Removes given span by name from the relation.
        Note thet span can be removed only if it is not the last span in the relation.
        """
        if name in self._named_spans.keys():
            if len(self._named_spans) > 1:
                del self._named_spans[name]
            else:
                raise Exception('(!) Cannot remove the last span of the relation '+\
                                '-- relation must have at least one span: {}'.format(self) )
        else:
            raise KeyError(name)

    def add_annotation(self, annotation: Union[Dict[str, Any], 'RelationAnnotation']={} ):
        if isinstance(annotation, RelationAnnotation):
            # Annotation object
            if annotation.relation is not self:
                raise ValueError('the annotation has a different relation {}'.format(annotation.relation))
            # Check that all attributes are valid
            if set(annotation) != set(self.legal_attribute_names):
                raise ValueError('the annotation has unexpected or missing attributes {}!={}'.format(
                        set(annotation), set(self.legal_attribute_names)))
        elif isinstance(annotation, dict):
            # Select only valid attributes
            valid_annotation = \
                { attr: annotation.get(attr, None) for attr in self.legal_attribute_names }
            annotation = RelationAnnotation(self, valid_annotation)
        else:
            raise TypeError('Cannot add annotation: unexpected annotation type: {}'.format(type(annotation)))
        # Check ambiguity
        if not self.relations_layer.ambiguous and len(self.annotations)+1 > 1:
            raise Exception(('Cannot add another annotation to {}: '+\
                             'the layer is not ambiguous').format(self) )
        if annotation not in self._annotations: # Avoid duplicate annotations
            self._annotations.append(annotation)
        return annotation

    def del_annotation(self, idx):
        """Deletes annotation by index `idx`.
        """
        del self._annotations[idx]

    def clear_annotations(self):
        """Removes all annotations from this relation.
        """
        self._annotations.clear()

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memo=None):
        raise NotImplementedError

    def __getitem__(self, item):
        if isinstance(item, str):
            if item in self.legal_span_names:
                return self._named_spans.get(item, None)
            elif item in self.legal_attribute_names:
                if self.relations_layer.ambiguous:
                    return [ann[item] for ann in self.annotations]
                else:
                    return self.annotations[0][item]
        elif isinstance(item, (list, tuple)) and all(isinstance(i, str) for i in item):
            selected_spans = []
            selected_attributes = []
            for i in item:
                if i in self.legal_span_names:
                    selected_spans.append(i)
                elif i in self.legal_attribute_names:
                    selected_attributes.append(i)
                else:
                    raise ValueError(('Unexpected keyword index {!r}. Should be '+\
                                      'either span name or attribute name. '+\
                                      'Legal span names: {!r}, legal attribute '+\
                                      'names: {!r}').format(i, self.legal_span_names, 
                                                               self.legal_attribute_names))
            # Get spans
            spans = [self._named_spans.get(sp, None) for sp in selected_spans]
            # Get annotations
            if not self.relations_layer.ambiguous:
                annotation_values = \
                    [self.annotations[0][a] for a in selected_attributes]
                return spans + annotation_values
            else:
                # ambiguous layer: multiply spans x annotation_values
                results = []
                for annotation in self.annotations:
                    annotation_values = \
                        [annotation[a] for a in selected_attributes]
                    results.append(spans + annotation_values)
                return results
            # TODO: return AmbiguousAttributeTupleList instead ?!
        raise KeyError(item)

    def __setitem__(self, key, value):
        self.set_span(key, value)

    def __setattr__(self, key, value):
        if key in {'_named_spans', '_annotations', '_relations_layer', '_span_level'}:
            super().__setattr__(key, value)
        else:
            raise AttributeError(key)

    def __getattr__(self, item):
        if isinstance(item, str):
            if item in self.legal_span_names:
                return self._named_spans.get(item, None)
            # note: only named spans can be retrieved this way,
            # attributes are not guaranteed to be valid identifiers
        raise KeyError(item)

    def __iter__(self):
        # TODO: is it a good idea? this returns unsorted spans
        yield from self.spans

    def __len__(self) -> int:
        return len(self.spans)

    def __contains__(self, item: str) -> bool:
        return item in self._named_spans

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Relation) \
               and len(self.spans) == len(other.spans) \
               and all(s in other.spans for s in self.spans) \
               and len(self.annotations) == len(other.annotations) \
               and all(s in other.annotations for s in self.annotations)

    @recursive_repr()
    def __repr__(self):
        try:
            annotation_strings = []
            attribute_names = self.relations_layer.attributes
            for annotation in self.annotations:
                attr_val_repr = _create_attr_val_repr( [(attr, annotation[attr]) for attr in attribute_names] )
                annotation_strings.append( attr_val_repr )
            annotations = '[{}]'.format(', '.join(annotation_strings))
        except:
            annotations = None
        return '{class_name}({named_spans!r}, {annotations})'.format(class_name=self.__class__.__name__, 
                                                                     named_spans=self.spans,
                                                                     annotations=annotations)

    # TODO: add HTML representation


class NamedSpan:
    """Named span of a Relation.
    
       TODO: This class copies some methods and logic from estnltk_core.Span.
       Consider making an abstract super class for the two in future.
    """
    __slots__ = ['_name', '_base_span', '_relation']
    
    def __init__(self, name: str, base_span: BaseSpan, relation: 'Relation'):
        assert isinstance(name, str), name
        assert isinstance(base_span, BaseSpan), base_span
        self._name = name
        self._base_span = base_span
        self._relation = relation

    @property
    def name(self):
        return self._name
        
    @property
    def relation(self):
        return self._relation

    @property
    def relations_layer(self):
        return self.relation.relations_layer

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
        return self._relation.text_object.text[self.start:self.end]

    @property
    def text_object(self):
        if self._relation is not None:
            return self._relation.text_object

    @property
    def as_tuple(self):
        return (self.name, self.base_span)

    @property
    def raw_text(self):
        return self.text_object.text

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memo=None):
        raise NotImplementedError

    def __setattr__(self, key, value):
        if key in self.__slots__:
            super().__setattr__(key, value)
        else:
            raise AttributeError(key)

    def __getattr__(self, item):
        raise AttributeError('Getting attribute {!r} not implemented.'.format(item))

    def __lt__(self, other: Any) -> bool:
        return self.base_span < other.base_span

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NamedSpan) \
               and self.base_span == other.base_span \
               and self.name == other.name

    def __repr__(self):
        try:
            text = self.text
        except:
            text = None
        return '{class_name}({name}: {text!r})'.format(class_name=self.__class__.__name__, 
                                                       name=self.name, text=text)

    # TODO: add HTML representation


class RelationAnnotation(Mapping):
    '''Mapping for Relation's attribute values.
       
       TODO: This class copies some methods and logic from estnltk_core.Annotation.
       Consider making an abstract super class for the two in future.
    '''
    __slots__ = ['__dict__', '_relation']

    def __init__(self, relation: 'Relation', attributes: Dict[str, Any]={}, **attributes_kwargs):
        """Initiates a new Annotation object tied to the given relation.
           
           Note that there are two parameters for assigning attributes 
           to the annotation: `attributes` and `attributes_kwargs`.
           
           `attributes` supports a dictionary-based assignment, 
           for example:
               Annotation( relation, {'attr1': ..., 'attr2': ...} )
           
           `attributes_kwargs` supports keyword argument assignments, 
           for example:
               Annotation( relation, attr1=..., attr2=... )
           
           While keyword arguments can only be valid Python keywords 
           (excluding the keyword 'relation'), using `attributes` dictionary 
           enables to bypass these restrictions while making the attribute 
           assignments.
           
           Note that you can use both `attributes` and `attributes_kwargs`
           simultaneously. In that case, if there are overlapping 
           argument assignments, then keyword arguments will override 
           dictionary-based assignments.
        """
        self._relation = relation
        merged_attributes = { **attributes, **attributes_kwargs }
        self.__dict__ = merged_attributes

    @property
    def relation(self):
        return self._relation

    @property
    def relations_layer(self):
        return self.relation.relations_layer

    @property
    def legal_attribute_names(self):
        if self.relation is not None and self.relation.relations_layer is not None:
            return self.relation.relations_layer.attributes
        return None

    @property
    def text_object(self):
        if self._relation is not None:
            return self._relation.text_object

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memo=None):
        raise NotImplementedError

    def __setattr__(self, key, value):
        if key in self.__slots__:
            super().__setattr__(key, value)
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
        if isinstance(other, RelationAnnotation):
            self_dict  = self.__dict__
            other_dict = other.__dict__
            # TODO: skip the comparison of the secondary attributes
            return self_dict == other_dict
        else:
            return False

    @recursive_repr()
    def __repr__(self):
        # Output key-value pairs in an ordered way
        # (to assure a consistent output, e.g. for automated testing)

        if self.legal_attribute_names is None:
            attribute_names = sorted(self.__dict__)
        else:
            attribute_names = self.legal_attribute_names

        attr_val_repr = _create_attr_val_repr( [(k, self.__dict__[k]) for k in attribute_names] )

        return '{class_name}({attributes})'.format(class_name=self.__class__.__name__, 
                                                   attributes=attr_val_repr)