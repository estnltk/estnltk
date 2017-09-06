from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger
from estnltk.rewriting import VerbExtensionSuffixRewriter


class VerbExtensionSuffixTagger(Tagger):
    description = 'Tags verb extension suffixes.'
    layer_name = 'verb_extension_suffix'
    attributes = VabamorfTagger.attributes + ('verb_extension_suffix',)
    depends_on = ['morph_analysis']
    configuration = {}

    def __init__(self):
        self.verb_extension_suffix_rewriter = VerbExtensionSuffixRewriter()

    def tag(self, text, return_layer=False):
        new_layer = text['morph_analysis']
        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ['verb_extension_suffix']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.verb_extension_suffix_rewriter,
            name = 'verb_extension_suffix',
            ambiguous = True
            )
        if return_layer:
            return new_layer
        text[self.layer_name] = new_layer
