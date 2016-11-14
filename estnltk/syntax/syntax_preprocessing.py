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

from estnltk.text import DependantLayer
from estnltk.legacy.core import PACKAGE_PATH
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


# ==================================================================================
# ==================================================================================
#   1)  Convert from estnltk Text to Filosoft's mrf
#       (former 'json2mrf.pl')
# ==================================================================================
# ==================================================================================

def convert_Text_to_mrf(text):
    ''' Converts from Text object into pre-syntactic mrf format, given as a list of 
        lines, as in the output of etmrf.
        *) If the input Text has already been morphologically analysed, uses the existing
            analysis;
        *) If the input has not been analysed, performs the analysis with required settings:
            word quessing is turned on, proper-name analyses are turned off;
    '''

    dep = DependantLayer(name='syntax_pp_1',
                     text_object=text,
                     frozen=False,
                     parent=text.words,
                     ambiguous=True,
                     attributes=['root', 'ending', 'clitic', 'pos', 'form_list']
                     )
    text.add_layer(dep)

    dep = DependantLayer(name='syntax_pp_2',
                     text_object=text,
                     frozen=False,
                     parent=text.words,
                     ambiguous=True,
                     attributes=['root', 'ending', 'clitic', 'pos', 'punctuation_type', 'pronoun_type', 'partic', 'letter_case' , 'form_list', 'initial_form', 'fin']
                     )
    text.add_layer(dep)

    dep =  DependantLayer(name='syntax_pp_3',
                     text_object=text,
                     frozen=False,
                     parent=text.words,
                     ambiguous=True,
                     attributes=['root', 'ending', 'clitic', 'pos', 'punctuation_type', 'pronoun_type', 'partic', 'letter_case', 'initial_form', 'fin', 'abileksikon']
                     )
    text.add_layer(dep)

    for word in text.words:
        for analysis in word.morf_analysis:
            m = word.mark('syntax_pp_1')
            #   NB! ending="0" erineb ending=""-st:
            #     1) eestlane (ending="0");
            #     2) Rio (ending="") de (ending="") Jaineros;
            m.root = _esc_double_quotes(analysis.root)
            m.ending = analysis.ending
            m.clitic = analysis.clitic
            m.pos = analysis.partofspeech
            m.form_list = []
            for _form in analysis.form.split(',')[::-1]:
                #kas form.split(',')==[form] sageli või alati?
                # [::-1] on eelmise versiooniga ühildumiseks
                _form = _form.strip()
                if _form:
                    m.form_list.append(_form)
    return text


# ==================================================================================
# ==================================================================================
#   2)  Convert from Filosoft's mrf to syntactic analyzer's mrf
#       (former 'rtolkija.pl')
# ==================================================================================
# ==================================================================================

def load_fs_mrf_to_syntax_mrf_translation_rules(fs_to_synt_rules_file):
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


# ================================================
    
_punctOrAbbrev = re.compile('//\s*_[ZY]_')

_punctConversions = [ ["…([\+0]*) //\s*_[ZY]_ //",   "Ell"], \
                      ["…$",      "Ell"], \
                      ["\.\.\.$", "Ell"], \
                      ["\.\.$",   "Els"], \
                      ["\.$",     "Fst"], \
                      [",$",      "Com"], \
                      [":$",      "Col"], \
                      [";$",      "Scl"], \
                      ["(\?+)$",  "Int"], \
                      ["(\!+)$",  "Exc"], \
                      ["(---?)$", "Dsd"], \
                      ["(-)$",    "Dsh"], \
                      ["\($",     "Opr"], \
                      ["\)$",     "Cpr"], \
                      ['\\\\"$',  "Quo"], \
                      ["«$",      "Oqu"], \
                      ["»$",      "Cqu"], \
                      ["“$",      "Oqu"], \
                      ["”$",      "Cqu"], \
                      ["<$",      "Grt"], \
                      [">$",      "Sml"], \
                      ["\[$",     "Osq"], \
                      ["\]$",     "Csq"], \
                      ["/$",      "Sla"], \
                      ["\+$",     "crd"], \
]# double quotes are escaped by \


