import os
import unittest
from importlib.util import find_spec
from unittest import TestCase

from packaging.version import Version, parse

from estnltk import Text
from estnltk_neural.taggers.neural_morph.old_neural_morph.data_utils import ConfigHolder
from estnltk_neural.taggers.neural_morph.old_neural_morph.general_utils import load_config_from_file

def check_if_tensorflow_is_available():
    # 1) Check if tensorflow is available
    tensorflow_available = find_spec("tensorflow") is not None
    if tensorflow_available:
        # 2) Check that tensorflow has version < 2.x.x
        # (needs to have module tensorflow.contrib, 
        #  which is not present in tf version 2)
        import tensorflow
        correct_version = parse(tensorflow.__version__) <  Version("2.0")
        return correct_version
    return tensorflow_available

NEURAL_MORPH_TAGGER_CONFIG = os.environ.get('NEURAL_MORPH_TAGGER_CONFIG')

skip_reason = "Environment variable NEURAL_MORPH_TAGGER_CONFIG is not defined."


class DummyTagger:
    def predict(self, snt_words, snt_analyses):
        tags = []
        for word, analyses in zip(snt_words, snt_analyses):
            assert len(analyses) > 0
            tag = analyses[0]
            tags.append(tag)
        return tags


@unittest.skipIf( not check_if_tensorflow_is_available(), "package tensorflow < 2.0.0 is required for this test")
class TestDummyTagger(TestCase):
    def test(self):
        from estnltk_neural.taggers.neural_morph.old_neural_morph.neural_morph_tagger import NeuralMorphTagger
        dummy_tagger = DummyTagger()
        tagger = NeuralMorphTagger(base_tagger=dummy_tagger)
        text = Text("Ära mine sinna.")
        text.tag_layer(["morph_analysis"])
        tagger.tag(text)

        for morph, morf_pred in zip(text.morph_analysis, text['neural_morph_analysis']):
            morf_true = "{} {}".format(morph.partofspeech[0], morph.form[0]).rstrip()
            self.assertEqual(morf_pred.morphtag, morf_true)


def str2input(text):
    words, tags, analyses = [], [], []
    for ln in text.strip().split("\n"):
        items = ln.strip().split("\t")
        word, tag, word_analyses = items[0], items[1], items[2:]
        words.append(word)
        tags.append(tag)
        analyses.append(word_analyses)
    return words, tags, analyses


test_sentence_1 = """
Kõik	_P_|pl|nom	P pl n	P sg n
riigid	_S_|com|pl|nom	S pl n
ei	_V_|aux|neg	V neg
täida	_V_|main|indic|pres|ps|neg	V o
kvalifikatsiooninorme	_S_|com|pl|part	S pl p
"""


@unittest.skipIf(NEURAL_MORPH_TAGGER_CONFIG is None, skip_reason)
@unittest.skipIf( not check_if_tensorflow_is_available(), "package tensorflow < 2.0.0 is required for this test")
@unittest.skip("legacy neural morph, tests are broken")
class TestNeuralModel(TestCase):
    def setUp(self):
        from estnltk_core.neural_morph import Model
        config = load_config_from_file(NEURAL_MORPH_TAGGER_CONFIG)
        model = Model(ConfigHolder(config))
        model.build()
        model.restore_session(config.dir_model)
        self.model = model

    def tearDown(self):
        self.model.reset()

    def test(self):
        """
        Sanity check: ensure that the model performs as expected on simple test cases.
        """
        words, tags, analyses = str2input(test_sentence_1)
        pred = self.model.predict(words, analyses)
        self.assertEqual(tags, pred)


@unittest.skipIf(NEURAL_MORPH_TAGGER_CONFIG is None, skip_reason)
@unittest.skipIf( not check_if_tensorflow_is_available(), "package tensorflow < 2.0.0 is required for this test")
@unittest.skip("legacy neural morph, tests are broken")
class TestNeuralTagger(TestCase):
    def setUp(self):
        from estnltk_neural.taggers.neural_morph.old_neural_morph.neural_morph_tagger import NeuralMorphTagger
        self.tagger = NeuralMorphTagger()

    def tearDown(self):
        self.tagger.base_tagger.reset()

    def test(self):
        words, tags, analyses = str2input(test_sentence_1)
        text = Text(" ".join(words))

        text.tag_layer(["morph_analysis"])
        self.tagger.tag(text)

        self.assertTrue(self.tagger.output_layer in text.layers)
        self.assertTrue(hasattr(text.words[0], 'morphtag'))

        for word, tag in zip(text.words, tags):
            self.assertEqual(word.morphtag, tag)
