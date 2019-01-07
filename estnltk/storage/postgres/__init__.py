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
from .jsonb_layer_query import JsonbLayerQuery
from .jsnob_text_query import JsonbTextQuery
from .pg_operations import create_schema
from .pg_operations import delete_schema
from .pg_operations import count_rows
from .pg_operations import create_table
from .pg_operations import drop_table
from .pg_operations import drop_table_if_exists
from .pg_operations import table_exists
from .db import RowMapperRecord
from .db import PgCollection
from .postgres_storage import PgStorageException
from .postgres_storage import PostgresStorage
