from typing import MutableMapping

from estnltk import Text
from estnltk import Layer
from estnltk.web_taggers import BatchProcessingWebTagger

class NeuralMoprhDisambWebTagger( BatchProcessingWebTagger ):
    """
    Tags neural morph disambiguation using EstNLTK NeuralMorphTagger's webservice. 
    Uses softmax emb_cat_sum model.

    Note: this model resolves only Vabamorf's partofspeech and form ambiguities, 
    lemma ambiguities will remain unresolved.

    See also Neural Morphological Tagger's documentation:
    https://github.com/estnltk/estnltk/blob/539ae945aa52df43b94699866a6f43d021807894/tutorials/nlp_pipeline/B_morphology/08_neural_morph_tagger_py37.ipynb
    """

    def __init__(self, url, output_layer='neural_morph_disamb'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('morphtag', 'pos', 'form')
        self.input_layers = ['words', 'sentences', 'morph_analysis']
        self.batch_layer            = self.input_layers[0]
        self.batch_layer_max_size   = 125
        self.batch_enveloping_layer = self.input_layers[1]


