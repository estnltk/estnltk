#
#  CompoundWordTagger adds compound word/subword boundaries on words. 
#  Uses Vabamorf's stem-based morphological analysis to find compound 
#  word boundaries.
#
#  For instance, 'Kaubahoovi' subwords are ['Kauba', 'hoovi'], 
#  and 'rehepeksumasina' subwords are ['rehe', 'peksu', 'masina']. 
#  In case of simple non-compound words, subwords list will just 
#  contain the word itself, e.g. 'on' subwords are ['on'].
#
#  Not to be confused with CompoundTokenTagger, which does not use 
#  linguistic analysis and does not mark compound word boundaries, 
#  but instead joins tokens with the help of regular expression 
#  patterns.
# 

import json

from estnltk import Layer
from estnltk.taggers import Tagger

from estnltk.taggers.standard.morph_analysis.morf_common import NORMALIZED_TEXT

class CompoundWordTagger(Tagger):
    """Tags compound word/subword boundaries on words. 
       Uses Vabamorf's stem-based morphological analysis to find compound 
       word boundaries.
    """
    output_layer      = 'compound_words'
    output_attributes = (NORMALIZED_TEXT, 'subwords')
    input_layers      = ['words', 'sentences']
    conf_param = ['disambiguate', 
                  'correct_case', 
                  # Names of specific input layers
                  '_input_words_layer',
                  '_input_sentences_layer',
                  # Inner parameters
                  '_vm_tagger', 
                 ]

    def __init__( self,
                  output_layer:str='compound_words',
                  input_words_layer:str='words',
                  input_sentences_layer:str='sentences',
                  disambiguate:bool=True, 
                  correct_case:bool=True):
        """Initializes Java-based ClauseSegmenter.
        
        Parameters
        ----------
        output_layer: str (default: 'compound_words')
            Name for the compound_words layer;

        input_words_layer: str (default: 'words')
            Name of the input words layer;

        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;

        disambiguate: bool (default: True)
            If set, then uses Vabamorf's stem-based morphological analysis 
            along with disambiguation to retrieve compound word boundaries. 
            Otherwise, if disambiguation is switched off, the output layer 
            can be highly ambiguous;

        correct_case: boolean (default: True)
             If set, then maintains upper-lower case distinctions in subwords 
             as they appear in words layer's 'normalized_text' attribute.
             Otherwise, subwords will be converted to lowercase as in the 
             output of the stem-based morphological analysis.
        """
        # Use internal import to avoid circular imports
        from estnltk.taggers.standard.morph_analysis.morf import VabamorfTagger
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer          = input_words_layer
        self._input_sentences_layer      = input_sentences_layer
        self.input_layers = [input_words_layer,
                             input_sentences_layer]
        # Set flags
        self.disambiguate = disambiguate
        self.correct_case = correct_case
        # Initialize VabamorfTagger for stem-based analysis
        self._vm_tagger = VabamorfTagger(output_layer='_stembased_morph',
                                         input_words_layer=input_words_layer,
                                         input_sentences_layer=input_sentences_layer,
                                         input_compound_tokens_layer='_empty_compound_tokens',
                                         disambiguate=disambiguate,
                                         stem=True)

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     parent=self._input_words_layer,
                     text_object=None,
                     attributes=self.output_attributes,
                     ambiguous=True)

    def _make_layer(self, text, layers, status: dict):
        """Tags compound_words layer.
        
        Parameters
        ----------
        raw_text: str
           Text string corresponding to the text which 
           words will be split into compound words;
          
        layers: MutableMapping[str, Layer]
           Layers of the raw_text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           the words and sentences layers.
          
        status: dict
           This can be used to store metadata on layer tagging.

        """
        layer = self._make_layer_template()
        layer.text_object = text
        # Make empty compound tokens layer
        cp_tokens_layer = \
            Layer(name='_empty_compound_tokens', text_object=text,
                       attributes=('type', 'normalized'),
                       ambiguous=True)
        # Create stem-based morph analysis layer
        detached_layers = layers.copy()
        detached_layers[cp_tokens_layer.name] = cp_tokens_layer
        morph_layer = \
            self._vm_tagger.make_layer( \
                text, layers=detached_layers, status=status)
        words_layer = layers[self._input_words_layer]
        assert len(morph_layer) == len(words_layer)
        for wid, word_span in enumerate(words_layer):
            morph_span = morph_layer[wid]
            assert morph_span.base_span == word_span.base_span
            for annotation in morph_span.annotations:
                normalized_text = annotation[NORMALIZED_TEXT]
                root_tokens = annotation['root_tokens']
                ending      = annotation['ending']
                clitic      = annotation['clitic']
                if ending not in ['0', '']:
                    # Add case ending
                    root_tokens[-1] = root_tokens[-1] + ending
                if len(clitic) > 0:
                    # Add clitic
                    root_tokens[-1] = root_tokens[-1] + clitic
                if self.correct_case:
                    # Apply case corrections
                    root_tokens = \
                        CompoundWordTagger._correct_cases(normalized_text, root_tokens)
                new_annotation = { \
                    NORMALIZED_TEXT: normalized_text,
                    'subwords': root_tokens
                }
                layer.add_annotation( word_span.base_span, new_annotation )
        assert len(layer) == len(words_layer)
        return layer


    @staticmethod
    def _correct_cases( normalized_text, root_tokens ):
        '''Corrects cases in root_tokens according to normalized_text.
        '''
        if '-' in normalized_text:
            # Remove hyphens/dashes (which are not in root_tokens)
            normalized_text = normalized_text.replace('-', '')
        new_root_tokens = []
        i = 0; c = 0
        while i < len(root_tokens):
            # Start a new subword
            subword = []
            j = 0
            while j < len(root_tokens[i]):
                rtc = root_tokens[i][j]
                wc = normalized_text[c]
                # Take only chars from normalized text
                subword.append( wc )
                c += 1
                j += 1
            # Finish subword
            new_root_tokens.append( ''.join(subword) )
            assert len(new_root_tokens[-1]) == len(root_tokens[i])
            i += 1
        return new_root_tokens

