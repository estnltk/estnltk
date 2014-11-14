# -*- encoding: utf8 -*-
from __future__ import unicode_literals, print_function

from ner import Token, Sentence, Document

def vabamorf_token_to_estner_token(vabamorf_token):
    word = vabamorf_token['text']
    anal = vabamorf_token['analysis'][0]
    ending = anal['ending']
    lemma = '_'.join(anal['root_tokens']) + ('+' + ending if ending else '')
    if not lemma:
        lemma = word
    morph = '_%s_' % anal['partofspeech']
    if anal['form']:
        morph += ' ' + anal['form'] 
    
    token = Token()
    token.word = word
    token.lemma = lemma
    token.morph = morph
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
