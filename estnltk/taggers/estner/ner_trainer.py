import os.path

from estnltk.core import DEFAULT_PY3_NER_MODEL_DIR
from estnltk.taggers.estner.fex import FeatureExtractor
from estnltk.taggers.estner import CrfsuiteTrainer
from estnltk.taggers.estner.model_storage_util import ModelStorageUtil
from estnltk import Text


class NerTrainer(object):
    """The class for training NER models. Uses crfsuite implementation."""

    def __init__(self, nersettings, morph_layer_input=('morph_analysis',)):
        """Initialize a new NerTrainer.

        Parameters
        ----------
        nersettings: module
            NER settings module.
        """
        self.settings = nersettings
        self.fex = FeatureExtractor(nersettings,morph_layer_input)
        self.trainer = CrfsuiteTrainer(algorithm=nersettings.CRFSUITE_ALGORITHM,
                                       c2=nersettings.CRFSUITE_C2)

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
        assert not os.path.samefile(model_dir, DEFAULT_PY3_NER_MODEL_DIR), \
                   '(!) Error: Do not overwrite the default NER model.'
        modelUtil = ModelStorageUtil(model_dir)
        modelUtil.makedir()
        modelUtil.copy_settings(self.settings)

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
                for snt in texts[i].sentences:
                    text_labels.append(list(t[layer].nertag[cur:len(snt)+cur]))
                    cur += len(snt)
                labels_list.append(text_labels)

            labels = labels_list

        if len(texts) != len(labels):
            raise Exception("Number of text objects isn't equal to number of NER-layers.")

        for i, text in enumerate(texts):
            sentences = text.sentences
            if len(sentences) != len(labels[i]):
                raise Exception("Number of sentences in text {} doesn't match number of sentences in NER-layer {}.".format(i, i))
            for idx, sentence in enumerate(sentences):
                if len(sentence) != len(labels[i][idx]):
                    raise Exception("Length of sentence {} in text {} doesn't match length of labels {} in NER-layer {}.".format(idx, i, idx, i))

        self.fex.process(texts)

        self.trainer.train(texts, labels, modelUtil.model_filename)
