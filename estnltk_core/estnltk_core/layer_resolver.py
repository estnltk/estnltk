from typing import List, Union, Sequence

from estnltk_core.taggers import Tagger, Retagger
from estnltk_core.taggers_registry import TaggersRegistry


class LayerResolver:
    """LayerResolver handles layer creation, and resolves layer dependencies automatically. 
       Upon creating a layer, it uses the TaggersRegistry to (recursively) find 
       and create all the prerequisite layers of the target layer.
       Also holds default layers: the layers that are created when Text object's tag_layer() 
       is called without layer name arguments. """

    def __init__(self, taggers: TaggersRegistry, default_layers: Union[str, Sequence[str]] = []):
        self._taggers = taggers
        self._default_layers = []
        self.set_default_layers( default_layers )

    def update(self, tagger: Union[Tagger, Retagger]) -> None:
        '''Updates the Taggers registry with the given tagger or retagger.'''
        self._taggers.update(tagger)

    def taggers(self):
        '''Returns TaggersRegistry of this Resolver.'''
        return self._taggers

    def get_default_layers(self):
        '''Returns default layers of this resolver.
           Default layers are the layers created when Text object's tag_layer() 
           is called without layer name arguments. '''
        return self._default_layers

    def set_default_layers(self, layers: Union[str, Sequence[str]]):
        '''Assigns default layers to this resolver.
           Default layers are the layers created when Text object's tag_layer() 
           is called without layer name arguments. 
           Raises a ValueError if given layers are not registered in resolver's
           TaggersRegistry. '''
        if not isinstance( layers, (list, tuple) ) and not isinstance( layers, str ):
            raise TypeError('(!) A list of layer names or a single layer name was expected.' )
        if isinstance( layers, str ):
            layers = tuple([layers])
        elif isinstance( layers, list ):
            layers = tuple(layers)
        creatable_layers = list(self.list_layers())
        for layer in layers:
            if layer not in creatable_layers:
                raise ValueError( ('(!) TaggersRegistry has no entry for layer {!r}. '+
                                   'Registered layers are: {!r}').format( layer, creatable_layers ) )
        self._default_layers = layers

    def get_tagger(self, layer_name: str) -> Tagger:
        '''Returns tagger responsible for creating the given layer.'''
        return self._taggers.get_tagger(layer_name)

    def get_retaggers(self, layer_name: str) -> List[Retagger]:
        '''Returns list of retaggers modifying the given layer.'''
        return self._taggers.get_retaggers(layer_name)

    def clear_retaggers(self, layer_name: str) -> None:
        '''Removes all the retaggers modifying the given layer.
           Note: the tagger creating the layer will remain. '''
        self._taggers.clear_retaggers(layer_name)

    def list_layers(self) -> List[str]:
        '''Lists layers that can be created by this resolver in the order 
           in which they should be created.'''
        return self._taggers.list_layers()

    def apply(self, text: Union['BaseText', 'Text'], layer_name: str) -> Union['BaseText', 'Text']:
        '''Creates the given layer along with all the prerequisite layers. 
           The layers will be attached to the input Text object. 
           Returns the input Text object.
        '''
        if layer_name in text.layers:
            return text
        if layer_name not in self._taggers._graph.nodes:
            raise Exception('(!) No tagger registered for creating layer {!r}.'.format( layer_name ) )
        for prerequisite in self._taggers._graph.predecessors(layer_name):
            self.apply(text, prerequisite)

        self._taggers.create_layer_for_text( layer_name, text )
        return text

    def __repr__(self):
        parameters_str = ''
        if self._taggers:
            default_layers = list(self.get_default_layers())
            parameters_str = 'taggers={},default_layers={!r}'.format(self._taggers, default_layers)
        return '{classname}({parameters})'.format(classname=self.__class__.__name__, parameters=parameters_str)

    def _repr_html_(self):
        if self._taggers:
            default_layers = list(self.get_default_layers())
            default_layers_str = 'Default layers: <b>'+(', '.join(default_layers))+'</b>'
            return ('<h4>{}</h4>'.format(self.__class__.__name__))+'\n<br>'+\
                    default_layers_str+'\n</br>'+self._taggers._repr_html_()

