import os
import unittest
from unittest import TestCase

from estnltk import Text
from estnltk.common import abs_path
from estnltk_neural.taggers.neural_morph.new_neural_morph.vabamorf_2_neural import neural_model_tags
from estnltk_neural.taggers.neural_morph.new_neural_morph.neural_2_vabamorf import vabamorf_tags
from estnltk_neural.taggers.neural_morph.new_neural_morph.neural_morph_tagger import NeuralMorphTagger

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
        tagger = NeuralMorphTagger(model=DummyTagger())
        
        text = Text("Ära mine sinna.")
        text.tag_layer(["morph_analysis"])
        tagger.tag(text)

        for word, morf_pred in zip(text.words, text.neural_morph_analysis):
            morf_true = neural_model_tags(word.text, word.morph_analysis['partofspeech'][0], word.morph_analysis['form'][0])[0]
            self.assertEqual(morf_pred.morphtag, morf_true)


class TestNeural2VabamorfPostfixes(TestCase):
    def test(self):
        # Test postfixes applied to neural -> vabamorf tag conversion
        assert vabamorf_tags('POS=S|NOUN_TYPE=prop|NUMBER=sg|CASE=nom') == ('H', 'sg n')
        assert vabamorf_tags('POS=A|DEGREE=pos|NUMBER=sg|CASE=adit')    == ('A', 'adt')


def get_test_sentences(filename):
    file = open(filename, 'r', encoding='utf-8')
    words, tags, analyses = [], [], []
    line = file.readline()
    
    while line:
        if line.strip() == "":
            yield words, tags, analyses
            words, tags, analyses = [], [], []
        else:
            items = line.strip().split("\t")
            word, tag, word_analyses = items[0], items[1], items[2:]
            words.append(word)
            tags.append(tag)
            analyses.append(word_analyses)
            
        line = file.readline()
        
    if len(words) > 0:
        yield words, tags, analyses
    file.close()


if NEURAL_MORPH_TAGGER_CONFIG is not None:
    if "softmax_emb_tag_sum" in NEURAL_MORPH_TAGGER_CONFIG:
        import estnltk_neural.taggers.neural_morph.new_neural_morph.softmax_emb_tag_sum as model_module
    elif "softmax_emb_cat_sum" in NEURAL_MORPH_TAGGER_CONFIG:
        import estnltk_neural.taggers.neural_morph.new_neural_morph.softmax_emb_cat_sum as model_module
    elif "seq2seq_emb_tag_sum" in NEURAL_MORPH_TAGGER_CONFIG:
        import estnltk_neural.taggers.neural_morph.new_neural_morph.seq2seq_emb_tag_sum as model_module
    else:
        import estnltk_neural.taggers.neural_morph.new_neural_morph.seq2seq_emb_cat_sum as model_module
        
    tagger = NeuralMorphTagger(model_module=model_module)


@unittest.skipIf(NEURAL_MORPH_TAGGER_CONFIG is None, skip_reason)
class TestNeuralModel(TestCase):
    def test(self):
        model = tagger.model
        sentences = get_test_sentences(abs_path("tests/test_taggers/neural_test_sentences.txt"))
        word_count = 0
        correct_count = 0
        
        for words, tags, analyses in sentences:
            word_count += len(words)
            
            preds = model.predict(words, analyses)
            for tag, prediction in zip(tags, preds):
                if tag == prediction:
                    correct_count += 1
                    
        self.assertTrue(correct_count/word_count >= 0.97)
                    

@unittest.skipIf(NEURAL_MORPH_TAGGER_CONFIG is None, skip_reason)
class TestNeuralTagger(TestCase):  
    def test(self):
        sentences = get_test_sentences(abs_path("tests/test_taggers/neural_test_sentences.txt"))
        word_count = 0
        correct_count = 0
        
        for words, tags, analyses in sentences:
            text = Text(" ".join(words))
            text.tag_layer(['morph_analysis'])
            tagger.tag(text)
            self.assertTrue(tagger.output_layer in text.layers)
            word_count += len(tags)
            
            for word, tag in zip(text.words, tags):
                if word.neural_morph_analysis['morphtag'] == tag:
                    correct_count += 1
                    
        self.assertTrue(correct_count/word_count >= 0.97)