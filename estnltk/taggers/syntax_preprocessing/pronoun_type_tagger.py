from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger
from estnltk.rewriting import PronounTypeRewriter


class PronounTypeTagger(Tagger):
    description = 'Tags pronouns with pronoun type attribute.'
    layer_name = 'pronoun_type'
    attributes = VabamorfTagger.attributes + ('pronoun_type',)
    depends_on = ['morph_analysis']
    configuration = {}

    def __init__(self):
        self.pronoun_type_rewriter = PronounTypeRewriter()

    def tag(self, text, return_layer=False):
        new_layer = text['morph_analysis']
        source_attributes = new_layer.attributes + ('text',)
        target_attributes = self.attributes
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.pronoun_type_rewriter,
            name = self.layer_name,
            ambiguous = True
            )
        if return_layer:
            return new_layer
        text[self.layer_name] = new_layer
