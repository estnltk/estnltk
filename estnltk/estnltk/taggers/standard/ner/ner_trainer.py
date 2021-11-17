import os.path

from estnltk.common import DEFAULT_PY3_NER_MODEL_DIR
from estnltk.taggers.standard.ner.fex import FeatureExtractor
from estnltk.taggers.standard.ner import CrfsuiteTrainer
from estnltk.taggers.standard.ner.model_storage_util import ModelStorageUtil
from estnltk import Text


class NerTrainer(object):
    """The class for training NER models. Uses crfsuite implementation."""

    def __init__(self, nersettings, morph_layer_input='morph_analysis', words_layer_input='words', sentences_layer_input='sentences'):
        """Initialize a new NerTrainer.

        Parameters
        ----------
        nersettings: module
            NER settings module.
        """
        self.settings = nersettings
        self.input_layers = (morph_layer_input, words_layer_input, sentences_layer_input)
        self.fex = FeatureExtractor(nersettings, self.input_layers)
        self.trainer = CrfsuiteTrainer(algorithm=nersettings.CRFSUITE_ALGORITHM,
                                       c2=nersettings.CRFSUITE_C2,
                                       input_sentences_layer=sentences_layer_input)

    def train(self, texts, labels=None, layer='wordner', model_dir='ner_model'):
        """ Train a NER model using given documents.

        Each word in the documents must have a "label" attribute, which
        denote the named entities in the documents.

        Parameters
        ----------
        texts: list of EstNLTK Text objects
            The texts are used for training the CRF model.
        labels: list of lists or None
            List of correct labels for each sentence and word
            The list has to be of the same size as the sentences layer of the text
            and the list corresponding to the sentence has to be of the same size as the number of spans in that sentence.
            If None, values are taken directly from the text objects
        layer: str
            Name of the NER layer.
            If labels aren't provided, the layer with the provided name is taken directly
            from the text objects and values obtained from said layer are used for training.
        model_dir: str
            A directory where the model will be saved.
        """
        if os.path.exists(model_dir):
            assert not os.path.samefile(model_dir, DEFAULT_PY3_NER_MODEL_DIR), \
                       '(!) Error: Do not overwrite the default NER model.'
        modelUtil = ModelStorageUtil(model_dir)
        modelUtil.makedir()
        modelUtil.copy_settings(self.settings)

        sentences_layer_name = self.input_layers[2]
        
        if isinstance(texts, Text):
            texts = [texts]

        if labels is None:
            labels_list = []
            for i, t in enumerate(texts):
                if layer not in t.layers:
                    raise Exception("Error in text {}: missing NER layer {!r}.".format(i, layer))
                if t[layer].ambiguous:
                    raise Exception("Error in text {}: expected unambiguous NER layer, but found ambiguous NER layer instead.".format(i))
                text_labels = []
                cur = 0
                for snt in texts[i][sentences_layer_name]:
                    text_labels.append(list(t[layer].nertag[cur:len(snt)+cur]))
                    cur += len(snt)
                labels_list.append(text_labels)

            labels = labels_list

        if len(texts) != len(labels):
            raise Exception("Number of text objects isn't equal to number of NER-layers.")

        for i, text in enumerate(texts):
            sentences = text[sentences_layer_name]
            if len(sentences) != len(labels[i]):
                raise Exception("Number of sentences in text {} doesn't match number of sentences in NER-layer {}.".format(i, i))
            for idx, sentence in enumerate(sentences):
                if len(sentence) != len(labels[i][idx]):
                    raise Exception("Length of sentence {} in text {} doesn't match length of labels {} in NER-layer {}.".format(idx, i, idx, i))

        self.fex.process(texts)

        self.trainer.train(texts, labels, modelUtil.model_filename)
