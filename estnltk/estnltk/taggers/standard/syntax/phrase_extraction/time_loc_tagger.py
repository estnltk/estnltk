#
#   Based on the source from:
#      https://github.com/estnltk/syntax_experiments/tree/ec864a6e20909b56f388d9f675b109310306d8e9/adverbials/estnltk_patches
#
from typing import MutableMapping

from estnltk import Layer, Text
from estnltk.taggers import Tagger

from estnltk.taggers.standard.syntax.phrase_extraction.phrase_extractor import PhraseExtractor
from estnltk.taggers.standard.syntax.phrase_extraction.time_loc_decorator import TimeLocDecorator

class TimeLocTagger(Tagger):
    """Tags time/location OBL phrases based on UD syntax layer."""
    conf_param = ['decorator', 'extractor']

    def __init__(self,
                 output_layer="time_loc_phrases",
                 syntax_layer="stanza_syntax",
                 sentences_layer="sentences",
                 morph_layer="morph_analysis",
                 time_lemmas_path=None, 
                 loc_lemmas_path=None,
                 discard_unclassified=False):
        ''' Initializes this TimeLocTagger.
            
            Parameters
            -----------
            output_layer: str (default: 'time_loc_phrases')
                Name for the time/location phrases layer;
            
            syntax_layer: str (default: 'stanza_syntax')
                Name of the input syntactic analysis layer. 
                This layer is used as a basis for extracting OBL phrases 
                and for determining phrase type. Must be an UD syntax 
                layer. 
            
            sentences_layer: str (default: 'sentences')
                Name of the input sentences layer;
            
            morph_layer: str (default: 'morph_analysis')
                Name of the input morph_analysis layer.
                Must be a morphological analysis layer using 
                Vabamorf's tagset. 
            
            time_lemmas_path: str (default: None)
                Path to a text file containing lemmas of head words of time phrases 
                (each lemma on new line). The file should be in "utf-8" encoding. 
                If path is not provided, then loads the default resource from the 
                path: 'estnltk/taggers/standard/syntax/phrase_extraction/resources/time_lemmas.txt'
            
            loc_lemmas_path: str (default: None)
                Path to a text file containing lemmas of head words of location phrases 
                (each lemma on new line). The file should be in "utf-8" encoding. 
                If path is not provided, then loads the default resource from the 
                path: 'estnltk/taggers/standard/syntax/phrase_extraction/resources/loc_lemmas.txt'
            
            discard_unclassified: bool (default: False)
                If set, then discards unclassified phrases, that is, phrases with phrase_type==None.  
                Otherwise, all OBL phrases will make it to the output layer, even if the tagger could 
                not classify some of them. 
        '''
        self.output_layer = output_layer
        self.input_layers = [sentences_layer, morph_layer, syntax_layer]
        self.output_attributes = ["phrase_type", "root_id", "root"]
        self.decorator = TimeLocDecorator(time_lemmas_path=time_lemmas_path, 
                                          loc_lemmas_path=loc_lemmas_path, 
                                          syntax_layer=syntax_layer, 
                                          morph_layer=morph_layer,
                                          discard_unclassified=discard_unclassified)
        self.extractor = PhraseExtractor(deprel="obl", 
                                         decorator=self.decorator, 
                                         sentences_layer=sentences_layer, 
                                         syntax_layer=syntax_layer, 
                                         output_layer=self.output_layer,
                                         output_attributes=self.output_attributes)

    def _make_layer_template(self):
        return self.extractor._make_layer_template()

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        return self.extractor._make_layer(text, layers, status)
