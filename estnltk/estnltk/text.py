from typing import Sequence, Union, Set, List, Union, Any, Mapping
from typing import DefaultDict

import networkx as nx

from estnltk_core.base_text import BaseText
from estnltk_core.base_text import Layer

class Text( BaseText ):

    # basic slots are inherited from the parent, therefore define only extra slots
    __slots__ = ['_shadowed_layers']

    def __init__(self, text: str = None) -> None:
        super().__init__( text )
        object.__setattr__(self, '_shadowed_layers', {})

    def __setstate__(self, state):
        super().__setstate__(state)
        object.__setattr__(self, '_shadowed_layers', {})

    def __getitem__(self, item):
        if item in self._shadowed_layers:
            return self._shadowed_layers[item]
        return super().__getitem__(item)

    @property
    def layers(self) -> Set[str]:
        """
        Returns the names of all layers in the text object in alphabetical order.
        """
        return super().layers | self._shadowed_layers.keys()
    
    @property
    def attributes(self) -> DefaultDict[str, List[str]]:
        """
        Returns all attributes together with layer names hosting them.
        """
        result = super().attributes
        
        # Collect attributes from shadowed layers
        for name, layer in self._shadowed_layers.items():
            for attrib in layer.attributes:
                result[attrib].append(name)

        return result

    def add_layer(self, layer: Layer):
        """
        Adds a layer to the text object.
        """
        # TODO: the validation logic below duplicates the logic in BaseText.add_layer(...) -- abstract it into separate method
        assert isinstance(layer, Layer), 'Layer expected, got {!r}'.format(type(layer))

        name = layer.name
        
        assert name not in self.__dict__, 'this {} object already has a layer with name {!r}'.format(self.__class__.__name__, name)

        if layer.text_object is None:
            layer.text_object = self
        else:
            assert layer.text_object is self, \
                "can't add layer {!r}, this layer is already bound to another {} object".format(name, self.__class__.__name__)

        if layer.parent:
            assert layer.parent in self.__dict__, 'Cant add a layer "{layer}" before adding its parent "{parent}"'.format(
                parent=layer.parent, layer=layer.name)

        if layer.enveloping:
            assert layer.enveloping in self.__dict__, "can't add an enveloping layer before adding the layer it envelops"

        if name in self.__class__.methods:
            self._shadowed_layers[name] = layer
        else:
            super().add_layer( layer )

    def pop_layer(self, name: str,  cascading: bool = True, default=Ellipsis) -> Union[Layer, Any]:
        """
        Removes a layer from the text object together with the layers that are computed from it by default.
        """
        if name in self._shadowed_layers:
            if not cascading:
                return self._shadowed_layers.pop(name, None)
            else:
                # TODO: the dependency-finding logic below duplicates the logic in BaseText.pop_layer(...) -- 
                #       abstract it into separate method
                
                # Find all dependencies between layers. The implementations is complete overkill.
                # However, further optimisation is not worth the time.
                relations = set()
                for layer_name, layer in self.__dict__.items():
                    relations.update((b, a) for a, b in [
                        (layer_name, layer.parent),
                        (layer_name, layer.enveloping)] if b is not None and a != b
                                     )

                g = nx.DiGraph()
                g.add_edges_from(relations)
                g.add_nodes_from(self.__dict__.keys())

                to_delete = nx.descendants(g, name)

                result = self._shadowed_layers.pop(name, None)
                for name in to_delete:
                    if not self.__dict__.pop(name):
                        self._shadowed_layers.pop(name, None)
                return result
        else:
            super().pop_layer(name)


    def tag_layer(self, layer_names: Union[str, Sequence[str]]=None, resolver=None) -> 'Text':
        from estnltk.default_resolver import DEFAULT_RESOLVER
        if resolver is None:
            resolver = DEFAULT_RESOLVER
        if isinstance(layer_names, str):
            layer_names = [layer_names]
        if layer_names is None:
            layer_names = resolver.get_default_layers()
        for layer_name in layer_names:
            resolver.apply(self, layer_name)
        return self

    def analyse(self, t: str, resolver=None) -> 'Text':
        """
        Analyses text by adding standard NLP layers. Analysis level specifies what layers must be present.
        # TODO: Complete documentation by explicitly stating what levels are present for which level
        """
        from estnltk.default_resolver import DEFAULT_RESOLVER
        if resolver is None:
            resolver = DEFAULT_RESOLVER
        if t == 'segmentation':
            self.tag_layer(['paragraphs'], resolver)
        elif t == 'morphology':
            self.tag_layer(['morph_analysis'], resolver)
        elif t == 'syntax_preprocessing':
            self.tag_layer(['sentences', 'morph_extended'], resolver)
        elif t == 'all':
            self.tag_layer(['paragraphs', 'morph_extended'], resolver)
        else:
            raise ValueError("invalid argument: '" + str(t) +
                             "', use 'segmentation', 'morphology' or 'syntax' instead")
        if 'tokens' in self.__dict__ and t != 'all':
            self.pop_layer('tokens')
        return self

    # attribute_mapping_for_elementary_layers: Mapping[str, str]
    attribute_mapping_for_elementary_layers = {
        'lemma': 'morph_analysis',
        'root': 'morph_analysis',
        'root_tokens': 'morph_analysis',
        'ending': 'morph_analysis',
        'clitic': 'morph_analysis',
        'form': 'morph_analysis',
        'partofspeech': 'morph_analysis'
    }

    attribute_mapping_for_enveloping_layers = attribute_mapping_for_elementary_layers

    def __getattr__(self, item):
        # Function __getattr__ is never called on items in __dict__

        # Resolve slots
        if item in self.__class__.__slots__:
            return self.__getattribute__(item)

        # Resolve all function calls
        if item in self.__class__.methods:
            return self.__getattribute__(item)

        # Resolve attributes that uniquely determine a layer, e.g. BaseText/Text.lemmas ==> BaseText/Text.morph_layer.lemmas
        attributes = self.__getattribute__('attributes')

        if len(attributes[item]) == 1:
            return getattr(self.__dict__[attributes[item][0]], item)

        # Nothing else to resolve
        raise AttributeError("'{}' object has no layer {!r}".format( self.__class__.__name__, item ))