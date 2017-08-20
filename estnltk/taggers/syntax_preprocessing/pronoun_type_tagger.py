from estnltk.rewriting import PronounTypeRewriter


class PronounTypeTagger():
    def __init__(self):
        self.pronoun_type_rewriter = PronounTypeRewriter()

    def tag(self, text):
        new_layer = text['morph_analysis']
        source_attributes = new_layer.attributes + ['text']
        target_attributes = new_layer.attributes + ['pronoun_type']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.pronoun_type_rewriter,
            name = 'pronoun_type',
            ambiguous = True
            )
        text['pronoun_type'] = new_layer
