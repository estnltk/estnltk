from estnltk.taggers import TaggerOld, Retagger
from estnltk.taggers import VabamorfTagger
from estnltk.rewriting import PronounTypeRewriter


class PronounTypeTagger(TaggerOld):
    description = 'Tags pronouns with pronoun type attribute.'
    layer_name = 'pronoun_type'
    attributes = VabamorfTagger.output_attributes + ('pronoun_type',)
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
        text.add_layer(new_layer)


class PronounTypeRetagger(Retagger):
    """Tags pronouns with pronoun type attribute.

    """
    conf_param = ['pronoun_type_rewriter']

    def __init__(self, layer_name: str):
        self.input_layers = [layer_name]
        self.output_layer = layer_name
        self.output_attributes = ['pronoun_type']
        self.pronoun_type_rewriter = PronounTypeRewriter()

    def _change_layer(self, text, layers, status: dict):
        layer = layers[self.input_layers[0]]
        layer.attributes = layer.attributes + self.output_attributes
        rewrite = self.pronoun_type_rewriter.rewrite
        for span in layer:
            rewrite(span.annotations)
        return layer
