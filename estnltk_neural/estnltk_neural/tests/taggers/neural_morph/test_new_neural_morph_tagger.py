import os
import unittest
from unittest import TestCase

from estnltk import Text
from estnltk.downloader import get_resource_paths
from estnltk.converters import layer_to_dict

from estnltk_neural.common import neural_abs_path
from estnltk_neural.taggers.neural_morph.new_neural_morph.vabamorf_2_neural import neural_model_tags
from estnltk_neural.taggers.neural_morph.new_neural_morph.neural_2_vabamorf import vabamorf_tags
from estnltk_neural.taggers.neural_morph.new_neural_morph.neural_morph_tagger import NeuralMorphTagger
from estnltk_neural.taggers.neural_morph.new_neural_morph.neural_morph_tagger import is_tensorflow_available
from estnltk_neural.taggers.neural_morph.new_neural_morph.general_utils import get_model_path_from_dir


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
        dummy_tagger = NeuralMorphTagger(model=DummyTagger(), bypass_tensorflow_check=True)
        
        text = Text("Ära mine sinna.")
        text.tag_layer(["morph_analysis"])
        dummy_tagger.tag(text)

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


def get_model_dir_from_esnltk_resources( neural_morph_tagger_config=None ):
    # Try to get the resources path for NeuralMorphTagger. If missing, do nothing. It's up for the user to download the missing resources
    resource_name = "neuralmorphdisamb"  # by default, any NeuralMorphTagger's model will do 
    if neural_morph_tagger_config is not None:
        # Or try to get configuration-specific model
        resource_name = NEURAL_MORPH_TAGGER_CONFIG.replace('_','')+'tagger'
    neural_morph_models = get_resource_paths( resource_name, only_latest=False, download_missing=False )
    if len(neural_morph_models) > 0:
        return neural_morph_models[0]
    else:
        return None


tagger = None
# Attempt to get specific neural morph model configuration that user wants to test
NEURAL_MORPH_TAGGER_CONFIG = os.environ.get('NEURAL_MORPH_TAGGER_CONFIG', None)
skip_reason_for_config = ''
skip_reason_download_instruction = 'estnltk.download("neuralmorphtagger")'
if isinstance(NEURAL_MORPH_TAGGER_CONFIG, str):
    # Check for valid value
    if NEURAL_MORPH_TAGGER_CONFIG not in ['softmax_emb_tag_sum', 'softmax_emb_cat_sum', \
                                          'seq2seq_emb_tag_sum', 'seq2seq_emb_cat_sum']:
        raise Exception( ("(!) Unexpected value for environment variable NEURAL_MORPH_TAGGER_CONFIG: {!r}."+\
                          "Must be one of the following: 'softmax_emb_tag_sum', 'softmax_emb_cat_sum', "+\
                          "'seq2seq_emb_tag_sum' or 'seq2seq_emb_cat_sum'.").format( model_dir ) )
    skip_reason_for_config = ' (for configuration {!r})'.format(NEURAL_MORPH_TAGGER_CONFIG)
    skip_reason_download_instruction = 'estnltk.download("{!r}")'.format(NEURAL_MORPH_TAGGER_CONFIG.replace('_','')+'tagger')

skip_reason = ("Could not load neural morph model{}. "+\
               'If the model has not been downloaded yet, please use {} to get the model for testing.').format( \
                             skip_reason_for_config, skip_reason_download_instruction )

model_dir = None
model_module = None
if is_tensorflow_available(): # Only proceed if tensorflow is available
    model_dir = get_model_dir_from_esnltk_resources( NEURAL_MORPH_TAGGER_CONFIG )
    if model_dir is not None:
        if 'softmax_emb_tag_sum' in model_dir:
            import estnltk_neural.taggers.neural_morph.new_neural_morph.softmax_emb_tag_sum as model_module
        elif 'softmax_emb_cat_sum' in model_dir:
            import estnltk_neural.taggers.neural_morph.new_neural_morph.softmax_emb_cat_sum as model_module
        elif 'seq2seq_emb_tag_sum' in model_dir:
            import estnltk_neural.taggers.neural_morph.new_neural_morph.seq2seq_emb_tag_sum as model_module
        elif 'seq2seq_emb_cat_sum' in model_dir:
            import estnltk_neural.taggers.neural_morph.new_neural_morph.seq2seq_emb_cat_sum as model_module
        else:
            raise Exception( ("(!) Unexpected NeuralMorphTagger's model path {!r}. Must contain string "+\
                              "'softmax_emb_tag_sum', 'softmax_emb_cat_sum', 'seq2seq_emb_tag_sum' or "+\
                              "'seq2seq_emb_cat_sum'.").format(model_dir) )
    if model_module is not None and model_dir is not None:
        tagger = NeuralMorphTagger(model_module=model_module, model_dir=model_dir)
