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

from estnltk.names import *
from estnltk.core import PACKAGE_PATH

import re, json
import os, os.path
import codecs


SYNTAX_PATH      = os.path.join(PACKAGE_PATH, 'syntax', 'files')
FS_TO_SYNT_RULES_FILE = os.path.join(SYNTAX_PATH,  'tmorftrtabel.txt')
SUBCAT_RULES_FILE     = os.path.join(SYNTAX_PATH,  'abileksikon06utf.lx')

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
#   1)  Convert from vabamorf JSON/estnltk Text to Filosoft's mrf
#       (former 'json2mrf.pl')
# ==================================================================================
# ==================================================================================

def convert_vm_json_to_mrf( vabamorf_json ):
    ''' Converts from vabamorf's JSON output, given as dict, into pre-syntactic mrf
        format, given as a list of lines, as in the output of etmrf. 
        The aimed format looks something like this:
        <s>
        Kolmandaks
            kolmandaks+0 //_D_  //
            kolmas+ks //_O_ sg tr //
        kihutas
            kihuta+s //_V_ s //
        end
            end+0 //_Y_ ? //
            ise+0 //_P_ sg p //
        soomlane
            soomlane+0 //_S_ sg n //
        </s>
    '''
    if not isinstance( vabamorf_json, dict ):
       raise Exception(' Expected dict as an input argument! ')
    json_sentences = []
    # 1) flatten paragraphs
    if 'paragraphs' in vabamorf_json:
       for pr in vabamorf_json['paragraphs']:
           if 'sentences' in pr:
              for sent in pr['sentences']:
                 json_sentences.append( sent )
    # 2) flatten sentences
    elif 'sentences' in vabamorf_json:
       for sent in vabamorf_json['sentences']:
           json_sentences.append( sent )
    # 3) Iterate over sentences and perform conversion
    results = []
    for sentJson in json_sentences:
        results.append('<s>')
        for wordJson in sentJson['words']:
            if wordJson['text'] == '<s>' or wordJson['text'] == '</s>':
               continue
            wordStr = wordJson['text']
            # Escape double quotation marks
            wordStr = _esc_double_quotes( wordStr )
            results.append( wordStr )
            for analysisJson in wordJson['analysis']:
               root   = analysisJson['root']
               root   = _esc_double_quotes( root )
               #   NB! ending="0" erineb ending=""-st:
               #     1) eestlane (ending="0");
               #     2) Rio (ending="") de (ending="") Jaineros;
               ending = analysisJson[ENDING]
               pos    = analysisJson['partofspeech']
               clitic = analysisJson['clitic']
               form   = analysisJson['form']
               if pos == 'Z':
                  results.append( ''.join(['    ',root,' //_Z_ //']) )
               else:
                  results.append( ''.join(['    ',root,'+',ending,clitic,' //', '_',pos,'_ ',form,' //']) )
            if 'analysis' not in wordJson:
               results.append( '    '+'####' )
        results.append('</s>')
    return results


