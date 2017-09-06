from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger
from estnltk.rewriting import MorphToSyntaxMorphRewriter
from estnltk.rewriting import SubcatRewriter


class SubcatTagger(Tagger):
    description = 'Tags subcategory information.'
    layer_name = 'subcat'
    attributes = VabamorfTagger.attributes + ('subcat',)
    depends_on = ['morph_analysis']
    configuration = {}

    def __init__(self, fs_to_synt_rules_file, subcat_rules_file):
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.subcat_rewriter = SubcatRewriter(subcat_rules_file)

        self.configuration['fs_to_synt_rules_file'] = fs_to_synt_rules_file
        self.configuration['subcat_rules_file'] = subcat_rules_file

    def tag(self, text, return_layer=False):
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
        target_attributes = self.attributes
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.subcat_rewriter,
            name = self.layer_name,
            ambiguous = True
            )
        if return_layer:
            return new_layer
        text[self.layer_name] = new_layer
