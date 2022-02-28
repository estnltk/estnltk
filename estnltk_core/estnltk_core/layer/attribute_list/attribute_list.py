from typing import Iterable, Union, List
from estnltk_core.layer.attribute_list.ambiguous_attribute_tuple_list import AmbiguousAttributeTupleList
from estnltk_core.layer.attribute_list.immutable_list import ImmutableList

class AttributeList(AmbiguousAttributeTupleList):
    """Immutable lists for representing values of a single attribute.
       
       The source of the attribute can be:
       *) A single span, which has ambiguous annotations, e.g.
          >>> t=Text('mis').tag_layer()
          >>> t['morph_analysis'][0]['lemma']
          AttributeList(['mis', 'mis'], ('lemma',))
       
       *) Multiple spans of an unambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['tokens']['text']
          AttributeList(['Tere', 'mis', 'teet'], ('text',))

        *) Enveloped layers, e.g.
          >>> t=Text('Tere! Mis teet').tag_layer()
          >>> t['sentences'].lemma
          AttributeList([AmbiguousAttributeList([['tere'], ['!']], ('lemma',)), 
                         AmbiguousAttributeList([['mis', 'mis'], ['teet']], ('lemma',))], ('lemma',))
    """

    def __init__(self, span_or_spanlist:Union['Span', List['Span']], 
                       attribute_name:str, 
                       index_type:str='spans',
                       index_attribute_name:str=None):
        if attribute_name is not None and index_attribute_name is not None:
            raise ValueError(('(!) Cannot set both attribute={!r} and index_attribute_name={!r} in '+\
                              '{}. One argument should be None.').format(attribute_name, 
                                                                         index_attribute_name, 
                                                                         self.__class__.__name__))
        super().__init__(span_or_spanlist, attribute_name, index_type=index_type, span_index_attributes=index_attribute_name)

    def __eq__(self, other):
        if isinstance(other, AttributeList):
            return super().__eq__(other)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            return ImmutableList([a[0][0] for a in self.amb_attr_tuple_list[item]])
        return self.amb_attr_tuple_list[item][0][0]
