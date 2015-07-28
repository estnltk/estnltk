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
        self.__index_name = index
        self.__doc_type = type

    @property
    def index_name(self):
        return self.__index_name

    @property
    def doc_type(self):
        return self.__doc_type

    @property
    def es(self):
        return self.__es

    def delete(self):
        self.es.delete(index=self.index_name, doc_type=self.doc_type, id=None)

    def count(self):
        return self.__es.count(index=self.index_name)['count']

    def index(self, text, id=None):
        converted = prepare_text(text)
        self.__es.index(index=self.__index_name, doc_type=self.doc_type, id=id, body=converted)

    def update(self, text, id=None):
        pass



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
        pass

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

