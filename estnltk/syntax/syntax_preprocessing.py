# -*- coding: utf-8 -*- 
#
#   Preprocessing methods for VISL-CG3 based syntactic analysis of Estonian;
#
#   Contains Python reimplementation for the pre-processing pipeline introduced
#   in  https://github.com/EstSyntax/EstCG  
#   ( from the EstCG snapshot: 
#   https://github.com/EstSyntax/EstCG/tree/467f0746ae870169776b0ed7aef8825730fea671 )
#   
#   The pipeline:
#   1) convert_vm_json_to_mrf( )
#      convert_Text_to_mrf( )
#       * converts vabamorf's JSON or Estnltk's Text into Filosoft's old mrf 
#         format;
#   2) convert_mrf_to_syntax_mrf( )
#       * converts Filosoft's old mrf format into syntactic analyzer's preprocessing 
#         mrf format;
#       * uses built-in rules for punctuation conversion and rules from the file 
#         'tmorftrtabel.txt' for word analysis conversion;
#       * this step performs a large part of the conversion, however, subsequent steps
#         are required for adding specific details;
#   3) convert_pronouns( )
#       * adds specific information/categories related to pronouns; uses a list
#         of built-in conversion rules;
#   4) remove_duplicate_analyses( )
#       * removes duplicate analyses;
#       * removes redundant adposition analyses (specific logic for that);
#   5) add_hashtag_info( ):
#       * adds hashtags containing information about capitalization, 
#                                                      finite verbs, 
#                                            nud/tud/mine/... forms;
#   6) tag_subcat_info( ):
#       * adds hashtags containing information about verb subcategorization;
#       * adds hashtags containing information about adposition subcategorization;
#   7) remove_duplicate_analyses( )
#       * removes duplicate analyses;
#       * removes redundant adposition analyses (specific logic for that);
#   8) convert_to_cg3_input( )
#       * converts from the syntax preprocessing format to cg3 input format;
#
#   Example usage:
#
#      from estnltk import Text
#      from syntax_preprocessing import SyntaxPreprocessing
#
#      #  Set the variables:
#      #    fsToSyntFulesFile -- path to 'tmorftrtabel.txt'
#      #    subcatFile        -- path to 'abileksikon06utf.lx'
#      #    text              -- the text to be analyzed, estnltk Text object;
# 
#      # Preprocessing for the syntax
#      pipeline1 = SyntaxPreprocessing( fs_to_synt=fsToSyntFulesFile, subcat=subcatFile )
#      results1  = pipeline1.process_Text( text )
#
#      print( results1 )
#

from __future__ import unicode_literals, print_function


import re
import os.path
import codecs
from collections import defaultdict

from estnltk.legacy.core import PACKAGE_PATH
from estnltk.text import Layer

SYNTAX_PATH      = os.path.join(PACKAGE_PATH, 'syntax', 'files')
FS_TO_SYNT_RULES_FILE = os.path.join(SYNTAX_PATH, 'tmorftrtabel.txt')
SUBCAT_RULES_FILE     = os.path.join(SYNTAX_PATH, 'abileksikon06utf.lx')

# ==================================================================================
#   Utils
# ==================================================================================

def _esc_double_quotes( str1 ):
    ''' Escapes double quotes.
    '''
    return str1.replace('"', '\\"').replace('\\\\\\"', '\\"').replace('\\\\"', '\\"')
    
def _esc_que_mark( analysis ):
    ''' Replaces a question mark in analysis (e.g. '//_N_ ? //')  
        with an escaped version of the question mark #?
    '''
    return (analysis.replace(' ?', ' #?')).replace(' ?', ' #?')


