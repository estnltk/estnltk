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
                 morph_layer="morph_analysis"):
        self.output_layer = output_layer
        self.input_layers = [sentences_layer, morph_layer, syntax_layer]
        self.output_attributes = ["phrase_type", "root_id", "root"]
        self.decorator = TimeLocDecorator(syntax_layer=syntax_layer,
                                          morph_layer=morph_layer)
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
