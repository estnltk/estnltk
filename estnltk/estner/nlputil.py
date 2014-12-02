# -*- encoding: utf8 -*-
from __future__ import unicode_literals, print_function

from estnltk.core import JsonPaths, as_unicode
from estnltk.names import *
from estnltk.estner.ner import Token, Sentence, Document

from pprint import pprint


def vabamorf_token_to_estner_token(vabamorf_token, label='label'):
    '''Convert a JSON-style word token to estner token.
    
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


def prepare_document(corpus):
    '''Prepare a document for estner feature extraction.
    
    Parameters
    ----------
    corpus: list or dict
        The input corpus.
    
    Returns
    -------
    estnltk.estner.ner.Document
        The Document suitable for feature extraction.
    '''
    document = Document()
    for ptr in JsonPaths.words.find(corpus):
        snt = Sentence()
        for vabamorf_token in ptr.value:
            token = vabamorf_token_to_estner_token(vabamorf_token)
            snt.append(token)
            document.tokens.append(token)
        if snt:
            for i in range(1, len(snt)):
                snt[i-1].next = snt[i]
                snt[i].prew = snt[i-1]
            document.snts.append(snt)
    return document


def prepare_documents(documents):
    '''Prepare a list of estnltk documents.
    
    Parameters
    ----------
    documents: list of dict
        List of estnltk JSON-style corpora. Each element denotes
        a document.
    
    Returns
    -------
    list of estnltk.estner.ner.Document
        List of prepared documents.
    '''
    prepared = []
    for document in documents:
        prepared.append(prepare_document(document))
    return prepared


def assign_labels(document, labels):
    '''Assign labels to given documents.
    
    Parameters
    ----------
    document: JSON-style estnltk document.
        The document to be assigned labels to.
    labels: list of list of str
        Each sublist denotes the labels for one sentence.
    
    Returns
    -------
    JSON-style estnltk document.
        The same document as argument.
    '''
    for ptr, snt_labels in zip(JsonPaths.words.find(document), labels):
        words = ptr.value
        assert len(words) == len(snt_labels)
        for word, label in zip(words, snt_labels):
            word[LABEL] = as_unicode(label)
    return document
