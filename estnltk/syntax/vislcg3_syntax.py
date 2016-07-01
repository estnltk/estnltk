# -*- coding: utf-8 -*- 
#
#   Methods for VISL-CG3 based syntactic analysis of Estonian.
#
#   A reimplementation of the Estonian VISL-CG3 based syntax processing 
#   pipeline from  https://github.com/EstSyntax/EstCG 
#
#   Developed and tested under Python's versions:  2.7.11,  3.4.4
#
#   VISLCG3Pipeline executes a pipeline of VISLCG3 based analysis steps.
#   *) Default steps in the pipeline:
#      1) 'clo.rul'     -- disambiguates finite/main verbs, and adds
#                          clause boundary information;
#      2) 'morfyhe.rul' -- rule-based morphological disambiguation;
#      3) 'PhVerbs.rul' -- detects phrasal verbs;
#      4) 'pindsyn.rul' -- adds surface-syntactic analyses (syntactic 
#                          functions of the words);
#      5) 'strukt_parand.rul' -- adds dependency syntactic relations;
#   *) VISLCG3Pipeline assumes input in the same format as the output of 
#      SyntaxPreprocessing;
#
#   Example usage:
#
#      from estnltk import Text
#      from syntax_preprocessing import SyntaxPreprocessing
#      from vislcg3_syntax import VISLCG3Pipeline
#
#      #  Set the variables:
#      #    fsToSyntFulesFile -- path to 'tmorftrtabel.txt'
#      #    subcatFile        -- path to 'abileksikon06utf.lx'
#      #    vislcgRulesDir    -- path to dir containing *.rul files for VISLCG3;
#      #    text              -- the text to be analyzed, estnltk Text object;
#      #    vislcg_path       -- name of the VISLCG3 executable, full path;
# 
#      # Preprocessing for the syntax
#      pipeline1 = SyntaxPreprocessing( fs_to_synt=fsToSyntFulesFile, subcat=subcatFile )
#      results1  = pipeline1.process_Text( text )
#
#      # Syntactic analysis
#      pipeline2 = VISLCG3Pipeline( rules_dir = vislcgRulesDir, vislcg_cmd = vislcg_path )
#      results2  = pipeline2.process_lines( results1 )
#
#      # Results of the syntactic analysis
#      print( results2 )
#
#
#

from __future__ import unicode_literals, print_function

#from estnltk.names import *
#from estnltk.text import Text
from estnltk.core import as_unicode

from syntax_preprocessing import SyntaxPreprocessing

import re
import os, os.path
import codecs
import tempfile
from subprocess import Popen, PIPE


# ==================================================================================
# ==================================================================================
#   Pipeline for VISLCG3 based syntactic analysis
# ==================================================================================
# ==================================================================================


