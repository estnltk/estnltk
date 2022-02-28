from typing import Union, List

from estnltk_core.layer.attribute_list.ambiguous_attribute_tuple_list import AmbiguousAttributeTupleList
from estnltk_core.layer.attribute_list.immutable_list import ImmutableList


class AmbiguousAttributeList(AmbiguousAttributeTupleList):
    """Immutable lists for representing values of a single attribute of an ambiguous layer.
       
       The source of the attribute can be:
       *) Multiple spans of an ambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['morph_analysis']['partofspeech']
          AmbiguousAttributeList([['I'], ['P', 'P'], ['S']], ('partofspeech',))
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
        if isinstance(other, AmbiguousAttributeList):
            return super().__eq__(other)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            return ImmutableList([[v[0] for v in t] for t in self.amb_attr_tuple_list[item]])
        return ImmutableList([v[0] for v in self.amb_attr_tuple_list[item]])
