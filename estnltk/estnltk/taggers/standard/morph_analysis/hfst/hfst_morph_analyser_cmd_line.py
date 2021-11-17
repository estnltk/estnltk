#
# Hfst morphological analyser for Estonian (based on HFST command line tools)
# This analyser uses a finite-state transducer to look up morphological 
# analyses of the words. The output of the analysis will be ambiguous.
#

from typing import MutableMapping
from collections import defaultdict

import os, os.path
import re

import tempfile
import subprocess
import atexit

from estnltk import Layer, Text
from estnltk.taggers import Tagger

from estnltk_core.converters import as_unicode, as_binary

from estnltk.taggers.standard.morph_analysis.morf_common import _get_word_texts

from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_common import HFST_MODEL_FILE
from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_common import HfstMorphOutputExtractor
from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_common import RawAnalysesHfstMorphOutputExtractor
from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_common import MorphemesLemmasHfstOutputExtractor

# ==================================================================================
#   Helper function
# ==================================================================================

def check_if_hfst_is_in_path( hfst_cmd:str='hfst-lookup' ):
    ''' Checks whether given hfst_cmd is in system's PATH. Returns True, there is 
        a file with given name (hfst_cmd) in the PATH, otherwise returns False;

        The idea borrows from:  http://stackoverflow.com/a/377028
    '''
    if os.getenv("PATH") == None:
        return False
    for path in os.environ["PATH"].split( os.pathsep ):
        path1 = path.strip('"')
        file1 = os.path.join(path1, hfst_cmd)
        if os.path.isfile(file1) or os.path.isfile(file1+'.exe'):
           return True
    return False

# keep track of started hfst processes
_STARTED_HFST_PROCESSES = []

# ==================================================================================
#   Main class
# ==================================================================================

