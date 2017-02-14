# -*- coding: utf-8 -*- 

from __future__ import unicode_literals, print_function
from estnltk.taggers import MorphExtendedTagger
from estnltk.taggers import QuickMorphExtendedTagger as MorphExtendedTagger

import re
import os.path

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
                    
                    if morph_extended.partofspeech == 'H':
                        line = re.sub(' L0 H  $',' L0 H   ', line)
                    morph_lines.append(line)
            morph_lines.append('"</s>"')
        return morph_lines


class SyntaxPreprocessing:
    ''' A preprocessing pipeline for VISL CG3 based syntactic analysis.
    '''


    def __init__( self, **kwargs):
        ''' Initializes MorphExtendedTagger and Cg3Exporter for VISL CG3 based
            syntax preprocessing pipeline. 
            
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
        self.allow_to_remove_all = False
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
        if not os.path.exists(self.fs_to_synt_rules_file):
            raise Exception('(!) Unable to find *fs_to_synt_rules_file* from location:',
                            self.fs_to_synt_rules_file)
        #  subcat_rules_file:
        if not os.path.exists(self.subcat_rules_file):
            raise Exception('(!) Unable to find *subcat_rules_file* from location:',
                            self.subcat_rules_file)
        self.morph_extended_tagger = MorphExtendedTagger(self.fs_to_synt_rules_file, 
                                                         self.allow_to_remove_all, 
                                                         self.subcat_rules_file)
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