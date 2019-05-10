# Support for parsing EstNLTK texts with Java-based Maltparser (performing dependency-syntactic analysis on texts);
# Based on EstNLTK 1.4 estnltk.syntax.parsers and estnltk.syntax.maltparser_support


from __future__ import unicode_literals, print_function
from estnltk.legacy.names import *

from estnltk.core import PACKAGE_PATH
import os, os.path
import codecs
import tempfile
import subprocess
from estnltk.taggers.syntax.conll_morph_to_str import conll_to_str


MALTPARSER_PATH = os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'java-res', 'maltparser')
MALTPARSER_MODEL = 'model1'
MALTPARSER_JAR = 'maltparser-1.9.0.jar'


class MaltParser(object):
    '''  A wrapper around Java-based MaltParser. Allows to process EstNLTK Text
        objects with Maltparser in order to obtain dependency syntactic relations
        between the words in the sentence.

        Example usage:

            text - EstNLTK Text object with conll_morph layer to be analysed;

            parser = MaltParser()

            # parse text, and return results as list of lines from maltparser's output
            results1 = parser.parse_text( text, return_type = "conll" )
            for line in results1:
                print(line)
    '''

    maltparser_dir = MALTPARSER_PATH
    model_name = MALTPARSER_MODEL
    maltparser_jar = MALTPARSER_JAR

    def __init__(self, **kwargs):
        ''' Initializes MaltParser's wrapper.

            Parameters
            -----------
            maltparser_dir : str
                Directory that contains Maltparser jar file and model file;
                This directory is also used for storing temporary files, so
                writing should be allowed in it;

            model_name : str
                Name of the Maltparser's model;

            maltparser_jar : str
                Name of the Maltparser jar file (e.g. 'maltparser-1.8.jar');
        '''
        for argName, argVal in kwargs.items():
            if argName == 'maltparser_dir':
                self.maltparser_dir = argVal
            elif argName == 'model_name':
                self.model_name = argVal
            elif argName == 'maltparser_jar':
                self.maltparser_jar = argVal
            else:
                raise Exception(' Unsupported argument given: ' + argName)
        if not self.maltparser_dir:
            raise Exception('Missing input argument: MaltParser directory')
        elif not os.path.exists(self.maltparser_dir):
            raise Exception('Invalid MaltParser directory:', self.maltparser_dir)
        elif not self.maltparser_jar:
            raise Exception('Missing input argument: MaltParser jar file name')
        elif not self.model_name:
            raise Exception('Missing input argument: MaltParser model name')

    def parse_text(self, text, **kwargs):
        ''' Parses given text with Maltparser.

            Parameters
            -----------
            text : Text with conll_morph layer
               The input text that should be analysed for dependency relations;

            return_type : string
                Returns Maltparser's results as list of CONLL format strings,
                each element in the list corresponding to one line in
                MaltParser's output;

        '''
        # Obtain CONLL formatted version of the text
        textConllStr = conll_to_str(text)
        # Execute MaltParser and get results as CONLL formatted string
        resultsConllStr = \
            _executeMaltparser(textConllStr, self.maltparser_dir, \
                               self.maltparser_jar, \
                               self.model_name)
        return resultsConllStr


def _executeMaltparser(input_string, maltparser_dir, maltparser_jar, model_name):
    ''' Executes Maltparser on given (CONLL-style) input string, and 
        returns the result. The result is an array of lines from Maltparser's 
        output.
        
        Parameters
        ----------
        input_string: string
              input text in CONLL format;
        maltparser_jar: string
              name of the Maltparser's jar file that should be executed;
        model_name: string
              name of the model that should be used;
        maltparser_dir: string
              the directory containing Maltparser's jar and the model file; 
        
        Few of the ideas were also borrowed from NLTK's MaltParser class,
        see  http://www.nltk.org/_modules/nltk/parse/malt.html   for the reference;
    '''

    temp_input_file = \
        tempfile.NamedTemporaryFile(prefix='malt_in.', mode='w', delete=False)
    temp_input_file.close()
    # We have to open separately here for writing, because Py 2.7 does not support
    # passing parameter   encoding='utf-8'    to the NamedTemporaryFile;
    out_f = codecs.open(temp_input_file.name, mode='w', encoding='utf-8')
    out_f.write(input_string)
    out_f.close()

    temp_output_file = tempfile.NamedTemporaryFile(prefix='malt_out.', mode='w', delete=False)
    temp_output_file.close()

    current_dir = os.getcwd()
    os.chdir(maltparser_dir)
    cmd = ['java', '-jar', os.path.join(maltparser_dir, maltparser_jar), \
           '-c', model_name, \
           '-i', temp_input_file.name, \
           '-o', temp_output_file.name, \
           '-m', 'parse']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait() != 0:
        raise Exception(' Error on running Maltparser: ', p.stderr.read())
    os.chdir(current_dir)

    results = []
    in_f = codecs.open(temp_output_file.name, mode='r', encoding='utf-8')
    for line in in_f:
        results.append(line.rstrip())
    in_f.close()

    if not temp_input_file.closed:
        raise Exception('Temp input file unclosed!')
    if not temp_output_file.closed:
        raise Exception('Temp input file unclosed!')
    if not out_f.closed:
        raise Exception('Output file unclosed!')
    if not in_f.closed:
        raise Exception('Input file unclosed!')
    # TODO: For some reason, the method gives "ResourceWarning: unclosed file"
    # in Python 3.4, although, apparently, all file handles seem to be closed;
    # Nothing seems to be wrong in Python 2.7;

    os.remove(temp_input_file.name)
    os.remove(temp_output_file.name)

    return results