def _convert_punctuation(syntax_pp):
    ''' Converts given analysis line if it describes punctuation; Uses the set 
        of predefined punctuation conversion rules from _punctConversions;
        
        _punctConversions should be a list of lists, where each outer list stands 
        for a single conversion rule and inner list contains a pair of elements:
        first is the regexp pattern and the second is the replacement, used in
           re.sub( pattern, replacement, line )
        
        Returns the converted line (same as input, if no conversion was 
        performed);
    '''
    for pattern, replacement in _punctConversions:
        if re.search(pattern, syntax_pp.root):
            # kas match või search?     "//", ".-"
            # või hoopis pattern==syntax_pp.root?
            # praegu on search, sest see klapib eelmise versiooniga
            syntax_pp.form_list = [replacement]
            break

def _get_punctuation_type(syntax_pp):
    ''' Converts given analysis line if it describes punctuation; Uses the set 
        of predefined punctuation conversion rules from _punctConversions;
        
        _punctConversions should be a list of lists, where each outer list stands 
        for a single conversion rule and inner list contains a pair of elements:
        first is the regexp pattern and the second is the replacement, used in
           re.sub( pattern, replacement, line )
        
        Returns the converted line (same as input, if no conversion was 
        performed);
    ''' 
    for pattern, punct_type in _punctConversions:
        if re.search(pattern, syntax_pp.root):
            # kas match või search?     "//", ".-"
            # või hoopis pattern==syntax_pp.root?
            # praegu on search, sest see klapib eelmise versiooniga
            return punct_type


def convert_mrf_to_syntax_mrf(text, fs_to_synt_rules):
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
    for word in text.words:
        for syntax_pp in word.syntax_pp_1:
            pos = syntax_pp.pos
            form_list = syntax_pp.form_list[:]#kas siin on koopiat vaja?
            # 1) Convert punctuation
            if pos == 'Z':
                _convert_punctuation(syntax_pp)
                m = word.mark('syntax_pp_2')
                m.root = syntax_pp.root
                m.ending = syntax_pp.ending
                m.clitic = syntax_pp.clitic
                m.pos = syntax_pp.pos
                m.punctuation_type = _get_punctuation_type(syntax_pp)
                m.pronoun_type = None
                m.form_list = syntax_pp.form_list[:]
                m.initial_form = syntax_pp.form_list[:]
            else:
                if pos == 'Y':
                    # järgmine rida on kasutu, siin tuleb _form muuta, kui _root=='…'
                    line = _convert_punctuation(syntax_pp)

            # 2) Convert morphological analyses that have a form specified
                if not form_list:
                    morphKeys = [(pos, '')]
                else:
                    morphKeys = [(pos, _form) for _form in form_list]#kas form.split(',')==[form] sageli või alati?
                for morphKey in morphKeys: # tsüklit pole vaja, kui alati len(form_list)==1
                    for pos, form in fs_to_synt_rules[morphKey]:
                        m = word.mark('syntax_pp_2')
                        if form == '':
                            m.form_list = []
                        else:
                            m.form_list = [_esc_que_mark(form).strip()]
                        m.root = syntax_pp.root
                        m.ending = syntax_pp.ending
                        m.clitic = syntax_pp.clitic
                        m.pos = pos
                        m.punctuation_type = None
                        m.pronoun_type = None
                        m.initial_form = m.form_list[:]
    return text


# ==================================================================================
# ==================================================================================
#   3)  Convert pronouns from Filosoft's mrf to syntactic analyzer's mrf
#       (former 'tpron.pl')
# ==================================================================================
# ==================================================================================

