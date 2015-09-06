# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import warnings
import json

from elasticsearch import Elasticsearch

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


def prepare_text(text):
    """Function that converts Text instance to format that can be easily indexed
    with ES database.

    TODO: seda koodi tuleb tõenõoliselt kohandada lähtuvalt ülesannetest.
    """
    layers = {}
    for layer, values in text.items():
        # all list elements in Text should be considered as layers
        if layer == 'words':  # do not index "words" layer separately
            continue
        if isinstance(values, list):
            elements = text.split_by(layer)
            texts = [elem.text for elem in elements]
            lemmas = [' '.join(elem.lemmas) for elem in elements]
            layers[layer] = {'texts': texts, 'lemmas': lemmas}
    return {'text': text, 'layers': layers}


class Database(object):
    def __init__(self, index, doc_type='document', **kwargs):
        self.__es = Elasticsearch(maxKeepAliveTime=0, **kwargs)
        self.__index = index
        self.__doc_type = doc_type

    @property
    def index(self):
        return self.__index

    @property
    def doc_type(self):
        return self.__doc_type

    @property
    def es(self):
        return self.__es

    def insert(self, text, id=None):
        """Insert a document to index.

        Parameters
        ----------
        text: estnltk.text.Text
            The text instance to be inserted.
        id: str
            Optional id for the document, if not omitted, a default value is generated.

        Returns
        -------
        str
            The id of the created document.
        """

        prepared_text = prepare_text(text)
        kwargs = {
            'index': self.index,
            'doc_type': self.doc_type,
            'body': prepared_text
        }
        if id is not None:
            kwargs['id'] = int(id)
        doc_id = self.es.create(**kwargs)['_id']
        self.refresh()
        return doc_id

    def bulk_insert(self, list_of_texts, id=None, refresh=True):
        """
        Generator to use for bulk inserts
        """

        bulk_text = []

        for n, text in enumerate(list_of_texts):
            prepared_text = prepare_text(text)
            bulk_text.append({
                'index': {
                }
            })
            bulk_text.append(prepared_text)

        insert_data = '\n'.join([json.dumps(x) for x in bulk_text])
        result = self.es.bulk(index=self.index, doc_type=self.doc_type, body=insert_data, refresh=refresh)

    def get(self, id):
        return self.es.get(index=self.index, doc_type=self.doc_type, id=id, ignore=[400, 404])['_source']['text']

    def refresh(self):
        """Commit all changes to the index."""
        self.es.indices.refresh(index=self.index, ignore=[400, 404])

    def delete_index(self):
        self.es.indices.delete(index=self.index, ignore=[400, 404])

    def delete(self, index, id):
        self.es.delete(index=index, doc_type=self.doc_type, id=id, ignore=[400, 404])

    def count(self):
        return self.es.count(index=self.index, doc_type=self.doc_type, ignore=[400, 404])['count']

    def update(self):
        pass

    def close_connection(self):
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

        es = self.__es
        for keyword in keywords:
            search = es.search(index='test', doc_type=self.__doc_type, body={
                "query": {
                    "match": {
                        "text": keyword,
                    }
                }
            })


        print("%d documents found" % search['hits']['total'])

        #for doc in search['hits']['hits']:
        #    print("%s) %s" % (doc['_id'], doc['_source']['text']))

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