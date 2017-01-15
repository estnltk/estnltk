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
from estnltk.taggers import MorphExtendedTagger
from estnltk.taggers import QuickMorphExtendedTagger

import re
import os.path

from estnltk.legacy.core import PACKAGE_PATH

SYNTAX_PATH      = os.path.join(PACKAGE_PATH, 'syntax', 'files')
FS_TO_SYNT_RULES_FILE = os.path.join(SYNTAX_PATH, 'tmorftrtabel.txt')
SUBCAT_RULES_FILE     = os.path.join(SYNTAX_PATH, 'abileksikon06utf.lx')



def is_partic_suffix(suffix):
    return suffix in {'tud', 'nud', 'v', 'tav', 'mata'} 

# ==================================================================================
# ==================================================================================
#   6) Add subcategorization information to verbs and adpositions;
#       (former 'tagger08.c')
# ==================================================================================
# ==================================================================================



analysisLemmaPat = re.compile('^\s+([^+ ]+)\+')
analysisPat      = re.compile('//([^/]+)//')



# ==================================================================================
# ==================================================================================
#   8) Convert from syntax preprocessing format to cg3 input format;
#       (former 'tkms2cg3.pl')
# ==================================================================================
# ==================================================================================

def _esc_double_quotes(str1):
    ''' Escapes double quotes.
    '''
    return str1.replace('"', '\\"').replace('\\\\\\"', '\\"').replace('\\\\"', '\\"')

def word_morph_extended_to_cg3(record):
    pass

def convert_to_cg3_input(text):
    ''' Converts text with morph_extended layer to cg3 input
        format.
          *) 
          *) surrounds word lemmas with " in analysis;
          *) separates word endings from lemmas in analysis, and adds prefix 'L';
          *) removes '//' and '//' from analysis;
          *) converts hashtags to tags surrounded by < and >;

        Returns list of strings in new format.
    ''' 
    morph_lines = []
    word_index = -1
    for sentence in text.sentences:
        morph_lines.append('"<s>"')
        for word in sentence.words:
            word_index += 1
            morph_lines.append('"<'+_esc_double_quotes(word.text)+'>"')
            for morph_extended in text.morph_extended[word_index]:
                new_form_list = []
                if morph_extended.pronoun_type:
                    new_form_list.extend(morph_extended.pronoun_type)
                if morph_extended.form:
                    new_form_list.append(morph_extended.form)
                if morph_extended.letter_case:
                    new_form_list.append(morph_extended.letter_case)
                if is_partic_suffix(morph_extended.verb_extension_suffix):
                    new_form_list.append('partic')
                if morph_extended.fin:
                    new_form_list.append('<FinV>')
                if morph_extended.verb_extension_suffix:
                    new_form_list.append('<'+morph_extended.verb_extension_suffix+'>')
                if morph_extended.subcat:
                    subcat = morph_extended.subcat
                    subcat = [''.join(('<', s, '>')) for s in subcat]
                    new_form_list.extend(subcat)
                if morph_extended.punctuation_type:
                    new_form_list.append(morph_extended.punctuation_type)

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
        self.subcat_rules_extra_file = None
        for argName, argVal in kwargs.items():
            if argName in ['fs_to_synt_rules_file', 'fs_to_synt_rules', 'fs_to_synt']:
                self.fs_to_synt_rules_file = argVal
            elif argName in ['subcat_rules_file', 'subcat_rules', 'subcat']:
                self.subcat_rules_file = argVal
            elif argName in ['subcat_rules_extra_file', 'subcat_rules_extra', 'subcat_extra']:
                self.subcat_rules_extra_file = argVal
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
        #  subcat_rules_extra_file:
        if self.subcat_rules_extra_file and not os.path.exists(self.subcat_rules_extra_file):
                raise Exception('(!) Unable to find *subcat_extra_rules* from location:', \
                                self.subcat_rules_extra_file)
        self.morph_extended_tagger = QuickMorphExtendedTagger(self.fs_to_synt_rules_file, self.allow_to_remove_all, self.subcat_rules_file, self.subcat_rules_extra_file)


    def process_Text(self, text, **kwargs):
        ''' Executes the preprocessing pipeline on estnltk's Text object.

            Returns a list: lines of analyses in the VISL CG3 input format;
            Executes the preprocessing pipeline on mrf_lines.

            The input should be an analysis of the text in Filosoft's old mrf format;

            Returns the input list, where elements (tokens/analyses) have been converted
            into the new format;
        '''
        self.morph_extended_tagger.tag(text)

        print('o ', end='', flush=True)
        text, morph_lines = convert_to_cg3_input(text)
        return text, morph_lines