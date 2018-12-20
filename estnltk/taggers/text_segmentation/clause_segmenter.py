#
#   ClauseSegmenter analyzes sentences, words and morphological
#  cues, and determines clause boundaries between the words. 
#  As  a  result, words inside  sentences will be grouped into 
#  clauses.
# 

import json

from estnltk.text import Layer, EnvelopingSpan

from estnltk.taggers import Tagger
from estnltk.taggers.morph_analysis.morf_common import _convert_morph_analysis_span_to_vm_dict
from estnltk.taggers.morph_analysis.morf_common import _is_empty_span

from estnltk.java.javaprocess import JavaProcess
from estnltk.core import JAVARES_PATH


class ClauseSegmenter(Tagger):
    """Tags clause boundaries inside sentences. 
       Uses Java-based clause segmenter (Osalausestaja) to perform the tagging."""
    output_layer      = 'clauses'
    output_attributes = ('clause_type',)
    input_layers      = ['words', 'sentences', 'morph_analysis']
    conf_param = [ 'ignore_missing_commas',
                   # Names of specific input layers
                   '_input_words_layer',
                   '_input_sentences_layer',
                   '_input_morph_analysis_layer',
                   # Inner parameters
                   '_java_process',
                   # For backward compatibility:
                   'depends_on', 'layer_name'
                 ]
    # For backward compatibility:
    layer_name = output_layer
    attributes = output_attributes
    depends_on = input_layers


    def __init__( self,
                  output_layer:str='clauses',
                  input_words_layer:str='words',
                  input_sentences_layer:str='sentences',
                  input_morph_analysis_layer:str='morph_analysis',
                  ignore_missing_commas:bool=False):
        """Initializes Java-based ClauseSegmenter.
        
        Parameters
        ----------
        output_layer: str (default: 'clauses')
            Name for the clauses layer;

        input_words_layer: str (default: 'words')
            Name of the input words layer;

        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;

        input_morph_analysis_layer: str (default: 'morph_analysis')
            Name of the input morph_analysis layer;

        ignore_missing_commas: boolean (default: False)
             Initializes ClauseSegmenter in a mode where the segmenter attempts to 
             guess clause boundaries even if the commas are missing in the input.
             Note that compared to the default mode, this mode may introduce some
             additional errors;
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer          = input_words_layer
        self._input_sentences_layer      = input_sentences_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [ input_words_layer, input_sentences_layer, \
                              input_morph_analysis_layer ]
        self.layer_name = self.output_layer  # <- For backward compatibility ...
        self.depends_on = self.input_layers  # <- For backward compatibility ...
        # Set flag
        self.ignore_missing_commas = ignore_missing_commas
        # Initialize JavaProcess
        args = ['-pyvabamorf']
        if self.ignore_missing_commas:
            args.append('-ins_comma_mis')
        # Initiate Java process
        self._java_process = \
            JavaProcess( 'Osalau.jar', jar_path=JAVARES_PATH, args=args )


    def __enter__(self):
        return self


    def __exit__(self, *args):
        """ Terminates Java process. """
        # The proper way to terminate the process:
        # 1) Send out the terminate signal
        self._java_process._process.terminate()
        # 2) Interact with the process. Read data from stdout and stderr, 
        #    until end-of-file is reached. Wait for process to terminate.
        self._java_process._process.communicate()
        # 3) Assert that the process terminated
        assert self._java_process._process.poll() is not None
        return False


    def close(self):
        if self._java_process._process.poll() is None:
            self.__exit__()


    def _make_layer(self, text, layers, status: dict):
        """Tags clauses layer.
        
        Parameters
        ----------
        raw_text: str
           Text string corresponding to the text which 
           will be split into clauses;
          
        layers: MutableMapping[str, Layer]
           Layers of the raw_text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           the words, sentences and morph_analysis layers.
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        assert self._java_process._process.poll() is None, \
           '(!) This '+str(self.__class__.__name__)+' cannot be used anymore, '+\
           'because its Java process has been terminated.'
        clause_spanlists = []
        # Iterate over sentences and words, tag clause boundaries
        morph_spans  = layers[ self._input_morph_analysis_layer ].span_list
        word_spans   = layers[ self._input_words_layer ].span_list
        assert len(morph_spans) == len(word_spans)
        word_span_id = 0
        for sentence in layers[ self._input_sentences_layer ].span_list:
            #  Collect all words/morph_analyses inside the sentence
            #  Assume: len(word_spans) == len(morph_spans)
            sentence_morph_dicts = []
            sentence_words       = []
            while word_span_id < len(word_spans):
                # Get corresponding word span
                word_span  = word_spans[word_span_id]
                morph_span = None
                if sentence.start <= word_span.start and \
                    word_span.end <= sentence.end:
                    morphFound = False
                    # Get corresponding morph span
                    if word_span_id < len(morph_spans):
                        morph_span = morph_spans[word_span_id]
                        if word_span.start == morph_span.start and \
                           word_span.end == morph_span.end and \
                           len(morph_span) > 0 and \
                           (not _is_empty_span(morph_span[0])):
                            # Convert span to Vabamorf dict
                            word_morph_dict = \
                                    _convert_morph_analysis_span_to_vm_dict( \
                                        morph_span )
                            sentence_morph_dicts.append( word_morph_dict )
                            morphFound = True
                    if not morphFound:
                        # No morph found: add an empty Vabamorf dict
                        empty_analysis_dict = { 'text' : word_span.text, \
                                                'analysis' : [] }
                        sentence_morph_dicts.append( empty_analysis_dict )
                    sentence_words.append( word_span )
                if sentence.end <= word_span.start:
                    # Break (end of the sentence)
                    break
                word_span_id += 1
            if sentence_morph_dicts:
                # Analyse collected sentence with the Java-based Clause Segmenter
                sentence_vm_json = json.dumps({'words': sentence_morph_dicts})
                result_vm_str    = \
                    self._java_process.process_line(sentence_vm_json)
                result_vm_json = json.loads( result_vm_str )
                # Sanity check: 'words' must be present and the number of words in 
                # the output must match the number of words in the input;
                # If not, then we likely have problems with the Java subprocess;
                assert 'words' in result_vm_json, \
                       "(!) Unexpected mismatch between ClauseSegmenter's input and output. "+\
                       "Probably there are problems with the Java subprocess. "
                assert len(result_vm_json['words']) == len(sentence_words), \
                       "(!) Unexpected mismatch between ClauseSegmenter's input and output. "+\
                       "Probably there are problems with the Java subprocess. "
                # Rewrite clause annotations to clause indices
                result_vm_json = \
                    self.annotate_clause_indices( result_vm_json['words'] )
                # Collect words belongs to each specific clause
                # And record clause types
                clause_index      = {}
                clause_type_index = {}
                for word_id, word in enumerate( result_vm_json ):
                    assert 'clause_id' in word
                    if word['clause_id'] not in clause_index:
                        clause_index[word['clause_id']] = []
                    # Get corresponding word span
                    word_span = sentence_words[word_id]
                    # Record the word span & clause type
                    clause_index[word['clause_id']].append( word_span )
                    clause_type_index[word['clause_id']] = \
                        word['clause_type']
                # Rewrite clause index to list of clause SpanList-s
                for clause_id in clause_index.keys():
                    clause_spans = EnvelopingSpan(spans=clause_index[clause_id])
                    clause_spans.clause_type = \
                        clause_type_index[clause_id]
                    #clause_spans.spans = clause_index[clause_id]
                    clause_spanlists.append( clause_spans )
        # Create and populate layer
        layer = Layer(name=self.output_layer, 
                      enveloping=self._input_words_layer,
                      text_object=text,
                      attributes=self.output_attributes, 
                      ambiguous=False)
        for clause_spl in clause_spanlists:
            layer.add_span( clause_spl )
        return layer



    def annotate_clause_indices( self, sentence ):
        """ Rewrites clause boundary markings in given sentence
            to clause indexes and clause types marked to words.
            
            Method is ported from:
             https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/clausesegmenter.py
             ( with slight modifications )
        """
        max_index = 0
        max_depth = 1
        stack_of_indexes = [ max_index ]
        stack_of_types   = [ 'regular' ]
        for token in sentence:
            if 'clauseAnnotation' not in token:
                token['clause_id']   = stack_of_indexes[-1]
                token['clause_type'] = stack_of_types[-1]
            else:
                # Annotations starting clause boundary
                for annotation in token['clauseAnnotation']:
                    if annotation == "KIILU_ALGUS":
                        # Increase depth, start a next embedded clause
                        max_index += 1
                        stack_of_indexes.append(max_index)
                        stack_of_types.append('embedded')
                        if (len(stack_of_indexes) > max_depth):
                            max_depth = len(stack_of_indexes)
                token['clause_id'] = stack_of_indexes[-1]
                token['clause_type'] = stack_of_types[-1]
                # Annotations ending clause boundary
                for annotation in token['clauseAnnotation']:
                    if annotation == "KINDEL_PIIR":
                        # Move on at the same level, start a next clause 
                        max_index += 1
                        stack_of_indexes[-1] = max_index
                    elif annotation == "KIILU_LOPP":
                        # Decrease depth, end the current embedded clause
                        stack_of_indexes.pop()
                        stack_of_types.pop()
        return sentence

