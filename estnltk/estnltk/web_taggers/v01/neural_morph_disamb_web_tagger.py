from typing import MutableMapping

from estnltk import Text
from estnltk import Layer
from estnltk import Retagger
from estnltk.web_taggers import BatchProcessingWebTagger

class NeuralMorphDisambWebTagger( BatchProcessingWebTagger, Retagger ):
    """
    Performs neural morphological disambiguation using EstNLTK NeuralMorphTagger's webservice. 
    Uses softmax emb_cat_sum model.
    Note: this model resolves only Vabamorf's partofspeech and form ambiguities, 
    lemma ambiguities will remain unresolved.

    NeuralMorphDisambWebTagger can be used either as a tagger or as a retagger: 
    *) if used as a tagger (output_layer != morph_analysis_layer), then 
       tagger.tag(...) / tagger.make_layer(...) methods create a new morph layer 
       with attributes ('morphtag', 'pos', 'form'). Attributes ('pos', 'form') 
       are based on Vabamorf's categories, and can be used to disambiguate the 
       input morph_analysis layer; the attribute 'morphtag' contains model-
       specific morphological features (mixed Vabamorf and UD categories);
    *) if used as a retagger (set output_layer = morph_analysis_layer), then 
       tagger.retag(...) / tagger.change_layer(...) methods disambiguate the 
       input morph_analysis layer; 

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
        self.batch_layer    = self.input_layers[0]
        self.batch_max_size = 125
        self.batch_enveloping_layer = self.input_layers[1]

    def _change_layer(self, text, layers, status):
        # Validate inputs
        if self.output_layer != self.input_layers[2]:
            raise Exception( ('(!) Mismatching output_layer and input_morph_analysis_layer {!r} != {!r}. '+\
                             'Cannot use as a retagger.').format(self.output_layer, self.input_layers[2]) )
        morph_layer = layers[self.output_layer]
        for attr in ['partofspeech', 'form']:
            if attr not in morph_layer.attributes:
                raise Exception( ('(!) Missing attribute {!r} in input_morph_analysis_layer {!r}.'+\
                                  '').format(attr, morph_layer.name) )
        # Create disambiguation layer
        disamb_layer = self._make_layer(text, layers, status)
        # Disambiguate input_morph_analysis_layer
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

