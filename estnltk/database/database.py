# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import json

from elasticsearch import Elasticsearch
from ..names import *
from ..text import Text

# define a list of standard layers we will not be indexing
STANDARD_LAYERS = frozenset([
    WORDS,
    PARAGRAPHS,
    SENTENCES,
    CLAUSES
])

# we need a way to index lemmas, postags and possibly other complicated data
# maybe it would be better to define it in code, but just in case, let's create a
# data structure that can be used to dynamically change the behaviour

# text.is_tagged(what?), destination layer name, function for value extraction
METALAYERS = [
    (ANALYSIS, 'lemmas', lambda text: ' '.join(text.lemmas)),
    (ANALYSIS, 'postags', lambda text: ' '.join(text.postags))
]

# set of layers actually used in metalayers
METALAYER_NAMES = frozenset([dst for src, dst, func in METALAYERS])


def prepare_text(text):
    """Function that converts Text instance to format that can be easily indexed
    with ES database.
    """
    layers = {}
    for layer, values in text.items():
        if layer in STANDARD_LAYERS:
            continue
        if isinstance(values, list):
            elements = text.split_by(layer)
            texts = [elem.text for elem in elements]
            lemmas = [' '.join(elem.lemmas) for elem in elements]
            layers[layer] = {'texts': texts, 'lemmas': lemmas}
    # process metalayers
    for tag, layer, extractor in METALAYERS:
        if text.is_tagged(tag):
            layers[layer] = extractor(text)
    return {'text': text, 'layers': layers}


class Database(object):
    """Database class represents a single index in Elastic
    and helps with inserting and querying Estnltk documents.

    Parameters
    ----------
    index: str
        The name of the Elastic index.
    doc_type:
        The document type to use (default: 'document')
    keyword_argument:
        All keyword arguments will be passed to Python Elasticsearch constructor.
    """

    def __init__(self, index, doc_type='document', **kwargs):
        self.__es = Elasticsearch(maxKeepAliveTime=0, timeout=30, **kwargs)
        self.__index = index
        self.__doc_type = doc_type

    @property
    def index(self):
        """The name of the index."""
        return self.__index

    @property
    def doc_type(self):
        """The doc_type property"""
        return self.__doc_type

    @property
    def es(self):
        """The ElasticSearch instance."""
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
        """Retrieve a document with given id."""
        return self.es.get(index=self.index, doc_type=self.doc_type, id=id, ignore=[400, 404])['_source']['text']

    def refresh(self):
        """Commit all changes to the index."""
        self.es.indices.refresh(index=self.index, ignore=[400, 404])

    def delete_index(self):
        """Delete the index."""
        self.es.indices.delete(index=self.index, ignore=[400, 404])

    def delete(self, index, id):
        self.es.delete(index=index, doc_type=self.doc_type, id=id, ignore=[400, 404])

    def count(self):
        return self.es.count(index=self.index, doc_type=self.doc_type, ignore=[400, 404])['count']

    def update(self):
        pass

    def close_connection(self):
        pass

    def query_documents(self, query, layer=None, size=10, es_result=False):
        """Find all Text documents that match keywords in the query.

        Check elasticsearch documentation for more information:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html

        Example queries:

        krokodill Gena
            Find documents containing "krokodill" or "gena" or both
        +venemaa -eesti
            Find documents containing word/lemma about venemaa, but not eesti
        "suur pauk"
            Find documents containing exact phrase "suur pauk"

        Parameters
        ----------
        query: str
            The keywords to use for search.
        layer: str
            The layer to search the text from (for example words, sentences, clauses, verb_phrases etc).
            If layer is None (default), then use the full document text for search.
        size: int (default: 10)
            Return size matches.
        es_result: boolean (default: False)
            if True, return the elasticsearch results, otherwise return a list of Text instances.
        Returns
        -------
        list of Text instances if es_result is False
        dict if es_result is True
        """

        query_string = {
            'query': query
        }

        if layer is not None:
            # if layer is one of the metalayers, then no need to match both text and lemmas
            if layer in METALAYER_NAMES:
                query_string['default_field'] = 'document.layers.' + layer
            else:
                query_string['fields'] = ['document.layers.' + 'lemmas', 'document.layers.' + 'text']

        body = {
            'query': {
                'bool': {
                    'must': {
                        'query_string': query_string
                    }
                }
            }
        }

        results = self.es.search(index=self.index, doc_type=self.doc_type, body=body, size=size)
        if es_result:
            return results
        else:
            return [Text(doc['_source']['text']) for doc in results['hits']['hits']]


    def query_matches(self, uqwy, layer=None):
        pass

