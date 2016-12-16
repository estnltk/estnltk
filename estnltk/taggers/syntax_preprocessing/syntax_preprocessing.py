from estnltk.text import Layer

from estnltk.rewriting import PunctuationTypeRewriter
from estnltk.rewriting import MorphToSyntaxMorphRewriter
from estnltk.rewriting import PronounTypeRewriter
from estnltk.rewriting import RemoveDuplicateAnalysesRewriter
from estnltk.rewriting import LetterCaseRewriter
from estnltk.rewriting import FiniteFormRewriter
from estnltk.rewriting import VerbExtensionSuffixRewriter
from estnltk.rewriting import SubcatRewriter



class PronounTypeTagger():
    def __init__(self):
        self.pronoun_type_rewriter = PronounTypeRewriter()

    def tag(self, text):
        morph_extended = text['morf_analysis']
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['pronoun_type']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.pronoun_type_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )
        text['morph_extended'] = morph_extended


class FiniteFormTagger():

    def __init__(self, fs_to_synt_rules_file):
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.finite_form_rewriter = FiniteFormRewriter()

    def tag(self, text):
        morph_extended = text['morf_analysis']
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.morph_to_syntax_morph_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['fin']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.finite_form_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )
        text['morph_extended'] = morph_extended


class VerbExtensionSuffixTagger():

    def __init__(self):
        self.verb_extension_suffix_rewriter = VerbExtensionSuffixRewriter()

    def tag(self, text):
        morph_extended = text['morf_analysis']
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['verb_extension_suffix']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.verb_extension_suffix_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )
        text['morph_extended'] = morph_extended



class MorphExtendedTagger():

    def __init__(self, fs_to_synt_rules_file, allow_to_remove_all, subcat_rules_file):
        self.punctuation_type_rewriter = PunctuationTypeRewriter()
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.pronoun_type_rewriter = PronounTypeRewriter()
        self.remove_duplicate_analyses_rewriter = RemoveDuplicateAnalysesRewriter(allow_to_remove_all)
        self.letter_case_rewriter = LetterCaseRewriter()
        self.finite_form_rewriter = FiniteFormRewriter()
        self.verb_extension_suffix_rewriter = VerbExtensionSuffixRewriter()
        self.subcat_rules = SubcatRewriter(subcat_rules_file)

    @staticmethod
    def _esc_double_quotes(str1):
        ''' Escapes double quotes.
        '''
        return str1.replace('"', '\\"').replace('\\\\\\"', '\\"').replace('\\\\"', '\\"')

    def tag(self, text):

        dep = Layer(name='syntax_pp_0',
                         parent='words',
                         ambiguous=True,
                         attributes=['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form']
                         )
        text._add_layer(dep)
        for word, morf_anal in zip(text.words, text.morf_analysis):
            for analysis in morf_anal:
                m = word.mark('syntax_pp_0')
                m.word_text = analysis.text
                m.root = self._esc_double_quotes(analysis.root)
                m.ending = analysis.ending
                m.clitic = analysis.clitic
                m.partofspeech = analysis.partofspeech
                m.form = analysis.form
        morph_extended = text['syntax_pp_0']

        print('z', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['punctuation_type']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.punctuation_type_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        print('m', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.morph_to_syntax_morph_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('p', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['pronoun_type']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.pronoun_type_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        print('d', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.remove_duplicate_analyses_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        print('c', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['letter_case']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.letter_case_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('f', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['fin']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.finite_form_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('p', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['verb_extension_suffix']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.verb_extension_suffix_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('s', end='', flush=True)
        source_attributes = morph_extended.attributes
        target_attributes = source_attributes + ['subcat']
        morph_extended = morph_extended.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.subcat_rules,
            name = 'morph_extended',
            ambiguous = True
            )

        text['morph_extended'] = morph_extended