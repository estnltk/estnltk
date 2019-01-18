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

from .sql_strings import fragment_table_name
from .sql_strings import layer_table_name

from .pg_operations import create_schema
from .pg_operations import create_collection_table
from .pg_operations import create_structure_table

from .pg_operations import delete_schema

from .pg_operations import collection_table_identifier
from .pg_operations import layer_table_identifier

from .pg_operations import table_exists
from .pg_operations import table_identifier
from .pg_operations import collection_table_exists
from .pg_operations import structure_table_exists
from .pg_operations import layer_table_exists
from .pg_operations import fragment_table_exists

from .pg_operations import drop_collection_table
from .pg_operations import drop_structure_table
from .pg_operations import drop_fragment_table
from .pg_operations import drop_layer_table

from .pg_operations import count_rows

from .collection import RowMapperRecord
from .collection import PgCollection
from .storage import PgStorageException
from .storage import PostgresStorage
