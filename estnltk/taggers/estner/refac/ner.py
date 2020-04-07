# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from estnltk import EnvelopingBaseSpan
from estnltk.layer.layer import Layer
from estnltk.layer.enveloping_span import EnvelopingSpan
from estnltk.layer.annotation import Annotation

"""
Module containing functionality for training and using NER models.

Attributes
----------
tagger: NerTagger
    Ner tagger with default model and parameters.

"""
import os
import shutil
import errno
import inspect

import six

from estnltk.core import DEFAULT_PY2_NER_MODEL_DIR, DEFAULT_PY3_NER_MODEL_DIR
from estnltk.taggers.estner.refac.names import *
from estnltk.taggers.estner import Document, Sentence, Token
from estnltk.taggers.estner import CrfsuiteTrainer, CrfsuiteTagger

from estnltk.taggers.estner.featureextraction import FeatureExtractor

# Use different NER models depending on Python version
DEFAULT_NER_MODEL_DIR = DEFAULT_PY3_NER_MODEL_DIR if six.PY3 else DEFAULT_PY2_NER_MODEL_DIR


class ModelStorageUtil(object):
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.model_filename = os.path.join(model_dir, 'model.bin')
        self.settings_filename = os.path.join(model_dir, 'settings.py')

    def makedir(self):
        """ Create model_dir directory """
        try:
            os.makedirs(self.model_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def copy_settings(self, settings_module):
        """ Copy settings module to the model_dir directory """
        source = inspect.getsourcefile(settings_module)
        dest = os.path.join(self.model_dir, 'settings.py')
        shutil.copyfile(source, dest)

    def load_settings(self):
        """Load settings module from the model_dir directory."""
        mname = 'loaded_module'
        if six.PY2:
            import imp
            return imp.load_source(mname, self.settings_filename)
        else:
            import importlib.machinery
            loader = importlib.machinery.SourceFileLoader(mname, self.settings_filename)
        return loader.load_module(mname)


def json_document_to_estner_document(jsondoc):
    """Convert an estnltk document to an estner document.

    Parameters
    ----------
    jsondoc: dict
        Estnltk JSON-style document.

    Returns
    -------
    estnltk.estner.ner.Document
        A ner document.
    """
    sentences = []
    snt = Sentence()
    jsondoc.tag_layer()
    zipped = list(zip(
        jsondoc['words'],
        jsondoc['morph_analysis']['lemma'],
        jsondoc['morph_analysis']['root_tokens'],
        jsondoc['morph_analysis']['form'],
        jsondoc['morph_analysis']['ending'],
        jsondoc['morph_analysis']['partofspeech']))
    json_toks = [{TEXT: text, LEMMA: lemma, ROOT_TOKENS: root_tokens, FORM: form, ENDING: ending, POSTAG: postag}
                 for text, lemma, root_tokens, form, ending, postag in zipped]
    # add labels, if they are present
    # also some 1.6 transformations
    for tok, word in zip(json_toks, jsondoc.words):
        tok['ending'] = tok['ending'][0]
        tok['partofspeech'] = tok['partofspeech'][0]
        tok['root_tokens'] = tok['root_tokens'][0]
        tok['lemma'] = tok['lemma'][0]
        tok['form'] = tok['form'][0]
        tok['text'] = tok['text'].annotations[0].text
        if LABEL in word.annotations:
            tok[LABEL] = word.annotations[LABEL]
    for json_tok in json_toks:
        token = json_token_to_estner_token(json_tok)
        snt.append(token)
    if snt:
        for i in range(1, len(snt)):
            snt[i - 1].next = snt[i]
            snt[i].prew = snt[i - 1]
        sentences.append(snt)

    return Document(sentences=sentences)


def json_token_to_estner_token(json_token):
    """Convert a JSON-style word token to an estner token.

    Parameters
    ----------
    vabamorf_token: dict
        Vabamorf token representing a single word.
    label: str
        The label string.

    Returns
    -------
    estnltk.estner.ner.Token
    """
    token = Token()
    word = json_token[TEXT]
    lemma = word
    morph = ''
    label = 'O'
    ending = json_token[ENDING]
    root_toks = json_token[ROOT_TOKENS]
    if isinstance(root_toks, list):
        root_toks = root_toks
    lemma = '_'.join(root_toks) + ('+' + ending if ending else '')
    if not lemma:
        lemma = word
    morph = '_%s_' % json_token[POSTAG]
    morph += ' ' + json_token[FORM]
    if LABEL in json_token:
        label = json_token[LABEL]
    return Token(word, lemma, morph, label)


class NerTrainer(object):
    """The class for training NER models. Uses crfsuite implementation."""

    def __init__(self, nersettings):
        """Initialize a new NerTrainer.
        
        Parameters
        ----------
        nersettings: module
            NER settings module.
        """
        self.settings = nersettings
        self.fex = FeatureExtractor(nersettings)
        self.trainer = CrfsuiteTrainer(algorithm=nersettings.CRFSUITE_ALGORITHM,
                                       c2=nersettings.CRFSUITE_C2)

    def train(self, jsondocs, model_dir):
        """ Train a NER model using given documents.
        
        Each word in the documents must have a "label" attribute, which
        denote the named entities in the documents.
        
        Parameters
        ----------
        jsondocs: list of JSON-style documents.
            The documents used for training the CRF model.
        model_dir: str
            A directory where the model will be saved.
        """
        modelUtil = ModelStorageUtil(model_dir)
        modelUtil.makedir()
        modelUtil.copy_settings(self.settings)

        # Convert json documents to ner documents
        nerdocs = [json_document_to_estner_document(jsondoc)
                   for jsondoc in jsondocs]

        self.fex.prepare(nerdocs)
        self.fex.process(nerdocs)

        self.trainer.train(nerdocs, modelUtil.model_filename)


class NerTagger(object):
    """The class for tagging named entities."""

    def __init__(self, model_dir=DEFAULT_NER_MODEL_DIR):
        """Initialize a new NerTagger instance.
        
        Parameters
        ----------
        model_dir: st
            A directory containing a trained ner model and a settings file.
        """
        modelUtil = ModelStorageUtil(model_dir)
        nersettings = modelUtil.load_settings()

        self.fex = FeatureExtractor(nersettings)
        self.tagger = CrfsuiteTagger(settings=nersettings,
                                     model_filename=modelUtil.model_filename)

    def tag_documents(self, documents):
        nerdocs = [json_document_to_estner_document(jsondoc) for jsondoc in documents]
        self.fex.process(nerdocs)
        # add the labels
        for nerdoc, jsondoc in zip(nerdocs, documents):
            snt_labels = self.tagger.tag(nerdoc)
            nerlayer = Layer(name="ner", attributes=("nertag","name"), text_object=jsondoc, enveloping="words")
            entity_spans = []
            for span,label in zip(jsondoc.words,snt_labels[0]):
                if label == "O":
                    if entity_spans:
                        ebs = EnvelopingBaseSpan(entity_spans)
                        envspan = EnvelopingSpan(ebs,nerlayer)
                        annotation = Annotation(span=envspan,nertag = entity_type, name="po")
                        envspan.add_annotation(annotation)
                        nerlayer.add_span(envspan)
                        entity_spans = []
                    continue
                entity_type = label[2:]
                entity_spans.append(span.base_span)

            jsondoc.add_layer(nerlayer)
        return documents

    def tag_document(self, document):
        return self.tag_documents([document])[0]
