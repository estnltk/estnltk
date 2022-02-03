import pandas

from typing import Union, List

from estnltk_core.layer.immutable_list import ImmutableList
from estnltk_core.layer.to_html import to_str

class AmbiguousAttributeTupleList:
    """Base structure for Immutable lists representing values of attributes.
    
       Depending on the number of attributes and the source of the attributes,
       this class provides basis for the following value structures:
       
       AttributeList
       =============
       
       *) 1 attribute from a single span, which has ambiguous annotations, e.g.
          >>> t=Text('mis').tag_layer()
          >>> t['morph_analysis'][0]['lemma']
          AttributeList(['mis', 'mis'], ('lemma',))
       
       *) 1 attribute from multiple spans of an unambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['tokens']['text']
          AttributeList(['Tere', 'mis', 'teet'], ('text',))

        *) 1 attribute from enveloped layers, e.g.
          >>> t=Text('Tere! Mis teet').tag_layer()
          >>> t['sentences'].lemma
          AttributeList([AmbiguousAttributeList([['tere'], ['!']], ('lemma',)), 
                         AmbiguousAttributeList([['mis', 'mis'], ['teet']], ('lemma',))], ('lemma',))

       AmbiguousAttributeList
       ===========================
       
       *) 1 attribute from multiple spans of an ambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['morph_analysis']['partofspeech']
          AmbiguousAttributeList([['I'], ['P', 'P'], ['S']], ('partofspeech',))

       AttributeTupleList
       ==================

        *) multiple attributes from a single span, which has ambiguous annotations, e.g.
          >>> t=Text('mis').tag_layer()
          >>> t['morph_analysis'][0]['lemma', 'form']
          AttributeTupleList([['mis', 'sg n'], ['mis', 'pl n']], ('lemma', 'form'))
       
       *) multiple attributes from multiple spans of an unambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['tokens']['text', 'text']
          AttributeTupleList([['Tere', 'Tere'], ['mis', 'mis'], ['teet', 'teet']], ('text', 'text'))

       AmbiguousAttributeTupleList
       ===========================
       
       *) multiple attributes from multiple spans of an ambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['morph_analysis']['lemma', 'form']
          AmbiguousAttributeTupleList([[['tere', '']], [['mis', 'sg n'], ['mis', 'pl n']], [['teet', 'sg n']]], ('lemma', 'form'))

    """

    def __init__(self, span_or_spanlist:Union['Span', List['Span'], List['BaseLayer']], 
                       attribute_names:Union[str, List[str]], 
                       index_type:str='spans',
                       span_index_attributes:List[str]=None):
        """ Initializes immutable lists representing values of attributes selected from the source.
            
            The exact structure depends on the number of attributes and the 
            source of the attributes (see the docstring of the class for examples).
            
            Parameters
            ==========
            span_or_spanlist:  Union['Span', List['Span'], List['BaseLayer']]
                source of the attribute values
            
            attribute_names:  Union[str, List[str]]
                names of the attributes which values will be selected from the source
            
            index_type: str (default: 'spans')
                whether elements of this immutable list represent (attribute values of) 
                'annotations', 'spans' or 'layers';
                this also guides how attribute values will be selected from the source
                `span_or_spanlist`.
            
            span_index_attributes: List[str] (default: None)
                list containing names of span's indexing attributes ('start', 'end', 'text')
                which values should also be selected. Note that the indexing attributes 
                will be prepended to `attribute_names`, so they always come first.
        """
        # Check input parameters
        if index_type not in ['layers', 'spans', 'annotations']:
            raise ValueError( ('Unexpected index_type parameter {!r}: should be either "layers" (indexed by layers), '+\
                               '"spans" (indexed by spans) or "annotations" (indexed by annotations).').format(index_type))
        if isinstance(span_or_spanlist, (list, tuple)) and index_type == 'annotations':
            raise TypeError('Unexpected index_type="annotations" for a list of spans. '+\
                            'This index_type can only be used with a single Span.')
        if span_index_attributes is not None:
            if not isinstance(span_index_attributes, (list, tuple)):
                raise TypeError("Expected a list of strings for span_index_attributes.")
            if not all([index_attr in ['start', 'end', 'text'] for index_attr in span_index_attributes]):
                raise ValueError(("span_index_attributes={!r} contains unexpected values. Please use only "+
                                  "values 'start', 'end', 'text'").format(span_index_attributes))
        
        # Unify input parameters
        if isinstance(attribute_names, str):
            # Assume that a string argument is a single attribute name,
            # while otherwise we have a list of attribute names
            attribute_names = [ attribute_names ]
        assert isinstance(attribute_names, (list, tuple)) and \
               all([isinstance(a, str) for a in attribute_names])
             
        # Yield attributes & values from a single annotation:
        def get_attribute_values( annotation, attributes, index_attributes ):
            if index_attributes:
                for index_attr in index_attributes:
                    if index_attr == 'text':
                        yield annotation.text
                    elif index_attr == 'start':
                        yield annotation.start
                    elif index_attr == 'end':
                        yield annotation.end
            for attribute in attributes:
                if attribute == 'text':
                    # for backwards compatibility
                    yield annotation.text
                else:
                    yield annotation[attribute]
                
        # Unpack attributes & values:        
        amb_attr_tuple_list = []
        if index_type == 'layers':
            assert isinstance(span_or_spanlist, (list, tuple))
            # Unpack layers
            for layer in span_or_spanlist:
                # Unpack spans of a layer
                # Assume we have a Layer, so calling layer[attribute_names] should 
                # give use AmbiguousAttributeTupleList via layer's attribute_values:
                attr_values = layer[ attribute_names if len(attribute_names)>1 else attribute_names[0] ] 
                assert isinstance(attr_values, AmbiguousAttributeTupleList)
                amb_attr_tuple_list.append( [[attr_values]] )
        elif index_type == 'spans':
            assert isinstance(span_or_spanlist, (list, tuple))
            # Unpack spans of spanlist
            amb_attr_tuple_list = \
                (( (get_attribute_values(a, attribute_names, span_index_attributes)) for a in sp.annotations) for sp in span_or_spanlist)
        else:
            # Unpack annotations of a span
            assert not isinstance(span_or_spanlist, (list, tuple))
            amb_attr_tuple_list = \
                ((( [get_attribute_values(a, attribute_names, span_index_attributes)] ) for a in span_or_spanlist.annotations))
            
        # Create ImmutableLists
        self.amb_attr_tuple_list = ImmutableList(ImmutableList(ImmutableList(v) for v in value_tuples)
                                                 for value_tuples in amb_attr_tuple_list)
        self.attribute_names = tuple(attribute_names)
        self.index_type = index_type

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AmbiguousAttributeTupleList(self.amb_attr_tuple_list[item], self.attribute_names)
        return self.amb_attr_tuple_list[item]

    def __len__(self):
        return len(self.amb_attr_tuple_list)

    def __eq__(self, other):
        if isinstance(other, AmbiguousAttributeTupleList):
            return self.attribute_names == other.attribute_names and \
                   self.amb_attr_tuple_list == other.amb_attr_tuple_list
        return False

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, list(self), self.attribute_names)

    def __str__(self):
        return str(list(self))

    def to_html(self, index=True):
        if index is True:
            columns = ['']
            columns.extend(self.attribute_names)
        else:
            columns = self.attribute_names
        records = []
        for i, value_tuples in enumerate(self.amb_attr_tuple_list):
            first = True
            for value_tuple in value_tuples:
                record = {k: to_str(v) for k, v in zip(self.attribute_names, value_tuple)}
                if index is True:
                    record[''] = i if first else ''
                elif isinstance(index, str) and not first:
                    record[index] = ''
                records.append(record)
                first = False
        df = pandas.DataFrame.from_records(records, columns=columns)
        return df.to_html(index=False, escape=True)

    def _repr_html_(self):
        return '\n'.join(('<h4>' + self.__class__.__name__ + ' ('+self.index_type+')</h4>',
                          self.to_html()))
