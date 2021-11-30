from typing import Sequence, Union, Set, List, Union, Any, Mapping
from typing import DefaultDict

import networkx as nx

from estnltk_core.base_text import BaseText
from estnltk_core.base_text import Layer

class Text( BaseText ):
    # All methods for BaseText/Text object
    # methods: Set[str]
    methods = {
        '_repr_html_',
        'add_layer',
        'analyse',
        'attributes',
        'pop_layer',
        'diff',
        'layers',
        'sorted_layers',
        'tag_layer',
        'topological_sort',
    } | {method for method in dir(object) if callable(getattr(object, method, None))}

    # presorted_layers used in for visualization purposes (BaseText._repr_html_)
    # presorted_layers: Tuple[str, ...]
    presorted_layers = (
        'paragraphs',
        'sentences',
        'tokens',
        'compound_tokens',
        'normalized_words',
        'words',
        'morph_analysis',
        'morph_extended'
    )

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
        if 'tokens' in self._layers and t != 'all':
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

    def __delattr__(self, item):
        raise TypeError("'{}' object does not support attribute deletion, use pop_layer(...) function instead".format( self.__class__.__name__ ))

    def __getattr__(self, item):
        # Resolve slots
        if item in self.__class__.__slots__:
            return self.__getattribute__(item)

        # Resolve all function calls
        if item in self.__class__.methods:
            return self.__getattribute__(item)

        # Resolve layers
        if item in self.layers:
            return self.__getitem__(item)

        # Resolve attributes that uniquely determine a layer, e.g. BaseText/Text.lemmas ==> BaseText/Text.morph_layer.lemmas
        attributes = self.__getattribute__('attributes')

        if len(attributes[item]) == 1:
            return getattr(self._layers[attributes[item][0]], item)

        # Nothing else to resolve
        raise AttributeError("'{}' object has no layer {!r}".format( self.__class__.__name__, item ))
    

