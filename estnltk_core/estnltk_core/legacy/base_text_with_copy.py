#
#  This is a legacy version of BaseText that supports shallow copy. 
#  However, shallow copying of a Text object is unsafe and therefore 
#  no longer supported. 
#
from copy import copy

from estnltk_core.base_text import BaseText

class BaseTextWithCopy( BaseText ):

    def __copy__(self):
        result = self.__class__( self.text )
        result.meta = self.meta
        # Layers must be created in the topological order
        for layer in self.sorted_layers():
            copied_layer = copy(layer)
            copied_layer.text_object = None
            result.add_layer(copied_layer)
        return result
