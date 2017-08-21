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
from estnltk.text import Layer
from estnltk import PACKAGE_PATH
import os


class MorphExtendedTagger:
    """
    Tags text object with morph_extended layer. In order to do so executes
    consecutively several syntax preprocessing rewriters.

    (Text object with morph_extended layer can be converted to VISL CG3 input
    format by export_CG3 method.)
    """
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
        
        self._layer_name = 'morph_extended'
        self._attributes=['lemma',
                          'root',
                          'root_tokens',
                          'ending',
                          'clitic',
                          'form',
                          'partofspeech',
                          'punctuation_type', 
                          'pronoun_type',
                          'letter_case',
                          'fin',
                          'verb_extension_suffix',
                          'subcat']
        self._depends_on = ['words', 'morph_analysis']
        self._conf = 'fs_to_synt_rules_file='+fs_to_synt_rules_file+\
                     ', allow_to_remove_all='+str(allow_to_remove_all)+\
                     ', subcat_rules_file='+subcat_rules_file 

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

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on':self._depends_on,
                  'conf':self._conf}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'conf'])
        return df.to_html(index=False)

    @staticmethod
    def _esc_double_quotes(str1):
        ''' Escapes double quotes.
        '''
        return str1.replace('"', '\\"').replace('\\\\\\"', '\\"').replace('\\\\"', '\\"')

    def tag(self, text):
        source_attributes = ['lemma', 'root', 'ending', 'clitic', 'partofspeech', 'form']
        target_attributes = source_attributes + ['punctuation_type', 
                                                 'pronoun_type',
                                                 'letter_case',
                                                 'fin',
                                                 'verb_extension_suffix',
                                                 'subcat']
        source_attributes.append('text')

        new_layer = text['morph_analysis'].rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.quick_morph_extended_rewriter,
            name = self._layer_name,
            ambiguous = True
            )
        text[self._layer_name] = new_layer