# ma, sa, ta ei lähe kunagi mängu, sest ma -> mina, sa -> sina, ta-> tema
_pronConversions = [ ["emb\+.*",             "det"], \
                     ["enda\+.*",            "pos refl"], \
                     ["enese\+.*",           "pos refl"], \
                     ["eikeegi.*",           "indef"], \
                     ["eimiski.*",           "indef"], \
                     ["emb-kumb.*",          "det"], \
                     ["esimene.*",           "dem"], \
                     ["iga\+.*",             "det"], \
                     ["iga_sugune.*",        "indef"], \
                     ["iga_.ks\+.*",         "det"], \
                     ["ise\+.*",             "pos det refl"], \
                     ["ise_enese.*",         "refl"], \
                     ["ise_sugune.*",        "dem"], \
                     ["keegi.*",             "indef"], \
                     ["kes.*",               "inter rel"], \
                     ["kumb\+.*",            "rel"], \
                     ["kumbki.*",            "det"], \
                     ["kõik.*",              "det"], \
                     ["k.ik.*",              "det"], \
                     ["meie_sugune.*",       "dem"], \
                     ["meie_taoline.*",      "dem"], \
                     ["mihuke\+.*",          "inter rel"], \
                     ["mihukene\+.*",        "inter rel"], \
                     ["mille_taoline.*",     "dem"], \
                     ["milli=?ne.*",         "rel"], \
                     ["mina\+.*",            "pers ps1"], \
                     [" ma\+.*",             "pers ps1"], \
                     ["mina=?kene\+.*",      "dem"], \
                     ["mina=?ke\+.*",        "dem"], \
                     ["mingi\+.*",           "indef"], \
                     ["mingi_sugune.*",      "indef"], \
                     ["minu_sugune.*",       "dem"], \
                     ["minu_taoline.*",      "dem"], \
                     ["miski.*",             "indef"], \
                     ["mis\+.*",             "inter rel"], \
                     ["mis_sugune.*",        "inter rel"], \
                     ["miski\+.*",           "inter rel"], \
                     ["miski_sugune.*",      "inter rel"], \
                     ["misu=?ke(ne)?\+.*",   "dem"], \
                     ["mitme_sugune.*",      "indef"], \
                     ["mitme_taoline.*",     "indef"], \
                     ["mitmendik\+.*",       "inter rel"], \
                     ["mitmes\+.*",          "inter rel indef"], \
                     ["mi=?tu.*",            "indef"], \
                     ["miuke(ne)?\+.*",      "inter rel"], \
                     ["muist\+.*",           "indef"], \
                     ["muu.*",               "indef"], \
                     ["m.lema.*",            "det"], \
                     ["m.ne_sugune\+.*",     "indef"], \
                     ["m.ni\+.*",            "indef"], \
                     ["m.ningane\+.*",       "indef"], \
                     ["m.ningas.*",          "indef"], \
                     ["m.herdune\+.*",       "indef rel"], \
                     ["määntne\+.*",         "dem"], \
                     ["na_sugune.*",         "dem"], \
                     ["nende_sugune.*",      "dem"], \
                     ["nende_taoline.*",     "dem"], \
                     ["nihuke(ne)?\+.*",     "dem"], \
                     ["nii_mi=?tu\+.*",      "indef inter rel"], \
                     ["nii_sugune.*",        "dem"], \
                     ["niisama_sugune.*",    "dem"], \
                     ["nii?su=?ke(ne)?\+.*", "dem"], \
                     ["niuke(ne)?\+.*",      "dem"], \
                     ["oma\+.*",             "pos det refl"], \
                     ["oma_enese\+.*",       "pos"], \
                     ["oma_sugune\+.*",      "dem"], \
                     ["oma_taoline\+.*",     "dem"], \
                     ["palju.*",             "indef"], \
                     ["sama\+.*",            "dem"], \
                     ["sama_sugune\+.*",     "dem"], \
                     ["sama_taoline\+.*",    "dem"], \
                     ["samune\+.*",          "dem"], \
                     ["see\+.*",             "dem"], \
                     ["see_sama\+.*",        "dem"], \
                     ["see_sam[au]ne\+.*",   "dem"], \
                     ["see_sinane\+.*",      "dem"], \
                     ["see_sugune\+.*",      "dem"], \
                     ["selle_taoline\+.*",   "dem"], \
                     ["selli=?ne\+.*",       "dem"], \
                     ["setu\+.*",            "indef"], \
                     ["setmes\+.*",          "indef"], \
                     ["sihuke\+.*",          "dem"], \
                     ["sina\+.*",            "pers ps2"], \
                     [" sa\+.*",             "pers ps2"], \
                     ["sinu_sugune\+.*",     "dem"], \
                     ["sinu_taoline\+.*",    "dem"], \
                     ["siuke(ne)?\+.*",      "dem"], \
                     ["säherdune\+.*",       "dem"], \
                     ["s.herdune\+.*",       "dem"], \
                     ["säärane\+.*",         "dem"], \
                     ["s..rane\+.*",         "dem"], \
                     ["taoline\+.*",         "dem"], \
                     ["teie_sugune\+.*",     "dem"], \
                     ["teie_taoline\+.*",    "dem"], \
                     ["teine\+.*",           "dem"], \
                     ["teine_teise\+.*",     "rec"], \
                     ["teist?_sugune\+.*",   "dem"], \
                     ["tema\+.*",            "pers ps3"], \
                     [" ta\+.*",             "pers ps3"], \
                     ["temake(ne)?\+.*",     "pers ps3"], \
                     ["tema_sugune\+.*",     "dem"], \
                     ["tema_taoline\+.*",    "dem"], \
                     ["too\+.*",             "dem"], \
                     ["too_sama\+.*",        "dem"], \
                     ["üks.*",               "dem indef"], \
                     [".ks.*",               "dem indef"], \
                     ["ükski.*",             "dem indef"], \
                     [".kski.*",             "dem indef"], \
                     ["üks_teise.*",         "rec indef"], \
                     [".ks_teise.*",         "rec"], \
]


