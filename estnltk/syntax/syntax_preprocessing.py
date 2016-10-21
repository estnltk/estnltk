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
                     attributes=['root', 'ending_clitic', 'pos', 'form']
                     )
    text.add_layer(dep)

    dep = DependantLayer(name='syntax_pp_2',
                     text_object=text,
                     frozen=False,
                     parent=text.words,
                     ambiguous=True,
                     attributes=['root', 'ending_clitic', 'pos', 'form', 'morph_line']
                     )
    text.add_layer(dep)

    dep = DependantLayer(name='syntax_pp_3',
                     text_object=text,
                     frozen=False,
                     parent=text.words,
                     ambiguous=True,
                     attributes=['morph_line']
                     )
    text.add_layer(dep)

    for sentence in text.sentences:
        for word in sentence.words:
            for root, ending, clitic, pos, form in zip(word.root, word.ending, word.clitic, word.partofspeech, word.form):
                root = _esc_double_quotes( root )
                #   NB! ending="0" erineb ending=""-st:
                #     1) eestlane (ending="0");
                #     2) Rio (ending="") de (ending="") Jaineros;
                m = word.mark('syntax_pp_1')
                m.root = root
                m.ending_clitic = ending + clitic
                m.pos = pos
                m.form = form
    return text


# ==================================================================================
# ==================================================================================
#   2)  Convert from Filosoft's mrf to syntactic analyzer's mrf
#       (former 'rtolkija.pl')
# ==================================================================================
# ==================================================================================

def load_fs_mrf_to_syntax_mrf_translation_rules( rulesFile ):
    ''' Loads rules that can be used to convert from Filosoft's mrf format to 
        syntactic analyzer's format. Returns a dict containing rules.

        Expects that each line in the input file contains a single rule, and that 
        different parts of the rule separated by @ symbols, e.g.
        
            1@_S_ ?@Substantiiv apellatiiv@_S_ com @Noun common@Nc@NCSX@kesk-
            32@_H_ ?@Substantiiv prooprium@_S_ prop @Noun proper@Np@NPCSX@Kesk-
            313@_A_@Adjektiiv positiiv@_A_ pos@Adjective positive@A-p@ASX@salkus
        
        Only 2nd element and 4th element are extracted from each line; 2nd element
        will be the key of the dict entry, and 4th element will be added to the 
        value of the dict entry (the value is a list of strings);

        A list is used for storing values because one Filosoft's analysis could
        be mapped to multiple syntactic analyzer's analyses;
        
        Lines that have ¤ in the beginning of the line will be skipped;
      
    '''
    rules = defaultdict(list)
    in_f = codecs.open(rulesFile, mode='r', encoding='utf-8')
    for line in in_f:
        line = line.rstrip()
        if line.startswith('¤'):
            continue
        parts = line.split('@')
        if len(parts) < 4:
            raise Exception(' Unexpected format of the line: ', line)
        rules[parts[1]].append( parts[3] )
    in_f.close()
    return rules


def load_fs_mrf_to_syntax_mrf_translation_rules_new( fs_to_synt_rules_file ):
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
    return rules

# ================================================
    
_punctOrAbbrev = re.compile('//\s*_[ZY]_')


_punctConversions_new = [ ["…([\+0]*) //\s*_[ZY]_ //",   "Ell"], \
                      ["…",      "Ell"], \
                      ["\.\.\.", "Ell"], \
                      ["\.\.",   "Els"], \
                      ["\.",     "Fst"], \
                      [",",      "Com"], \
                      [":",      "Col"], \
                      [";",      "Scl"], \
                      ["(\?+)",  "Int"], \
                      ["(\!+)",  "Exc"], \
                      ["(---?)", "Dsd"], \
                      ["(-)",    "Dsh"], \
                      ["\(",     "Opr"], \
                      ["\)",     "Cpr"], \
                      ['\\\\"',  "Quo"], \
                      ["«",      "Oqu"], \
                      ["»",      "Cqu"], \
                      ["“",      "Oqu"], \
                      ["”",      "Cqu"], \
                      ["<",      "Grt"], \
                      [">",      "Sml"], \
                      ["\[",     "Osq"], \
                      ["\]",     "Csq"], \
                      ["/",      "Sla"], \
                      ["\+",     "crd"], \
]# double quotes are escaped by \

