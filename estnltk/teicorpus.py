# -*- coding: utf-8 -*-
'''Module for reading koondcorpus files. See http://www.cl.ut.ee/korpused/segakorpus/index.php?lang=et

The implementation is quite simplistic, though.
'''
from __future__ import unicode_literals, print_function

from estnltk.tokenize import Tokenizer
from estnltk.core import get_filenames
from estnltk.names import *

from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup

from pprint import pprint
from copy import deepcopy

import os

def parse_tei_corpora(root, prefix='', suffix='.xml', target=['artikkel']):
    '''Parse all XML files in a root directory.
    
    Gives each document 'file' attribute that denotes the original filename.
    
    Parameters
    ----------
    root: str
        The directory path containing the TEI corpora XMl files.
    prefix: str
        The prefix of filenames to include (default: '')
    suffix: str
        The suffix of filenames to include (default: '.xml')
    '''
    documents = []
    for fnm in get_filenames(root, prefix, suffix):
        path = os.path.join(root, fnm)
        corpus = parse_tei_corpus(path, target)
        for d in corpus:
            d['file'] = fnm
        documents.extend(corpus)
    return documents

def parse_tei_corpus(path, target=['artikkel']):
    '''Parse documents from a TEI style XML file from the disk.
    
    Parameters
    ----------
    path: str
        The path of the XML file.
    target: list of str
        What to consider a document in the file. (default: ["artikkel"])
    '''
    with open(path, 'rb') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc)
    title = soup.find_all('title')[0].string
    
    documents = []
    for div1 in soup.find_all('div1'):
        documents.extend(parse_div(div1, dict(), target))
    return tokenize_documents(documents)

        
def parse_div(soup, metadata, target):
    '''Parse a section in the XML file.'''
    documents = []
    div_type = soup.get('type', None)
    div_title = list(soup.children)[0].string.strip()
    
    if div_type in target:
        div_authors = soup.find_all('author')
        document = {
            'type': div_type,
            'title': div_title,
            'paragraphs': parse_paragraphs(soup)
        }
        # add author, if it exists
        if len(div_authors) > 0:
            div_author = div_authors[0].text.strip()
            document['author'] = div_author
        # add collected metadata
        for k, v in metadata.items():
            document[k] = v
        documents.append(document)
    else:
        metadata[div_type] = div_title

        # recurse subdivs
        subdiv_name = {'div1': 'div2', 'div2': 'div3'}.get(soup.name, None)
        subdivs = []
        if subdiv_name is not None:
            subdivs = soup.find_all(subdiv_name)
        if len(subdivs) > 0:
            for subdiv in subdivs:
                documents.extend(parse_div(subdiv, deepcopy(metadata), target))
    return documents


def parse_paragraphs(soup):
    '''Parse sentences and paragraphs in the section.'''
    paragraphs = []
    for para in soup.find_all('p'):
        sentences = []
        for sent in para.find_all('s'):
            sentence = sent.text.strip()
            if len(sentence) > 0:
                sentences.append(sentence)
        if len(sentences) > 0:
            paragraphs.append({'sentences': sentences})
    return paragraphs


def tokenize_documents(docs):
    '''Given a document containing paragraphs and sentences, reconstruct
    a document and add indices to it.'''
    tokenizer = Tokenizer(
        paragraph_tokenizer=RegexpTokenizer('\n\n', gaps=True, discard_empty=True),
        sentence_tokenizer=RegexpTokenizer('\n', gaps=True, discard_empty=True),
        word_tokenizer=RegexpTokenizer('\s+', gaps=True, discard_empty=True))
    for doc in docs:
        txt = '\n\n'.join(['\n'.join(p[SENTENCES]) for p in doc[PARAGRAPHS]])
        doc[PARAGRAPHS] = tokenizer(txt)[PARAGRAPHS]
        doc[TEXT] = txt
        doc[START] = 0
        doc[REL_START] = 0
        doc[END] = len(txt)
        doc[REL_END] = len(txt)
    return docs
