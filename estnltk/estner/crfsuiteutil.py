# -*- coding: utf-8 -*-
''' Defines wrappers over crfsuite package for named entity recognition.'''

from __future__ import unicode_literals, print_function

import pycrfsuite


class Trainer(object):
    '''Trains a crfsuite model.'''


    def __init__(self, algorithm='l2sgd', c2=0.001, verbose=True):
        '''Initialize the trainer.

        Parameters
        ----------
        algorithm: str
            Crfsuite training algorithm
        c2: float
            Crfsuite c2 parameter
        verbose: boolean
            Enable Crfsuite trainer verbose output
        '''
        self.algorithm = algorithm
        self.c2 = c2
        self.verbose = verbose


    def train(self, nerdocs, mode_filename):
        '''Train a CRF model using given documents.

        Parameters
        ----------
        nerdocs: list of estnltk.estner.ner.Document.
            The documents for model training.
        mode_filename: str
            The fielname where to save the model.
        '''

        trainer = pycrfsuite.Trainer(algorithm=self.algorithm, 
                                     params={'c2': self.c2},
                                     verbose=self.verbose)

        for doc in nerdocs:
            for snt in doc.snts:
                xseq = [t.feature_list() for t in snt]
                yseq = [t.label for t in snt]
                trainer.append(xseq, yseq)

        trainer.train(mode_filename)


class Tagger():
    '''Class for named entity tagging using a crfsuite model.'''

    def __init__(self, settings, model_filename):
        '''Initialize the tagger.
        
        Parameters
        ----------
        settings: estnltk.estner.Settings
            The settings module used for feature extraction.
        model_filename: str
            The filename pointing to the path of the model that
            should be loaded.
        '''
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(model_filename)


    def tag(self, nerdoc):
        '''Tag the given document.
        Parameters
        ----------
        nerdoc: estnltk.estner.Document
            The document to be tagged.
        
        Returns
        -------
        labels: list of lists of str
            Predicted token Labels for each sentence in the document
        '''

        labels = []
        for snt in nerdoc.snts:
            xseq = [t.feature_list() for t in snt]
            yseq = self.tagger.tag(xseq)
            labels.append(yseq)
        return labels

