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
                       index_type:str='spans'):
        # Check input parameters
        if index_type not in ['layers', 'spans', 'annotations']:
            raise ValueError( ('Unexpected index_type parameter {!r}: should be either "layers" (indexed by layers), '+\
                               '"spans" (indexed by spans) or "annotations" (indexed by annotations).').format(index_type))
        if isinstance(span_or_spanlist, (list, tuple)) and index_type == 'annotations':
            raise TypeError('Unexpected index_type="annotations" for a list of spans. '+\
                            'This index_type can only be used with a single Span.')
        # Unify input parameters
        if isinstance(attribute_names, str):
            # Assume that a string argument is a single attribute name,
            # while otherwise we have a list of attribute names
            attribute_names = [ attribute_names ]
        assert isinstance(attribute_names, (list, tuple)) and \
               all([isinstance(a, str) for a in attribute_names])
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
                (((a[attr] if attr != 'text' else a.text for attr in attribute_names) for a in sp.annotations) for sp in span_or_spanlist)
        else:
            # Unpack annotations of a span
            assert not isinstance(span_or_spanlist, (list, tuple))
            amb_attr_tuple_list = \
                ((( [[a[attr] if attr != 'text' else a.text for attr in attribute_names]] ) for a in span_or_spanlist.annotations))
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
