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




# ==================================================================================
# ==================================================================================
#   6) Add subcategorization information to verbs and adpositions;
#       (former 'tagger08.c')
# ==================================================================================
# ==================================================================================



# ==================================================================================
# ==================================================================================
#   8) Convert from syntax preprocessing format to cg3 input format;
#       (former 'tkms2cg3.pl')
# ==================================================================================
# ==================================================================================


    
# ==================================================================================
# ==================================================================================
#   Syntax  preprocessing  pipeline
# ==================================================================================
# ==================================================================================
class Cg3Exporter():


    @staticmethod
    def _esc_double_quotes(str1):
        ''' Escapes double quotes.
        '''
        return str1.replace('"', '\\"').replace('\\\\\\"', '\\"').replace('\\\\"', '\\"')

    @staticmethod
    def is_partic_suffix(suffix):
        return suffix in {'tud', 'nud', 'v', 'tav', 'mata'}
    

    def export(self, text):
        ''' Converts text with morph_extended layer to cg3 input format.
    
            Returns list of strings in new format.
        ''' 
        morph_lines = []
        word_index = -1
        for sentence in text.sentences:
            morph_lines.append('"<s>"')
            for word in sentence.words:
                word_index += 1
                morph_lines.append('"<'+self._esc_double_quotes(word.text)+'>"')
                for morph_extended in text.morph_extended[word_index]:
                    form_list = [morph_extended.partofspeech]
                    if morph_extended.pronoun_type:
                        form_list.extend(morph_extended.pronoun_type)
                    if morph_extended.form:
                        form_list.append(morph_extended.form)
                    if morph_extended.punctuation_type:
                        form_list.append(morph_extended.punctuation_type)
                    if morph_extended.letter_case:
                        form_list.append(morph_extended.letter_case)
                    if morph_extended.fin:
                        form_list.append('<FinV>')
                    for ves in morph_extended.verb_extension_suffix:
                        if self.is_partic_suffix(ves):
                            form_list.append('partic')
                        form_list.append(''.join(('<', ves, '>')))
                    if morph_extended.subcat:
                        subcat = morph_extended.subcat
                        subcat = [''.join(('<', s, '>')) for s in subcat]
                        form_list.extend(subcat)
                    
                    form_list = ' '.join(form_list)
            
                    if morph_extended.ending or morph_extended.clitic:
                        line = ''.join(('    "',morph_extended.root,
                                        '" L', morph_extended.ending, morph_extended.clitic,
                                        ' ', form_list, '  '))
                    else:
                        if morph_extended.partofspeech == 'Z':
                            line = ''.join(('    "',morph_extended.root,'" ', 
                                            form_list, '  '))
                        else:
                            line = ''.join(('    "',morph_extended.root,'+" ', 
                                            form_list, '  '))
                    
                    if line == '    "" L0 Y nominal  ':
                        line = '    "+0" Y nominal  ' # '!~~~'
                    if line == '    "" Z  ':
                        line = '     //_Z_ //' # '<<'
                    # FinV on siin arvatavasti ebakorrektne ja tekkis cap märgendi tõttu
                    if morph_extended.form == 'aux neg':
                        line = re.sub('ei" L0(.*) V aux neg cap ','ei" L0\\1 V aux neg cap <FinV> ', line) # 'Astun-ei'
                    if morph_extended.partofspeech == 'H':
                        line = re.sub(' L0 H  $',' L0 H   ', line)
                    if '#' in morph_extended.root:
                        line = re.sub('####', '', line) # '####'
                        if '#' in line:
                            line = re.sub('#(\S+ L0)','<\\1>', line) # '!#'
                        else:
                            line = '    "+0" Y nominal  ' # '####'
                    if '$' in morph_extended.root:
                        line = re.sub('\$([,.;!?:<]+)','\\1', line) # '$#!%$#'
                    if '+' in morph_extended.root and not (morph_extended.ending + morph_extended.clitic):
                        line = re.sub('(\s+"\S+)\+(\S+)"( .*)', '\\1" L\\2\\3', line) # '!++'
                        if morph_extended.partofspeech == 'Z':
                            if line ==   '    "(" L) Z Cpr  ':
                                line =   '    "(" L) Z Cpr Opr  ' # '(+)'
                            elif line == '    "(" L)- Z Dsh  ':
                                line =   '    "(" L)- Z Dsh Opr  ' # '(+)-'
                            elif line == '    ")" L( Z Opr  ':
                                line =   '    ")" L( Z Opr Cpr  ' # ')+('
                            elif line == '    "." L( Z Opr  ':
                                line =   '    "." L( Z Opr Fst  ' # '.+('

                    morph_lines.append(line)
            morph_lines.append('"</s>"')
        return morph_lines


SYNTAX_PATH      = os.path.join(PACKAGE_PATH, 'syntax', 'files')
FS_TO_SYNT_RULES_FILE = os.path.join(SYNTAX_PATH, 'tmorftrtabel.txt')
SUBCAT_RULES_FILE     = os.path.join(SYNTAX_PATH, 'abileksikon06utf.lx')


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
        
        self.cg3_exporter = Cg3Exporter()


    def process_Text(self, text):
        ''' Executes the syntax preprocessing pipeline on estnltk's Text object.
            Tags text with morph_extended layer and exports it in VISL CG3 input
            format.
            
            Parameters
            ----------
                text: Text
                    A Text object with morf_analysis layer (in Filosoft's old 
                    mrph format).

            Returns
            -------
                cg3_lines: list of str
                    A list of strings in the VISL CG3 input format.
        '''
        self.morph_extended_tagger.tag(text)

        return self.cg3_exporter.export(text)