class VISLCG3Pipeline:
    ''' A pipeline for VISL CG3 based syntactic analysis.

        *) Default steps in the pipeline:
              1) 'clo.rul'     -- disambiguates finite/main verbs, and adds
                                  clause boundary information;
              2) 'morfyhe.rul' -- rule-based morphological disambiguation;
              3) 'PhVerbs.rul' -- detects phrasal verbs;
              4) 'pindsyn.rul' -- adds surface-syntactic analyses (syntactic 
                                  functions of words);
              5) 'strukt_parand.rul' -- adds dependency syntactic relations;

                 ( The complete Estonian VISL-CG3 based syntax processing pipeline
                   is available at https://github.com/EstSyntax/EstCG )

        *) VISLCG3Pipeline assumes that the input is in the same format, as the 
           output of SyntaxPreprocessing;

        Example usage:

            from estnltk import Text
            from syntax_preprocessing import SyntaxPreprocessing
            from vislcg3_syntax import VISLCG3Pipeline

            #  Set the variables:
            #    fsToSyntFulesFile -- path to 'tmorftrtabel.txt'
            #    subcatFile        -- path to 'abileksikon06utf.lx'
            #    vislcgRulesDir    -- path to dir containing *.rul files for VISLCG3;
            #    text              -- the text to be analyzed, estnltk Text object;
            #    vislcg_path       -- path to VISLCG3 executable;
            
            # Preprocessing for the syntax
            pipeline1 = SyntaxPreprocessing( fs_to_synt=fsToSyntFulesFile, subcat=subcatFile )
            results1  = pipeline1.process_Text( text )

            # Syntactic analysis
            pipeline2 = VISLCG3Pipeline( rules_dir = vislcgRulesDir, vislcg_cmd = vislcg_path )
            results2  = pipeline2.process_lines( results1 )

            # Results of the syntax
            print( results2 )

    '''

    rules_pipeline = ['clo.rul', 'morfyhe.rul', 'PhVerbs.rul', 'pindsyn.rul', 'strukt_parand.rul']
    rules_dir      = None
    vislcg_cmd     = 'vislcg3'
    
    def __init__( self, **kwargs):
        ''' Initializes VISL CG3 based syntax pipeline. 
        
            Parameters
            -----------
            vislcg_cmd : str
                Name of visl_cg3 binary executable. If the executable is accessible from system's 
                PATH variable, full path can be omitted, otherwise, the name must contain full 
                path to the executable.
                Default: 'vislcg3'

            pipeline : list of str
                List of VISLCG3 rule file names. In the processing phase, these rules
                are executed exactly the same order as in the list.
                NB! Do not add path to the name of rules, instead ensure that all the rules
                are in one directory, and provide the name of the directory as parameter 
                rules_dir.
                
            rules_dir : str
                Directory from where to find rules that are executed on the pipeline.
                All files listed in pipeline must be in that directory.
                Required parameter.

        '''
        cmd_changed = False
        for argName, argVal in kwargs.items():
            if argName == 'pipeline':
                self.rules_pipeline = argVal
            elif argName == 'rules_dir':
                self.rules_dir = argVal
            elif argName in ['vislcg_cmd', 'vislcg']:
                self.vislcg_cmd = argVal
                cmd_changed = True
            else:
                raise Exception(' Unsupported argument given: '+argName)
        # Validate input arguments
        if not self.rules_dir:
            raise Exception('Missing input argument: rules_dir')
        if not self.rules_pipeline or len( self.rules_pipeline ) == 0:
            raise Exception('(!) Pipeline is missing or empty. Please provide correct pipeline!')
        # Check for the existence of rules
        if not os.path.exists( self.rules_dir ):
            raise Exception('Invalid rules directory:',self.rules_dir)
        for rule_file in self.rules_pipeline:
            rule_path = os.path.join( self.rules_dir, rule_file )
            if not os.path.exists( rule_path ):
               raise Exception('Rules file not found:', rule_path)
        # Check for existence of VISLCG3 executable
        if not os.path.exists( self.vislcg_cmd ):
           # If the full path is not accessible, check whether the command is in PATH
           if not self.check_if_vislcg_is_in_path( self.vislcg_cmd ):
              msg = " Could not find VISLCG3 executable: "+str(self.vislcg_cmd)+"!\n"+\
                    " Please make sure that VISLCG3 is installed in your system and\n"+\
                    " available from system's PATH variable. Alternatively, you can\n"+\
                    " provide the location of VISLCG3 executable via the input\n"+\
                    " argument 'vislcg_cmd'. ";
              raise Exception( msg )


    def check_if_vislcg_is_in_path( self, vislcg_cmd1 ):
        ''' Checks whether given vislcg_cmd1 is in system's PATH. Returns True, there is 
            a file named  vislcg_cmd1  in the path, otherwise returns False;

            The idea borrows from:  http://stackoverflow.com/a/377028
        '''
        for path in os.environ["PATH"].split( os.pathsep ):
            path1 = path.strip('"')
            file1 = os.path.join(path1, vislcg_cmd1)
            if os.path.isfile(file1) or os.path.isfile(file1+'.exe'):
               return True
        return False
        

    def process_lines( self, input_lines, **kwargs ):
        ''' Executes the pipeline of subsequent VISL_CG3 commands. The first process
            in pipeline gets input_lines as an input, and each subsequent process gets
            the output of the previous process as an input.
            Returns the result of the last process in the pipeline, either as a string 
            or, alternatively, as a list of strings (if split_result == True);
 
            Parameters
            -----------
            input_lines : list of str
                 The input text for the pipeline; Should be in same format as the output
                 of SyntaxPreprocessing;

            split_result : bool
                 Optional argument specifying whether the result should be split by 
                 newlines, and returned as a list of strings/lines instead;
                 Default:False

            remove_info : bool
                 Optional argument specifying whether the additional information added 
                 during the preprocessing and syntactic processing should be removed
                 from the results;
                 Default:True;
                 The method  cleanup_lines()  will be used for removing additional info,
                 and all the parameters passed to this method will be also forwarded to 
                 the cleanup method;

        '''
        split_result_lines = False
        remove_info = True
        for argName, argVal in kwargs.items() :
            if argName in ['split_result_lines', 'split_result'] and argVal in [True, False]:
               split_result_lines = argVal
            if argName in ['remove_info', 'info_remover', 'clean_up'] and argVal in [True, False]:
               remove_info = argVal

        # 1) Construct the input file for the first process in the pipeline
        temp_input_file = \
            tempfile.NamedTemporaryFile(prefix='vislcg3_in.', mode='w', delete=False)
        temp_input_file.close()
        # We have to open separately here for writing, because Py 2.7 does not support
        # passing parameter   encoding='utf-8'    to the NamedTemporaryFile;
        out_f = codecs.open(temp_input_file.name, mode='w', encoding='utf-8')
        for line in input_lines:
            out_f.write( line.rstrip() )
            out_f.write( '\n' )
        out_f.close()
        # TODO: tempfile is currently used to ensure that the input is in 'utf-8',
        #       but perhaps we can somehow ensure it without using tempfile ??


        # 2) Dynamically construct the pipeline and open processes
        pipeline = []
        for i in range( len(self.rules_pipeline) ):
            rule_file = self.rules_pipeline[i]
            process_cmd = [self.vislcg_cmd, '-o', '-g', os.path.join(self.rules_dir, rule_file)]
            process = None
            if i == 0:
               # The first process takes input from the file
               process_cmd.extend( ['-I', temp_input_file.name] )
               process = Popen(process_cmd, stdin=PIPE, stdout=PIPE)
            else:
               # A subsequent process takes output of the last process as an input
               process = Popen(process_cmd, stdin=pipeline[-1]['process'].stdout, stdout=PIPE)
            # Record the process
            process_dict = {'process':process, 'cmd':process_cmd}
            pipeline.append( process_dict )
        
        # 3) Close all stdout streams, except the last one
        for i in range( len(pipeline) ):
           if i != len(pipeline) - 1:
              pipeline[i]['process'].stdout.close()

        # 4) Communicate results form the last item in the pipeline
        result = as_unicode( pipeline[-1]['process'].communicate()[0] )
        pipeline[-1]['process'].stdout.close() # Close the last process

        # Clean-up
        # 1) remove temp file
        os.remove(temp_input_file.name)

        # 2) remove additional info, if required
        if remove_info:
              result = '\n'.join( cleanup_lines( result.split('\n'), **kwargs ))

        return result if not split_result_lines else result.split('\n')



