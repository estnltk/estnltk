# -*- coding: utf-8 -*-
"""Defines wrappers over crfsuite package for named entity recognition."""

import pycrfsuite


class Trainer(object):
    """Trains a crfsuite model."""

    def __init__(self, algorithm='l2sgd', c2=0.001, verbose=True, input_sentences_layer='sentences'):
        """Initialize the trainer.

        Parameters
        ----------
        algorithm: str
            Crfsuite training algorithm
        c2: float
            Crfsuite c2 parameter
        verbose: boolean
            Enable Crfsuite trainer verbose output
        """
        self.algorithm = algorithm
        self.c2 = c2
        self.verbose = verbose
        self.input_sentences_layer = input_sentences_layer

    def train(self, texts, correct_labels, mode_filename):
        """Train a CRF model using given Text objects and NER labels.

        Parameters
        ----------

        texts:
            List of EstNLTK text objects used for training.

        correct_labels:
            List of lists of lists of strings.
            Each list in the outermost list corresponds to one Text object.
            Each list in those inner lists corresponds to one sentence in the Text object.
            The strings correspond to NER-tags.

            The length of correct_labels has to be equal to the length of texts. The number of
            lists in each outermost list has to be equal to the number of sentences in the
            corresponding Text object. The number of strings in each innermost list has to be
            equal to the number of words in the corresponding sentence of the corresponding Text.

        mode_filename: str
            The filename where to save the model.

        """

        trainer = pycrfsuite.Trainer(algorithm=self.algorithm, params={'c2': self.c2}, verbose=self.verbose)

        for idx, text in enumerate( texts ):
            for i,snt in enumerate( text[self.input_sentences_layer] ):
                xseq = [t.ner_features.F for t in snt]

                new_xseq = []
                for word in xseq:
                    new_xseq.append(list(word)[0])
                trainer.append(new_xseq, correct_labels[idx][i])

        trainer.train(mode_filename)



class CRF():
    """Class for named entity tagging using a crfsuite model."""

    def __init__(self, settings, model_filename):
        """Initialize the tagger.

        Parameters
        ----------
        settings: estnltk.ner.Settings
            The settings module used for feature extraction.
        model_filename: str
            The filename pointing to the path of the model that
            should be loaded.
        """
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(model_filename)

    def tag(self, nerdoc, layers=["morph_analysis", "words", "sentences"]):
        """Tag the given document.
        Parameters
        ----------
        nerdoc: estnltk.ner.Document
            The document to be tagged.

        Returns
        -------
        labels: list of lists of str
            Predicted token Labels for each sentence in the document
        """

        labels = []
        sentences = layers[2]
        for snt in getattr(nerdoc, sentences):
            xseq = [t.ner_features.F for t in snt]
            to_be_tagged = []
            for word in xseq:
                to_be_tagged.append(word[0])
            yseq = self.tagger.tag(to_be_tagged)
            labels.append(yseq)
        return labels
