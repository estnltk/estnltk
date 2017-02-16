from estnltk.text import Layer

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


class PronounTypeTagger():
    def __init__(self):
        self.pronoun_type_rewriter = PronounTypeRewriter()

    def tag(self, text):
        new_layer = text['morf_analysis']
        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ['pronoun_type']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.pronoun_type_rewriter,
            name = 'pronoun_type',
            ambiguous = True
            )
        text['pronoun_type'] = new_layer


class FiniteFormTagger():

    def __init__(self, fs_to_synt_rules_file):
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.finite_form_rewriter = FiniteFormRewriter()

    def tag(self, text):
        new_layer = text['morf_analysis']
        source_attributes = new_layer.attributes
        target_attributes = source_attributes
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.morph_to_syntax_morph_rewriter,
            name = 'finite_form',
            ambiguous = True
            )

        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ['fin']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.finite_form_rewriter,
            name = 'finite_form',
            ambiguous = True
            )
        text['finite_form'] = new_layer


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


class SubcatTagger():

    def __init__(self, fs_to_synt_rules_file, subcat_rules_file):
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.subcat_rewriter = SubcatRewriter(subcat_rules_file)

    def tag(self, text):
        new_layer = text['morf_analysis']
        source_attributes = new_layer.attributes
        target_attributes = source_attributes
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.morph_to_syntax_morph_rewriter,
            name = 'subcat',
            ambiguous = True
            )

        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ['subcat']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.subcat_rewriter,
            name = 'subcat',
            ambiguous = True
            )
        text['subcat'] = new_layer


class MorphExtendedTagger():

    def __init__(self, fs_to_synt_rules_file, allow_to_remove_all, subcat_rules_file):
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
        new_layer = text['syntax_pp_0']

        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ['punctuation_type', 
                                                 'pronoun_type',
                                                 'letter_case',
                                                 'fin',
                                                 'verb_extension_suffix',
                                                 'subcat']
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.quick_morph_extended_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )
        text['morph_extended'] = new_layer