def convert_pronouns(text):
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
    for word in text.words:
        for syntax_pp in word.syntax_pp_2:
            if syntax_pp.pos == 'P':  # only consider lines containing pronoun analyses
                root_ec = ''.join((syntax_pp.root, '+', syntax_pp.ending, syntax_pp.clitic))
                for pattern, pron_type in _pronConversions:
                    if re.search(pattern, root_ec):
                        # kas search või match? "enese" vs "iseenese"
                        syntax_pp.pronoun_type = pron_type
                        break    
    return text



# ==================================================================================
# ==================================================================================
#   4)  Remove duplicate analysis lines;
#       Remove adpositions (_K_) that do not have subcategorization information;
#       (former 'tcopyremover.pl')
# ==================================================================================
# ==================================================================================

def remove_duplicate_analyses(text, allow_to_delete_all=True):
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
    for word in text.words:
        seen_analyses  = []
        to_delete      = []
        Kpre_index     = -1
        Kpost_index    = -1
        for i, syntax_pp in enumerate(word.syntax_pp_2):
            #analysis = (syntax_pp.root, syntax_pp.ending, syntax_pp.clitic, syntax_pp.pos, syntax_pp.form_list)
            analysis = (syntax_pp.root, syntax_pp.ending, syntax_pp.clitic, syntax_pp.pos, syntax_pp.initial_form)
            if analysis in seen_analyses:
                # Remember line that has been already seen as a duplicate
                to_delete.append(i)
            else:
                # Remember '_K_ pre' and '_K_ post' indices
                if analysis[3] == 'K':
                    if analysis[4][0] == 'pre':
                        Kpre_index  = i
                    elif analysis[4][0] == 'post':
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
            if not allow_to_delete_all and len(word.syntax_pp_2) < 2:
                continue
            # Delete the analysis line
            word.syntax_pp_2.items.pop(j)
    return text


# ==================================================================================
# ==================================================================================
#   5)  Add hashtag information to analyses
#       (former 'TTRELLID.AWK')
# ==================================================================================
# ==================================================================================

# Information about verb finite forms
_morfFinV        = re.compile('//\s*(_V_).*\s+(ps.|neg|quot|impf imps|pres imps)\s')
_morfNotFinV     = re.compile('//\s*(_V_)\s+(aux neg)\s+//')
#_morfFinV_new    = re.compile('(ps.|neg|quot|impf imps|pres imps)')
#_morfNotFinV_new = re.compile('^(aux neg)$')

