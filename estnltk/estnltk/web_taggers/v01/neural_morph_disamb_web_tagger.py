from typing import MutableMapping

from estnltk import Text
from estnltk import Layer
from estnltk import Retagger
from estnltk.web_taggers import BatchProcessingWebTagger

class NeuralMoprhDisambWebTagger( BatchProcessingWebTagger, Retagger ):
    """
    Tags neural morph disambiguation using EstNLTK NeuralMorphTagger's webservice. 
    Uses softmax emb_cat_sum model.

    Note: this model resolves only Vabamorf's partofspeech and form ambiguities, 
    lemma ambiguities will remain unresolved.

    See also Neural Morphological Tagger's documentation:
    https://github.com/estnltk/estnltk/blob/539ae945aa52df43b94699866a6f43d021807894/tutorials/nlp_pipeline/B_morphology/08_neural_morph_tagger_py37.ipynb
    """

    def __init__(self, url, output_layer='neural_morph_disamb',
                            input_words_layer='words',
                            input_sentences_layer='sentences',
                            input_morph_analysis_layer='morph_analysis'):
        self.url = url
        self.output_layer = output_layer
        self.input_layers = [input_words_layer, 
                             input_sentences_layer, 
                             input_morph_analysis_layer]
        self.output_attributes = ('morphtag', 'pos', 'form')
        self.batch_layer            = self.input_layers[0]
        self.batch_layer_max_size   = 125
        self.batch_enveloping_layer = self.input_layers[1]

    def _change_layer(self, text, layers, status):
        if self.output_layer != self.input_layers[2]:
            raise Exception( ('(!) Mismatching output_layer and input_morph_analysis_layer {!r} != {!r}. '+\
                             'Cannot use as a retagger.').format(self.output_layer, self.input_layers[2]) )
        disamb_layer = self._make_layer(text, layers, status)
        morph_layer = layers[self.output_layer]
        assert len(morph_layer) == len(disamb_layer)
        for original_word, disamb_word in zip(morph_layer, disamb_layer):
            disamb_pos  = disamb_word.annotations[0]['pos']
            disamb_form = disamb_word.annotations[0]['form']
            # Filter annotations of the original morph layer: keep only those
            # annotations that are matching with the disambiguated annotation
            # (note: there can be multiple suitable annotations due to lemma 
            #  ambiguities)
            keep_annotations = []
            for annotation in original_word.annotations:
                if annotation['partofspeech'] == disamb_pos and annotation['form'] == disamb_form:
                    keep_annotations.append(annotation)
            if len(keep_annotations) > 0:
                # Only disambiguate if there is at least one annotation left
                # (can't leave a word without any annotations)
                original_word.clear_annotations()
                for annotation in keep_annotations:
                    original_word.add_annotation( annotation )

