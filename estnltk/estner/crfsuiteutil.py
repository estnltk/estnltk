# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

import pycrfsuite
import tempdir
import os

from estnltk.estner.featureextraction import FeatureExtractor
from estnltk.estner import nlputil
from pprint import pprint


class Trainer(object):
    '''Class for training CRF models.'''
    
    def __init__(self, settings):
        self.settings = settings
    
    def extract_features(self, docs):
        '''Extract the features on selected docs.'''
        fex = FeatureExtractor(self.settings)
        nerdocs = nlputil.prepare_documents(docs)
        fex.prepare(nerdocs)
        fex.process(nerdocs)
        return nerdocs
    
    def train(self, docs, filename=None):
        '''Train a CRF model on given documents.
        
        Parameters
        ----------
        docs: list of JSON-style documents.
            The documents used for training the CRF model.
        filename: str
            The fielname to save the serialized model.
        
        Returns
        -------
        binary
            The serialized binary of the model.
        '''
        nerdocs = self.extract_features(docs)
        trainer = pycrfsuite.Trainer()
        for doc in nerdocs:
            for snt in doc.snts:
                xseq = [t.feature_list() for t in snt]
                yseq = [t.label for t in snt]
                trainer.append(xseq, yseq)
        
        trainer.select('l2sgd', 'crf1d')
        trainer.set('c2', '0.001')
        
        with tempdir.TempDir() as t:
            if filename is None:
                filename = os.path.join(t, 'model.bin')
            trainer.train(filename)
            # get the binary model and return it
            with open(filename, 'rb') as f:
                return f.read()


class Tagger(object):
    '''Class for named entity tagging.'''
    
    def __init__(self, settings, filename=None, model=None):
        '''Initialize the tagger.
        
        Parameters
        ----------
        settings: estnltk.estner.settings.Settings
            The settings used for feature extraction.
        filename: str
            The filename pointing to the path of the model that
            should be loaded.
        model: binary
            The serialized binary representation of the model.
        
        If both the `model` and `filename` are given, then it ignores
        the filename.
        '''
        assert model is not None or filename is not None
        
        self.settings = settings
        self.tagger = pycrfsuite.Tagger()
        # initialize the tagger and load the model
        with tempdir.TempDir() as t:
            if model is not None:
                filename = os.path.join(t, 'model.bin')
                with open(filename, 'wb') as f:
                    f.write(model)
            self.tagger.open(filename)
        self.fex = FeatureExtractor(self.settings)

    def extract_features(self, docs):
        '''Extract features on given docs.'''
        nerdocs = nlputil.prepare_documents(docs)
        self.fex.prepare(nerdocs)
        self.fex.process(nerdocs)
        return nerdocs

    def tag(self, docs):
        '''Tag the given documents.
        
        Parameters
        ----------
        docs: list of JSON-style documents/corpora.
            The documents to be tagged.
            
        The tagger requires a list of document as the NER tagging
        system uses global features that use documents
        as contexts.
        
        Returns
        -------
        list of JSON-style documents/corpora.
        '''
        nerdocs = self.extract_features(docs)
        for nerdoc, vabadoc in zip(nerdocs, docs):
            vabadoc = self._tag_doc(nerdoc, vabadoc)
        return docs

    def _tag_doc(self, nerdoc, vabadoc):
        labels = []
        for snt in nerdoc.snts:
            xseq = [t.feature_list() for t in snt]
            labels.append(self.tagger.tag(xseq))
        return nlputil.assign_labels(vabadoc, labels)