_punctConversions = [ ["…([\+0]*) //\s*_[ZY]_ //",   "…\\1 //_Z_ Ell //"], \
                      ["\.\.\.([\+0]*) //\s*_Z_ //", "...\\1 //_Z_ Ell //"], \
                      ["\.\.([\+0]*) //\s*_Z_ //",   "..\\1 //_Z_ Els //"], \
                      ["\.([\+0]*) //\s*_Z_ //",     ".\\1 //_Z_ Fst //"], \
                      [",([\+0]*) //\s*_Z_ //",      ",\\1 //_Z_ Com //"], \
                      [":([\+0]*) //\s*_Z_ //",      ":\\1 //_Z_ Col //"], \
                      [";([\+0]*) //\s*_Z_ //",      ";\\1 //_Z_ Scl //"], \
                      ["(\?+)([\+0]*) //\s*_Z_ //",  "\\1\\2 //_Z_ Int //"], \
                      ["(\!+)([\+0]*) //\s*_Z_ //",  "\\1\\2 //_Z_ Exc //"], \
                      ["(---?)([\+0]*) //\s*_Z_ //", "\\1\\2 //_Z_ Dsd //"], \
                      ["(-)([\+0]*) //\s*_Z_ //",    "\\1\\2 //_Z_ Dsh //"], \
                      ["\(([\+0]*) //\s*_Z_ //",     "(\\1 //_Z_ Opr //"], \
                      ["\)([\+0]*) //\s*_Z_ //",     ")\\1 //_Z_ Cpr //"], \
                      ["\"([\+0]*) //\s*_Z_ //",     "\"\\1 //_Z_ Quo //"], \
                      ["«([\+0]*) //\s*_Z_ //",      "«\\1 //_Z_ Oqu //"], \
                      ["»([\+0]*) //\s*_Z_ //",      "»\\1 //_Z_ Cqu //"], \
                      ["“([\+0]*) //\s*_Z_ //",      "“\\1 //_Z_ Oqu //"], \
                      ["”([\+0]*) //\s*_Z_ //",      "”\\1 //_Z_ Cqu //"], \
                      ["<([\+0]*) //\s*_Z_ //",      "<\\1 //_Z_ Grt //"], \
                      [">([\+0]*) //\s*_Z_ //",      ">\\1 //_Z_ Sml //"], \
                      ["\[([\+0]*) //\s*_Z_ //",     "[\\1 //_Z_ Osq //"], \
                      ["\]([\+0]*) //\s*_Z_ //",     "]\\1 //_Z_ Csq //"], \
                      ["/([\+0]*) //\s*_Z_ //",      "/\\1 //_Z_ Sla //"], \
                      ["\+([\+0]*) //\s*_Z_ //",     "+\\1 //_Z_ crd //"], \
]



def _convert_punctuation( line ):
    ''' Converts given analysis line if it describes punctuation; Uses the set 
        of predefined punctuation conversion rules from _punctConversions;
        
        _punctConversions should be a list of lists, where each outer list stands 
        for a single conversion rule and inner list contains a pair of elements:
        first is the regexp pattern and the second is the replacement, used in
           re.sub( pattern, replacement, line )
        
        Returns the converted line (same as input, if no conversion was 
        performed);
    ''' 
    for [pattern, replacement] in _punctConversions:
        lastline = line
        line = re.sub(pattern, replacement, line)
        if lastline != line:
            break
    return line 


def _convert_punctuation_new(syntax_pp):
    ''' Converts given analysis line if it describes punctuation; Uses the set 
        of predefined punctuation conversion rules from _punctConversions;
        
        _punctConversions should be a list of lists, where each outer list stands 
        for a single conversion rule and inner list contains a pair of elements:
        first is the regexp pattern and the second is the replacement, used in
           re.sub( pattern, replacement, line )
        
        Returns the converted line (same as input, if no conversion was 
        performed);
    ''' 
    for pattern, replacement in _punctConversions_new:
        if re.match(pattern, syntax_pp.root):
            syntax_pp.form = replacement
            break


