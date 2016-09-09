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
#   Developed and tested under Python's versions:  2.7.11,  3.4.4
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
#      #    vislcg_path       -- name of the VISLCG3 executable with full path;
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

from estnltk.names import *
from estnltk.core import PACKAGE_PATH, as_unicode

import re
import os, os.path, sys
import codecs
import tempfile
from subprocess import Popen, PIPE

SYNTAX_PATH = os.path.join(PACKAGE_PATH, 'syntax', 'files')
SYNTAX_PIPELINE_1_4 = \
    ['clo_ub.rle', 'morfyhe_ub.rle', 'PhVerbs_ub.rle', 'pindsyn_ub.rle', 'strukt_ub.rle']
SYNTAX_PIPELINE_ESTCG = \
    ['clo.rul', 'morfyhe.rul', 'PhVerbs.rul', 'pindsyn.rul', 'strukt_parand.rul']


# ==================================================================================
# ==================================================================================
#   Pipeline for VISLCG3 based syntactic analysis
# ==================================================================================
# ==================================================================================


class VISLCG3Pipeline:
    ''' A pipeline for VISL CG3 based syntactic analysis.

        *) Default steps in the pipeline:
              1) 'clo.*'     -- disambiguates finite/main verbs, and adds
                                  clause boundary information;
              2) 'morfyhe.*' -- rule-based morphological disambiguation;
              3) 'PhVerbs.*' -- detects phrasal verbs;
              4) 'pindsyn.*' -- adds surface-syntactic analyses (syntactic 
                                  functions of words);
              5) 'strukt.*'  -- adds dependency syntactic relations;

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



# ==================================================================================
#   Post-processing/clean-up steps for VISLCG3 based syntactic analysis
#   ( former 'inforemover.pl' )
# ==================================================================================


def cleanup_lines( lines, **kwargs ):
    ''' Cleans up annotation after syntactic pre-processing and processing:
        -- Removes embedded clause boundaries "<{>" and "<}>";
        -- Removes CLBC markings from analysis;
        -- Removes additional information between < and > from analysis;
        -- Removes additional information between " and " from analysis;
        -- If remove_caps==True , removes 'cap' annotations from analysis;
        -- If remove_clo==True , removes CLO CLC CLB markings from analysis;
        -- If double_quotes=='esc'   then "   will be overwritten with \\";
           and 
           if double_quotes=='unesc' then \\" will be overwritten with ";
        -- If fix_sent_tags=True, then sentence tags (<s> and </s>) will be
           checked for mistakenly added analysis, and found analysis will be
           removed;
        
        Returns the input list, which has been cleaned from additional information;
    '''
    if not isinstance( lines, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    remove_caps   = False
    remove_clo    = False
    double_quotes = None
    fix_sent_tags = False
    for argName, argVal in kwargs.items() :
        if argName in ['remove_caps', 'remove_cap']:
           remove_caps = bool(argVal)
        if argName == 'remove_clo':
           remove_clo = bool(argVal)
        if argName == 'fix_sent_tags':
           fix_sent_tags = bool(argVal)
        if argName in ['double_quotes', 'quotes'] and argVal and \
           argVal.lower() in ['esc', 'escape', 'unesc', 'unescape']:
           double_quotes = argVal.lower()
    pat_token_line     = re.compile('^"<(.+)>"\s*$')
    pat_analysis_start = re.compile('^(\s+)"(.+)"(\s[LZT].*)$')
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
           #  2) Convert double quotes (if required)
           if double_quotes:
              #  '^"<(.+)>"\s*$'
              if pat_token_line.match( lines[i] ):
                 token_cleaned = (pat_token_line.match(lines[i])).group(1)
                 # Escape or unescape double quotes
                 if double_quotes in ['esc', 'escape']:
                    token_cleaned = token_cleaned.replace('"', '\\"')
                    lines[i] = '"<'+token_cleaned+'>"'
                 elif double_quotes in ['unesc', 'unescape']:
                    token_cleaned = token_cleaned.replace('\\"', '"')
                    lines[i] = '"<'+token_cleaned+'>"'
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
           #  Convert double quotes (if required)
           if double_quotes and double_quotes in ['unesc', 'unescape']:
              lines[i] = lines[i].replace('\\"', '"')
           elif double_quotes and double_quotes in ['esc', 'escape']:
              m = pat_analysis_start.match( lines[i] )
              if m:
                 # '^(\s+)"(.+)"(\s[LZT].*)$'
                 start   = m.group(1)
                 content = m.group(2)
                 end     = m.group(3)
                 content = content.replace('"', '\\"')
                 lines[i] = ''.join([start, '"', content, '"', end])
           #  Remove CLO CLC CLB markings
           if remove_clo and 'CL' in lines[i]:
              lines[i] = re.sub('\sCL[OCB]', ' ', lines[i])
              lines[i] = re.sub('\s{2,}', ' ', lines[i])
           #  Fix sentence tags that mistakenly could have analysis (in EDT corpus)
           if fix_sent_tags:
              if i-1 > -1 and ('"</s>"' in lines[i-1] or '"<s>"' in lines[i-1]):
                 lines[i] = ''
        i += 1
    return lines


# ==================================================================================
#   Align VISLCG3 output lines with words in EstNLTK Text
# ==================================================================================

def align_cg3_with_Text( lines, text, **kwargs ):
    ''' Aligns VISLCG3's output (a list of strings) with given EstNLTK\'s Text object.
        Basically, for each word position in the Text object, finds corresponding VISLCG3's
        analyses;

        Returns a list of dicts, where each dict has following attributes:
          'start'   -- start index of the word in Text;
          'end'     -- end index of the word in Text;
          'sent_id' -- index of the sentence in Text, starting from 0;
          'parser_out' -- list of analyses from the output of the syntactic parser;

        Parameters
        -----------
        lines : list of str
            The input text for the pipeline; Should be in same format as the output
            of VISLCG3Pipeline;

        text : Text
            EstNLTK Text object containing the original text that was analysed via 
            VISLCG3Pipeline;

        check_tokens : bool
            Optional argument specifying whether tokens should be checked for match 
            during the alignment. In case of a mismatch, an exception is raised.
            Default:False
        
        add_word_ids : bool
            Optional argument specifying whether each alignment should include attributes:
            * 'text_word_id' - current word index in the whole Text, starting from 0;
            * 'sent_word_id' - index of the current word in the sentence, starting from 0;
            Default:False


        Example output (for text 'Jah . Öö oli täiesti tuuletu .'):
        -----------------------------------------------------------
        {'sent_id': 0, 'start': 0, 'end': 3, 'parser_out': ['\t"jah" L0 D @ADVL #1->0\r']}
        {'sent_id': 0, 'start': 4, 'end': 5, 'parser_out': ['\t"." Z Fst CLB #2->2\r']}
        {'sent_id': 1, 'start': 6, 'end': 8, 'parser_out': ['\t"öö" L0 S com sg nom @SUBJ #1->2\r']}
        {'sent_id': 1, 'start': 9, 'end': 12, 'parser_out': ['\t"ole" Li V main indic impf ps3 sg ps af @FMV #2->0\r']}
        {'sent_id': 1, 'start': 13, 'end': 20, 'parser_out': ['\t"täiesti" L0 D @ADVL #3->4\r']}
        {'sent_id': 1, 'start': 21, 'end': 28, 'parser_out': ['\t"tuuletu" L0 A pos sg nom @PRD #4->2\r']}
        {'sent_id': 1, 'start': 29, 'end': 30, 'parser_out': ['\t"." Z Fst CLB #5->5\r']}

    '''
    from estnltk.text import Text
    if not isinstance( text, Text ):
        raise Exception('(!) Unexpected type of input argument! Expected EstNLTK\'s Text. ')
    if not isinstance( lines, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    check_tokens = False
    add_word_ids = False
    for argName, argVal in kwargs.items() :
        if argName in ['check_tokens', 'check'] and argVal in [True, False]:
           check_tokens = argVal
        if argName in ['add_word_ids', 'word_ids'] and argVal in [True, False]:
           add_word_ids = argVal
    pat_empty_line     = re.compile('^\s+$')
    pat_token_line     = re.compile('^"<(.+)>"$')
    pat_analysis_start = re.compile('^(\s+)"(.+)"(\s[LZTS].*)$')
    pat_sent_bound     = re.compile('^("<s>"|"</s>"|<s>|</s>)\s*$')
    generalWID  = 0
    sentWID     = 0
    sentenceID  = 0
    j = 0
    # Iterate over the sentences and perform the alignment
    results = []
    for sentence in text.divide( layer=WORDS, by=SENTENCES ):
        sentWID = 0
        for i in range(len(sentence)):
            # 1) take the next word in Text
            wordJson = sentence[i]
            wordStr  = wordJson[TEXT]
            cg3word     = None
            cg3analyses = []
            # 2) find next word in the VISLCG3's output
            while (j < len(lines)):
                # a) a sentence boundary: skip it entirely
                if pat_sent_bound.match( lines[j] ) and j+1 < len(lines) and \
                   (len(lines[j+1])==0 or pat_empty_line.match(lines[j+1])):
                    j += 2
                    continue
                # b) a word token: collect the analyses
                token_match = pat_token_line.match( lines[j].rstrip() )
                if token_match:
                    cg3word = token_match.group(1)
                    j += 1
                    while (j < len(lines)):
                        if pat_analysis_start.match(lines[j]):
                            cg3analyses.append(lines[j])
                        else:
                            break
                        j += 1
                    break
                j += 1
            # 3) Check whether two tokens match (if requested)
            if cg3word:
                if check_tokens and wordStr != cg3word: 
                    raise Exception('(!) Unable to align EstNLTK\'s token nr ',generalWID,\
                                    ':',wordStr,' vs ',cg3word)
                # Populate the alignment
                result_dict = { START:wordJson[START], END:wordJson[END], \
                                SENT_ID:sentenceID, PARSER_OUT: cg3analyses }
                if add_word_ids:
                    result_dict['text_word_id'] = generalWID # word id in the text
                    result_dict['sent_word_id'] = sentWID    # word id in the sentence
                results.append( result_dict )
            else:
                if j >= len(lines):
                    print('(!) End of VISLCG3 analysis reached: '+str(j)+' '+str(len(lines)),\
                          file = sys.stderr)
                raise Exception ('(!) Unable to find matching syntactic analysis ',\
                                 'for EstNLTK\'s token nr ', generalWID, ':', wordStr)
            sentWID    += 1
            generalWID += 1
        sentenceID += 1
    return results


# ==================================================================================
#   Convert VISLCG format annotations to CONLL format
# ==================================================================================

def convert_cg3_to_conll( lines, **kwargs ):
    ''' Converts the output of VISL_CG3 based syntactic parsing into CONLL format.
        Expects that the output has been cleaned ( via method cleanup_lines() ).
        Returns a list of CONLL format lines;
        
        Parameters
        -----------
        lines : list of str
            The input text for the pipeline; Should be in same format as the output
            of VISLCG3Pipeline;

        fix_selfrefs : bool
            Optional argument specifying  whether  self-references  in  syntactic 
            dependencies should be fixed;
            Default:True
        
        fix_open_punct : bool
            Optional argument specifying  whether  opening punctuation marks should 
            be made dependents of the following token;
            Default:True
        
        unesc_quotes : bool
            Optional argument specifying  whether double quotes should be unescaped
            in the output, i.e.  converted from '\"' to '"';
            Default:True
        
        rep_spaces : bool
            Optional argument specifying  whether spaces in a multiword token (e.g. 
            'Rio de Janeiro') should be replaced with underscores ('Rio_de_Janeiro');
            Default:False
            
        error_on_unexp : bool
            Optional argument specifying  whether an exception should be raised in 
            case of missing or unexpected analysis line; if not, only prints warnings 
            in case of such lines;
            Default:False

        Example input
        --------------
        "<s>"

        "<Öö>"
                "öö" L0 S com sg nom @SUBJ #1->2
        "<oli>"
                "ole" Li V main indic impf ps3 sg ps af @FMV #2->0
        "<täiesti>"
                "täiesti" L0 D @ADVL #3->4
        "<tuuletu>"
                "tuuletu" L0 A pos sg nom @PRD #4->2
        "<.>"
                "." Z Fst CLB #5->5
        "</s>"


        Example output
        ---------------
        1       Öö      öö      S       S       com|sg|nom      2       @SUBJ   _       _
        2       oli     ole     V       V       main|indic|impf|ps3|sg|ps|af    0       @FMV    _       _
        3       täiesti täiesti D       D       _       4       @ADVL   _       _
        4       tuuletu tuuletu A       A       pos|sg|nom      2       @PRD    _       _
        5       .       .       Z       Z       Fst|CLB 4       xxx     _       _


    '''
    if not isinstance( lines, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    fix_selfrefs   = True
    fix_open_punct = True
    unesc_quotes   = True
    rep_spaces     = False
    error_on_unexp = False
    for argName, argVal in kwargs.items() :
        if argName in ['selfrefs', 'fix_selfrefs'] and argVal in [True, False]:
           fix_selfrefs = argVal
        if argName in ['fix_open_punct'] and argVal in [True, False]:
           fix_open_punct = argVal
        if argName in ['error_on_unexp'] and argVal in [True, False]:
           error_on_unexp = argVal
        if argName in ['unesc_quotes'] and argVal in [True, False]:
           unesc_quotes = argVal
        if argName in ['rep_spaces'] and argVal in [True, False]:
           rep_spaces = argVal
    pat_empty_line    = re.compile('^\s+$')
    pat_token_line    = re.compile('^"<(.+)>"$')
    pat_analysis_line = re.compile('^\s+"(.+)"\s([^"]+)$')
    # 3 types of analyses: 
    pat_ending_pos_form = re.compile('^L\S+\s+\S\s+([^#@]+).+$')
    pat_pos_form        = re.compile('^\S\s+([^#@]+).+$')
    pat_ending_pos      = re.compile('^(L\S+\s+)?\S\s+[#@].+$')
    pat_opening_punct   = re.compile('.+\s(Opr|Oqu|Quo)\s')
    analyses_added = 0
    conll_lines = []
    word_id = 1
    i = 0
    while ( i < len(lines) ):
        line = lines[i]
        # Check, whether it is an analysis line or not
        if not (line.startswith('  ') or line.startswith('\t')):
            # ******  TOKEN
            if len(line)>0 and not (line.startswith('"<s>"') or \
               line.startswith('"</s>"')) and not pat_empty_line.match(line):
               # Convert double quotes back to normal form (if requested)
               if unesc_quotes:
                  line = line.replace( '\\"', '"' )
               # Broken stuff: if previous word was without analysis
               if analyses_added == 0 and word_id > 1:
                  # Missing analysis line
                  if error_on_unexp:
                      raise Exception('(!) Analysis missing at line '+str(i)+': '+\
                                      '\n'+lines[i-1])
                  else:
                      print('(!) Analysis missing at line '+str(i)+': '+\
                            '\n'+lines[i-1], file=sys.stderr)
                  # Add an empty analysis
                  conll_lines[-1] += '\t_'
                  conll_lines[-1] += '\tX'
                  conll_lines[-1] += '\tX'
                  conll_lines[-1] += '\t_'
                  conll_lines[-1] += '\t'+str(word_id-2)
                  conll_lines[-1] += '\txxx'
                  conll_lines[-1] += '\t_'
                  conll_lines[-1] += '\t_'
               # Start of a new token/word
               token_match = pat_token_line.match( line.rstrip() )
               if token_match:
                  word = token_match.group(1)
               else:
                  raise Exception('(!) Unexpected token format: ', line)
               if rep_spaces and re.search('\s', word):
                  # Replace spaces in the token with '_' symbols
                  word = re.sub('\s+', '_', word)
               conll_lines.append( str(word_id) + '\t' + word )
               analyses_added = 0
               word_id += 1
            # End of a sentence
            if line.startswith('"</s>"'):
                conll_lines.append('')
                word_id = 1
        else:
            # ******  ANALYSIS
            # If there is more than one pair of "", we have some kind of
            # inconsistency: try to remove extra quotation marks from the 
            # end of the analysis line ...
            if line.count('"') > 2:
                new_line = []
                q_count = 0
                for j in range( len(line) ):
                    if line[j]=='"' and (j==0 or line[j-1]!='\\'):
                        q_count += 1
                        if q_count < 3:
                            new_line.append(line[j])
                    else:
                        new_line.append(line[j])
                line = ''.join( new_line )
            # Convert double quotes back to normal form (if requested)
            if unesc_quotes:
                line = line.replace( '\\"', '"' )
            analysis_match = pat_analysis_line.match( line )
            # Analysis line; in case of multiple analyses, pick the first one;
            if analysis_match and analyses_added==0:
                lemma = analysis_match.group(1)
                cats  = analysis_match.group(2)
                if cats.startswith('Z '):
                    postag = 'Z'
                else:
                    postag = (cats.split())[1] if len(cats.split())>1 else 'X'
                deprels = re.findall( '(@\S+)', cats )
                deprel  = deprels[0] if deprels else 'xxx'
                heads   = re.findall( '#\d+\s*->\s*(\d+)', cats )
                head    = heads[0] if heads else str(word_id-2)
                m1 = pat_ending_pos_form.match(cats)
                m2 = pat_pos_form.match(cats)
                m3 = pat_ending_pos.match(cats)
                if m1:
                    forms = (m1.group(1)).split()
                elif m2:
                    forms = (m2.group(1)).split()
                elif m3:
                    forms = ['_']  # no form (in case of adpositions and adverbs)
                else:
                    # Unexpected format of analysis line
                    if error_on_unexp:
                        raise Exception('(!) Unexpected format of analysis line: '+line)
                    else:
                        postag = 'X'
                        forms = ['_']
                        print('(!) Unexpected format of analysis line: '+line, file=sys.stderr)
                # If required, fix self-references (in punctuation):
                if fix_selfrefs and int(head) == word_id-1 and word_id-2>0:
                    head = str(word_id-2) # add link to the previous word
                # Fix opening punctuation
                if fix_open_punct and pat_opening_punct.match(line):
                    head = str(word_id)   # add link to the following word
                conll_lines[-1] += '\t'+lemma
                conll_lines[-1] += '\t'+postag
                conll_lines[-1] += '\t'+postag
                conll_lines[-1] += '\t'+('|'.join(forms))
                conll_lines[-1] += '\t'+head
                conll_lines[-1] += '\t'+deprel
                conll_lines[-1] += '\t_'
                conll_lines[-1] += '\t_'
                analyses_added += 1
        i += 1
    return conll_lines