# Various information about word endings
_mrfHashTagConversions = [ ["=[td]ud",   "partic <tud>"], \
                           ["=nud",      "partic <nud>"], \
                           ["=mine",     "<mine>"], \
                           ["=nu$",      "<nu>"], \
                           ["=[td]u$",   "<tu>"], \
                           ["=v$",       "partic <v>"], \
                           ["=[td]av",   "partic <tav>"], \
                           ["=mata",     "partic <mata>"], \
                           ["=ja",       "<ja>"], \
]


def add_hashtag_info(text):
    ''' Augments analysis lines with various hashtag information:
          *) marks words with capital beginning with #cap;
          *) marks finite verbs with #FinV;
          *) marks nud/tud/mine/nu/tu/v/tav/mata/ja forms;
        Hashtags are added at the end of the analysis content (just before the 
        last '//');

        Returns the input list where the augmentation has been applied;
    ''' 
    for word in text.words:
        cap = _esc_double_quotes(word.text)[0].isupper()
        for syntax_pp in word.syntax_pp_2:            
            syntax_pp.letter_case = None
            if cap:
                syntax_pp.letter_case = 'cap'

            syntax_pp.fin = None
            if syntax_pp.pos == 'V':
                line = '//_V_ ' + ' '.join(syntax_pp.form_list)+' //'
                if _morfFinV.search( line ) and not _morfNotFinV.search( line ):
                    syntax_pp.form_list.append('<FinV>')
                    syntax_pp.fin = '<FinV>'

            syntax_pp.partic = None
            for pattern, value in _mrfHashTagConversions:
                if re.search(pattern, syntax_pp.root):
                    syntax_pp.form_list.append(value)
                    syntax_pp.partic = value
                    break
    return text


# ==================================================================================
# ==================================================================================
#   6) Add subcategorization information to verbs and adpositions;
#       (former 'tagger08.c')
# ==================================================================================
# ==================================================================================

def load_subcat_info(subcat_lex_file):
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
    in_f = codecs.open(subcat_lex_file, mode='r', encoding='utf-8')
    root = None
    subcatRules = None
    for line in in_f:
        # seda võib kirjutada lihtsamaks, kui võib eeldada, et faili vormaat on range
        line = line.rstrip()
        if posTagPattern.search(line) and root:
            subcatRules = line
            parts = subcatRules.split('&')
            for part in parts:
                part = part.strip()
                rules[root].append(part)
            root = None
            subcatRules = None
        elif nonSpacePattern.match(line):
            root = line
    in_f.close()
    #print( len(rules.keys()) )   # 4484
    return rules


analysisLemmaPat = re.compile('^\s+([^+ ]+)\+')
analysisPat      = re.compile('//([^/]+)//')


