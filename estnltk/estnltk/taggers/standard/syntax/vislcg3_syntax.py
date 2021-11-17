# -*- coding: utf-8 -*- 
#
#   Methods for VISL-CG3 based syntactic analysis of Estonian.
#
#   A reimplementation of the Estonian VISL-CG3 based syntax processing 
#   pipeline from  https://github.com/EstSyntax/EstCG 
#
#   Note that 
#    In the pipeline SYNTAX_PIPELINE_ESTCG:
#      all files, except 'strukt_parand.rul', are from the EstCG snapshot: 
#      https://github.com/EstSyntax/EstCG/tree/467f0746ae870169776b0ed7aef8825730fea671 
#      ('strukt_parand.rul' is currently distributed separately)
#    In the pipeline SYNTAX_PIPELINE_1_4:
#      rule files (*._ub.rle) are from: http://math.ut.ee/~tiinapl/CGParser.tar.gz
#
#   Developed and tested under Python's versions:  3.4.4, 3.5
#
#   VISLCG3Pipeline executes a pipeline of VISLCG3 based analysis steps.
#   *) Default steps in the pipeline:
#      1) 'clo.*'     -- disambiguates finite/main verbs, and adds
#                          clause boundary information;
#      2) 'morfyhe.*' -- rule-based morphological disambiguation;
#      3) 'PhVerbs.*' -- detects phrasal verbs;
#      4) 'pindsyn.*' -- adds surface-syntactic analyses (syntactic 
#                          functions of the words);
#      5) 'strukt.*'  -- adds dependency syntactic relations;
#   *) VISLCG3Pipeline assumes input in the same format as the output of 
#      estnltk.converters.CG3_exporter;
#
#   Example usage:
#
#      from estnltk import Text
#      from estnltk.converters import export_CG3
#      from estnltk.taggers.standard.syntax.vislcg3_syntax import VISLCG3Pipeline
#
#      #  Set the variables:
#      #    fsToSyntFulesFile -- path to 'tmorftrtabel.txt'
#      #    subcatFile        -- path to 'abileksikon06utf.lx'
#      #    vislcgRulesDir    -- path to dir containing *.rul files for VISLCG3;
#      #    text              -- the text to be analyzed, estnltk Text object;
#      #    vislcg_path       -- name of the VISLCG3 executable with full path;
# 
#      # Preprocessing for the syntax
#      text.analyse('syntax_preprocessing')
#      results1  = export_CG3(text)
#
#      # Syntactic analysis
#      pipeline2 = VISLCG3Pipeline( rules_dir = vislcgRulesDir, vislcg_cmd = vislcg_path )
#      results2  = pipeline2.process_lines( results1 )
#
#      # Results of the syntactic analysis
#      print( results2 )
#

from estnltk.common import abs_path
from estnltk_core.converters import as_unicode

from estnltk.converters.cg3.helpers import cleanup_lines

from os import linesep as OS_NEWLINE
import re
import os, os.path, sys
import codecs
import tempfile
from subprocess import Popen, PIPE

SYNTAX_PATH = abs_path('taggers/standard/syntax/files')
SYNTAX_PIPELINE_1_4 = \
    ['clo_ub.rle', 'morfyhe_ub.rle', 'PhVerbs_ub.rle', 'pindsyn_ub.rle', 'strukt_ub.rle']
SYNTAX_PIPELINE_ESTCG = \
    ['clo.rul', 'morfyhe.rul', 'PhVerbs.rul', 'pindsyn.rul', 'strukt_parand.rul']


# ==================================================================================
#   Helper function
# ==================================================================================

def check_if_vislcg_is_in_path( vislcg_cmd:str ):
    ''' Checks whether given vislcg_cmd is in system's PATH. Returns True, there is 
        a file with given name (vislcg_cmd) in the PATH, otherwise returns False;

        The idea borrows from:  http://stackoverflow.com/a/377028
    '''
    if os.getenv("PATH") == None:
        return False
    for path in os.environ["PATH"].split( os.pathsep ):
        path1 = path.strip('"')
        file1 = os.path.join(path1, vislcg_cmd)
        if os.path.isfile(file1) or os.path.isfile(file1+'.exe'):
           return True
    return False


# ==================================================================================
# ==================================================================================
#   Pipeline for VISLCG3 based syntactic analysis
# ==================================================================================
# ==================================================================================


class VISLCG3Pipeline:

    rules_pipeline = SYNTAX_PIPELINE_1_4
    rules_dir      = SYNTAX_PATH
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
            
            rules_dir : str
                A default directory from where to find rules that are executed on the 
                pipeline.
                If a file name listed in *pipeline* does not contain path, it is assumed 
                to reside within *rules_dir*;
            
            pipeline : list of str
                List of VISLCG3 rule file names. In the processing phase, these rules
                are executed exactly the same order as in the list.
                NB! If the rule file is given without path, it is assumed that the file
                resides in the directory *rules_dir*; Otherwise, a full path to the rule
                file must be provided within the name;

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
        else:
            # Make a local copy of the pipeline to ensure that, if anyone changes the local 
            # pipeline, the global one will remain the same:
            self.rules_pipeline = self.rules_pipeline[:]
        # Check for the existence of rules
        if not os.path.exists( self.rules_dir ):
            raise Exception('Invalid rules directory:',self.rules_dir)
        for rule_file in self.rules_pipeline:
            if rule_file == os.path.basename(rule_file):
                # if the rule is without a path, assume it is located in the rules dir
                rule_path = os.path.join( self.rules_dir, rule_file )
            else:
                # otherwise, assume that the path is provided within the rule
                rule_path = rule_file
            if not os.path.exists( rule_path ):
               raise Exception('Rules file not found:', rule_path)
        # Check for existence of VISLCG3 executable
        if not os.path.exists( self.vislcg_cmd ):
           # If the full path is not accessible, check whether the command is in PATH
           if not check_if_vislcg_is_in_path( self.vislcg_cmd ):
              msg = " Could not find VISLCG3 executable: "+str(self.vislcg_cmd)+"!\n"+\
                    " Please make sure that VISLCG3 is installed in your system and\n"+\
                    " available from system's PATH variable. Alternatively, you can\n"+\
                    " provide the location of VISLCG3 executable via the input\n"+\
                    " argument 'vislcg_cmd'. ";
              raise Exception( msg )




    def process_lines( self, input_lines, **kwargs ):
        ''' Executes the pipeline of subsequent VISL_CG3 commands. The first process
            in pipeline gets input_lines as an input, and each subsequent process gets
            the output of the previous process as an input.
            
            The idea of how to construct the pipeline borrows from:
              https://github.com/estnltk/estnltk/blob/1.4.0/estnltk/syntax/tagger.py
            
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

