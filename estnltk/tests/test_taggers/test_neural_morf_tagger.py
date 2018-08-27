import unittest
import os
from unittest import TestCase

from estnltk import Text
from estnltk.taggers.neural_morph.neural_morph_tagger import NeuralMorphTagger
from estnltk.neural_morph.data_utils import ConfigHolder
from estnltk.neural_morph.general_utils import load_config_from_file
from estnltk.neural_morph.model import Model

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


class TestDummyTagger(TestCase):
    def test(self):
        dummy_tagger = DummyTagger()
        tagger = NeuralMorphTagger(base_tagger=dummy_tagger)
        text = Text("Ära mine sinna.")
        text.tag_layer(["morph_analysis"])
        tagger.tag(text)

        for word in text.words:
            morf_pred = word.morphtag
            morf_true = "{} {}".format(word.partofspeech[0], word.form[0]).rstrip()
            self.assertEqual(morf_pred, morf_true)


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
class TestNeuralModel(TestCase):
    def setUp(self):
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
class TestNeuralTagger(TestCase):
    def setUp(self):
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