def tag_subcat_info(text, subcat_rules):
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
    for word in text.words:
        for syntax_pp in word.syntax_pp_2:
            match = False

            root = syntax_pp.root
            # Find whether there is subcategorization info associated 
            # with the root
            if root in subcat_rules:
                #analysis = ['_'+syntax_pp.pos+'_'] + syntax_pp.form_list
                #analysis = {'_'+syntax_pp.pos+'_', syntax_pp.punctuation_type, syntax_pp.pronoun_type, syntax_pp.partic, syntax_pp.letter_case, *syntax_pp.initial_form, syntax_pp.fin}
                # kas eelneva asemel piisab järgnevast?
                analysis = {'_'+syntax_pp.pos+'_'}
                analysis.update(syntax_pp.initial_form)

                for rule in subcat_rules[root]:
                    condition, addition = rule.split('>')
                    # Check the condition string; If there are multiple conditions, 
                    # all must be satisfied for the rule to fire
                    condition  = condition.strip()
                    conditions = condition.split()
                    satisfied = [c in analysis for c in conditions]
                    if all(satisfied):
                        #
                        # There can be multiple additions:
                        #   1) additions without '|' must be added to a single analysis line;
                        #   2) additions separated by '|' must be placed on separate analysis 
                        #      lines;
                        #
                        additions = addition.split('|')
                        # Add new line or lines
                        for a in additions[::-1]:
                            m = word.mark('syntax_pp_3')
                            m.root = syntax_pp.root
                            m.ending = syntax_pp.ending
                            m.clitic = syntax_pp.clitic
                            m.pos = syntax_pp.pos
                            m.punctuation_type = syntax_pp.punctuation_type
                            m.pronoun_type = syntax_pp.pronoun_type
                            m.partic = syntax_pp.partic
                            m.letter_case = syntax_pp.letter_case
                            items_to_add = a.split()

                            form_list_new = syntax_pp.form_list[:]
                            abileksikon = []
                            for item in items_to_add:
                                if not item in form_list_new:
                                    form_list_new.append(item)
                                    abileksikon.append(item)
                            #m.form_list = form_list_new
                            m.initial_form = syntax_pp.initial_form
                            m.fin = syntax_pp.fin
                            m.abileksikon = abileksikon
                                                        
                            match = True
                        # No need to search forward
                        break
            if not match:
                m = word.mark('syntax_pp_3')
                m.root = syntax_pp.root
                m.ending = syntax_pp.ending
                m.clitic = syntax_pp.clitic
                m.pos = syntax_pp.pos
                m.punctuation_type = syntax_pp.punctuation_type
                m.pronoun_type = syntax_pp.pronoun_type
                m.partic = syntax_pp.partic
                m.letter_case = syntax_pp.letter_case
                #m.form_list = syntax_pp.form_list
                m.initial_form = syntax_pp.initial_form
                m.fin = syntax_pp.fin
                m.abileksikon = None
    return text


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
    for sentence in text.sentences:
        morph_lines.append('"<s>"')
        for word in sentence.words:
            morph_lines.append('"<'+_esc_double_quotes(word.text)+'>"')
            for syntax_pp in word.syntax_pp_3:
                new_form_list = []
                if syntax_pp.pronoun_type:
                    new_form_list.append(syntax_pp.pronoun_type)
                if syntax_pp.initial_form:
                    new_form_list.extend(syntax_pp.initial_form)
                #if syntax_pp.punctuation_type:
                    # kasutu
                #    if syntax_pp.punctuation_type not in new_form_list:
                #        new_form_list.append(syntax_pp.punctuation_type)
                if syntax_pp.letter_case:
                    new_form_list.append(syntax_pp.letter_case)
                if syntax_pp.partic:
                    new_form_list.append(syntax_pp.partic)
                if syntax_pp.fin:
                    new_form_list.append(syntax_pp.fin)
                if syntax_pp.abileksikon:
                    new_form_list.extend(syntax_pp.abileksikon)

                #if syntax_pp.form_list != new_form_list:
                #    print('-----------------------------------')
                #    print(syntax_pp.form_list)
                #    print(new_form_list)
                #    print(syntax_pp.initial_form, syntax_pp.fin, syntax_pp.abileksikon, syntax_pp.punctuation_type, syntax_pp.pronoun_type, syntax_pp.partic, syntax_pp.letter_case)
                #syntax_pp.form_list = [re.sub('#(\S+)','<\\1>', f) for f in syntax_pp.form_list]
                new_form_list = [re.sub('#(\S+)','<\\1>', f) for f in new_form_list]

                if syntax_pp.ending + syntax_pp.clitic:
                    line_new = '    "'+syntax_pp.root+'" L'+syntax_pp.ending+syntax_pp.clitic+' ' + ' '.join([syntax_pp.pos]+new_form_list+[' '])
                else:
                    if syntax_pp.pos == 'Z':
                        line_new = '    "'+syntax_pp.root+'" '+' '.join([syntax_pp.pos]+new_form_list+[' '])
                    else:
                        line_new = '    "'+syntax_pp.root+'+" '+' '.join([syntax_pp.pos]+new_form_list+[' '])

                if syntax_pp.root == '':
                    line_new = '     //_Z_ //'  
                if syntax_pp.root == '#':
                    line_new = '    "<" L0> Y nominal   '
                line_new = re.sub('digit  $','digit   ', line_new)
                line_new = re.sub('nominal  $','nominal   ', line_new)
                line_new = re.sub('prop  $','prop   ', line_new)
                line_new = re.sub('com  $','com   ', line_new)
                m = re.match('(\s+"tead\+a-tund".*\S)\s*$', line_new)
                if m:
                    line_new = m.group(1) + ' <NGP-P> <InfP>  '
                if word.morf_analysis[0].form == '?':
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
                    print("ending+clitic: '", syntax_pp.ending+syntax_pp.clitic, "'", sep="")
                    print('form_list:', syntax_pp.form_list)
                    print("morf_analysis[0].form:'",  word.morf_analysis[0].form, "'", sep='')
                    print("result:        '", line_new,                "'", sep="")
                morph_lines.append(line_new)
        morph_lines.append('"</s>"')

    return text, morph_lines


