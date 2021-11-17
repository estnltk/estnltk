#
#    An experimental noun phrase chunker that detects Estonian 
#   noun phrases based on the output of dependency syntactic 
#   parser. 
#
#   Note: This is simply a wrapper around the NP chunker 
#   source from EstNLTK v1.4. Because of that, it includes 
#   some processing overhead as it needs to convert v1.6 
#   data to the version 1.4 data structures (and back).
#

# Interface of the version 1.6
from estnltk import Text, Layer

from estnltk.taggers import Tagger

# Converting morphological analysis structures from v1.6 to v1.4.1
from estnltk.taggers.standard.morph_analysis.morf_common import _convert_morph_analysis_span_to_vm_dict
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation

# NP chunker functionality from the version 1.4.1
from estnltk.taggers.miscellaneous.np_chunker_v1_4_1 import NounPhraseChunkerV1_4
# Constants
from estnltk.taggers.miscellaneous.np_chunker_v1_4_1 import PARSER_OUT, SENT_ID
from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.vcd_common_names import WORDS


class NounPhraseChunker( Tagger ):
    """Tags noun phrase chunks in sentences. ( v1.4.1, experimental )
       Note: this is simply a wrapper around v1.4 noun phrase 
       chunker.  Because  of  that, it includes some processing 
       overhead due to converting v1.6 data to the version 1.4 
       data structures (and back).
    """
    output_layer      = 'np_chunks'
    output_attributes = ()
    input_layers      = ['words', 'sentences', 'morph_analysis']
    conf_param = [ 'syntax_layer',
                   # Chunker's arguments from the version 1.4.1:
                   'cutPhrases',
                   'cutMaxThreshold',
                   # Names of specific input layers:
                   '_input_words_layer',
                   '_input_sentences_layer',
                   '_input_morph_analysis_layer',
                   # Inner parameters:
                   '_np_chunker'
                 ]

    def __init__( self,
                  syntax_layer:str,
                  output_layer:str='np_chunks',
                  input_words_layer:str='words',
                  input_sentences_layer:str='sentences',
                  input_morph_analysis_layer:str='morph_analysis',
                  cutPhrases:bool=True,
                  cutMaxThreshold:int=3,
                  np_chunker:NounPhraseChunkerV1_4=None):
        """Initializes NounPhraseChunker.
        
        Parameters
        ----------
        syntax_layer: str
            Name of the layer containing dependency syntactic analyses.
            The layer must contain attributes 'head' and 'deprel'.
        output_layer: str (default: 'np_chunks')
            Name for the noun phrase chunks layer;
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        input_morph_analysis_layer: str (default: 'morph_analysis')
            Name of the input morph_analysis layer;
        cutPhrases: boolean (default: True)
            If True, all phrases exceeding the cutMaxThreshold will be 
            cut into single word phrases, consisting only of part-of-
            speech categories 'S', 'Y', 'H';
            (default: True)
        cutMaxThreshold: int (default:3)
            Threshold indicating the maximum number of words allowed 
            in a phrase.
            If cutPhrases is set, all phrases exceeding the threshold 
            will be cut into single word phrases, consisting only of 
            part-of-speech categories 'S', 'Y', 'H';
            Automatic analysis of the Balanced Corpus of Estonian 
            (with EstNLTK v1.4) suggests that 97% of all NP chunks are 
            likely chunks of length 1-3, thus the default threshold is 
            set to 3;
         np_chunker: NounPhraseChunkerV1_4 (default: None)
            Overrides the default NP chunker with the given 
            NounPhraseChunkerV1_4 instance. 
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self.syntax_layer = syntax_layer
        self._input_words_layer          = input_words_layer
        self._input_sentences_layer      = input_sentences_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [ input_words_layer, input_sentences_layer, \
                              input_morph_analysis_layer, syntax_layer ]
        # Configuration
        self.cutPhrases = cutPhrases
        self.cutMaxThreshold = cutMaxThreshold
        # Initialize v1.4.1 NP chunker
        if np_chunker is None:
            self._np_chunker = NounPhraseChunkerV1_4()
        else:
            # Use a custom NounPhraseChunker
            assert isinstance(np_chunker, NounPhraseChunkerV1_4), \
                '(!) np_chunker should be an instance of NounPhraseChunkerV1_4!'
            self._np_chunker = np_chunker

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     enveloping=self._input_words_layer,
                     text_object=None,
                     attributes=self.output_attributes,
                     ambiguous=False)

    def _make_layer(self, text, layers, status: dict):
        """Tags noun phrase chunks layer.
        
        Parameters
        ----------
        text: Text
           Text in which NP chunks will be tagged;
          
        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           the words, sentences, morph_analysis and syntax 
           layers.
          
        status: dict
           This can be used to store metadata on layer tagging.

        """
        layer = self._make_layer_template()
        layer.text_object = text

        word_spans   = layers[ self._input_words_layer ]
        morph_spans  = layers[ self._input_morph_analysis_layer ]
        syntax_spans = layers[ self.syntax_layer ]
        # Check syntactic analysis layer's attributes
        assert 'head' in syntax_spans.attributes, \
            "(!) syntax_layer {!r} is missing the attribute 'head'!".format( self.syntax_layer )
        assert 'deprel' in syntax_spans.attributes, \
            "(!) syntax_layer {!r} is missing the attribute 'deprel'!".format( self.syntax_layer )
        # Check span_list lengths
        assert len(morph_spans) == len(word_spans)
        assert len(morph_spans) == len(syntax_spans)
        # Process input sentence-by-sentence:
        # *) convert input to v1.4.1 data format;
        # *) NP chunks with NounPhraseChunker from v1.4.1;
        # *) convert output back to v1.6 data format;
        word_span_id = 0
        for sid, sentence in enumerate(layers[ self._input_sentences_layer ]):
            sent_start = sentence.start
            sent_end = sentence.end
            # A) Collect all words/morph_analyses/syntactic analyses of the sentence
            #    Assume: len(word_spans) == len(morph_spans)
            #            len(syntax_spans) == len(morph_spans)
            sentence_morph_dicts  = []
            sentence_words        = []
            sentence_word_ids     = []
            sentence_syntax_dicts = []
            while word_span_id < len(word_spans):
                # Get corresponding word span
                word_span  = word_spans[word_span_id]
                if sent_start <= word_span.start and \
                    word_span.end <= sent_end:
                    # Get corresponding morph span
                    morphFound = False
                    if word_span_id < len(morph_spans):
                        morph_span = morph_spans[word_span_id]
                        if word_span.base_span == morph_span.base_span and \
                           len(morph_span.annotations) > 0 and \
                           not _is_empty_annotation(morph_span.annotations[0]):
                            # Convert span to Vabamorf dict
                            word_morph_dict = \
                                    _convert_morph_analysis_span_to_vm_dict(
                                        morph_span )
                            sentence_morph_dicts.append( word_morph_dict )
                            morphFound = True
                    if not morphFound:
                        # No morph found: add an empty Vabamorf dict
                        empty_analysis_dict = {'text': word_span.text,
                                               'analysis': []}
                        sentence_morph_dicts.append( empty_analysis_dict )
                    # Get corresponding syntax span
                    syntaxFound = False
                    if word_span_id < len(syntax_spans):
                        syntax_span = syntax_spans[word_span_id]
                        # Reconstruct syntax representation of v1.4
                        parset_out_combinations = \
                               self._convert_to_v1_4_syntactic_repr(syntax_span)
                        syntax_span_dict = { PARSER_OUT: parset_out_combinations, SENT_ID: sid }
                        sentence_syntax_dicts.append( syntax_span_dict )
                        syntaxFound = True
                    if not syntaxFound:
                        # No syntax found: add a self-pointing relation ( better than nothing )
                        syntax_span_dict = { PARSER_OUT: [['_', len(sentence_words)]], SENT_ID: sid }
                        sentence_syntax_dicts.append( syntax_span_dict )
                    # Collect word spans
                    sentence_words.append( word_span )
                    sentence_word_ids.append( word_span_id )
                if sent_end <= word_span.start:
                    # Break (end of the sentence)
                    break
                word_span_id += 1
        
            # B) Create the v1.4 data structure
            old_sentence_text = { WORDS: sentence_morph_dicts, 'syntax': sentence_syntax_dicts }
            
            # C) Detect noun chunks
            np_chunkings = self._np_chunker.analyze_sentence( old_sentence_text, 'syntax',
                                                              cutPhrases=self.cutPhrases, \
                                                              cutMaxThreshold=self.cutMaxThreshold )

            # D) Format chunks as phrases enveloping around words
            last_phrase = []
            for wid, word in enumerate( sentence_words ):
                word_span = sentence_words[wid]
                label = np_chunkings[wid]
                if label == 'B' and len(last_phrase) > 0:
                    # Finish last phrase, start a new one
                    layer.add_annotation(last_phrase)
                    last_phrase = [word_span]
                elif label == 'B' and len(last_phrase) == 0:
                    # Start a new phrase
                    last_phrase.append(word_span)
                if label == 'O' and len(last_phrase) > 0:
                    # Finish last phrase
                    layer.add_annotation(last_phrase)
                    last_phrase = []
                if label == 'I':
                    # Continue last phrase
                    last_phrase.append(word_span)
            if len(last_phrase) > 0:
                # Finish the very last phrase
                layer.add_annotation(last_phrase)

        # Small sanity check: all words should be exhausted by now 
        assert word_span_id == len(word_spans)

        return layer

    def _convert_to_v1_4_syntactic_repr(self, syntax_span):
        '''Converts head and deprel from v1.6 syntax annotation span to (possibly ambiguous) 
           v1.4 syntactic representation. Returns a list of combinations deprels x heads.'''
        # Homogenize data types ( AmbiguousSpan vs Span )
        heads   = [syntax_span.head] if isinstance(syntax_span.head, int) else list(syntax_span.head)
        deprels = [syntax_span.deprel] if isinstance(syntax_span.deprel, str) else list(syntax_span.deprel)
        # Check types
        if len(deprels) > 0 and all([isinstance(deprel, str) for deprel in deprels]):
            deprels = deprels
        elif len(deprels) > 0 and all([isinstance(deprel, list) for deprel in deprels]):
            # Flatten the list
            deprels = [deprel for sub_deprels in deprels for deprel in sub_deprels]
        elif len(deprels) > 0:
            raise Exception("(!) Unexpected type for 'deprel' attribute in syntax_layer. \n {!r}".format(deprels))
        assert all([isinstance(head, (str, int)) for head in heads]), \
            "(!) Unexpected type for 'head' attribute in syntax_layer: expected numeric strings or integers. \n {!r}".format(heads)
        # Create combinations
        parset_out_combinations = []
        for deprel in deprels:
            for head in heads:
                if isinstance(head, str):
                    assert head.isnumeric(), \
                        "(!) Expected a numeric string for 'head' attribute in syntax_layer. {!r}".format(heads)
                    parset_out_combinations.append( [deprel, int(head)-1] )
                elif isinstance(head, int):
                    parset_out_combinations.append( [deprel, head-1] )
        return parset_out_combinations

