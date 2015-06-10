# -*- coding: utf-8 -*-
"""Module for reading koondcorpus files. See http://www.cl.ut.ee/korpused/segakorpus/index.php?lang=et

The corpus contains variety of documents from different domains and can be used freely for non-commercial purposes.
Estnltk is capable of reading XML formatted files of the corpus and parse the
documents, paragraphs, sentences and words with some additional metadata found in XML files.

The implementation is currently quite simplistic, though. But it should
be sufficient for simpler use cases.
"""
from __future__ import unicode_literals, print_function, absolute_import

from .core import get_filenames
from .names import *
from .text import Text
from bs4 import BeautifulSoup
from copy import deepcopy

import os


def parse_tei_corpora(root, prefix='', suffix='.xml', target=['artikkel']):
    """Parse documents from TEI style XML files.
    
    Gives each document FILE attribute that denotes the original filename.
    
    Parameters
    ----------
    root: str
        The directory path containing the TEI corpora XMl files.
    prefix: str
        The prefix of filenames to include (default: '')
    suffix: str
        The suffix of filenames to include (default: '.xml')
    target: list of str
        List of <div> types, that are considered documents in the XML files (default: ["artikkel"]).
        
    Returns
    -------
    list of estnltk.text.Text
        Corpus containing parsed documents from all files. The file path
        is stored in FILE attribute of the documents.
    """
    documents = []
    for fnm in get_filenames(root, prefix, suffix):
        path = os.path.join(root, fnm)
        docs = parse_tei_corpus(path, target)
        for doc in docs:
            doc[FILE] = fnm
        documents.extend(docs)
    return documents


def parse_tei_corpus(path, target=['artikkel']):
    """Parse documents from a TEI style XML file.
    
    Parameters
    ----------
    path: str
        The path of the XML file.
    target: list of str
        List of <div> types, that are considered documents in the XML files (default: ["artikkel"]).
        
    Returns
    -------
    list of esnltk.text.Text
    """
    with open(path, 'rb') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc)
    title = soup.find_all('title')[0].string
    
    documents = []
    for div1 in soup.find_all('div1'):
        documents.extend(parse_div(div1, dict(), target))
    return tokenize_documents(documents)

        
def parse_div(soup, metadata, target):
    """Parse a <div> tag from the file.
    
    The sections in XML files are given in <div1>, <div2> and <div3>
    tags. Each such tag has a type and name (plus possibly more extra attributes).
    
    If the div type is found in target variable, the div is parsed
    into structured paragraphs, sentences and words.
    
    Otherwise, the type and name are added as metadata to subdivs
    and stored in.
    
    Parameters
    ----------
    soup: bs4.BeautifulSoup
        The parsed XML data.
    metdata: dict
        The metadata for parent divs.
    target: list of str
        List of <div> types, that are considered documents in the XML files.
    
    """
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
    """Parse sentences and paragraphs in the section.
    
    Parameters
    ----------
    soup: bs4.BeautifulSoup
        The parsed XML data.
        
    Returns
    -------
    list of (list of str)
        List of paragraphs given as list of sentences.
    """
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


def concatenate(texts, sep=' ', offset=0):
    l = len(sep)
    spans = []
    for t in texts:
        spans.append({START: offset, END: offset + len(t)})
        offset += l + len(t)
    return sep.join(texts), spans


def tokenize_documents(docs):
    """Convert the imported documents to :py:class:'~estnltk.text.Text' instances."""
    sep = '\n\n'
    texts = []
    for doc in docs:
        text = '\n\n'.join([' '.join(para[SENTENCES]) for para in doc[PARAGRAPHS]])
        doc[TEXT] = text
        del doc[PARAGRAPHS]
        texts.append(Text(doc).tokenize_paragraphs().tokenize_words())
    return texts
