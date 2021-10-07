from typing import Sequence, Union

from estnltk_core.base_text import BaseText
from estnltk_core.base_text import Layer

class Text( BaseText ):

    def tag_layer(self, layer_names: Union[str, Sequence[str]] = ('morph_analysis', 'sentences'), resolver=None) -> 'Text':
        from estnltk.resolve_layer_dag import DEFAULT_RESOLVER  # TODO: can we avoid inner import here?
        if resolver is None:
            resolver = DEFAULT_RESOLVER
        if isinstance(layer_names, str):
            layer_names = [layer_names]
        for layer_name in layer_names:
            resolver.apply(self, layer_name)
        return self

    def analyse(self, t: str, resolver=None) -> 'Text':
        """
        Analyses text by adding standard NLP layers. Analysis level specifies what layers must be present.
        # TODO: Complete documentation by explicitly stating what levels are present for which level
        """
        from estnltk.resolve_layer_dag import DEFAULT_RESOLVER  # TODO: can we avoid inner import here?
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



