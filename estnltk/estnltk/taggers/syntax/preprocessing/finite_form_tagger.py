from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger
from .morph_to_syntax_morph_retagger import MorphToSyntaxMorphRetagger
from .finite_form_retagger import FiniteFormRetagger


class FiniteFormTagger(Tagger):
    """FiniteFormTagger

    """
    conf_param = ['morph_to_syntax_morph_tagger', 'finite_form_retagger']

    def __init__(self, input_layer='morph_analysis', output_layer='morph_extended', fs_to_synt_rules_file=None):
        self.input_layers = [input_layer]
        self.output_layer = output_layer
        self.output_attributes = VabamorfTagger.output_attributes + ('fin',)

        self.morph_to_syntax_morph_tagger = MorphToSyntaxMorphRetagger(input_layer=input_layer,
                                                                       output_layer=output_layer,
                                                                       fs_to_synt_rules_file=fs_to_synt_rules_file)
        self.finite_form_retagger = FiniteFormRetagger()

    def _make_layer(self, text, layers, status=None):
        layer = self.morph_to_syntax_morph_tagger.make_layer(text, layers)
        layers[layer.name] = layer
        self.finite_form_retagger.change_layer(text, layers)
        return layer
