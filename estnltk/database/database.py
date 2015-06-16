# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from elasticsearch import Elasticsearch


def prepare_text(text):
    """Function that converts Text instance to format that can be easily indexed
    with ES database.

    TODO: seda koodi tuleb tõenõoliselt kohandada lähtuvalt ülesannetest.
    """
    layers = {}
    for layer, values in text.items():
        # all list elements in Text should be considered as layers
        if layer == 'words': # do not index "words" layer separately
            continue
        if isinstance(values, list):
            elements = text.split_by(layer)
            texts = [elem.text for elem in elements]
            lemmas = [' '.join(elem.lemmas) for elem in elements]
            layers[layer] = {'texts': texts, 'lemmas': lemmas}
    return {'text': text, 'layers': layers}


class Database(object):


    def __init__(self, index, type='document'):
        self.__es = Elasticsearch(index=index, type=type)


    def keyword_documents(self, keywords, layer=None, n=None):
        """Find all Text documents that match given keywords.

        Parameters
        ----------
        keywords: str
            The keywords to use for search.
        layer: str
            The layer to search the text from (for example words, sentences, clauses, verb_phrases etc).
            If layer is None (default), then use the full document text for search.
        n: int (default: None)
            If None, then return all matching documents.
            If integer, return only n best matches.

        Returns
        -------
        Iterable of Text instances.
        """

    def keyword_matches(self, keywords, layer=None):
        """Find all Text documents and matched regions for given keywords.

        Parameters
        ----------
        keywords: str
            The keywords to use for search.
        layer: str
            The layer to search the text from (for example words, sentences, clauses, verb_phrases etc).
            If layer is None (default), then use the full document text for search.
        n: int (default: None)
            If None, then return all matching documents.
            If integer, return only n best matches.

        Returns
        -------
        Iterable of {"text": document, "matches": layer}
        """
        pass

# prepare_text näide
from ..text import Text
from pprint import pprint

text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid.')
text.tag_clauses().tag_named_entities()

converted = prepare_text(text)
pprint(converted)
pprint(converted['layers'])