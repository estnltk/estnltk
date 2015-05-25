# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .names import *
from .text import Text


class Disambiguator(object):

    def disambiguate(self, docs, **kwargs):
        # convert input
        kwargs = kwargs
        kwargs['disambiguate'] = False # do not use disambiguation right now
        docs = [Text(doc, **kwargs) for doc in docs]

        # morf.analysis without disambiguation
        docs = [doc.compute_analysis() for doc in docs]

        docs = self.pre_disambiguate(docs)
        docs = self.stat_disambiguate(docs)

        docs = self.__vabamorf_disambiguate(docs)
        docs = self.post_disambiguate(docs)

        return docs

    def __vabamorf_disambiguate(self, docs):
        # TODO for Timo: extract vabamorf disambiguator from analyzer and apply it here
        return docs

    def pre_disambiguate(self, docs):
        return docs

    def stat_disambiguate(self, docs):
        return docs

    def post_disambiguate(self, docs):
        return docs

