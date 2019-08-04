from estnltk.taggers import Tagger
from estnltk.rewriting import PunctuationTypeRewriter
from estnltk.rewriting import MorphToSyntaxMorphRewriter
from estnltk.rewriting import PronounTypeRewriter
from estnltk.rewriting import RemoveDuplicateAnalysesRewriter
from estnltk.rewriting import RemoveAdpositionAnalysesRewriter
from estnltk.rewriting import LetterCaseRewriter
from estnltk.rewriting import FiniteFormRewriter
from estnltk.rewriting import VerbExtensionSuffixRewriter
from estnltk.rewriting import SubcatRewriter
from estnltk.rewriting import MorphExtendedRewriter
from estnltk.taggers import VabamorfTagger
from estnltk import PACKAGE_PATH
from estnltk.layer.layer import Layer
import os


class MorphExtendedTagger(Tagger):
    """Creates morph_extended layer which contains morph analysis attributes and syntax preprocessing attributes.
    In order to do so executes consecutively several syntax preprocessing rewriters.

    (Text object with morph_extended layer can be converted to VISL CG3 input
    format by export_CG3 method.)

    """
    input_layers = ['morph_analysis']
    output_layer = 'morph_extended'
    output_attributes = VabamorfTagger.output_attributes + ('punctuation_type',
                                                            'pronoun_type',
                                                            'letter_case',
                                                            'fin',
                                                            'verb_extension_suffix',
                                                            'subcat')

    conf_param = ['fs_to_synt_rules_file', 'allow_to_remove_all', 'subcat_rules_file',
                  'quick_morph_extended_rewriter']

    # TODO: remove next three lines
    layer_name = output_layer
    attributes = output_attributes
    depends_on = input_layers

    def __init__(self,
                 fs_to_synt_rules_file=None,
                 allow_to_remove_all=False,
                 subcat_rules_file=None):
        """ Initializes MorphExtendedTagger

            Parameters
            -----------
            fs_to_synt_rules_file : str
                Name of the file containing rules for mapping from Filosoft's
                old mrf format to syntactic analyzer's preprocessing mrf format;
                (~~'tmorftrtabel.txt')

            subcat_rules_file : str
                Name of the file containing rules for adding subcategorization
                information to verbs/adpositions;
                (~~'abileksikon06utf.lx')

            allow_to_remove_all : bool
                Specifies whether the method remove_duplicate_analyses() is allowed to
                remove all analysis of a word token (due to the specific _K_-removal rules).
                The original implementation allowed this, but we are now restricting it
                in order to avoid words without any analyses;
                Default: False

        """
        if fs_to_synt_rules_file is None:
            fs_to_synt_rules_file = os.path.relpath(os.path.join(
                    PACKAGE_PATH, 'rewriting/syntax_preprocessing/rules_files/tmorftrtabel.txt'))
        if subcat_rules_file is None:
            subcat_rules_file = os.path.relpath(os.path.join(
                    PACKAGE_PATH, 'rewriting/syntax_preprocessing/rules_files/abileksikon06utf.lx'))

        self.fs_to_synt_rules_file = fs_to_synt_rules_file
        self.allow_to_remove_all = allow_to_remove_all
        self.subcat_rules_file = subcat_rules_file

        punctuation_type_rewriter = PunctuationTypeRewriter()
        morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        pronoun_type_rewriter = PronounTypeRewriter()
        remove_duplicate_analyses_rewriter = RemoveDuplicateAnalysesRewriter()
        remove_adposition_analyses_rewriter = RemoveAdpositionAnalysesRewriter(allow_to_remove_all)
        letter_case_rewriter = LetterCaseRewriter()
        finite_form_rewriter = FiniteFormRewriter()
        verb_extension_suffix_rewriter = VerbExtensionSuffixRewriter()
        subcat_rewriter = SubcatRewriter(subcat_rules_file)

        self.quick_morph_extended_rewriter = MorphExtendedRewriter(
                punctuation_type_rewriter=punctuation_type_rewriter,
                morph_to_syntax_morph_rewriter=morph_to_syntax_morph_rewriter,
                pronoun_type_rewriter=pronoun_type_rewriter,
                remove_duplicate_analyses_rewriter=remove_duplicate_analyses_rewriter,
                remove_adposition_analyses_rewriter=remove_adposition_analyses_rewriter,
                letter_case_rewriter=letter_case_rewriter,
                finite_form_rewriter=finite_form_rewriter,
                verb_extension_suffix_rewriter=verb_extension_suffix_rewriter,
                subcat_rewriter=subcat_rewriter)

    def _make_layer(self, text, layers, status=None):
        morph_layer = layers[self.input_layers[0]]

        layer = Layer(name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=text,
                      parent=morph_layer.name,
                      ambiguous=True,
                      )

        for span in morph_layer:
            input_record = span.to_records(with_text=True)
            for record in self.quick_morph_extended_rewriter.rewrite(input_record):
                layer.add_annotation(span.base_span, **record)

        return layer
