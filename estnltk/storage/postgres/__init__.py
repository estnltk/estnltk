"""This package provides tools to conveniently store and search `estnltk` text objects in a postgres database.

Example usage:

    # connect to database, create a new table
    storage = PostgresStorage(dbname='estnltk', user='***', password='***')
    table = 'tmp'
    storage.create_table(table)

    # insert some data
    text = Text('ööbik laulab.').analyse('morphology')
    key = storage.insert(table, text)

    # select all data in the table
    for key, text in storage.select(table):
        print(key, text)

    # search by key
    txt = storage.select_by_key(table, key=key)

    # search using layer attributes
    q = JsonbQuery('morph_analysis', lemma='laulma')
    for key, txt in storage.select(table, query=q):
        print(key, txt)

    # search using composite query
    q = (JsonbQuery('morph_analysis', lemma='ööbik') | JsonbQuery('morph_analysis', lemma='öökull')) &
        JsonbQuery('morph_analysis', lemma='laulma')
    for key, txt in storage.select(table, query=q):
        print(key, txt)

"""
from .db import PostgresStorage, JsonbQuery
