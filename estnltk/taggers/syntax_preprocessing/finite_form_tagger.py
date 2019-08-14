from estnltk.taggers import TaggerOld, Retagger, SpanRewriter
from estnltk.taggers import VabamorfTagger
from estnltk.rewriting import MorphToSyntaxMorphRewriter
from estnltk.rewriting import FiniteFormRewriter
from estnltk.layer.annotation import Annotation


class FiniteFormTagger(TaggerOld):
    description = 'Tags finite form tags for verbs.'
    layer_name = 'finite_form'
    attributes = VabamorfTagger.output_attributes + ('fin',)
    depends_on = ['morph_analysis']
    configuration = {}

    def __init__(self, fs_to_synt_rules_file):
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.finite_form_rewriter = FiniteFormRewriter()

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
            rules = self.finite_form_rewriter,
            name = self.layer_name,
            ambiguous = True
            )
        if return_layer:
            return new_layer
        text[self.layer_name] = new_layer


class _FiniteFormRetagger(Retagger):
    """Tags finite form tags for verbs.

    """
    layer_name = 'finite_form'
    attributes = VabamorfTagger.output_attributes + ('fin',)
    conf_param = ['morph_to_syntax_morph_rewriter', 'finite_form_rewriter']

    def __init__(self, layer_name, fs_to_synt_rules_file):
        self.input_layers = [layer_name]
        self.output_layer = layer_name
        self.output_attributes = ['fin']

        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.finite_form_rewriter = FiniteFormRewriter()

    def _change_layer(self, text, layers, status: dict):
        layer = layers[self.input_layers[0]]
        layer.attributes = layer.attributes + self.output_attributes
        rewrite_morph_to_syntax_morph = self.morph_to_syntax_morph_rewriter.rewrite
        rewrite_finite_form = self.finite_form_rewriter.rewrite
        for span in layer:
            records = span.to_records(with_text=True)
            span.clear_annotations()
            records = rewrite_morph_to_syntax_morph(records)
            records = rewrite_finite_form(records)
            for record in records:
                span.add_annotation(Annotation(**record))
        return layer


class FiniteFormRetagger(SpanRewriter):
    """Tags finite form tags for verbs.

    """

    def __init__(self, layer_name, fs_to_synt_rules_file):
        morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        finite_form_rewriter = FiniteFormRewriter()

        def function(records):
            records = morph_to_syntax_morph_rewriter.rewrite(records)
            records = finite_form_rewriter.rewrite(records)
            return records

        super().__init__(layer_name=layer_name, output_attributes=['fin'], function=function)
