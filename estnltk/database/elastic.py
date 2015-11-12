# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import copy
import itertools
import json

import elasticsearch
import elasticsearch.helpers

from ..text import Text


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
    mapping = json.load(open('mapping.json'))
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
        client : elasticsearch.Elasticsearch
        index_name : str

        """
        self.index_name = index_name
        self.client = client
        assert client.indices.exists(index=index_name), 'Index "{}" does not exist'.format(index_name)

    def sentences(self, exclude_ids=None, query=None, **kwargs):
        if exclude_ids is None:
            for document in elasticsearch.helpers.scan(self.client, query=query, doc_type='sentence', **kwargs):
                # text = Text(document['estnltk_text'])
                # text.__db_meta = document['meta']
                # yield text

                # for i in index.sentences(query={
                #
                #         'fields':['estnltk_text_object']
                #     }):
                #     print(i)

                yield Text(json.loads(document['fields']['estnltk_text_object'][0]))
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

    def save(self, document):
        if getattr(document, '__db_meta', None):
            # we should overwrite a previous object
            raise NotImplementedError
        else:
            # we should create a new object
            document_in_es = self.client.index(self.index_name, 'document', {})
            for sent in self._get_indexable_sentences(document):
                self.client.index(self.index_name, 'sentence', sent, parent=document_in_es['_id'])
