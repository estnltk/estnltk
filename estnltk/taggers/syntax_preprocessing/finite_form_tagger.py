from estnltk.rewriting import MorphToSyntaxMorphRewriter
from estnltk.rewriting import FiniteFormRewriter


class FiniteFormTagger():

    def __init__(self, fs_to_synt_rules_file):
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.finite_form_rewriter = FiniteFormRewriter()

    def tag(self, text):
        new_layer = text['morph_analysis']
        source_attributes = new_layer.attributes
        target_attributes = source_attributes
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.morph_to_syntax_morph_rewriter,
            name = 'morph_analysis',
            ambiguous = True
            )

        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ['fin']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.finite_form_rewriter,
            name = 'finite_form',
            ambiguous = True
            )
        text['finite_form'] = new_layer
