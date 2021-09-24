"""Provides Neural morphological tagger.

Neural morphological tagger performs morphological analysis and disambiguation.
Unlike the `VabamorfTagger`, which in some cases outputs ambiguous results,
the neural tagger always returns exactly one analysis per word.

The default model was trained on Morphologically Disambiguated Corpus [1] and
achieves an accuracy of 98.02%. As a side effect, the neural tagger uses a
tag set [2] which is not compatible with the Vabamorf's own.

For more technical details, check the paper [3], where the current model is referred
to as a multiclass (MC).

[1]	Morphologically disambiguated corpus http://www.cl.ut.ee/korpused/morfkorpus/index.php?lang=en
[2]	Morpho-syntactic categories http://www.cl.ut.ee/korpused/morfliides/seletus
[3]	Tkachenko, A. and Sirts, K. (2018, September). Neural Morphological Tagging for Estonian. In BalticHLT.

"""
import os

from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger
from estnltk.neural_morph.old_neural_morph.data_utils import ConfigHolder
from estnltk.neural_morph.old_neural_morph.model import Model
from estnltk.neural_morph.old_neural_morph.general_utils import load_config_from_file

# Environment variable which points to a configuration file
NEURAL_MORPH_TAGGER_CONFIG = 'NEURAL_MORPH_TAGGER_CONFIG'

MORPH_ATTRIBUTES = ('morphtag',)


class NeuralMorphTagger(Tagger):
    """Neural morphological tagger.

    """
    conf_param = ("base_tagger",)
    input_layers = ("morph_analysis",)
    output_layer = "neural_morph_analysis"
    output_attributes = MORPH_ATTRIBUTES

    def __init__(self,
                 output_layer: str = 'neural_morph_analysis',
                 base_tagger: object = None):
        """
        Initialises a new NeuralMorphTagger instance.

        :param output_layer: str
            The name of the new layer.
        :param base_tagger: object
            Base tagger instance. Used only in unit tests.
        """
        self.output_layer = output_layer
        if base_tagger is not None:
            self.base_tagger = base_tagger
        else:
            # get configuration file
            if NEURAL_MORPH_TAGGER_CONFIG not in os.environ:
                raise RuntimeError("Environment variable NEURAL_MORPH_TAGGER_CONFIG not set.")
            config_file = os.environ[NEURAL_MORPH_TAGGER_CONFIG]
            if not os.path.exists(config_file):
                raise ValueError(
                    "Configuration file '%s' specified by the env variable NEURAL_MORPH_TAGGER_CONFIG not found." % config_file)
            config = load_config_from_file(config_file)
            # load model
            tagger = Model(ConfigHolder(config))
            tagger.build()
            tagger.restore_session(config.dir_model)
            self.base_tagger = tagger

    def _make_layer(self, text, layers, status=None):
        layer = Layer(name=self.output_layer,
                      text_object=text,
                      parent='morph_analysis',
                      ambiguous=False,
                      attributes=MORPH_ATTRIBUTES)
        analysed_words = layers['morph_analysis']
        word_idx = 0
        for sentence in layers["sentences"]:
            snt_words, snt_analyses = [], []
            for word in sentence:
                word_analysis = analysed_words[word_idx]
                assert word_analysis.text == word.text
                analyses = [("%s %s" % (pos, form)).rstrip()
                            for pos, form in zip(word_analysis.partofspeech, word_analysis.form)]
                snt_words.append(word_analysis.text)
                snt_analyses.append(analyses)
                word_idx += 1

            snt_tags = self.base_tagger.predict(snt_words, snt_analyses)

            for word, tag in zip(sentence.words, snt_tags):
                layer.add_annotation(word, morphtag=tag)

        return layer