def convert_mrf_to_syntax_mrf_new(text, fs_to_synt_rules):
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
            root = syntax_pp.root
            pos = syntax_pp.pos
            form = syntax_pp.form
            if pos == 'Z':
                root_ec = root
            else:
                root_ec = ''.join((root,'+',syntax_pp.ending_clitic))
            # 1) Convert punctuation
            if pos == 'Z':
                _convert_punctuation_new(syntax_pp)
                m = word.mark('syntax_pp_2')
                m.morph_line = '    '+root_ec+' //_'+syntax_pp.pos+'_ '+_esc_que_mark(syntax_pp.form)+' //'
                m.root = syntax_pp.root
                m.ending_clitic = syntax_pp.ending_clitic
                m.pos = syntax_pp.pos
                m.form = syntax_pp.form
            else:
                if pos == 'Y':
                    # järgmine rida on kasutu, siin tuleb _form muuta, kui _root=='…'
                    line = _convert_punctuation_new(syntax_pp)

            # 2) Convert morphological analyses that have a form specified
                if form == '':
                    morphKeys = [(pos, form)]
                else:
                    morphKeys = [(pos, _form.strip()) for _form in form.split(',')]#kas form.split(',')==[form] sageli või alati?
                for morphKey in morphKeys[::-1]: # [::-1] is for equivalence with old version
                    new_poses = []
                    new_forms = []
                    for pos, form in fs_to_synt_rules[morphKey]:
                        new_poses.append(pos)
                        new_forms.append(form)
                    for pos, form in zip(new_poses[::-1], new_forms[::-1]):
                        m = word.mark('syntax_pp_2')
                        if form == '':
                            m.morph_line = '    '+root_ec+' //_'+pos+'_ //'
                        else:
                            m.morph_line = '    '+root_ec+' //_'+pos+'_ '+_esc_que_mark(form)+' //'
                        m.root = root
                        m.ending_clitic = syntax_pp.ending_clitic
                        m.pos = pos
                        m.form = _esc_que_mark(form)
                if len(new_poses) == 0:
                    print(pos, form)
    return text


# ==================================================================================
# ==================================================================================
#   3)  Convert pronouns from Filosoft's mrf to syntactic analyzer's mrf
#       (former 'tpron.pl')
# ==================================================================================
# ==================================================================================

