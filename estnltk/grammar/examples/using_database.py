# -*- coding: utf-8 -*-
"""Example showing how to use a grammar with a database and prettyprinter.
The example assumes the user is running an ElasticSearch instance containing
some documents from Estonian Koondkorpus.
"""
from __future__ import unicode_literals, print_function, absolute_import

from ..grammar import *
from ...prettyprinter import PrettyPrinter, HEADER, MIDDLE, FOOTER
from ...database import Database
from pprint import pprint

space = Regex('\s+')


# grammar extracting three adjectives + one substantive
grammar = Concatenation(
    Postags('A'),
    space,
    Postags('A'),
    space,
    Postags('A'),
    space,
    Postags('S'),
    name='fraas'
)


if __name__ == '__main__':
    db = Database('koond')
    docs = db.query_documents('"A A A S"', size=10)
    #docs = db.query_documents('universum', size=10)
    for doc in docs:
        grammar.annotate(doc)
        pprint(doc.texts('fraas'))

    # kui prettyprinter toimima saab, siis peaks järgneb kood töötama
    '''
    pp = PrettyPrinter(background='sentences')
    parts = [HEADER, pp.css, MIDDLE]
    for doc in docs:
        pprint (doc.keys())
        grammar.annotate(doc)
        parts.append(pp.render(doc, add_header=False))
        parts.append('\n')
    parts.append(FOOTER)
    print ('\n'.format(parts))
    '''