class HfstClMorphAnalyser(Tagger):
    """ Hfst morphological analyser for Estonian (based on HFST command line tools)
        Note: resulting analyses can be ambiguous.
    """
    output_layer='hfst_gt_morph_analysis'
    output_attributes = ()
    conf_param = ['transducer_file',
                  'output_extractor',
                  'use_stream',
                  'remove_guesses',
                  'hfst_cmd',
                  # Internal components:
                  '_input_words_layer',
                  '_flag_cleaner_re',
                  '_hfst_process'
                 ]

    def __init__(self,
                 output_layer:str='hfst_gt_morph_analysis',
                 input_words_layer:str='words',
                 output_format:str='morphemes_lemmas',
                 transducer_file:str=HFST_MODEL_FILE,
                 hfst_cmd:str=None,
                 use_stream:bool=True,
                 remove_guesses:bool=False):
        r"""Initializes HfstClMorphAnalyser class.
        
        Parameters
        ----------
        output_layer: str (default: 'hfst_gt_morph_analysis')
            Name of the created morphological analysis layer. 

        input_words_layer: str (default: 'words')
            Name of the input words layer;
        
        output_format: str (default: 'morphemes_lemmas')
            Specifies how the results of the hfst morphological 
            analysis will be formatted in the layer. Possible 
            options:
            
            * 'raw' -- there will be only two attributes in the
                       layer: 'raw_analysis', which contains 
                       analyses in raw / unparsed format, and 
                       'weight', which contains corresponding 
                       weights (floating point numbers);
            
            * 'morphemes_lemmas' -- the analysis will be split
                       into  morphemes / lemmas,  and   their 
                       corresponding part-of-speech tags  and
                       form listings. In total, each analysis 
                       will have the following attributes:
                          'morphemes_lemmas'
                          'postags'
                          'forms'
                          'is_guessed',
                          'has_clitic',
                          'usage',
                          'weight'
            
        transducer_file: str
            Path to the ('analyser-gt-desc.hfstol') file, from
            which Estonian morphological analyser can be 
            loaded;
            Note: this argument will be overridden by the 
            argument transducer: if the transducer is specified
            (default), then loading it from file will not be 
            attempted;
            ( default file: 
                estnltk\taggers\standard\morph_analysis\hfst\models\analyser-gt-desc.hfstol )
        
        hfst_cmd: str (default: None)
            Name and full path to the 'hfst-lookup' command 
            line tool.
            If not provided (default), then attempts to find 
            the command from system's PATH variable. 
            And if the command is not available from PATH, 
            dies with an exception.
        
        use_stream:bool (default: True)
            If true, then hfst-lookup will be launched as a
            persistent process and its input/output will be 
            communicated via stream. 
            Otherwise, hfst-lookup process will be launched
            only if _make_layer is called and its input/output
            will be communicated via files (which is slow).
        
        remove_guesses:bool (default: False)
            Specifies if guessed analyses need to be removed 
            from the output.
            By default, the guessed analyses will be kept in 
            the output, but this also depends on the transducer.
            ( our default transducer model has the guesser 
              component, so it produces guesses. but you can 
              also compile a model without the component )
        """
        # Set output_extractor
        self.output_extractor   = None
        expected_output_formats = ['raw', 'morphemes_lemmas']
        if output_format:
            if output_format.lower() == 'raw':
                self.output_extractor = \
                     RawAnalysesHfstMorphOutputExtractor()
            elif output_format.lower() == 'morphemes_lemmas':
                self.output_extractor = \
                     MorphemesLemmasHfstOutputExtractor()
        if self.output_extractor is None:
            # Failed to create output_extractor: probably because wrong output_format
            raise ValueError('(!) output_format should be one of the following: {!r}'.format(expected_output_formats))
        assert isinstance(self.output_extractor, HfstMorphOutputExtractor)
        self.output_extractor.set_output_attributes(self)
        
        # Set attributes & configuration
        self.output_layer = output_layer
        self.input_layers = [ input_words_layer ]
        self._input_words_layer = self.input_layers[0]
        self.remove_guesses = remove_guesses
        self.use_stream = use_stream
        
        # Utils: create a flag cleaner
        self._flag_cleaner_re = re.compile('@[PNDRCU][.][^@]*@')

        self.hfst_cmd = None
        # Try to get HFST executable from command line arguments
        if hfst_cmd is not None:
            if not os.path.exists( hfst_cmd ):
                raise Exception( '(!) hfst-lookup executable {!r} does not exist! '.format( hfst_cmd ) )
            self.hfst_cmd = hfst_cmd
        
        # Check for existence of HFST executable in the PATH
        if self.hfst_cmd is None:
           # If the HFST command was not provided, check whether the command is in the PATH
           command = 'hfst-lookup'
           if not check_if_hfst_is_in_path( command ):
              msg = " Could not find HFST executable: "+command+" !\n"+\
                    " Please make sure that HFST binaries are installed in your system and\n"+\
                    " available from system's PATH variable. Alternatively, you can\n"+\
                    " provide the HFST executable command via the input\n"+\
                    " argument 'hfst_cmd'. ";
              raise Exception( msg )
           self.hfst_cmd = command
        
        # Check for transducer_file
        self.transducer_file = None
        if transducer_file:
            if os.path.exists(transducer_file):
                self.transducer_file = transducer_file
            else:
                raise FileNotFoundError('(!) Unable to load transducer_file {!r}'.format(transducer_file))
        else:
            raise Exception("(!) Missing HFST's transducer file. Please specify the argument transducer_file.")

        # Launch hfst process (if streaming will be used)
        self._hfst_process = None
        if self.use_stream:
            # Launch hfst process
            process_cmd = [self.hfst_cmd, '-i', self.transducer_file, 
                                          '-O', 'xerox']
            self._hfst_process = subprocess.Popen(process_cmd, stdin=subprocess.PIPE,
                                                               stdout=subprocess.PIPE, 
                                                               stderr=subprocess.STDOUT)
            #
            # Note: if we use stderr=subprocess.PIPE, the reading from stdout will hang after 
            #       processing a large amount of input. But setting stderr=subprocess.STDOUT 
            #       seems to fix the problem;
            #
            _STARTED_HFST_PROCESSES.append( self._hfst_process )


    def _write_hfst_input_file(self, input_layer ):
        '''Writes content of the words layer into a temporary file, in a format
           suitable for hfst's input.
           Returns object of the temporary file and a mapping from line numbers
           to word id-s.
        '''
        temp_input_file = \
            tempfile.NamedTemporaryFile(prefix='hfst_in.', mode='w', 
                                        encoding='utf-8', delete=False)
        input_mapping = defaultdict( int )
        line_count = 0
        for wid, word in enumerate( input_layer ):
            # Write out analyses for all normalized variants of the word
            all_raw_analyses = []
            for word_str in _get_word_texts(word):
                temp_input_file.write( word_str.rstrip('\n\r') )
                temp_input_file.write( '\n' )
                input_mapping[line_count] = wid
                line_count += 1
        temp_input_file.close()
        return temp_input_file, input_mapping


    def _read_results_from_hfst_output(self, output_file, line_2_word_map, input_layer, new_layer ):
        ''' Reads xerox format results from hfst's output_file, 
            collects raw analyses and adds them to new_layer (which 
            parent is input_layer), using the mapping 
            line_2_word_map.
            
            An example of the expected xerox output format:
                Tere    tere+Interj     7,000000
                Tere    tere+N+Sg+Nom   7,000000
                Tere    tere+N+Sg+Gen   8,000000

                !       !+CLB   0,000000
            (analysis parts are separated by tabs)
            (words are separated by empty lines)
        '''
        word_ids_used = set()
        with open(output_file, 'r', encoding='utf-8') as in_f:
            # Collect analyses for all normalized variants of each word
            all_raw_analyses = []
            old_line_id = 0
            cur_word_id = -1
            prev_line = ''
            for line in in_f:
                line_clean = line.rstrip()
                if len(line_clean) == 0 and len(prev_line) > 0:
                    # Empty line (== separator between two words)
                    # Get word id corresponding to the next line (if possible)
                    next_word_id = None
                    if old_line_id+1 in line_2_word_map:
                        next_word_id = line_2_word_map[old_line_id+1]
                    
                    if next_word_id is None or cur_word_id != next_word_id:
                        # The next word is either a new word or it 
                        # does not exist (because current word is 
                        # last one): record the current word
                        # Get span of the old word
                        word_ids_used.add( cur_word_id )
                        word = input_layer[ cur_word_id ]
                        # Remove flag diacritics
                        cleaned_analyses = self.filter_flags( '\n'.join(all_raw_analyses) )
                        # Use output_extractor for getting the output
                        self.output_extractor.extract_annotation_and_add_to_layer( \
                            word, cleaned_analyses, new_layer, \
                            remove_guesses = self.remove_guesses )
                        # Empty the buffer
                        all_raw_analyses = []

                    # advance the (old) line counter
                    old_line_id += 1
                elif len(line_clean) > 0:
                    # Content line: reformat it
                    new_line_clean = self._reformat_xerox_output_content_line( line_clean )
                    # Add to raw analyses
                    all_raw_analyses.append( new_line_clean )
                    # If this is a first content line after an empty line:
                    # get the word id associated with the line
                    if len(prev_line) == 0:
                        cur_word_id = line_2_word_map[old_line_id]
                prev_line = line_clean
            if len(all_raw_analyses) > 0:
                # Empty the buffer 
                # Get span of the old word
                word_ids_used.add( cur_word_id )
                word = input_layer[ cur_word_id ]
                # Remove flag diacritics
                cleaned_analyses = self.filter_flags( '\n'.join(all_raw_analyses) )
                # Use output_extractor for getting the output
                self.output_extractor.extract_annotation_and_add_to_layer( \
                    word, cleaned_analyses, new_layer, \
                    remove_guesses = self.remove_guesses )
        # Small sanity check
        assert len(word_ids_used) == len(input_layer), \
            "(!) Mismatching numbers of words in hfst's input ({}) and output ({})".format(len(input_layer), len(word_ids_used))


    def _reformat_xerox_output_content_line( self, line_clean ):
        '''Applies some reformatting to a hfst CLI output line, so 
           that the output format matches with the output format 
           of hfst python bindings.
           Note: line_clean needs to be a line stripped from ending 
           newline.'''
        # Check the format
        assert line_clean.count('\t') == 2, \
               '(!) Unexpected xerox line format {!r}'.format(line_clean)
        # Remove surface/normalized text from the beginning of line
        line_parts = line_clean.split('\t')[1:]
        # Convert decimal separator from comma to point (if needed)
        if ',' in line_parts[-1]:
            line_parts[-1] = line_parts[-1].replace(',', '.')
        # Reconstruct line (use the same format as in Python's hfst)
        line_clean = '\t'.join( line_parts )
        # Collect analyses
        if line_parts[-1] == 'inf' and line_parts[0].endswith('+?'):
            # In case of an unknown word, record an empty string
            return ''
        else:
            return line_clean


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     parent=self._input_words_layer,
                     text_object=None,
                     ambiguous=True,
                     attributes=self.output_attributes )


    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict = None) -> Layer:
        """Applies HFST-based morphological analyser on the words layer, 
           captures the output of analyser with output_extractor,  and  
           creates a new  hfst_gt_morph_analysis  layer  based  on  the 
           output.
           
           Parameters
           ----------
           text: Text
              Text object to be analysed.
              
           layers: MutableMapping[str, Layer]
              Layers of the text. Contains mappings from the name 
              of the layer to the Layer object.  The  mapping  must 
              contain words layer. 
              The  hfst_gt_morph_analysis  layer will be created.
              
           status: dict
              This can be used to store metadata on layer tagging.
        """
        if not self.use_stream:
            # Use file-based processing (I/O via files)
            return self._make_layer__file_based(text, layers, status)
        else:
            # Stream-based processing (I/O via stream)
            return self._make_layer__stream_based(text, layers, status)


    def _make_layer__stream_based(self, text: Text, layers: MutableMapping[str, Layer], status: dict = None) -> Layer:
        """Process text with HFST-based morphological analyser using
           stream based input/output processing.
        """
        # Check the stream
        assert self._hfst_process is not None, \
           '(!) hfst process stream is not initialized in '+\
           'this tagger.'
        assert self._hfst_process.poll() is None, \
           '(!) The tagger cannot be used anymore, '+\
           'because its hfst process has been terminated.'
        new_layer = self._make_layer_template()
        new_layer.text_object = text
        line_count = 0
        for wid, word in enumerate( layers[ self._input_words_layer ] ):
            # Analyse all normalized variants of the word
            all_raw_analyses = []
            for word_str in _get_word_texts(word):
                try:
                    self._hfst_process.stdin.write(as_binary(word_str.rstrip('\n\r')))
                    self._hfst_process.stdin.write(as_binary('\n'))
                    self._hfst_process.stdin.flush()
                    # Collect all analyses
                    while self._hfst_process.stdout.readable():
                        line = as_unicode( self._hfst_process.stdout.readline() )
                        result = line.rstrip()
                        if len(result) > 0:
                            # Reformat content line
                            line_clean = self._reformat_xerox_output_content_line(result)
                            #print('{!r}'.format(line_clean))
                            all_raw_analyses.append( line_clean )
                        else:
                            break
                except Exception:
                    stderr = as_unicode( self._hfst_process.stderr.read() )
                    print('(!) Streaming exception. Stderr is {!r}'.format(stderr))
                    self.close()
                    raise
            # Clean analyses
            cleaned_analyses = self.filter_flags( '\n'.join(all_raw_analyses) )
            # Use output_extractor for getting the output
            self.output_extractor.extract_annotation_and_add_to_layer( \
                        word, cleaned_analyses, new_layer, \
                        remove_guesses = self.remove_guesses )
        return new_layer
        
        
    def _make_layer__file_based(self, text: Text, layers: MutableMapping[str, Layer], status: dict = None) -> Layer:
        """Process text with HFST-based morphological analyser using
           file based input/output processing (which is slow).
        """
        temp_input_file, line_2_word_map = \
            self._write_hfst_input_file( layers[ self._input_words_layer ] )
        
        temp_output_file = tempfile.NamedTemporaryFile(prefix='hfst_out.', mode='w', delete=False)
        temp_output_file.close()
        
        process_cmd = [self.hfst_cmd, '-i', self.transducer_file, 
                                      '-I', temp_input_file.name, 
                                      '-o', temp_output_file.name,
                                      '-O', 'xerox']
        p = subprocess.Popen(process_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.wait() != 0:
            raise Exception(' Error on running hfst-lookup: ', p.stderr.read())
        
        if not temp_input_file.closed:
            raise Exception('Temp input file unclosed!')
        # Remove temporary input file
        os.remove(temp_input_file.name)
        
        new_layer = self._make_layer_template()
        new_layer.text_object = text
        self._read_results_from_hfst_output( temp_output_file.name, line_2_word_map, 
                                             layers[ self._input_words_layer ],
                                             new_layer )
        
        if not temp_output_file.closed:
            raise Exception('Temp output file unclosed!')
        # Remove temporary output file
        os.remove(temp_output_file.name)

        return new_layer


    def lookup(self, input_word:str):
        """ Analyses a singe word with the transducer. Note: this functionality 
            is not available for command line based HFST analyser. 
            Instead of analysing words one by one via lookup, please analyse texts 
            as a whole via make_layer.
        """
        raise NotImplementedError("Single-word lookup functionality is not available for command line based HFST analyser.")


    def filter_flags(self, o_str):
        """ Cleans the output string of the transducer from flag diacritics.
        """
        return self._flag_cleaner_re.sub('', o_str)


    def close(self):
        """ Terminates streaming HFST process. """
        if self._hfst_process is not None: # if the process was initialized
            # The proper way to terminate the process:
            # 1) Send out the terminate signal
            self._hfst_process.terminate()
            # 2) Interact with the process. Read data from stdout and stderr, 
            #    until end-of-file is reached. Wait for process to terminate.
            self._hfst_process.communicate()
            # 3) Assert that the process terminated
            assert self._hfst_process.poll() is not None
        return False



# ==============================================================================
#   Clean-up : terminate all started hfst processes
# ==============================================================================

@atexit.register
def _close_hfst_processes():
    for process in _STARTED_HFST_PROCESSES:
        if process is not None: # if the process was initialized ...
            if process.poll() is None: # ... and it is still up and running ...
                # The proper way to terminate the process:
                # 1) Send out the terminate signal
                process.terminate()
                # 2) Interact with the process. Read data from stdout and stderr, 
                #    until end-of-file is reached. Wait for process to terminate.
                process.communicate()
                # 3) Assert that the process terminated
                assert process.poll() is not None