def apply_regex(layer, attribute, rules):
    ''' Applies regex to layer attribute.
    '''
    for word_data in layer:
        for layer in word_data:
            line = getattr(layer, attribute)
            for rule in rules:
                line = re.sub(*rule, line)
            setattr(layer, attribute, line)

    rules = (('#cap #cap','cap'),
             #('#cap','cap'),
             ('\*\*CLB','CLB'),
             ('#Correct!','<Correct!>'),
             ('####',''),
             ('#(\S+)','<\\1>'),
             ('\$([,.;!?:<]+)','\\1'),
             ('_Y_\s+\? _Z_','_Z_'),
             ('_Y_\s+\?\s+_Z_','_Z_'),
             ('_Y_\s+_Z_','_Z_'),
             ('_Z_\s+\?','_Z_'),
             ('^\s+(\S+)(.*)\+(\S+)\s*//_(\S)_ (.*)//(.*)$', '    "\\1\\2" L\\3 \\4 \\5 \\6'),
             ('^\s+(\S+)(.*)\s+//_(\S)_ (.*)//(.*)$', '    "\\1\\2" \\3 \\4 \\5'))


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
        if not self.fs_to_synt_rules_file or not os.path.exists( self.fs_to_synt_rules_file ):
            raise Exception('(!) Unable to find *fs_to_synt_rules_file* from location:', \
                            self.fs_to_synt_rules_file)
        else:
            self.fs_to_synt_rules = \
                load_fs_mrf_to_syntax_mrf_translation_rules( self.fs_to_synt_rules_file )
        #  subcat_rules_file:
        if not self.subcat_rules_file or not os.path.exists( self.subcat_rules_file ):
            raise Exception('(!) Unable to find *subcat_rules* from location:', \
                            self.subcat_rules_file)
        else:
            self.subcat_rules = load_subcat_info(self.subcat_rules_file)


    def process_Text( self, text, **kwargs ):
        ''' Executes the preprocessing pipeline on estnltk's Text object.

            Returns a list: lines of analyses in the VISL CG3 input format;
        ''' 
        text = convert_Text_to_mrf( text )
        return self.process_mrf_lines(text, **kwargs )


    def process_mrf_lines(self, text, **kwargs):
        ''' Executes the preprocessing pipeline on mrf_lines.

            The input should be an analysis of the text in Filosoft's old mrf format;

            Returns the input list, where elements (tokens/analyses) have been converted
            into the new format;
        '''
        print('c', end='', flush=True)
        text = convert_mrf_to_syntax_mrf(text, self.fs_to_synt_rules)
        print('p', end='', flush=True)
        text = convert_pronouns(text)
        print('d', end='', flush=True)
        text = remove_duplicate_analyses(text, allow_to_delete_all=self.allow_to_remove_all)
        print('h', end='', flush=True)
        text = add_hashtag_info(text)
        print('s', end='', flush=True)
        text = tag_subcat_info(text, self.subcat_rules )
        #print('d', end='', flush=True)
        #text = remove_duplicate_analyses(text, allow_to_delete_all=self.allow_to_remove_all) # kas omab efekti?
        print('c ', end='', flush=True)
        text, morph_lines = convert_to_cg3_input(text)
        return text, morph_lines