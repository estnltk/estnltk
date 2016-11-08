# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__all__ = ['Index', 'create_index', 'connect', 'query_grammar']

import copy
import elasticsearch
import elasticsearch.helpers
import itertools
import json

from .mapping import mapping
from estnltk.text import Text


def create_index(index_name, **kwargs):
    """
    Parameters
    ----------
    index_name : str
        Name of the index to be created
    **kwargs
        Arguments to pass to Elasticsearch instance.

    Returns
    -------

    Index
    """
    es = elasticsearch.Elasticsearch(**kwargs)
    es.indices.create(index=index_name, body=mapping)
    return connect(index_name, **kwargs)


def connect(index_name, **kwargs):
    """

    Parameters
    ----------
    index_name : str
        Index name to connect to.
    **kwargs
        Parameters to pass to Elasticsearch instance.

    Returns
    -------

    Index

    """
    client = elasticsearch.Elasticsearch(**kwargs)
    return Index(client, index_name)


class Index:
    def __init__(self, client, index_name):
        """

        Parameters
        ----------
        client : Elasticsearch
        index_name : str
        """
        self.index_name = index_name
        self.client = client
        assert client.indices.exists(index=index_name), 'Index "{}" does not exist'.format(index_name)

    def sentences(self, exclude_ids=None, query=None, return_estnltk_object=True, **kwargs):
        if query is None:
            query = {}

        if return_estnltk_object:
            if query.get('fields', None) is None:
                query['fields'] = ['estnltk_text_object']
            else:
                if 'estnltk_text_object' not in query['fields']:
                    raise AssertionError('Query contained the "fields" parameter without the "estnltk_text_object" argument'
                                         'Consider setting the "return_estnltk_object" parameter to False to disable respose handling')
                pass

        if exclude_ids is None:
            for document in elasticsearch.helpers.scan(self.client, query=query, doc_type='sentence', **kwargs):
                if return_estnltk_object:
                    yield Text(json.loads(document['fields']['estnltk_text_object'][0]))
                else:
                    yield json.loads(document)
        else:
            raise NotImplementedError('ID exclusion is not implemented')

    @staticmethod
    def _get_indexable_sentences(document):
        """
        Parameters
        ----------
        document : Text
            Article, book, paragraph, chapter, etc. Anything that is considered a document on its own.

       Yields
       ------
       str
            json representation of elasticsearch type sentence

        """

        def unroll_lists(list_of_lists):
            for i in itertools.product(*[set(j) for j in list_of_lists]):
                yield ' '.join(i)

        sents = document.split_by_sentences()
        for order, sent in enumerate(sents):
            postags = list(unroll_lists(sent.postag_lists))
            lemmas = list(unroll_lists(sent.lemma_lists))
            text = sent.text
            words = copy.deepcopy(sent.words)
            for i in words:
                del i['start']
                del i['end']

            sentence = {
                'estnltk_text_object': json.dumps(sent),
                'meta': {
                    'order_in_parent': order
                },
                'text': text,
                'words': words,
                'postags': postags,
                'lemmas': lemmas
            }
            yield json.dumps(sentence)

    def save(self, document, meta=None):
        if getattr(document, '__db_meta', None):
            # we should overwrite a previous object
            raise NotImplementedError('Changing objects in the database has not been implemented.')
        else:
            # we should create a new object
            document_in_es = self.client.index(self.index_name, 'document', {} if meta is None else meta)
            for sent in self._get_indexable_sentences(document):
                self.client.index(self.index_name,
                    'sentence',
                    sent,
                    parent=document_in_es['_id'])

    def get_iter(self, document, meta=None):
        if getattr(document, '__db_meta', None):
            # we should overwrite a previous object
            raise NotImplementedError('Changing objects in the database has not been implemented.')
        else:
            # we should create a new
            yield ('document', {} if meta is None else meta)
            for sent in self._get_indexable_sentences(document):
                yield ('sentence',
                       sent
                       )
