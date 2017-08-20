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
    def __init__(self,
                 fs_to_synt_rules_file=None,
                 allow_to_remove_all=False,
                 subcat_rules_file=None):
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

        # TODO: remove 'word_text'
        dep = Layer(name='syntax_pp_0',
                         parent='words',
                         ambiguous=True,
                         attributes=['word_text', 'lemma', 'root', 'ending', 'clitic', 'partofspeech', 'form']
                         )
        text._add_layer(dep)
        for word, morf_anal in zip(text.words, text.morph_analysis):
            for analysis in morf_anal:
                m = word.mark('syntax_pp_0')
                m.word_text = analysis.text
                m.lemma = analysis.lemma
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
            name = self._layer_name,
            ambiguous = True
            )
        text[self._layer_name] = new_layer
