# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
'''
Module containing functionality for training and using NER models.

Attributes
----------
tagger: NerTagger
    Ner tagger with default model and parameters.

'''
import os
import json
import codecs
import sys
import bz2
from pprint import pprint
from base64 import b64encode, b64decode
import shutil
import errno
import inspect

import six

from estnltk.core import as_unicode, JsonPaths
from estnltk.core import DEFAULT_NER_DATASET, DEFAULT_PY2_NER_MODEL_DIR, DEFAULT_PY3_NER_MODEL_DIR
from estnltk.textprocessor import TextProcessor
from estnltk.corpus import Corpus
from estnltk.names import *
from estnltk.estner import Document, Sentence, Token, CrfsuiteTrainer, CrfsuiteTagger
from estnltk.estner import settings as default_nersettings
from estnltk.estner.featureextraction import FeatureExtractor


# Use different NER models depending on Python version
DEFAULT_NER_MODEL_DIR = DEFAULT_PY3_NER_MODEL_DIR if six.PY3 else DEFAULT_PY2_NER_MODEL_DIR


class NerTrainer(object):
    '''The class for training NER models. Uses crfsuite implementation.'''


    def __init__(self, nersettings):
        '''Initialize a new NerTrainer.
        
        Parameters
        ----------
        nersettings: module
            NER settings module.
        '''
        self.settings = nersettings
        self.fex = FeatureExtractor(nersettings)
        self.trainer = CrfsuiteTrainer(algorithm=nersettings.CRFSUITE_ALGORITHM,
                                       c2=nersettings.CRFSUITE_C2)


    def train(self, jsondocs, model_dir):
        ''' Train a NER model using given documents.
        
        Each word in the documents must have a "label" attribute, which
        denote the named entities in the documents.
        
        Parameters
        ----------
        jsondocs: list of JSON-style documents.
            The documents used for training the CRF model.
        model_dir: str
            A directory where the model will be saved.
        '''
        modelUtil = ModelStorageUtil(model_dir)
        modelUtil.makedir()
        modelUtil.copy_settings(self.settings)

        # Convert json documents to ner documents
        nerdocs = [json_document_to_estner_document(jsondoc) 
                   for jsondoc in jsondocs]         

        self.fex.prepare(nerdocs)
        self.fex.process(nerdocs)

        self.trainer.train(nerdocs, modelUtil.model_filename)


class NerTagger(TextProcessor):
    '''The class for tagging named entities.'''


    def __init__(self, model_dir=DEFAULT_NER_MODEL_DIR):
        '''Initialize a new NerTagger instance.
        
        Parameters
        ----------
        model_dir: str
            A directory containing a trained ner model and a settings file.
        '''
        modelUtil = ModelStorageUtil(model_dir)
        nersettings = modelUtil.load_settings()

        self.fex = FeatureExtractor(nersettings)
        self.tagger = CrfsuiteTagger(settings=nersettings,
                                     model_filename=modelUtil.model_filename)


    def process_json(self, corpus, **kwargs):
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
        # TODO: this is inefficient. try to make it work directly on JSON
        return self.process_corpus(Corpus.construct(corpus)).to_json()


    def process_corpus(self, corpus, **kwargs):
        jsondocs = corpus.root_elements
        nerdocs = [json_document_to_estner_document(jsondoc) for jsondoc in jsondocs] 

        self.fex.process(nerdocs)

        for nerdoc, jsondoc in zip(nerdocs, jsondocs):
            snt_labels = self.tagger.tag(nerdoc)
            # Assigns labels to original documents
            for ptr, snt_labels in zip(JsonPaths.words.find(jsondoc), snt_labels):
                words = ptr.value
                assert len(words) == len(snt_labels)
                for word, label in zip(words, snt_labels):
                    word[LABEL] = as_unicode(label)
        return corpus


class ModelStorageUtil(object):

    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.model_filename = os.path.join(model_dir, 'model.bin')
        self.settings_filename = os.path.join(model_dir, 'settings.py')


    def makedir(self):
        ''' Create model_dir directory '''
        try:
            os.makedirs(self.model_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


    def copy_settings(self, settings_module):
        ''' Copy settings module to the model_dir directory '''
        source = inspect.getsourcefile(settings_module)
        dest = os.path.join(self.model_dir, 'settings.py')
        shutil.copyfile(source, dest)


    def load_settings(self):
        '''Load settings module from the model_dir directory.'''
        mname = 'loaded_module'
        if six.PY2:
            import imp
            return imp.load_source(mname, self.settings_filename)
        else:
            import importlib.machinery
            loader = importlib.machinery.SourceFileLoader(mname, self.settings_filename)
        return loader.load_module(mname)


def json_document_to_estner_document(jsondoc):
    '''Convert an estnltk document to an estner document.
    
    Parameters
    ----------
    jsondoc: dict
        Estnltk JSON-style document.
    
    Returns
    -------
    estnltk.estner.ner.Document
        A ner document.
    '''
    estnerdoc = Document()
    for ptr in JsonPaths.words.find(jsondoc):
        snt = Sentence()
        for vabamorf_token in ptr.value:
            token = vabamorf_token_to_estner_token(vabamorf_token)
            snt.append(token)
            estnerdoc.tokens.append(token)
        if snt:
            for i in range(1, len(snt)):
                snt[i-1].next = snt[i]
                snt[i].prew = snt[i-1]
            estnerdoc.snts.append(snt)
    return estnerdoc


def vabamorf_token_to_estner_token(vabamorf_token, label='label'):
    '''Convert a JSON-style word token to an estner token.
    
    Parameters
    ----------
    vabamorf_token: dict
        Vabamorf token representing a single word.
    label: str
        The label string.
    
    Returns
    -------
    estnltk.estner.ner.Token
    '''
    token = Token()
    word = vabamorf_token[TEXT]
    lemma = word
    morph = ''
    label = 'O'
    if len(vabamorf_token[ANALYSIS]) > 0:
        anal = vabamorf_token[ANALYSIS][0]
        ending = anal[ENDING]
        lemma = '_'.join(anal[ROOT_TOKENS]) + ('+' + ending if ending else '')
        if not lemma:
            lemma = word
        morph = '_%s_' % anal[POSTAG]
        if anal[FORM]:
            morph += ' ' + anal[FORM]
        if LABEL in vabamorf_token:
            label = vabamorf_token[LABEL]
    token.word = word
    token.lemma = lemma
    token.morph = morph
    token.label = label
    return token


def train_default_model():
    '''Function for training the default NER model.
    
    NB! It overwrites the default model, so do not use it unless
    you know what are you doing.
    
    The training data is in file estnltk/corpora/estner.json.bz2 .
    The resulting model will be saved to estnltk/estner/models/default.bin
    '''
    with codecs.open(DEFAULT_NER_DATASET, 'rb') as f:
        nerdata = f.read()
    nerdata = bz2.decompress(nerdata)
    nerdata = json.loads(nerdata.decode('utf-8'))
    documents = nerdata['documents']
    trainer = NerTrainer(default_nersettings)
    trainer.train(documents, DEFAULT_NER_MODEL_DIR)


if __name__ == '__main__':
    # todo: make this script capable of training and annotating corpora
    # from command line. for now, programmatic approach is good enough
    args = sys.argv[1:]

    if len(args) == 1 and args[0] == 'train_default_model':
        train_default_model()