def convert_Text_to_mrf( text ):
    ''' Converts from Text object into pre-syntactic mrf format, given as a list of 
        lines, as in the output of etmrf.
        *) If the input Text has already been morphologically analysed, uses the existing
            analysis;
        *) If the input has not been analysed, performs the analysis with required settings:
            word quessing is turned on, proper-name analyses are turned off;
    '''
    from estnltk.text import Text
    if not isinstance( text, Text ):
       raise Exception(' Expected estnltk\'s Text as an input argument! ')
    if not text.is_tagged( ANALYSIS ):
       # If morphological analysis has not been performed yet, set the right arguments and 
       # perform the analysis 
       kwargs = text.get_kwargs()
       kwargs['vabamorf']     = True
       kwargs['guess']        = True
       kwargs['propername']   = False
       kwargs['disambiguate'] = False
       text.__kwargs = kwargs
       text = text.tag_analysis()
    # Iterate over sentences and perform conversion
    results = []
    for sentence in text.divide( layer=WORDS, by=SENTENCES ):
       results.append('<s>')
       for i in range(len(sentence)):
           wordJson = sentence[i]
           wordStr  = wordJson[TEXT]
           # Escape double quotation marks
           wordStr = _esc_double_quotes( wordStr )
           results.append( wordStr )
           for analysisJson in wordJson[ANALYSIS]:
               root   = analysisJson[ROOT]
               root   = _esc_double_quotes( root )
               #   NB! ending="0" erineb ending=""-st:
               #     1) eestlane (ending="0");
               #     2) Rio (ending="") de (ending="") Jaineros;
               ending = analysisJson[ENDING]
               pos    = analysisJson[POSTAG]
               clitic = analysisJson[CLITIC]
               form   = analysisJson[FORM]
               if pos == 'Z':
                  results.append( ''.join(['    ',root,' //_Z_ //']) )
               else:
                  results.append( ''.join(['    ',root,'+',ending,clitic,' //', '_',pos,'_ ',form,' //']) )
           if ANALYSIS not in wordJson:
               results.append( '    '+'####' )
       results.append('</s>')
    return results


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
    rules = {}
    in_f = codecs.open(rulesFile, mode='r', encoding='utf-8')
    for line in in_f:
        line = line.rstrip()
        if line.startswith('¤'):
           continue
        parts = line.split('@')
        if len(parts) < 4:
           raise Exception(' Unexpected format of the line: ', line)
        if parts[1] not in rules:
           rules[parts[1]] = []
        rules[parts[1]].append( parts[3] )
    in_f.close()
    return rules

# ================================================
    
_punctOrAbbrev = re.compile('//\s*_[ZY]_')

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
    
# ================================================

_morfWithForm    = re.compile('^\s*(\S.*)\s+//\s*(_._)\s+(\S[^/]*)//')
_morfWithoutForm = re.compile('^\s*(\S.*)\s+//\s*(_._)\s+//')

# ================================================

def convert_mrf_to_syntax_mrf( mrf_lines, conversion_rules ):
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
    i = 0
    while ( i < len(mrf_lines) ):
        line = mrf_lines[i]
        if line.startswith('  '):  # only consider lines of analysis 
            # 1) Convert punctuation
            if _punctOrAbbrev.search(line):
                mrf_lines[i] = _convert_punctuation( line )
                if '_Y_' not in line:
                    i += 1
                    continue
            # 2) Convert morphological analyses that have a form specified
            withFormMatch = _morfWithForm.search(line)
            if withFormMatch:
                root    = withFormMatch.group(1)
                pos     = withFormMatch.group(2)
                formStr = withFormMatch.group(3)
                forms   = formStr.split(',')
                all_new_lines = []
                for form in forms:
                    morphKey = pos+' '+form.strip()
                    if morphKey in conversion_rules:
                        newlines = [ '    '+root+' //'+_esc_que_mark(r)+' //' for r in conversion_rules[morphKey] ]
                        all_new_lines.extend( newlines )
                if all_new_lines:
                    del mrf_lines[i] 
                    for newline in all_new_lines:
                        mrf_lines.insert(i, newline)
                    i += len(newlines)
                    continue
            else:
                withoutFormMatch = _morfWithoutForm.search(line)
                if withoutFormMatch:
                    # 3) Convert morphological analyses that have only POS specified
                    root = withoutFormMatch.group(1)
                    pos  = withoutFormMatch.group(2)
                    morphKey = pos
                    all_new_lines = []
                    if morphKey in conversion_rules:
                        newlines = [ '    '+root+' //'+_esc_que_mark(r)+' //' for r in conversion_rules[morphKey] ]
                        all_new_lines.extend( newlines )
                    if all_new_lines:
                        del mrf_lines[i] 
                        for newline in all_new_lines:
                            mrf_lines.insert(i, newline)
                        i += len(newlines)
                        continue
        i += 1
    return mrf_lines


# ==================================================================================
# ==================================================================================
#   3)  Convert pronouns from Filosoft's mrf to syntactic analyzer's mrf
#       (former 'tpron.pl')
# ==================================================================================
# ==================================================================================

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


def convert_pronouns( mrf_lines ):
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
    i = 0
    while ( i < len(mrf_lines) ):
        line = mrf_lines[i]
        if '_P_' in line:  # only consider lines containing pronoun analyses
           for [pattern, replacement] in _pronConversions:
               lastline = line
               line = re.sub(pattern, replacement, line)
               if lastline != line:
                  mrf_lines[i] = line
                  break
        i += 1
    return mrf_lines


