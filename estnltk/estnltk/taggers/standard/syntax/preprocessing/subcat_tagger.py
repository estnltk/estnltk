from estnltk.taggers import Tagger
from .subcat_retagger import SubcatRetagger
from .morph_to_syntax_morph_retagger import MorphToSyntaxMorphRetagger
from estnltk.taggers import VabamorfTagger

class SubcatTagger(Tagger):
    """Tags subcategory information.

    """
    conf_param = ['morph_to_syntax_morph_tagger', 'subcat_retagger']

    def __init__(self, input_layer='morph_analysis', output_layer='morph_extended', fs_to_synt_rules_file=None,
                 subcat_rules_file=None):
        self.input_layers = [input_layer]
        self.output_layer = output_layer
        self.output_attributes = VabamorfTagger.output_attributes + ('subcat',)

        self.morph_to_syntax_morph_tagger = MorphToSyntaxMorphRetagger(input_layer=input_layer,
                                                                       output_layer=output_layer,
                                                                       fs_to_synt_rules_file=fs_to_synt_rules_file)
        self.subcat_retagger = SubcatRetagger(subcat_rules_file)

    def _make_layer(self, text, layers, status=None):
        layer = self.morph_to_syntax_morph_tagger.make_layer(text, layers)
        layers[layer.name] = layer
        self.subcat_retagger.change_layer(text, layers)
        return layer