# ==================================================================================
#   Post-processing/clean-up steps for VISLCG3 based syntactic analysis
# ==================================================================================


def cleanup_lines( lines, **kwargs ):
    ''' Cleans up annotation after syntactic pre-processing and processing:
        -- Removes embedded clause boundaries "<{>" and "<}>";
        -- Removes CLBC markings from analysis;
        -- Removes additional information between < and > from analysis;
        -- Removes additional information between " and " from analysis;
        -- If remove_caps==True , removes 'cap' annotations from analysis;
        -- If esc_double_quotes==True , " will be overwritten with \\";
        -- If remove_clo==True , removes CLO CLC CLB markings from analysis;
        
        Returns the input list, which has been cleaned from additional information;
        
    '''
    remove_caps       = False
    esc_double_quotes = False
    remove_clo        = False
    for argName, argVal in kwargs.items() :
        if argName in ['remove_caps', 'remove_cap'] and argVal in [True, False]:
           remove_caps = argVal
        if argName in ['esc_double_quotes', 'esc_quotes'] and argVal in [True, False]:
           esc_double_quotes = argVal
        if argName == 'remove_clo' and argVal in [True, False]:
           remove_clo = argVal
    i = 0
    to_delete = []
    while ( i < len(lines) ):
        line = lines[i]
        isAnalysisLine = line.startswith('  ') or line.startswith('\t')
        if not isAnalysisLine:
           removeCurrentTokenAndAnalysis = False
           #  1) Remove embedded clause boundaries "<{>" and "<}>"
           if line.startswith('"<{>"'):
              if i+1 == len(lines) or (i+1 < len(lines) and not '"{"' in lines[i+1]):
                 removeCurrentTokenAndAnalysis = True
           if line.startswith('"<}>"'):
              if i+1 == len(lines) or (i+1 < len(lines) and not '"}"' in lines[i+1]):
                 removeCurrentTokenAndAnalysis = True
           if removeCurrentTokenAndAnalysis:
              # Remove the current token and all the subsequent analyses
              del lines[i]
              j=i
              while ( j < len(lines) ):
                 line2 = lines[j]
                 if line2.startswith('  ') or line2.startswith('\t'):
                    del lines[j]
                 else:
                    break
              continue
           #  Escape double quotes
           if esc_double_quotes:
              lines[i] = lines[i].replace('"<">"', '"<\\">"')
              lines[i] = lines[i].replace('"<"">"', '"<\\"\\">"')
              lines[i] = lines[i].replace('"<""">"', '"<\\"\\"\\">"')
        else:
           #  Normalize analysis line
           lines[i] = re.sub('^\s{4,}', '\t', lines[i])
           #  Remove clause boundary markings
           lines[i] = re.sub('(.*)" ([LZT].*) CLBC (.*)', '\\1" \\2 \\3', lines[i])
           #  Remove additional information that was added during the analysis
           lines[i] = re.sub('(.*)" L([^"<]*) ["<]([^@]*) (@.*)', '\\1" L\\2 \\4', lines[i]) 
           #  Remove 'cap' tags
           if remove_caps:
              lines[i] = lines[i].replace(' cap ', ' ')
           #  Escape double quotes
           if esc_double_quotes:
              lines[i] = lines[i].replace('\t""" Z', '\t"\\"" Z')
              lines[i] = lines[i].replace('\t"""" Z', '\t"\\"\\"" Z')
              lines[i] = lines[i].replace('\t""""" Z', '\t"\\"\\"\\"" Z')
           #  Remove CLO CLC CLB markings
           if remove_clo and 'CL' in lines[i]:
              lines[i] = re.sub('\sCL[OCB]', ' ', lines[i])
              lines[i] = re.sub('\s{2,}', ' ', lines[i])
        i += 1
    return lines