# ==================================================================================
# ==================================================================================
#   4)  Remove duplicate analysis lines;
#       Remove adpositions (_K_) that do not have subcategorization information;
#       (former 'tcopyremover.pl')
# ==================================================================================
# ==================================================================================

def remove_duplicate_analyses( mrf_lines, allow_to_delete_all = True ):
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
    i = 0
    seen_analyses  = []
    analyses_count = 0
    to_delete      = []
    Kpre_index     = -1
    Kpost_index    = -1
    while ( i < len(mrf_lines) ):
        line = mrf_lines[i]
        if not line.startswith('  '): 
           if Kpre_index != -1 and Kpost_index != -1:
              # If there was both _K_pre and _K_post, add _K_pre to removables;
              to_delete.append( Kpre_index )
           elif Kpost_index != -1:
              # If there was only _K_post, add _K_post to removables;
              to_delete.append( Kpost_index )
           # Delete found duplicates
           if to_delete:
              for k, j in enumerate(sorted(to_delete, reverse=True)):
                  # If we must preserve at least one analysis, and
                  # it has been found that all should be deleted, then 
                  # keep the last one
                  if not allow_to_delete_all and \
                     analyses_count == len(to_delete) and \
                     k == len(to_delete) - 1:
                     continue
                  # Delete the analysis line
                  del mrf_lines[j]
                  i -= 1
           # Reset the memory for each new word/token
           seen_analyses = []
           analyses_count = 0
           to_delete     = []
           Kpre_index    = -1
           Kpost_index   = -1
        elif line.startswith('  '):   # the line of analysis 
           analyses_count += 1
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
              seen_analyses.append( line )
        i += 1
    return mrf_lines


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


def add_hashtag_info( mrf_lines ):
    ''' Augments analysis lines with various hashtag information:
          *) marks words with capital beginning with #cap;
          *) marks finite verbs with #FinV;
          *) marks nud/tud/mine/nu/tu/v/tav/mata/ja forms;
        Hashtags are added at the end of the analysis content (just before the 
        last '//');

        Returns the input list where the augmentation has been applied;
    ''' 
    i   = 0
    cap = False
    while ( i < len(mrf_lines) ):
        line = mrf_lines[i]
        if not line.startswith('  ') and len(line) > 0:
           cap = (line[0]).isupper()
        elif line.startswith('  '): 
           if cap:
              line = re.sub('(//.+\S)\s+//', '\\1 #cap //', line)
           if _morfFinV.search( line ) and not _morfNotFinV.search( line ):
              line = re.sub('(//.+\S)\s+//', '\\1 #FinV //', line)
           for [pattern, replacement] in _mrfHashTagConversions:
               line = re.sub(pattern, replacement, line)
           mrf_lines[i] = line
        i += 1
    return mrf_lines


# ==================================================================================
# ==================================================================================
#   6) Add subcategorization information to verbs and adpositions;
#       (former 'tagger08.c')
# ==================================================================================
# ==================================================================================

def load_subcat_info( subcat_lex_file ):
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
    rules = {}
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
           if lemma not in rules:
              rules[lemma] = []
           parts = subcatRules.split('&')
           for part in parts:
              part = part.strip()
              rules[lemma].append( part )
           lemma = ''
           subcatRules = ''
    in_f.close()
    #print( len(rules.keys()) )   # 4484
    return rules


def _check_condition( cond_string, target_string ):
    ''' Checks whether cond_string is at the beginning of target_string, or
        whether cond_string is within target_string, preceded by whitespace.

        Returns boolean indicating the result of the check-up;
    '''
    return ((target_string.startswith(cond_string)) or (' '+cond_string in target_string))


analysisLemmaPat = re.compile('^\s+([^+ ]+)\+')
analysisPat      = re.compile('//([^/]+)//')