# ma, sa, ta ei lähe kunagi mängu, sest ma -> mina, sa -> sina, ta-> tema
_pronConversions_new = [ ["emb\+.*",             "det"], \
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

_pronConversions = [ ["(emb\+.* //\s*_P_)\s+([sp])",             "\\1 det \\2"], \
                     ["(enda\+.* //\s*_P_)\s+([sp])",            "\\1 pos refl \\2"], \
                     ["(enese\+.* //\s*_P_)\s+([sp])",           "\\1 pos refl \\2"], \
                     ["(eikeegi.* //\s*_P_)\s+([sp])",           "\\1 indef \\2"], \
                     ["(eimiski.* //\s*_P_)\s+([sp])",           "\\1 indef \\2"], \
                     ["(emb-kumb.* //\s*_P_)\s+([sp])",          "\\1 det \\2"], \
                     ["(esimene.* //\s*_P_)\s+([sp])",           "\\1 dem \\2"], \
                     ["(iga\+.* //\s*_P_)\s+([sp])",             "\\1 det \\2"], \
                     ["(iga_sugune.* //\s*_P_)\s+([sp])",        "\\1 indef \\2"], \
                     ["(iga_.ks\+.* //\s*_P_)\s+([sp])",         "\\1 det \\2"], \
                     ["(ise\+.* //\s*_P_)\s+([sp])",             "\\1 pos det refl \\2"], \
                     ["(ise_enese.* //\s*_P_)\s+([sp])",         "\\1 refl \\2"], \
                     ["(ise_sugune.* //\s*_P_)\s+([sp])",        "\\1 dem \\2"], \
                     ["(keegi.* //\s*_P_)\s+([sp])",             "\\1 indef \\2"], \
                     ["(kes.* //\s*_P_)\s+([sp])",               "\\1 inter rel \\2"], \
                     ["(kumb\+.* //\s*_P_)\s+([sp])",            "\\1 rel \\2"], \
                     ["(kumbki.* //\s*_P_)\s+([sp])",            "\\1 det \\2"], \
                     ["(kõik.* //\s*_P_)\s+([sp])",              "\\1 det \\2"], \
                     ["(k.ik.* //\s*_P_)\s+([sp])",              "\\1 det \\2"], \
                     ["(meie_sugune.* //\s*_P_)\s+([sp])",       "\\1 dem \\2"], \
                     ["(meie_taoline.* //\s*_P_)\s+([sp])",      "\\1 dem \\2"], \
                     ["(mihuke\+.* //\s*_P_)\s+([sp])",          "\\1 inter rel \\2"], \
                     ["(mihukene\+.* //\s*_P_)\s+([sp])",        "\\1 inter rel \\2"], \
                     ["(mille_taoline.* //\s*_P_)\s+([sp])",     "\\1 dem \\2"], \
                     ["(milli=?ne.* //\s*_P_)\s+([sp])",         "\\1 rel \\2"], \
                     ["(mina\+.* //\s*_P_)\s+([sp])",            "\\1 pers ps1 \\2"], \
                     ["( ma\+.* //\s*_P_)\s+([sp])",             "\\1 pers ps1 \\2"], \
                     ["(mina=?kene\+.* //\s*_P_)\s+([sp])",      "\\1 dem \\2"], \
                     ["(mina=?ke\+.* //\s*_P_)\s+([sp])",        "\\1 dem \\2"], \
                     ["(mingi\+.* //\s*_P_)\s+([sp])",           "\\1 indef \\2"], \
                     ["(mingi_sugune.* //\s*_P_)\s+([sp])",      "\\1 indef \\2"], \
                     ["(minu_sugune.* //\s*_P_)\s+([sp])",       "\\1 dem \\2"], \
                     ["(minu_taoline.* //\s*_P_)\s+([sp])",      "\\1 dem \\2"], \
                     ["(miski.* //\s*_P_)\s+([sp])",             "\\1 indef \\2"], \
                     ["(mis\+.* //\s*_P_)\s+([sp])",             "\\1 inter rel \\2"], \
                     ["(mis_sugune.* //\s*_P_)\s+([sp])",        "\\1 inter rel \\2"], \
                     ["(miski\+.* //\s*_P_)\s+([sp])",           "\\1 inter rel \\2"], \
                     ["(miski_sugune.* //\s*_P_)\s+([sp])",      "\\1 inter rel \\2"], \
                     ["(misu=?ke(ne)?\+.* //\s*_P_)\s+([sp])",   "\\1 dem \\3"], \
                     ["(mitme_sugune.* //\s*_P_)\s+([sp])",      "\\1 indef \\2"], \
                     ["(mitme_taoline.* //\s*_P_)\s+([sp])",     "\\1 indef \\2"], \
                     ["(mitmendik\+.* //\s*_P_)\s+([sp])",       "\\1 inter rel \\2"], \
                     ["(mitmes\+.* //\s*_P_)\s+([sp])",          "\\1 inter rel indef \\2"], \
                     ["(mi=?tu.* //\s*_P_)\s+([sp])",            "\\1 indef \\2"], \
                     ["(miuke(ne)?\+.* //\s*_P_)\s+([sp])",      "\\1 inter rel \\3"], \
                     ["(muist\+.* //\s*_P_)\s+([sp])",           "\\1 indef \\2"], \
                     ["(muu.* //\s*_P_)\s+([sp])",               "\\1 indef \\2"], \
                     ["(m.lema.* //\s*_P_)\s+([sp])",            "\\1 det \\2"], \
                     ["(m.ne_sugune\+.* //\s*_P_)\s+([sp])",     "\\1 indef \\2"], \
                     ["(m.ni\+.* //\s*_P_)\s+([sp])",            "\\1 indef \\2"], \
                     ["(m.ningane\+.* //\s*_P_)\s+([sp])",       "\\1 indef \\2"], \
                     ["(m.ningas.* //\s*_P_)\s+([sp])",          "\\1 indef \\2"], \
                     ["(m.herdune\+.* //\s*_P_)\s+([sp])",       "\\1 indef rel \\2"], \
                     ["(määntne\+.* //\s*_P_)\s+([sp])",         "\\1 dem \\2"], \
                     ["(na_sugune.* //\s*_P_)\s+([sp])",         "\\1 dem \\2"], \
                     ["(nende_sugune.* //\s*_P_)\s+([sp])",      "\\1 dem \\2"], \
                     ["(nende_taoline.* //\s*_P_)\s+([sp])",     "\\1 dem \\2"], \
                     ["(nihuke(ne)?\+.* //\s*_P_)\s+([sp])",     "\\1 dem \\3"], \
                     ["(nii_mi=?tu\+.* //\s*_P_)\s+([sp])",      "\\1 indef inter rel \\2"], \
                     ["(nii_sugune.* //\s*_P_)\s+([sp])",        "\\1 dem \\2"], \
                     ["(niisama_sugune.* //\s*_P_)\s+([sp])",    "\\1 dem \\2"], \
                     ["(nii?su=?ke(ne)?\+.* //\s*_P_)\s+([sp])", "\\1 dem \\3"], \
                     ["(niuke(ne)?\+.* //\s*_P_)\s+([sp])",      "\\1 dem \\3"], \
                     ["(oma\+.* //\s*_P_)\s+([sp])",             "\\1 pos det refl \\2"], \
                     ["(oma_enese\+.* //\s*_P_)\s+([sp])",       "\\1 pos \\2"], \
                     ["(oma_sugune\+.* //\s*_P_)\s+([sp])",      "\\1 dem \\2"], \
                     ["(oma_taoline\+.* //\s*_P_)\s+([sp])",     "\\1 dem \\2"], \
                     ["(palju.* //\s*_P_)\s+([sp])",             "\\1 indef \\2"], \
                     ["(sama\+.* //\s*_P_)\s+([sp])",            "\\1 dem \\2"], \
                     ["(sama_sugune\+.* //\s*_P_)\s+([sp])",     "\\1 dem \\2"], \
                     ["(sama_taoline\+.* //\s*_P_)\s+([sp])",    "\\1 dem \\2"], \
                     ["(samune\+.* //\s*_P_)\s+([sp])",          "\\1 dem \\2"], \
                     ["(see\+.* //\s*_P_)\s+([sp])",             "\\1 dem \\2"], \
                     ["(see_sama\+.* //\s*_P_)\s+([sp])",        "\\1 dem \\2"], \
                     ["(see_sam[au]ne\+.* //\s*_P_)\s+([sp])",   "\\1 dem \\2"], \
                     ["(see_sinane\+.* //\s*_P_)\s+([sp])",      "\\1 dem \\2"], \
                     ["(see_sugune\+.* //\s*_P_)\s+([sp])",      "\\1 dem \\2"], \
                     ["(selle_taoline\+.* //\s*_P_)\s+([sp])",   "\\1 dem \\2"], \
                     ["(selli=?ne\+.* //\s*_P_)\s+([sp])",       "\\1 dem \\2"], \
                     ["(setu\+.* //\s*_P_)\s+([sp])",            "\\1 indef \\2"], \
                     ["(setmes\+.* //\s*_P_)\s+([sp])",          "\\1 indef \\2"], \
                     ["(sihuke\+.* //\s*_P_)\s+([sp])",          "\\1 dem \\2"], \
                     ["(sina\+.* //\s*_P_)\s+([sp])",            "\\1 pers ps2 \\2"], \
                     ["( sa\+.* //\s*_P_)\s+([sp])",             "\\1 pers ps2 \\2"], \
                     ["(sinu_sugune\+.* //\s*_P_)\s+([sp])",     "\\1 dem \\2"], \
                     ["(sinu_taoline\+.* //\s*_P_)\s+([sp])",    "\\1 dem \\2"], \
                     ["(siuke(ne)?\+.* //\s*_P_)\s+([sp])",      "\\1 dem \\3"], \
                     ["(säherdune\+.* //\s*_P_)\s+([sp])",       "\\1 dem \\2"], \
                     ["(s.herdune\+.* //\s*_P_)\s+([sp])",       "\\1 dem \\2"], \
                     ["(säärane\+.* //\s*_P_)\s+([sp])",         "\\1 dem \\2"], \
                     ["(s..rane\+.* //\s*_P_)\s+([sp])",         "\\1 dem \\2"], \
                     ["(taoline\+.* //\s*_P_)\s+([sp])",         "\\1 dem \\2"], \
                     ["(teie_sugune\+.* //\s*_P_)\s+([sp])",     "\\1 dem \\2"], \
                     ["(teie_taoline\+.* //\s*_P_)\s+([sp])",    "\\1 dem \\2"], \
                     ["(teine\+.* //\s*_P_)\s+([sp])",           "\\1 dem \\2"], \
                     ["(teine_teise\+.* //\s*_P_)\s+([sp])",     "\\1 rec \\2"], \
                     ["(teist?_sugune\+.* //\s*_P_)\s+([sp])",   "\\1 dem \\2"], \
                     ["(tema\+.* //\s*_P_)\s+([sp])",            "\\1 pers ps3 \\2"], \
                     ["( ta\+.* //\s*_P_)\s+([sp])",             "\\1 pers ps3 \\2"], \
                     ["(temake(ne)?\+.* //\s*_P_)\s+([sp])",     "\\1 pers ps3 \\3"], \
                     ["(tema_sugune\+.* //\s*_P_)\s+([sp])",     "\\1 dem \\2"], \
                     ["(tema_taoline\+.* //\s*_P_)\s+([sp])",    "\\1 dem \\2"], \
                     ["(too\+.* //\s*_P_)\s+([sp])",             "\\1 dem \\2"], \
                     ["(too_sama\+.* //\s*_P_)\s+([sp])",        "\\1 dem \\2"], \
                     ["(üks.* //\s*_P_)\s+([sp])",               "\\1 dem indef \\2"], \
                     ["(.ks.* //\s*_P_)\s+([sp])",               "\\1 dem indef \\2"], \
                     ["(ükski.* //\s*_P_)\s+([sp])",             "\\1 dem indef \\2"], \
                     ["(.kski.* //\s*_P_)\s+([sp])",             "\\1 dem indef \\2"], \
                     ["(üks_teise.* //\s*_P_)\s+([sp])",         "\\1 rec indef \\2"], \
                     ["(.ks_teise.* //\s*_P_)\s+([sp])",         "\\1 rec \\2"], \

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
        for morph in word.syntax_pp_2:
            line = morph.morph_line
            if morph.pos == 'P':  # only consider lines containing pronoun analyses
                for pattern, replacement in _pronConversions:
                    lastline = line
                    line = re.sub(pattern, replacement, line)
                    if lastline != line:
                        morph.morph_line = line
                        break    
    return text

def convert_pronouns_new(text):
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
            root_ec = ''.join((syntax_pp.root,'+',syntax_pp.ending_clitic))
            morph = '_'+syntax_pp.pos+'_ '+_esc_que_mark(syntax_pp.form)
            if syntax_pp.pos == 'P':  # only consider lines containing pronoun analyses
                for pattern, replacement in _pronConversions_new:
                    if re.match(pattern, root_ec):
                        morph = re.sub("(\s*_P_)\s+([sp])", "\\1 " + replacement + " \\2", morph)
                        syntax_pp.morph_line = ''.join(['    ',root_ec,' //', morph,' //'])
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

        for i, morph in enumerate(word.syntax_pp_2):
            line = morph.morph_line
            if line in seen_analyses:
                # Remember line that has been already seen as a duplicate
                to_delete.append( i )
            else:
                # Remember '_K pre' and '_K_ post' indices
                if re.search('/_K_\s+pre\s+//', line):
                    Kpre_index  = i
                elif re.search('/_K_\s+post\s+//', line):
                    Kpost_index = i
                # Remember that the line has already been seen
                seen_analyses.append(line)

        if Kpre_index != -1 and Kpost_index != -1:
            # If there was both _K_pre and _K_post, add _K_pre to removables;
            to_delete.append( Kpre_index )
        elif Kpost_index != -1:
            # If there was only _K_post, add _K_post to removables;
            to_delete.append( Kpost_index )
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
_morfFinV    = re.compile('//\s*(_V_).*\s+(ps.|neg|quot|impf imps|pres imps)\s')
_morfNotFinV = re.compile('//\s*(_V_)\s+(aux neg)\s+//')

# Various information about word endings
_mrfHashTagConversions = [ ["(=[td]ud.+//.+)(\s+//)",   "\\1 partic #tud //"], \
                           ["(=nud.+//.+)(\s+//)",      "\\1 partic #nud //"], \
                           ["(=mine.+//.+)(\s+//)",     "\\1 #mine //"], \
                           ["(=nu[+].+//.+)(\s+//)",    "\\1 #nu //"], \
                           ["(=[td]u[+].+//.+)(\s+//)", "\\1 #tu //"], \
                           ["(=v[+].+//.+)(\s+//)",     "\\1 partic #v //"], \
                           ["(=[td]av.+//.+)(\s+//)",   "\\1 partic #tav //"], \
                           ["(=mata.+//.+)(\s+//)",     "\\1 partic #mata //"], \
                           ["(=ja.+//.+)(\s+//)",       "\\1 #ja //"], \
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
        for morph in word.syntax_pp_2:
            line = morph.morph_line
            if cap:
                line = re.sub('(//.+\S)\s+//', '\\1 #cap //', line)
            if _morfFinV.search( line ) and not _morfNotFinV.search( line ):
                line = re.sub('(//.+\S)\s+//', '\\1 #FinV //', line)
            for [pattern, replacement] in _mrfHashTagConversions:
                line = re.sub(pattern, replacement, line)
            morph.morph_line = line
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

        Returns a dict of lemma to a-list-of-subcatrules mappings.
    '''
    rules = defaultdict(list)
    nonSpacePattern = re.compile('^\S+$')
    posTagPattern   = re.compile('_._')
    in_f = codecs.open(subcat_lex_file, mode='r', encoding='utf-8')
    lemma = ''
    subcatRules = ''
    for line in in_f:
        line = line.rstrip()
        if nonSpacePattern.match(line) and not posTagPattern.search(line):
            lemma = line
        elif posTagPattern.search(line):
            subcatRules = line
        if len(lemma) > 0 and len(subcatRules) > 0:
            parts = subcatRules.split('&')
            for part in parts:
                part = part.strip()
                rules[lemma].append( part )
            lemma = ''
            subcatRules = ''
    in_f.close()
    #print( len(rules.keys()) )   # 4484
    return rules


def _check_condition(cond_string, target_string):
    ''' Checks whether cond_string is at the beginning of target_string, or
        whether cond_string is within target_string, preceded by whitespace.

        Returns boolean indicating the result of the check-up;
    '''
    return ((target_string.startswith(cond_string)) or (' '+cond_string in target_string))


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
        for morph in word.syntax_pp_2:
            line = morph.morph_line
            lemma_match = analysisLemmaPat.match(line)
            match = False
            if lemma_match:
                lemma = lemma_match.group(1)
                # Find whether there is subcategorization info associated 
                # with the lemma
                if lemma in subcat_rules:
                    analysis_match = analysisPat.search(line)
                    if not analysis_match:
                        raise Exception(' Could not find analysis from the line:',line)
                    analysis = analysis_match.group(1)
                    for rule in subcat_rules[lemma]:
                        condition, addition = rule.split('>')
                        # Check the condition string; If there are multiple conditions, 
                        # all must be satisfied for the rule to fire
                        condition  = condition.strip()
                        conditions = condition.split()
                        satisfied1 = [ _check_condition(c, analysis) for c in conditions ]
                        if all( satisfied1 ):
                            #
                            # There can be multiple additions:
                            #   1) additions without '|' must be added to a single analysis line;
                            #   2) additions separated by '|' must be placed on separate analysis 
                            #      lines;
                            #
                            additions = addition.split('|')
                            # Add new line or lines
                            all_new_lines = []
                            for a in additions:
                                items_to_add = a.split()
                                line_new = line
                                for item in items_to_add:
                                    if not _check_condition(item, analysis):
                                        line_new = re.sub('(//.+\S)\s+//', '\\1 '+item+' //', line_new)
                                all_new_lines.append(line_new)
                            for morph_line in all_new_lines[::-1]:
                                match = True
                                m = word.mark('syntax_pp_3')
                                m.morph_line = morph_line
                            # No need to search forward
                            break
            if not match:
                word.mark('syntax_pp_3').morph_line = line
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
            for line in word.syntax_pp_3.morph_line:
                line = re.sub('#cap #cap','cap', line) # kas on vaja?
                line = re.sub('#cap','cap', line)
                line = re.sub('\*\*CLB','CLB', line) # kas on vaja?
                line = re.sub('#Correct!','<Correct!>', line) # kas on vaja?
                line = re.sub('####','', line) # kas on vaja?
                line = re.sub('#(\S+)','<\\1>', line)
                line = re.sub('\$([,.;!?:<]+)','\\1', line) # kas on vaja?
                line = re.sub('_Y_\s+\? _Z_','_Z_', line) # kas on vaja?
                line = re.sub('_Y_\s+\?\s+_Z_','_Z_', line) # kas on vaja?
                line = re.sub('_Y_\s+_Z_','_Z_', line) # kas on vaja?
                line = re.sub('_Z_\s+\?','_Z_', line) # kas on vaja?
                #  2. convert analysis line \w word ending
                line = re.sub('^\s+(\S+)(.*)\+(\S+)\s*//_(\S)_ (.*)//(.*)$', \
                              '    "\\1\\2" L\\3 \\4 \\5 \\6', line)
                #  3. convert analysis line \wo word ending
                line = re.sub('^\s+(\S+)(.*)\s+//_(\S)_ (.*)//(.*)$', \
                             '    "\\1\\2" \\3 \\4 \\5', line)
                morph_lines.append(line)
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


def convert_to_cg3_input_new(text):
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

    rules = (('#cap #cap','cap'),
             ('#cap','cap'),
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

    apply_regex(text.syntax_pp_3, 'morph_line', rules)
    morph_lines = []
    for sentence in text.sentences:
        morph_lines.append('"<s>"')
        for word in sentence.words:
            morph_lines.append('"<'+_esc_double_quotes(word.text)+'>"')
            for line in word.syntax_pp_3.morph_line:
                morph_lines.append(line)
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
        if not self.fs_to_synt_rules_file or not os.path.exists( self.fs_to_synt_rules_file ):
            raise Exception('(!) Unable to find *fs_to_synt_rules_file* from location:', \
                            self.fs_to_synt_rules_file)
        else:
            self.fs_to_synt_rules = \
                load_fs_mrf_to_syntax_mrf_translation_rules( self.fs_to_synt_rules_file )
            self.fs_to_synt_rules_new = \
                load_fs_mrf_to_syntax_mrf_translation_rules_new( self.fs_to_synt_rules_file )
        #  subcat_rules_file:
        if not self.subcat_rules_file or not os.path.exists( self.subcat_rules_file ):
            raise Exception('(!) Unable to find *subcat_rules* from location:', \
                            self.subcat_rules_file)
        else:
            self.subcat_rules = load_subcat_info( self.subcat_rules_file )


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
#        text = convert_mrf_to_syntax_mrf(text, self.fs_to_synt_rules )
        text = convert_mrf_to_syntax_mrf_new(text, self.fs_to_synt_rules_new )
        text = convert_pronouns_new(text)
        text = remove_duplicate_analyses(text, allow_to_delete_all=self.allow_to_remove_all )
        text = add_hashtag_info(text)
        text = tag_subcat_info(text, self.subcat_rules )
        text = remove_duplicate_analyses(text, allow_to_delete_all=self.allow_to_remove_all )
        text, morph_lines = convert_to_cg3_input_new(text)
        return text, morph_lines