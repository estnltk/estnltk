from typing import List, Union, Sequence

from estnltk_core.taggers import Tagger, Retagger
from estnltk_core.taggers_registry import TaggersRegistry


class LayerResolver:
    """LayerResolver handles layer creation, and resolves layer dependencies automatically. 
       Upon creating a layer, it uses the TaggersRegistry to (recursively) find 
       and create all the prerequisite layers of the target layer.
       LayerResolver also holds default layers: the layers that are created when Text object's 
       tag_layer() is called without layer name arguments.
    """

    __slots__ = ['_initialized', '_taggers', 'default_layers']

    def __init__(self, taggers: TaggersRegistry, default_layers: Union[str, Sequence[str]] = []):
        object.__setattr__(self, '_initialized', False)
        self._taggers = taggers
        self.default_layers = default_layers

    def __copy__(self):
        raise Exception( ("Copying of {} object is not allowed. "+\
                          "If you want to create a new instance of EstNLTK's DEFAULT_RESOLVER, "+\
                          "use the make_resolver() function from module estnltk.default_resolver."+\
                          "").format( self.__class__.__name__ ) )

    def __deepcopy__(self, memo={}):
        raise Exception( ("Copying of {} object is not allowed. "+\
                          "If you want to create a new instance of EstNLTK's DEFAULT_RESOLVER, "+\
                          "use the make_resolver() function from module estnltk.default_resolver."+\
                          "").format( self.__class__.__name__ ) )

    def __setattr__(self, key, value):
        if key == 'default_layers':
            """
            Assign default layers to this resolver.
            Default layers are the layers created when Text object's tag_layer() 
            is called without layer name arguments. 
            Raises a ValueError if given layers are not registered in resolver's
            TaggersRegistry, and TypeError in case of wrong input type.
            """
            layers = value
            # Check that default_layers have expected format
            if not isinstance( layers, (list, tuple) ) and not isinstance( layers, str ):
                raise TypeError('(!) A list of layer names or a single layer name was expected.' )
            if isinstance( layers, str ):
                layers = tuple([layers])
            elif isinstance( layers, list ):
                layers = tuple(layers)
            creatable_layers = list(self.layers)
            for layer in layers:
                if layer not in creatable_layers:
                    raise ValueError( ('(!) TaggersRegistry has no entry for layer {!r}. '+
                                       'Registered layers are: {!r}').format( layer, creatable_layers ) )
            super().__setattr__('default_layers', layers)
            return
        elif key == '_taggers':
            """
            Assign _taggers. Can be done only in constructor.
            """
            if not self._initialized:
                if not isinstance( value, TaggersRegistry ):
                    raise TypeError( ('(!) Expected an instance of TaggersRegistry, '+
                                      'but got {}').format(type(value)) )
                super().__setattr__('_taggers', value)
                super().__setattr__('_initialized', True)
                return
        raise AttributeError('{} attribute {!r} cannot be set'.format(self.__class__.__name__, key))

    @property
    def layers(self) -> List[str]:
        '''Lists layers that can be created by this resolver in the order 
           in which they should be created.'''
        return list(self._taggers.list_layers())
    
    @property
    def layer_attributes(self) -> 'LayerResolver':
        """Changes TaggersRegistry's representation to show attributes of each layer.
        Returns self.
        """
        self._taggers.repr_format='brief_attr'
        return self
    
    @property
    def layer_dependencies(self) -> 'LayerResolver':
        """Changes TaggersRegistry's representation to show dependencies of each layer.
        Returns self.
        """
        self._taggers.repr_format='brief_dep'
        return self

    def update(self, tagger: Union[Tagger, Retagger]) -> None:
        '''Updates the Taggers registry with the given tagger or retagger.'''
        self._taggers.update(tagger)

    def taggers(self):
        '''Returns TaggersRegistry of this Resolver.'''
        return self._taggers

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
        default_layers = list(self.default_layers)
        default_layers_str = 'default_layers={!r}'.format(default_layers)
        taggers_str = ''
        if self._taggers:
            taggers_str = str(self._taggers) # this is a formatted table
        return '{classname}({default_layers})\n{info_table}'.format( classname=self.__class__.__name__, 
                                                                    default_layers=default_layers_str, 
                                                                    info_table=taggers_str)

    def _repr_html_(self):
        if self._taggers:
            default_layers = list(self.default_layers)
            default_layers_str = 'Default layers: <b>'+(', '.join(default_layers))+'</b>'
            return ('<h4>{}</h4>'.format(self.__class__.__name__))+'\n<br>'+\
                    default_layers_str+'\n</br>'+self._taggers._repr_html_()

