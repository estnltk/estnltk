# -*- coding: utf-8 -*-
'''
Module containing functionality for training and using NER models.

Attributes
----------
tagger: NerTagger
    Ner tagger with default model and parameters.

'''

from __future__ import unicode_literals, print_function

from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from estnltk.estner.settings import Settings, DEFAULT_SETTINGS_MODULE
from estnltk.core import DEFAULT_NER_DATASET, DEFAULT_NER_MODEL
from estnltk.estner.crfsuiteutil import Trainer, Tagger

from pprint import pprint
from base64 import b64encode, b64decode
import bz2
import tempdir
import os
import json


class NerModel(object):
    '''Class containing the settings and the model for the NER system.'''
    
    def __init__(self, settings_module_contents, model):
        '''Initialize the NER model.
        
        Parameters
        ----------
        settings_module_contents: str
            The actual Python code of the configuration.
        model: binary
            The serialized trained model used by crfsuite library.
        '''
        self.settings_module_contents = settings_module_contents
        self.model = model
        
    def serialize(self):
        '''Serialize the NerModel to a JSON string.
        
        Returns
        -------
        JSON string containing the configuration module source code
        and the model, both base64 encoded.
        '''
        return json.dumps(
            {'settings_module_contents': b64encode(self.settings_module_contents),
             'model': b64encode(bz2.compress(self.model))})
        
    def serialize_to_file(self, filename):
        '''Serialize the NerModel to a file.
        
        Parameters
        ----------
        filename: str
            The path where the serialized data will be saved to.
        '''
        with open(filename, 'wb') as f:
            f.write(self.serialize())
        
    @staticmethod
    def deserialize(serialized):
        '''Deserialize a NerModel.
        
        Parameters
        ----------
        serialized: str
            JSON string containing data previously created using serialize() method.
        
        Returns
        -------
        NerModel
            The NerModel instance.
        '''
        data = json.loads(serialized)
        return NerModel(b64decode(data['settings_module_contents']),
                        bz2.decompress(b64decode(data['model'])))
        
    @staticmethod
    def deserialize_from_file(filename):
        '''deserialize a NerModel from file.
        
        Parameters
        ----------
        filename: str
            The path pointing to previously serialized and saved NerModel.
            
        Returns
        -------
            The NerModel instance.
        '''
        with open(filename, 'rb') as f:
            return NerModel.deserialize(f.read())
        

class NerTrainer(object):
    '''The class for training NER models.'''
    
    def __init__(self, settings_module=DEFAULT_SETTINGS_MODULE):
        '''Initialize a new NerTrainer.
        
        Parameters
        ----------
        settings_module: str
            The path to the settings.
        '''
        with open(settings_module, 'rb') as f:
            self.settings_module_contents = f.read()
        self.settings = Settings(settings_module)
        self.trainer = Trainer(self.settings)
        
    def train(self, docs):
        ''' Train a NER model on given documents.
        
        Each word in the documents must have a "label" attribute, which
        denote the named entities in the documents.
        
        Parameters
        ----------
        docs: list of JSON-style documents.
            The documents used for training the CRF model.
        
        Returns
        -------
        NerModel
            The trained NER model.
        '''
        model = self.trainer.train(docs)
        return NerModel(self.settings_module_contents, model)
        

class NerTagger(object):
    '''The class for tagging named entities.'''
    
    def __init__(self, nermodel=None):
        '''Initialize a new NerTagger instance.
        
        Parameters
        ----------
        nermodel: NerModel
            A Previously trained NER model to be used with this tagger.
            If None, then loads and uses the default model.
        '''
        if nermodel is None:
            nermodel = NerModel.deserialize_from_file(DEFAULT_NER_MODEL)
        assert isinstance(nermodel, NerModel)
        with tempdir.TempDir() as t:
            settings_path = os.path.join(t, 'ner_settings.py')
            with open(settings_path, 'wb') as f:
                f.write(nermodel.settings_module_contents)
            self.settings = Settings(settings_path)
        self.tagger = Tagger(self.settings, model=nermodel.model)
    
    def __call__(self, docs):
        return self.tag(docs)
    
    def tag(self, docs):
        '''Tag the given documents with named entities. The tags
        will be stored in "label" attribute of the words.
        
        Parameters
        ----------
        docs: list of JSON-style documents/corpora.
            The documents that will be tagged.
            
        Returns
        -------
        docs: list of JSON-style documents/corpora.
            The documents given as the argument, but with added
            tags.
        '''
        return self.tagger.tag(docs)
        
        
def train_default_model():
    '''Function for training the default NER model.
    
    NB! It overwrites the default model, so do not use it unless
    you know what are you doing.
    
    The training data is in file estnltk/corpora/estner.json.bz2 .
    The resulting model will be saved to estnltk/estner/models/default.bin
    '''
    with open(DEFAULT_NER_DATASET) as f:
        nerdata = json.loads(bz2.decompress(f.read()))
        documents = nerdata['documents']
        trainer = NerTrainer()
        model = trainer.train(documents)
        model.serialize_to_file(DEFAULT_NER_MODEL)

