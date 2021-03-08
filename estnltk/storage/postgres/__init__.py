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
from estnltk.storage.postgres.sql_composition.sql_table_naming import collection_table_name
from estnltk.storage.postgres.sql_composition.sql_table_naming import structure_table_name
from estnltk.storage.postgres.sql_composition.sql_table_naming import layer_table_name
from estnltk.storage.postgres.sql_composition.sql_table_naming import fragment_table_name

from .pg_operations import pytype2dbtype

from .pg_operations import collection_table_identifier
from .pg_operations import structure_table_identifier
from .pg_operations import layer_table_identifier
from .pg_operations import fragment_table_identifier

from .pg_operations import create_schema
from .pg_operations import create_collection_table

from .pg_operations import table_exists
from .pg_operations import table_identifier
from .pg_operations import get_all_table_names
from .pg_operations import get_all_tables
from .pg_operations import collection_table_exists
from .pg_operations import structure_table_exists
from .pg_operations import layer_table_exists
from .pg_operations import fragment_table_exists

from .pg_operations import delete_schema
from .pg_operations import drop_table
from .pg_operations import drop_collection_table
from .pg_operations import drop_structure_table
from .pg_operations import drop_fragment_table
from .pg_operations import drop_layer_table

from .pg_operations import count_rows

from estnltk.storage.postgres.queries.layer_query import LayerQuery
from estnltk.storage.postgres.queries.substring_query import SubstringQuery
from estnltk.storage.postgres.queries.block_query import BlockQuery
from estnltk.storage.postgres.queries.index_query import IndexQuery
from estnltk.storage.postgres.queries.missing_layer_query import MissingLayerQuery
from estnltk.storage.postgres.queries.layer_ngram_query import LayerNgramQuery
from estnltk.storage.postgres.queries.metadata_query import MetadataQuery

from estnltk.storage.postgres.context_managers.buffered_table_insert import BufferedTableInsert
from estnltk.storage.postgres.context_managers.collection_text_object_inserter import CollectionTextObjectInserter
from estnltk.storage.postgres.context_managers.collection_detached_layer_inserter import CollectionDetachedLayerInserter

from .structure.base.collection_structure_base import CollectionStructureBase
from .structure import v00
from .structure import v10
from .structure import v20

from .collection import RowMapperRecord
from .collection import PgCollection
from .collection import PgCollectionException

from .sql_composition.where_clause import WhereClause
from .sql_composition.selected_columns import SelectedColumns

from .pgpass_parsing import parse_pgpass

from .subcollectionlayer import PgSubCollectionLayer
from .subcollectionfragments import PgSubCollectionFragments
from .subcollection import PgSubCollection

from .storage_collections import StorageCollections
from .storage import PgStorageException
from .storage import PostgresStorage
