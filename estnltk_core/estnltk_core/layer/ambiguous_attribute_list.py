from typing import Union, List

from estnltk_core.layer import AmbiguousAttributeTupleList
from estnltk_core.layer.immutable_list import ImmutableList


class AmbiguousAttributeList(AmbiguousAttributeTupleList):
    """Immutable lists for representing values of a single attribute of an ambiguous layer.
       
       The source of the attribute can be:
       *) Multiple spans of an ambiguous layer, e.g.
          >>> t=Text('Tere mis teet').tag_layer()
          >>> t['morph_analysis']['partofspeech']
          AmbiguousAttributeList([['I'], ['P', 'P'], ['S']], ('partofspeech',))
    """

    def __init__(self, span_or_spanlist:Union['Span', List['Span']], attribute_name:str, index_type:str='spans'):
        super().__init__(span_or_spanlist, [attribute_name], index_type=index_type)

    def __eq__(self, other):
        if isinstance(other, AmbiguousAttributeList):
            return super().__eq__(other)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AmbiguousAttributeList([[v[0] for v in t] for t in self.amb_attr_tuple_list[item]],
                                          self.attribute_names)
        return ImmutableList([v[0] for v in self.amb_attr_tuple_list[item]])
