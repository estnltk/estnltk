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
import os


class MorphExtendedTagger(Tagger):
    """
    Tags text object with morph_extended layer. In order to do so executes
    consecutively several syntax preprocessing rewriters.

    (Text object with morph_extended layer can be converted to VISL CG3 input
    format by export_CG3 method.)
    """
    description = "Extends 'morph_analysis' layer with syntax preprocessing attributes."
    layer_name = 'morph_extended'
    attributes = VabamorfTagger.attributes + ('punctuation_type', 
                                              'pronoun_type',
                                              'letter_case',
                                              'fin',
                                              'verb_extension_suffix',
                                              'subcat')
    depends_on = ['morph_analysis']
    configuration = None

    def __init__(self,
                 fs_to_synt_rules_file=None,
                 allow_to_remove_all=False,
                 subcat_rules_file=None):
        ''' Initializes MorphExtendedTagger

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
        '''

        if fs_to_synt_rules_file is None:
            fs_to_synt_rules_file = os.path.join(PACKAGE_PATH,
                'rewriting/syntax_preprocessing/rules_files/tmorftrtabel.txt')
        if subcat_rules_file is None:
            subcat_rules_file = os.path.join(PACKAGE_PATH,
                'rewriting/syntax_preprocessing/rules_files/abileksikon06utf.lx')
        self.configuration = {'fs_to_synt_rules_file': fs_to_synt_rules_file,
                              'allow_to_remove_all': allow_to_remove_all,
                              'subcat_rules_file': subcat_rules_file}

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

    @staticmethod
    def _esc_double_quotes(str1):
        ''' Escapes double quotes.
        '''
        return str1.replace('"', '\\"').replace('\\\\\\"', '\\"').replace('\\\\"', '\\"')

    def tag(self, text, return_layer=False):
        source_attributes = text['morph_analysis'].attributes + ('text',)

        new_layer = text['morph_analysis'].rewrite(
                                    source_attributes=source_attributes,
                                    target_attributes=self.attributes,
                                    rules=self.quick_morph_extended_rewriter,
                                    name=self.layer_name,
                                    ambiguous = True
                                    )
        if return_layer:
            return new_layer
        text[self.layer_name] = new_layer
