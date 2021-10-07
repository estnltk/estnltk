from typing import Sequence, Union

from estnltk_core.base_text import BaseText
from estnltk_core.base_text import Layer

class Text( BaseText ):
    # All methods for BaseText/Text object

    def tag_layer(self, layer_names: Union[str, Sequence[str]] = ('morph_analysis', 'sentences'), resolver=None) -> 'Text':
        raise NotImplementedError('(!) The NLP pipeline is not available in estnltk-core. Please use the full EstNLTK package for the pipeline.')

    def analyse(self, t: str, resolver=None) -> 'Text':
        """
        Analyses text by adding standard NLP layers. Analysis level specifies what layers must be present.

        # TODO: Complete documentation by explicitly stating what levels are present for which level
        """
        raise NotImplementedError('(!) The NLP pipeline is not available in estnltk-core. Please use the full EstNLTK package for the pipeline.')