class MorphExtendedTagger():

    def __init__(self, fs_to_synt_rules_file, allow_to_remove_all, subcat_rules_file):
        self.initial_morph_rewriter = InitialMorphRewriter()
        self.punctuation_type_rewriter = PunctuationTypeRewriter()
        self.morph_to_syntax_morph_rewriter = MorphToSyntaxMorphRewriter(fs_to_synt_rules_file)
        self.pronoun_type_rewriter = PronounTypeRewriter()
        self.remove_duplicate_analyses_rewriter = RemoveDuplicateAnalysesRewriter(allow_to_remove_all)
        self.letter_case_rewriter = LetterCaseRewriter()
        self.finite_form_rewriter = FiniteFormRewriter()
        self.partic_rewriter = ParticRewriter()
        self.subcat_rules = SubcatRewriter(subcat_rules_file)


    def tag(self, text):
        
        #morph_extended = text['morf_analysis']

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
                m.root = _esc_double_quotes(analysis.root)
                m.ending = analysis.ending
                m.clitic = analysis.clitic
                m.partofspeech = analysis.partofspeech
                m.form = analysis.form
        morph_extended = text['syntax_pp_0']

        print('i', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form'],
            rules = self.initial_morph_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        print('z', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type'],
            rules = self.punctuation_type_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        print('m', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type'],
            rules = self.morph_to_syntax_morph_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('p', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type'],
            rules = self.pronoun_type_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        print('d', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type'],
            rules = self.remove_duplicate_analyses_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        print('c', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type', 'letter_case'],
            rules = self.letter_case_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('f', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type', 'letter_case'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type', 'letter_case', 'fin'],
            rules = self.finite_form_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('p', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type', 'letter_case', 'fin'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type', 'letter_case', 'fin', 'verb_extension_suffix'],
            rules = self.partic_rewriter,
            name = 'morph_extended',
            ambiguous = True
            )

        # kasulik
        print('s', end='', flush=True)
        morph_extended = morph_extended.rewrite(
            source_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type', 'letter_case', 'fin', 'verb_extension_suffix'],
            target_attributes = ['word_text', 'root', 'ending', 'clitic', 'partofspeech', 'form', 'punctuation_type', 'pronoun_type', 'letter_case', 'fin', 'verb_extension_suffix', 'abileksikon'],
            rules = self.subcat_rules,
            name = 'morph_extended',
            ambiguous = True
            )

        text['morph_extended'] = morph_extended


# ==================================================================================
# ==================================================================================
#   1)  Convert from estnltk Text to Filosoft's mrf
#       (former 'json2mrf.pl')
# ==================================================================================
# ==================================================================================


class InitialMorphRewriter():
    ''' Converts from Text object into pre-syntactic mrf format, given as a list of 
        lines, as in the output of etmrf.
        *) If the input Text has already been morphologically analysed, uses the existing
            analysis;
        *) If the input has not been analysed, performs the analysis with required settings:
            word quessing is turned on, proper-name analyses are turned off;
    '''
    def rewrite(self, record):
        # kasutu
        return record
        result = []
        print('rec', record)
        for rec in record:
            rec['root'] = _esc_double_quotes(rec['root'])
            for form in rec['form'].split(',')[::-1]:
                #kas form.split(',')==[form] sageli või alati?
                # [::-1] on eelmise versiooniga ühildumiseks
                form = form.strip()
                if form:
                    rec_copy = rec.copy()
                    rec_copy['form'] = form
                    result.append(rec_copy)
        print('res', result)
        return result

# ==================================================================================
# ==================================================================================
#   2)  Convert from Filosoft's mrf to syntactic analyzer's mrf
#       (former 'rtolkija.pl')
# ==================================================================================
# ==================================================================================

    
_punctOrAbbrev = re.compile('//\s*_[ZY]_')


class PunctuationTypeRewriter():
    ''' Converts given analysis line if it describes punctuation; Uses the set 
        of predefined punctuation conversion rules from _punctConversions;
        
        _punctConversions should be a list of lists, where each outer list stands 
        for a single conversion rule and inner list contains a pair of elements:
        first is the regexp pattern and the second is the replacement, used in
           re.sub( pattern, replacement, line )
        
        Returns the converted line (same as input, if no conversion was 
        performed);
    ''' 

    def rewrite(self, record):
        result = []
        for rec in record:
            if rec['partofspeech'] == 'Z':
                rec['punctuation_type'] = self._get_punctuation_type(rec)
            else:
                rec['punctuation_type'] = None
            result.append(rec)
        return result

    _punctConversions = (
                          ("…$",      "Ell"),
                          ("\.\.\.$", "Ell"),
                          ("\.\.$",   "Els"),
                          ("\.$",     "Fst"),
                          (",$",      "Com"),
                          (":$",      "Col"),
                          (";$",      "Scl"),
                          ("(\?+)$",  "Int"),
                          ("(\!+)$",  "Exc"),
                          ("(---?)$", "Dsd"),
                          ("(-)$",    "Dsh"),
                          ("\($",     "Opr"),
                          ("\)$",     "Cpr"),
                          ('\\\\"$',  "Quo"),
                          ("«$",      "Oqu"),
                          ("»$",      "Cqu"),
                          ("“$",      "Oqu"),
                          ("”$",      "Cqu"),
                          ("<$",      "Grt"),
                          (">$",      "Sml"),
                          ("\[$",     "Osq"),
                          ("\]$",     "Csq"),
                          ("/$",      "Sla"),
                          ("\+$",     "crd")
    )# double quotes are escaped by \
    # puudu '‹'

    def _get_punctuation_type(self, morph_extended):
        for pattern, punct_type in self._punctConversions:
            if re.search(pattern, morph_extended['root']):
                # kas match või search?     "//", ".-"
                # või hoopis pattern==morph_extended.root?
                # praegu on search, sest see klapib eelmise versiooniga
                return punct_type



class MorphToSyntaxMorphRewriter():
    ''' Converts given lines from Filosoft's mrf format to syntactic analyzer's
        format, using the morph-category conversion rules from conversion_rules,
        and punctuation via method _convert_punctuation();
        As a result of conversion, the input list  mrf_lines  will be modified,
        and also returned after a successful conversion;

        Morph-category conversion rules should be loaded via method
            load_fs_mrf_to_syntax_mrf_translation_rules( rulesFile ),
        usually from a file named 'tmorftrtabel.txt';

        Note that the resulting list of lines likely has more lines than the
        original list had, because the conversion often requires that the
        original Filosoft's analysis is expanded into multiple analyses
        suitable for the syntactic analyzer;
    '''    
    def __init__(self, fs_to_synt_rules_file):
        self.fs_to_synt_rules = \
            self.load_fs_mrf_to_syntax_mrf_translation_rules(fs_to_synt_rules_file)

    
    def rewrite(self, record):
        result = []
        for rec in record:
            pos = rec['partofspeech']
            form = rec['form']
            # 1) Convert punctuation
            if pos == 'Z':
                pass
                #rec['punctuation_type'] = _get_punctuation_type(rec)
                #rec['pronoun_type'] = None
                #rec['form_list'] = [rec['punctuation_type']]
                #rec['initial_form'] = [rec['punctuation_type']]
                result.append(rec)
            else:
                if pos == 'Y':
                    # järgmine rida on kasutu, siin tuleb _form muuta, kui _root=='…'
                    #line = _convert_punctuation(rec)
                    pass

            # 2) Convert morphological analyses that have a form specified
                if form:
                    morphKey = (pos, form)
                else:
                    morphKey = (pos, '')
                for pos, form in self.fs_to_synt_rules[morphKey]:
                    rec['partofspeech'] = pos
                    rec['form'] = _esc_que_mark(form).strip()
                    result.append(rec.copy())
        return result


    def load_fs_mrf_to_syntax_mrf_translation_rules(self, fs_to_synt_rules_file):
        ''' Loads rules that can be used to convert from Filosoft's mrf format to
            syntactic analyzer's format. Returns a dict containing rules.
    
            Expects that each line in the input file contains a single rule, and that
            different parts of the rule are separated by @ symbols, e.g.
    
                1@_S_ ?@Substantiiv apellatiiv@_S_ com @Noun common@Nc@NCSX@kesk-
                32@_H_ ?@Substantiiv prooprium@_S_ prop @Noun proper@Np@NPCSX@Kesk-
                313@_A_@Adjektiiv positiiv@_A_ pos@Adjective positive@A-p@ASX@salkus
    
            Only the 2nd element and the 4th element are extracted from each line.
            Both are treated as a pair of strings. The 2nd element will be the key
            of the dict entry, and 4th element will be added to the value of the
            dict entry:
            {('S', '?'): [('S', 'com ')],
             ('H', '?'): [('S', 'prop ')],
             ('A', ''): [('A', 'pos')]
            }
    
            A list is used for storing values because one Filosoft's analysis could
            be mapped to multiple syntactic analyzer's analyses;
    
            Lines that have ¤ in the beginning of the line will be skipped;
        '''
        rules = defaultdict(list)
        rules_pattern = re.compile('(¤?)[^@]*@(_(.)_\s*([^@]*)|####)@[^@]*@_(.)_\s*([^@]*)')
        in_f = codecs.open(fs_to_synt_rules_file, mode='r', encoding='utf-8')
        for line in in_f:
            m = rules_pattern.match(line)
            if m == None:
                raise Exception(' Unexpected format of the line: ', line)
            if m.group(1): #line starts with '¤'
                continue
            rules[(m.group(3), m.group(4))].append((m.group(5), m.group(6)))
            # siin tekib korduvaid reegleid, mille võiks siinsamas välja filtreerida
            # näiteks P, sg n -> P, sg nom
            # ja kasutuid reegleid Z, '' -> Z, Fst
            # võiks olla ka m.group(6).strip()
        in_f.close()
        for key, value in rules.items():
            # eelmise versiooniga ühildumise jaoks
            rules[key] = tuple(value[::-1])
        return rules


# ==================================================================================
# ==================================================================================
#   3)  Convert pronouns from Filosoft's mrf to syntactic analyzer's mrf
#       (former 'tpron.pl')
# ==================================================================================
# ==================================================================================

class PronounTypeRewriter():
    ''' Converts pronouns (analysis lines with '_P_') from Filosoft's mrf to 
        syntactic analyzer's mrf format;
        Uses the set of predefined pronoun conversion rules from _pronConversions;
        
        _pronConversions should be a list of lists, where each outer list stands 
        for a single conversion rule and inner list contains a pair of elements:
        first is the regexp pattern and the second is the replacement, used in
           re.sub( pattern, replacement, line )
        
        Returns the input mrf list, with the lines converted from one format
        to another;
    '''
    # ma, sa, ta ei lähe kunagi mängu, sest ma -> mina, sa -> sina, ta-> tema
    _pronConversions = ( ("emb\+.*",             ("det",)),
                         ("enda\+.*",            ("pos", "refl")),
                         ("enese\+.*",           ("pos", "refl")),
                         ("eikeegi.*",           ("indef",)),
                         ("eimiski.*",           ("indef",)),
                         ("emb-kumb.*",          ("det",)),
                         ("esimene.*",           ("dem",)),
                         ("iga\+.*",             ("det",)),
                         ("iga_sugune.*",        ("indef",)),
                         ("iga_.ks\+.*",         ("det",)),
                         ("ise\+.*",             ("pos", "det", "refl")),
                         ("ise_enese.*",         ("refl",)),
                         ("ise_sugune.*",        ("dem",)),
                         ("keegi.*",             ("indef",)),
                         ("kes.*",               ("inter rel",)),
                         ("kumb\+.*",            ("rel",)),
                         ("kumbki.*",            ("det",)),
                         ("kõik.*",              ("det",)),
                         ("k.ik.*",              ("det",)),
                         ("meie_sugune.*",       ("dem",)),
                         ("meie_taoline.*",      ("dem",)),
                         ("mihuke\+.*",          ("inter rel",)),
                         ("mihukene\+.*",        ("inter rel",)),
                         ("mille_taoline.*",     ("dem",)),
                         ("milli=?ne.*",         ("rel",)),
                         ("mina\+.*",            ("pers ps1",)),
                         (" ma\+.*",             ("pers ps1",)),
                         ("mina=?kene\+.*",      ("dem",)),
                         ("mina=?ke\+.*",        ("dem",)),
                         ("mingi\+.*",           ("indef",)),
                         ("mingi_sugune.*",      ("indef",)),
                         ("minu_sugune.*",       ("dem",)),
                         ("minu_taoline.*",      ("dem",)),
                         ("miski.*",             ("indef",)),
                         ("mis\+.*",             ("inter rel",)),
                         ("mis_sugune.*",        ("inter rel",)),
                         ("miski\+.*",           ("inter rel",)),
                         ("miski_sugune.*",      ("inter rel",)),
                         ("misu=?ke(ne)?\+.*",   ("dem",)),
                         ("mitme_sugune.*",      ("indef",)),
                         ("mitme_taoline.*",     ("indef",)),
                         ("mitmendik\+.*",       ("inter rel",)),
                         ("mitmes\+.*",          ("inter rel", "indef")),
                         ("mi=?tu.*",            ("indef",)),
                         ("miuke(ne)?\+.*",      ("inter rel",)),
                         ("muist\+.*",           ("indef",)),
                         ("muu.*",               ("indef",)),
                         ("m.lema.*",            ("det",)),
                         ("m.ne_sugune\+.*",     ("indef",)),
                         ("m.ni\+.*",            ("indef",)),
                         ("m.ningane\+.*",       ("indef",)),
                         ("m.ningas.*",          ("indef",)),
                         ("m.herdune\+.*",       ("indef", "rel")),
                         ("määntne\+.*",         ("dem",)),
                         ("na_sugune.*",         ("dem",)),
                         ("nende_sugune.*",      ("dem",)),
                         ("nende_taoline.*",     ("dem",)),
                         ("nihuke(ne)?\+.*",     ("dem",)),
                         ("nii_mi=?tu\+.*",      ("indef", "inter rel")),
                         ("nii_sugune.*",        ("dem",)),
                         ("niisama_sugune.*",    ("dem",)),
                         ("nii?su=?ke(ne)?\+.*", ("dem",)),
                         ("niuke(ne)?\+.*",      ("dem",)),
                         ("oma\+.*",             ("pos", "det", "refl")),
                         ("oma_enese\+.*",       ("pos",)),
                         ("oma_sugune\+.*",      ("dem",)),
                         ("oma_taoline\+.*",     ("dem",)),
                         ("palju.*",             ("indef",)),
                         ("sama\+.*",            ("dem",)),
                         ("sama_sugune\+.*",     ("dem",)),
                         ("sama_taoline\+.*",    ("dem",)),
                         ("samune\+.*",          ("dem",)),
                         ("see\+.*",             ("dem",)),
                         ("see_sama\+.*",        ("dem",)),
                         ("see_sam[au]ne\+.*",   ("dem",)),
                         ("see_sinane\+.*",      ("dem",)),
                         ("see_sugune\+.*",      ("dem",)),
                         ("selle_taoline\+.*",   ("dem",)),
                         ("selli=?ne\+.*",       ("dem",)),
                         ("setu\+.*",            ("indef",)),
                         ("setmes\+.*",          ("indef",)),
                         ("sihuke\+.*",          ("dem",)),
                         ("sina\+.*",            ("pers ps2",)),
                         (" sa\+.*",             ("pers ps2",)),
                         ("sinu_sugune\+.*",     ("dem",)),
                         ("sinu_taoline\+.*",    ("dem",)),
                         ("siuke(ne)?\+.*",      ("dem",)),
                         ("säherdune\+.*",       ("dem",)),
                         ("s.herdune\+.*",       ("dem",)),
                         ("säärane\+.*",         ("dem",)),
                         ("s..rane\+.*",         ("dem",)),
                         ("taoline\+.*",         ("dem",)),
                         ("teie_sugune\+.*",     ("dem",)),
                         ("teie_taoline\+.*",    ("dem",)),
                         ("teine\+.*",           ("dem",)),
                         ("teine_teise\+.*",     ("rec",)),
                         ("teist?_sugune\+.*",   ("dem",)),
                         ("tema\+.*",            ("pers ps3",)),
                         (" ta\+.*",             ("pers ps3",)),
                         ("temake(ne)?\+.*",     ("pers ps3",)),
                         ("tema_sugune\+.*",     ("dem",)),
                         ("tema_taoline\+.*",    ("dem",)),
                         ("too\+.*",             ("dem",)),
                         ("too_sama\+.*",        ("dem",)),
                         ("üks.*",               ("dem", "indef")),
                         (".ks.*",               ("dem", "indef")),
                         ("ükski.*",             ("dem", "indef")),
                         (".kski.*",             ("dem", "indef")),
                         ("üks_teise.*",         ("rec", "indef")),
                         (".ks_teise.*",         ("rec",))
    )
    
    def rewrite(self, record):
        result = []
        for rec in record:
            rec['pronoun_type'] = None
            if rec['partofspeech'] == 'P':  # only consider lines containing pronoun analyses
                root_ec = ''.join((rec['root'], '+', rec['ending'], rec['clitic']))
                for pattern, pron_type in self._pronConversions:
                    if re.search(pattern, root_ec):
                        # kas search või match? "enese" vs "iseenese"
                        rec['pronoun_type'] = pron_type
                        break
            result.append(rec)
        return result


# ==================================================================================
# ==================================================================================
#   4)  Remove duplicate analysis lines;
#       Remove adpositions (_K_) that do not have subcategorization information;
#       (former 'tcopyremover.pl')
# ==================================================================================
# ==================================================================================

class RemoveDuplicateAnalysesRewriter():
    ''' Removes duplicate analysis lines from mrf_lines. 
        
        Uses special logic for handling adposition analyses ('_K_ pre' && '_K_ post')
        that do not have subcategorization information:
         *) If a word has both adposition analyses, removes '_K_ pre';
         *) If a word has '_K_ post', removes it;
        Note that '_K_ pre' and '_K_ post' with subcategorization information will
        be kept.
        
        The parameter  allow_to_delete_all  specifies whether it is allowed to delete
        all analysis or not. If allow_to_delete_all == False, then one last analysis
        won't be deleted, regardless whether it should be deleted considering the 
        adposition-deletion rules;
        The original implementation corresponds to the settings allow_to_delete_all=True 
        (and this is also the default value of the parameter);
        
        Returns the input list where the removals have been applied;
    '''     
    def __init__(self, allow_to_delete_all=True):
        self.allow_to_delete_all = allow_to_delete_all

    def rewrite(self, record):
        seen_analyses  = []
        to_delete      = []
        Kpre_index     = -1
        Kpost_index    = -1
        for i, rec in enumerate(record):
            analysis = (rec['root'], rec['ending'], rec['clitic'], rec['partofspeech'], rec['form'])
            if analysis in seen_analyses:
                # Remember line that has been already seen as a duplicate
                to_delete.append(i)
            else:
                # Remember '_K_ pre' and '_K_ post' indices
                if analysis[3] == 'K':
                    if analysis[4] == 'pre':
                        Kpre_index  = i
                    elif analysis[4] == 'post':
                        Kpost_index = i
                # Remember that the line has already been seen
                seen_analyses.append(analysis)

        if Kpre_index != -1 and Kpost_index != -1:
            # If there was both _K_pre and _K_post, add _K_pre to removables;
            to_delete.append(Kpre_index)
        elif Kpost_index != -1:
            # If there was only _K_post, add _K_post to removables;
            to_delete.append(Kpost_index)
        # Delete found duplicates
        for j in sorted(to_delete, reverse=True):
            # If we must preserve at least one analysis, and
            # it has been found that all should be deleted, then 
            # keep the last one
            if not self.allow_to_delete_all and len(record) < 2:
                continue
            # Delete the analysis line
            del record[j]

        return record


# ==================================================================================
# ==================================================================================
#   5)  Add hashtag information to analyses
#       (former 'TTRELLID.AWK')
# ==================================================================================
# ==================================================================================


class LetterCaseRewriter():
    ''' Marks words with capital beginning with 'cap'.
    '''
    def rewrite(self, record):
        result = []
        for rec in record:
            # cap võib for alt välja tõsta, kui alati len(record)>0
            cap = _esc_double_quotes(rec['word_text'][0]).isupper()
            if cap:
                rec['letter_case'] = 'cap'
            else:
                rec['letter_case'] = None
            result.append(rec)
        return result


class FiniteFormRewriter():
    ''' Marks finite verbs with #FinV.
    '''
    # Information about verb finite forms
    #_morfFinV        = re.compile('//\s*(_V_).*\s+(ps.|neg|quot|impf imps|pres imps)\s')
    #_morfNotFinV     = re.compile('//\s*(_V_)\s+(aux neg)\s+//')
    _morfFinV        = re.compile('(ps[123]|neg|quot|impf imps|pres imps)')

    def rewrite(self, record):
        result = []
        for rec in record:
            rec['fin'] = None
            if rec['partofspeech'] == 'V':
                if self._morfFinV.search(rec['form']):
                    if rec['form'] != 'aux neg':
                        rec['fin'] = '<FinV>'
            result.append(rec)
        return result


class ParticRewriter():
    ''' Marks nud/tud/mine/nu/tu/v/tav/mata/ja forms.
    '''
    # Various information about word endings
    _mrfHashTagConversions = ( ("=[td]ud",   "<tud>"),
                               ("=nud",      "<nud>"),
                               ("=mine",     "<mine>"),
                               ("=nu$",      "<nu>"),
                               ("=[td]u$",   "<tu>"),
                               ("=v$",       "<v>"),
                               ("=[td]av",   "<tav>"),
                               ("=mata",     "<mata>"),
                               ("=ja",       "<ja>")
    )
    
    def rewrite(self, record):
        result = []
        for rec in record:
            rec['verb_extension_suffix'] = None
            for pattern, value in self._mrfHashTagConversions:
                if re.search(pattern, rec['root']):
                    rec['verb_extension_suffix'] = value
                    break
            result.append(rec)
        return result

def is_partic_suffix(suffix):
    return suffix in {'<tud>', '<nud>', '<v>', '<tav>', '<mata>'} 

# ==================================================================================
# ==================================================================================
#   6) Add subcategorization information to verbs and adpositions;
#       (former 'tagger08.c')
# ==================================================================================
# ==================================================================================



analysisLemmaPat = re.compile('^\s+([^+ ]+)\+')
analysisPat      = re.compile('//([^/]+)//')

class SubcatRewriter():
    ''' Adds subcategorization information (hashtags) to verbs and adpositions;
        
        Argument subcat_rules must be a dict containing subcategorization information,
        loaded via method load_subcat_info();

        Performs word lemma lookups in subcat_rules, and in case of a match, checks 
        word part-of-speech conditions. If the POS conditions match, adds subcategorization
        information either to a single analysis line, or to multiple analysis lines 
        (depending on the exact conditions in the rule);

        Returns the input list where verb/adposition analyses have been augmented 
        with available subcategorization information;
    '''
    def __init__(self, subcat_rules_file):
        self.v_rules, self.k_rules = self._load_subcat_info(subcat_rules_file)

    def rewrite(self, record):
        result = []
        for rec in record:
            match = False
            
            for subcat in self.v_rules[(rec['root'], rec['partofspeech'])]:
                match = True
                rec_copy = rec.copy()
                rec_copy['abileksikon'] = subcat
                result.append(rec_copy)
            if not match:
                for subcat in self.k_rules[(rec['root'], rec['partofspeech'], rec['form'] )]:
                    match = True
                    rec_copy = rec.copy()
                    rec_copy['abileksikon'] = subcat
                    result.append(rec_copy)
            
            if not match:
                rec['abileksikon'] = None
                result.append(rec)

        return result

    def _load_subcat_info(self,subcat_rules_file):
        ''' Loads subcategorization rules (for verbs and adpositions) from a text 
            file. 
            It is expected that the rules are given as pairs, where the first item is 
            the lemma (of verb/adposition), followed on the next line by the 
            subcategorization rule, in the following form: 
               on the left side of '>' is the condition (POS-tag requirement for the 
               lemma), 
             and 
               on the right side is the listing of subcategorization settings (hashtag 
               items, e.g. names of morphological cases of nominals);
            If there are multiple subcategorization rules to be associated with a
            single lemma, different rules are separated by '&'.
    
            Example, an excerpt from the rules file:
              läbi
              _V_ >#Part &_K_ post >#gen |#nom |#el &_K_ pre >#gen 
              läbista
              _V_ >#NGP-P 
              läbistu
              _V_ >#Intr 
    
            Returns a dict of root to a-list-of-subcatrules mappings.
        '''
        rules = defaultdict(list)
        nonSpacePattern = re.compile('^\S+$')
        posTagPattern   = re.compile('_._')
        in_f = codecs.open(subcat_rules_file, mode='r', encoding='utf-8')
        root = None
        subcatRules = None
        for line in in_f:
            # seda võib kirjutada lihtsamaks, kui võib eeldada, et faili formaat on range
            line = line.rstrip()
            if posTagPattern.search(line) and root:
                subcatRules = line
                parts = subcatRules.split('&')#[::-1]#76 tekst 
                for part in parts:
                    part = part.strip()
                    rules[root].append(part)
                root = None
                subcatRules = None
            elif nonSpacePattern.match(line):
                root = line
        in_f.close()
        #print( len(rules.keys()) )   # 4484
    
        v_rules = defaultdict(list)
        k_rules = defaultdict(list)
        for root, rulelist in rules.items():
            for rule in rulelist:
                pos, subcats = rule.split('>')
                for subcat in subcats.split('|'):
                    pos = pos.strip()
                    subcat = subcat.strip()
                    if pos == '_V_':
                        if all([subcat not in s for s in v_rules[(root, 'V')]]):
                        # ei tea, kas see if teeb mõistlikku asja, aga igatahes aitab ühilduda eelmise versiooniga
                            v_rules[(root, 'V')].append(subcat)
                    elif pos == '_K_ post':
                        if all([subcat not in s for s in k_rules[(root, 'K', 'post')]]):
                            k_rules[(root, 'K', 'post')].append(subcat)
                    elif pos == '_K_ pre':
                        if all([subcat not in s for s in k_rules[(root, 'K', 'pre')]]):
                            k_rules[(root, 'K', 'pre')].append(subcat)
        # [::-1] eelmise versiooniga ühildumiseks
        for k, v in v_rules.items():
            v_rules[k] = v[::-1]
        for k, v in k_rules.items():
            k_rules[k] = v[::-1]
        
        for key in v_rules:
            for i, subcat in enumerate(v_rules[key]):
                v_rules[key][i] = [s.strip(' #') for s in subcat.split()]
        for key in k_rules:
            for i, subcat in enumerate(k_rules[key]):
                k_rules[key][i] = [s.strip(' #') for s in subcat.split()]

        return v_rules, k_rules


# ==================================================================================
# ==================================================================================
#   8) Convert from syntax preprocessing format to cg3 input format;
#       (former 'tkms2cg3.pl')
# ==================================================================================
# ==================================================================================

def convert_to_cg3_input(text):
    ''' Converts given mrf lines from syntax preprocessing format to cg3 input
        format:
          *) surrounds words/tokens with "< and >"
          *) surrounds word lemmas with " in analysis;
          *) separates word endings from lemmas in analysis, and adds prefix 'L';
          *) removes '//' and '//' from analysis;
          *) converts hashtags to tags surrounded by < and >;
          ... and provides other various fix-ups;

        Returns the input list, where elements (tokens/analyses) have been converted
        into the new format;
    ''' 
    morph_lines = []
    word_index = -1
    for sentence in text.sentences:
        morph_lines.append('"<s>"')
        for word in sentence.words:
            word_index += 1
            morph_lines.append('"<'+_esc_double_quotes(word.text)+'>"')
            for morph_extended in text.morph_extended[word_index]:
                #if word.text=='.':
                #    print(morph_extended)
                new_form_list = []
                if morph_extended.pronoun_type:
                    new_form_list.extend(morph_extended.pronoun_type)
                if morph_extended.form:
                    new_form_list.append(morph_extended.form)
                if morph_extended.letter_case:
                    new_form_list.append(morph_extended.letter_case)
                if is_partic_suffix(morph_extended.verb_extension_suffix):
                    new_form_list.append('partic')
                if morph_extended.verb_extension_suffix:
                    new_form_list.append(morph_extended.verb_extension_suffix)
                if morph_extended.fin:
                    new_form_list.append(morph_extended.fin)
                if morph_extended.abileksikon:
                    subcat = morph_extended.abileksikon
                    subcat = ' '.join(['<'+s+'>' for s in subcat])
                    new_form_list.append(subcat)
                if morph_extended.punctuation_type:
                    # jama, et abileksikon06utf.lx sisaldab ka punktuation type
                #    if morph_extended.punctuation_type not in new_form_list:
                    new_form_list.append(morph_extended.punctuation_type)

                #if morph_extended.form_list != new_form_list:
                #    print('-----------------------------------')
                #    print(morph_extended.form_list)
                #    print(new_form_list)
                #    print(morph_extended.initial_form, morph_extended.fin, morph_extended.abileksikon, morph_extended.punctuation_type, morph_extended.pronoun_type, morph_extended.partic, morph_extended.letter_case)
                #morph_extended.form_list = [re.sub('#(\S+)','<\\1>', f) for f in morph_extended.form_list]
                new_form_list = [re.sub('#(\S+)','<\\1>', f) for f in new_form_list]

                if morph_extended.ending + morph_extended.clitic:
                    line_new = '    "'+morph_extended.root+'" L'+morph_extended.ending+morph_extended.clitic+' ' + ' '.join([morph_extended.partofspeech]+new_form_list+[' '])
                else:
                    if morph_extended.partofspeech == 'Z':
                        line_new = '    "'+morph_extended.root+'" '+' '.join([morph_extended.partofspeech]+new_form_list+[' '])
                    else:
                        line_new = '    "'+morph_extended.root+'+" '+' '.join([morph_extended.partofspeech]+new_form_list+[' '])

                if morph_extended.root == '':
                    line_new = '     //_Z_ //'  
                if morph_extended.root == '#':
                    line_new = '    "<" L0> Y nominal   '
                line_new = re.sub('digit  $','digit   ', line_new)
                line_new = re.sub('nominal  $','nominal   ', line_new)
                line_new = re.sub('prop  $','prop   ', line_new)
                line_new = re.sub('com  $','com   ', line_new)
                # FinV on siin arvatavasti ebakorrektne ja tekkis cap märgendi tõttu
                line_new = re.sub('"ei" L0 V aux neg cap  ','"ei" L0 V aux neg cap <FinV>  ', line_new)
                m = re.match('(\s+"tead\+a-tund".*\S)\s*$', line_new)
                if m:
                    line_new = m.group(1) + ' <NGP-P> <InfP>  '
                if text.morf_analysis[word_index][0].form == '?':
                    line_new = re.sub('pos  $','pos   ', line_new)
                #312 Paevakajaline_valiidne.xml_145.txt      Not OK. First mismatching line:
                #result:   '    "oota+me-vaata+me-jälgi" Lme V mod indic pres ps1 pl ps af <FinV>  '
                #expected: '    "oota+me-vaata+me-jälgi" Lme V mod indic pres ps1 pl ps af <FinV> <Part-P>  '
                #376 aja_ee_1996_48.xml_26.txt               ----------------------------------
                #result:        '    "öel=nu+d-kirjuta" Lnud V mod indic impf ps neg <FinV>  '
                #expected:      '    "öel=nu+d-kirjuta" Lnud V mod indic impf ps neg <FinV> <nu>  '
                #718 aja_EPL_1998_06_02.xml_14.txt           Not OK. First mismatching line:
                #result:   '    "vali+des-katseta" Ldes V mod ger  '
                #expected: '    "vali+des-katseta" Ldes V mod ger <NGP-P> <All>  '
                #973 aja_EPL_1998_06_18.xml_5.txt            ----------------------------------
                #result:        '    "viha=tu+d-armasta" Ltud V mod indic impf imps neg <FinV>  '
                #expected:      '    "viha=tu+d-armasta" Ltud V mod indic impf imps neg <FinV> <tu>  '

                if False:
                    print('----------------------------------')
                    print("ending+clitic: '", morph_extended.ending+morph_extended.clitic, "'", sep="")
                    print('form_list:', morph_extended.form_list)
                    print("morf_analysis[0].form:'",  word.morf_analysis[0].form, "'", sep='')
                    print("result:        '", line_new,                "'", sep="")
                morph_lines.append(line_new)
        morph_lines.append('"</s>"')

    return text, morph_lines


# ==================================================================================
# ==================================================================================
#   Syntax  preprocessing  pipeline
# ==================================================================================
# ==================================================================================

class SyntaxPreprocessing:
    ''' A preprocessing pipeline for VISL CG3 based syntactic analysis.

        Contains the following processing steps:
         1) convert_vm_json_to_mrf( )
            convert_Text_to_mrf( )
            * converts vabamorf's JSON or Estnltk's Text into Filosoft's old mrf 
              format;
         2) convert_mrf_to_syntax_mrf( )
            * converts Filosoft's old mrf format into syntactic analyzer's preprocessing 
              mrf format;
            * uses built-in rules for punctuation conversion and rules from the file 
              'tmorftrtabel.txt' for word analysis conversion;
            * this step performs a large part of the conversion, however, subsequent steps
              are required for adding specific details;
         3) convert_pronouns( )
            * adds specific information/categories related to pronouns; uses a list
              of built-in conversion rules;
         4) remove_duplicate_analyses( )
            * removes duplicate analyses;
            * removes redundant adposition analyses (specific logic for that);
         5) add_hashtag_info( ):
            * adds hashtags containing information about capitalization, 
                                                           finite verbs, 
                                                 nud/tud/mine/... forms;
         6) tag_subcat_info( ):
            * adds hashtags containing information about verb subcategorization;
            * adds hashtags containing information about adposition subcategorization;
         7) remove_duplicate_analyses( )
            * removes duplicate analyses;
            * removes redundant adposition analyses (specific logic for that);
         8) convert_to_cg3_input( )
            * converts from the syntax preprocessing format to cg3 input format;

    '''

    fs_to_synt_rules_file = FS_TO_SYNT_RULES_FILE
    subcat_rules_file     = SUBCAT_RULES_FILE
    
    fs_to_synt_rules = None
    subcat_rules     = None
    
    allow_to_remove_all = False
    
    def __init__( self, **kwargs):
        ''' Initializes VISL CG3 based syntax preprocessing pipeline. 
            
            Parameters
            -----------
            fs_to_synt_rules : str
                Name of the file containing rules for mapping from Filosoft's old mrf 
                format to syntactic analyzer's preprocessing mrf format;
                (~~'tmorftrtabel.txt')
            
            subcat_rules : str
                Name of the file containing rules for adding subcategorization information
                to verbs/adpositions;
                (~~'abileksikon06utf.lx')
            
            allow_to_remove_all : bool
                Specifies whether the method remove_duplicate_analyses() is allowed to 
                remove all analysis of a word token (due to the specific _K_-removal rules).
                The original implementation allowed this, but we are now restricting it
                in order to avoid words without any analyses;
                Default: False
            
        '''
        for argName, argVal in kwargs.items():
            if argName in ['fs_to_synt_rules_file', 'fs_to_synt_rules', 'fs_to_synt']:
                self.fs_to_synt_rules_file = argVal
            elif argName in ['subcat_rules_file', 'subcat_rules', 'subcat']:
                self.subcat_rules_file = argVal
            elif argName in ['allow_to_remove_all','allow_to_remove'] and argVal in [True,False]:
                self.allow_to_remove_all = argVal
            else:
                raise Exception('(!) Unsupported argument given: '+argName)
        #  fs_to_synt_rules_file:
        if not self.fs_to_synt_rules_file or not os.path.exists(self.fs_to_synt_rules_file):
            raise Exception('(!) Unable to find *fs_to_synt_rules_file* from location:', \
                            self.fs_to_synt_rules_file)
        #  subcat_rules_file:
        if not self.subcat_rules_file or not os.path.exists(self.subcat_rules_file):
            raise Exception('(!) Unable to find *subcat_rules* from location:', \
                            self.subcat_rules_file)
        self.super_tagger = MorphExtendedTagger(self.fs_to_synt_rules_file, self.allow_to_remove_all, self.subcat_rules_file)


    def process_Text(self, text, **kwargs):
        ''' Executes the preprocessing pipeline on estnltk's Text object.

            Returns a list: lines of analyses in the VISL CG3 input format;
            Executes the preprocessing pipeline on mrf_lines.

            The input should be an analysis of the text in Filosoft's old mrf format;

            Returns the input list, where elements (tokens/analyses) have been converted
            into the new format;
        '''
        self.super_tagger.tag(text)

        print('o ', end='', flush=True)
        text, morph_lines = convert_to_cg3_input(text)
        return text, morph_lines