else:
    skip_reason = "Tensorflow is not installed. You'll need tensorflow <= 1.15.5 for running this test."

@unittest.skipIf(tagger is None, skip_reason)
class TestNeuralModel(TestCase):
    def test(self):
        model = tagger.model
        sentences = get_test_sentences(neural_abs_path("tests/taggers/neural_morph/neural_test_sentences.txt"))
        word_count = 0
        correct_count = 0
        
        for words, tags, analyses in sentences:
            word_count += len(words)
            
            preds = model.predict(words, analyses)
            for tag, prediction in zip(tags, preds):
                if tag == prediction:
                    correct_count += 1
                    
        self.assertTrue(correct_count/word_count >= 0.97)


@unittest.skipIf(tagger is None, skip_reason)
class TestNeuralTagger(TestCase):
    def test(self):
        sentences = get_test_sentences(neural_abs_path("tests/taggers/neural_morph/neural_test_sentences.txt"))
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


@unittest.skipIf(tagger is None or model_module is None or model_dir is None, skip_reason)
class TestNeuralRetagger(TestCase):

    def test(self):
        # Smoke test that NeuralMorphTagger can also be used as a Retagger
        tagger.reset()
        retagger = NeuralMorphTagger(output_layer='morph_analysis', 
                                     model_module=model_module, 
                                     model_dir=model_dir)
        text = Text('Nad on läinud. Aga kadunud poeg on tagasi.').tag_layer('morph_analysis')
        retagger.retag(text)

        expected_morph_layer_dict = \
            {'ambiguous': True,
             'attributes': ('normalized_text',
                            'lemma',
                            'root',
                            'root_tokens',
                            'ending',
                            'clitic',
                            'form',
                            'partofspeech'),
             'enveloping': None,
             'meta': {},
             'name': 'morph_analysis',
             'parent': 'words',
             'secondary_attributes': (),
             'serialisation_module': None,
             'spans': [{'annotations': [{'clitic': '',
                                         'ending': 'd',
                                         'form': 'pl n',
                                         'lemma': 'tema',
                                         'normalized_text': 'Nad',
                                         'partofspeech': 'P',
                                         'root': 'tema',
                                         'root_tokens': ['tema']}],
                        'base_span': (0, 3)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'vad',
                                         'lemma': 'olema',
                                         'normalized_text': 'on',
                                         'partofspeech': 'V',
                                         'root': 'ole',
                                         'root_tokens': ['ole']}],
                        'base_span': (4, 6)},
                       {'annotations': [{'clitic': '',
                                         'ending': 'nud',
                                         'form': 'nud',
                                         'lemma': 'minema',
                                         'normalized_text': 'läinud',
                                         'partofspeech': 'V',
                                         'root': 'mine',
                                         'root_tokens': ['mine']}],
                        'base_span': (7, 13)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '.',
                                         'normalized_text': '.',
                                         'partofspeech': 'Z',
                                         'root': '.',
                                         'root_tokens': ['.']}],
                        'base_span': (13, 14)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': '',
                                         'lemma': 'aga',
                                         'normalized_text': 'Aga',
                                         'partofspeech': 'J',
                                         'root': 'aga',
                                         'root_tokens': ['aga']}],
                        'base_span': (15, 18)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': '',
                                         'lemma': 'kadunud',
                                         'normalized_text': 'kadunud',
                                         'partofspeech': 'A',
                                         'root': 'kadunud',
                                         'root_tokens': ['kadunud']}],
                        'base_span': (19, 26)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'sg n',
                                         'lemma': 'poeg',
                                         'normalized_text': 'poeg',
                                         'partofspeech': 'S',
                                         'root': 'poeg',
                                         'root_tokens': ['poeg']}],
                        'base_span': (27, 31)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': 'b',
                                         'lemma': 'olema',
                                         'normalized_text': 'on',
                                         'partofspeech': 'V',
                                         'root': 'ole',
                                         'root_tokens': ['ole']}],
                        'base_span': (32, 34)},
                       {'annotations': [{'clitic': '',
                                         'ending': '0',
                                         'form': '',
                                         'lemma': 'tagasi',
                                         'normalized_text': 'tagasi',
                                         'partofspeech': 'D',
                                         'root': 'tagasi',
                                         'root_tokens': ['tagasi']}],
                        'base_span': (35, 41)},
                       {'annotations': [{'clitic': '',
                                         'ending': '',
                                         'form': '',
                                         'lemma': '.',
                                         'normalized_text': '.',
                                         'partofspeech': 'Z',
                                         'root': '.',
                                         'root_tokens': ['.']}],
                        'base_span': (41, 42)}]}
        assert layer_to_dict(text['morph_analysis']) == expected_morph_layer_dict
