#
#   ClauseSegmenter analyzes sentences, words and morphological
#  cues, and determines clause boundaries between the words. 
#  As  a  result, words inside  sentences will be grouped into 
#  clauses.
# 

from typing import Union

import json

from estnltk.text import Text, Layer, Span, SpanList

from estnltk.taggers import TaggerOld
from estnltk.taggers.morph_analysis.morf_common import _convert_morph_analysis_span_to_vm_dict
from estnltk.taggers.morph_analysis.morf_common import _is_empty_span

from estnltk.java.javaprocess import JavaProcess
from estnltk.core import JAVARES_PATH


class ClauseSegmenter(TaggerOld):
    description   = 'Tags clause boundaries inside sentences. Uses Java-based clause '+\
                    'segmenter (Osalausestaja) to perform the tagging.'
    layer_name    = 'clauses'
    attributes    = ('clause_type', )
    depends_on    = ['words', 'sentences', 'morph_analysis']
    configuration = None


    def __init__(self, ignore_missing_commas:bool=False):
        """Initializes Java-based ClauseSegmenter.
        
        Parameters
        ----------
        ignore_missing_commas: boolean (default: False)
             Initializes ClauseSegmenter in a mode where the segmenter attempts to 
             guess clause boundaries even if the commas are missing in the input.
             Note that compared to the default mode, this mode may introduce some
             additional errors;
        """
        args = ['-pyvabamorf']
        if ignore_missing_commas:
            args.append('-ins_comma_mis')
        self._java_process = \
            JavaProcess( 'Osalau.jar', jar_path=JAVARES_PATH, args=args )
        # Record configuration
        self.configuration = {'ignore_missing_commas': ignore_missing_commas}


    def tag(self, text: Text, return_layer=False) ->  Union['Text', Layer]:
        """Tags clauses layer.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed. It needs to have
            layers 'words', 'sentences', 'morph_analysis'.

        return_layer: boolean (default: False)
            If True, then the new layer is returned; otherwise 
            the new layer is attached to the Text object, and 
            the Text object is returned;

        Returns
        -------
        Text or Layer
            If return_layer==True, then returns the new layer, 
            otherwise attaches the new layer to the Text object 
            and returns the Text object;
        """
        clause_spanlists = []
        # Iterate over sentences and words, tag clause boundaries
        morph_spans  = text['morph_analysis'].spans
        word_spans   = text['words'].spans
        assert len(morph_spans) == len(word_spans)
        word_span_id = 0
        for sentence in text['sentences'].spans:
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
                result_vm_json   = json.loads( result_vm_str )
                # Sanity check: the number of words in the output must match 
                # the number of words in the input;
                assert len(result_vm_json['words']) == len(sentence_words)
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
                    clause_spans = SpanList()
                    clause_spans.clause_type = \
                        clause_type_index[clause_id]
                    clause_spans.spans = clause_index[clause_id]
                    clause_spanlists.append( clause_spans )
        # Create and populate layer
        layer = Layer(name=self.layer_name, 
                      enveloping ='words', 
                      attributes=self.attributes, 
                      ambiguous=False)
        for clause_spl in clause_spanlists:
            layer.add_span( clause_spl )
        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text


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