def tag_subcat_info( mrf_lines, subcat_rules ):
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
    i = 0
    while ( i < len(mrf_lines) ):
        line = mrf_lines[i]
        if line.startswith('  '):
           lemma_match = analysisLemmaPat.match(line)
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
                        j = i
                        # Add new line or lines
                        for a in additions:
                            line_copy = line if i == j else line[:] 
                            items_to_add = a.split()
                            for item in items_to_add:
                                if not _check_condition(item, analysis):
                                   line_copy = \
                                       re.sub('(//.+\S)\s+//', '\\1 '+item+' //', line_copy)
                            if j == i:
                               # 1) replace the existing line
                               mrf_lines[i] = line_copy
                            else:
                               # 2) add a new line 
                               mrf_lines.insert(i, line_copy)
                            j += 1
                        i = j - 1
                        # No need to search forward
                        break
        i += 1
    return mrf_lines


# ==================================================================================
# ==================================================================================
#   8) Convert from syntax preprocessing format to cg3 input format;
#       (former 'tkms2cg3.pl')
# ==================================================================================
# ==================================================================================

def convert_to_cg3_input( mrf_lines ):
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
    i = 0
    while ( i < len(mrf_lines) ):
        line = mrf_lines[i]
        if not line.startswith('  ') and len(line) > 0:
           #
           # A line containing word/token
           #
           #  a. surround the word with "< and >"
           line = re.sub('^(\S.*)([\n\r]*)$','"<\\1>"\\2', line)
           #  b. fix the sentence begin/end tags
           line = re.sub('<<(s|/s)>>', '<\\1>', line)
           mrf_lines[i] = line
        elif line.startswith('  '):
           #
           # A line containing analysis
           #
           #  1. perform various fixes:
           line = re.sub('#cap #cap','cap', line)
           line = re.sub('#cap','cap', line)
           line = re.sub('\*\*CLB','CLB', line)
           line = re.sub('#Correct!','<Correct!>', line)
           line = re.sub('####','', line)
           line = re.sub('#(\S+)','<\\1>', line)
           line = re.sub('\$([,.;!?:<]+)','\\1', line)
           line = re.sub('_Y_\s+\? _Z_','_Z_', line)
           line = re.sub('_Y_\s+\?\s+_Z_','_Z_', line)
           line = re.sub('_Y_\s+_Z_','_Z_', line)
           line = re.sub('_Z_\s+\?','_Z_', line)
           #  2. convert analysis line \w word ending
           line = re.sub('^\s+(\S+)(.*)\+(\S+)\s*//_(\S)_ (.*)//(.*)$', \
                         '    "\\1\\2" L\\3 \\4 \\5 \\6', line)
           #  3. convert analysis line \wo word ending
           line = re.sub('^\s+(\S+)(.*)\s+//_(\S)_ (.*)//(.*)$', \
                         '    "\\1\\2" \\3 \\4 \\5', line)
           mrf_lines[i] = line
        i += 1
    return mrf_lines


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
            self.subcat_rules = load_subcat_info( self.subcat_rules_file )



    def process_vm_json( self, json_dict, **kwargs ):
        ''' Executes the preprocessing pipeline on vabamorf's JSON, given as a dict;

            Returns a list: lines of analyses in the VISL CG3 input format;
        ''' 
        mrf_lines = convert_vm_json_to_mrf( json_dict )
        return self.process_mrf_lines( mrf_lines, **kwargs )


    def process_Text( self, text, **kwargs ):
        ''' Executes the preprocessing pipeline on estnltk's Text object.

            Returns a list: lines of analyses in the VISL CG3 input format;
        ''' 
        mrf_lines = convert_Text_to_mrf( text )
        return self.process_mrf_lines( mrf_lines, **kwargs )


    def process_mrf_lines( self, mrf_lines, **kwargs ):
        ''' Executes the preprocessing pipeline on mrf_lines.

            The input should be an analysis of the text in Filosoft's old mrf format;

            Returns the input list, where elements (tokens/analyses) have been converted
            into the new format;
        '''
        converted1 = convert_mrf_to_syntax_mrf( mrf_lines, self.fs_to_synt_rules )
        converted2 = convert_pronouns( converted1 )
        converted3 = remove_duplicate_analyses( converted2, allow_to_delete_all=self.allow_to_remove_all )
        converted4 = add_hashtag_info( converted3 )
        converted5 = tag_subcat_info( converted4, self.subcat_rules )
        converted6 = remove_duplicate_analyses( converted5, allow_to_delete_all=self.allow_to_remove_all )
        converted7 = convert_to_cg3_input( converted6 )
        return converted7



