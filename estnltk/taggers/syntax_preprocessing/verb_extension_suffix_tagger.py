from estnltk.rewriting import VerbExtensionSuffixRewriter


class VerbExtensionSuffixTagger():

    def __init__(self):
        self.verb_extension_suffix_rewriter = VerbExtensionSuffixRewriter()

    def tag(self, text):
        new_layer = text['morf_analysis']
        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ['verb_extension_suffix']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.verb_extension_suffix_rewriter,
            name = 'verb_extension_suffix',
            ambiguous = True
            )
        text['verb_extension_suffix'] = new_layer
