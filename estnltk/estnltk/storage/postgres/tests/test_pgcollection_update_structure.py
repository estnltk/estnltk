""""
Test updating postgres' collection to a new version.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.
"""
import time
import random
import unittest
from collections import OrderedDict

from psycopg2.sql import SQL, Literal, Identifier
from psycopg2.extensions import STATUS_BEGIN

from estnltk import Text
from estnltk import get_logger_with_tqdm_handler
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer

from estnltk.storage import postgres as pg
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres.structure.update_structure import update_structure


logger = get_logger_with_tqdm_handler('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


def _create_collection_with_version(storage: 'PostgresStorage', name: str, version: str, \
                                    meta=[], create_index=False):
    '''Creates a collection with specific version for testing. 
       This code has been taken from the PostgresStorage.add_collection(...) method.
    '''
    # Add storage.collections entry (collection name + version)
    with storage.conn.cursor() as c:
        try:
            # EXCLUSIVE locking -- this mode allows only reads from the table 
            # can proceed in parallel with a transaction holding this lock mode.
            # Prohibit all other modification operations such as delete, insert, 
            # update, create index.
            # (https://www.postgresql.org/docs/9.4/explicit-locking.html)
            c.execute(SQL('LOCK TABLE ONLY {} IN EXCLUSIVE MODE').format( \
                                storage.collections_table ) )
            # Check if collection has been recorded in collection's table
            storage.refresh(omit_commit=True, omit_rollback=True)
            if name not in storage.collections:
                # Note: we need to make insertion before creating PgCollection, 
                # because creating PgCollection involves db queries with commits, 
                # which would release the lock
                c.execute(SQL(
                        "INSERT INTO {} (collection, version) "
                        "VALUES ({}, {});").format(
                        storage.collections_table,
                        Literal(name),
                        Literal(version)
                ))
                collection = PgCollection(name, storage, version=version)
            else:
                raise Exception(('collection {!r} already exists.').format(name))
        except Exception as adding_error:
            storage.conn.rollback()
            raise Exception(('(!) Cannot add new collection {!r} '+\
                                      'due to an exception: {}').format( \
                                            name, adding_error)) from adding_error
        finally:
            if storage.conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                storage.conn.commit()
    # At this point, either PgCollection object was successfully created and 
    # inserted into the collections table, or exception was encountered (due
    # to collection already existing or some other problem).
    # Update the storage_collections view
    try:
        # Create structure table (contains information about collection's layers)
        collection.structure.create_layer_info_table()
        description = 'created by {} on {}'.format(storage.user, time.asctime())
        # Create collection table (stores Text objects with attached layers and metadata columns)
        collection.structure.create_collection_table(meta_columns=meta,
                                                     description=description,
                                                     create_index=create_index)
        logger.info('new empty collection {!r} (with version {}) created'.format(name, version))
    except Exception as adding_error:
        raise Exception(('(!) Cannot add new collection {!r} '+\
                                     'due to an exception: {}').format( \
                                        name, adding_error)) from adding_error
    storage.conn.commit()
    return collection

def get_columns_of_table(storage: 'PostgresStorage', table_name: str, only_names=False):
    '''Find table's columns along with their respective data types from the Pg 
       information_schema table. 
       If parameter only_names is set, then returns only column names (a list of 
       strings). 
    '''
    with storage.conn.cursor() as c:
        c.execute(SQL('SELECT column_name, data_type from information_schema.columns '
                      'WHERE table_schema={} and table_name={} '
                      'ORDER BY ordinal_position'
                      ).format(Literal(storage.schema), 
                               Literal(table_name)))
        results = list(c.fetchall())
        if not only_names:
            return results
        else:
            return [cname for (cname, ctype) in results]
    return []


class TestPgCollectionUpdateStructure(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = pg.PostgresStorage(pgpass_file='~/.pgpass', schema=schema, \
                                          dbname='test_db', create_schema_if_missing=True)

    def tearDown(self):
        pg.delete_schema(self.storage)
        self.storage.close()
    
    def restart_connection(self):
        self.storage.close()
        schema = "test_schema"
        self.storage = pg.PostgresStorage(pgpass_file='~/.pgpass', schema=schema, \
                                          dbname='test_db', create_schema_if_missing=False)

    def test_update_v2_0_to_v4_0(self):
        # Create an old collection with version 2.0
        collection_name = get_random_collection_name()
        collection = _create_collection_with_version(self.storage, collection_name, '2.0', 
                                                     meta=OrderedDict([('meta_1', 'str'), 
                                                                       ('meta_2', 'int')]))
        # Check version
        self.storage.refresh()
        collection = self.storage[collection_name]
        self.assertEqual(collection.version, '2.0')
        # Add data to the collection
        texts = ['Esimene lause. Teine lause. Kolmas lause.',
                 'Teine tekst',
                 'Ööbik laulab. Öökull ei laula.',
                 'Mis kell on?']
        with collection.insert() as collection_insert:
            for i, t in enumerate(texts):
                text = Text(t).tag_layer(['compound_tokens'])
                collection_insert(text, meta_data={'meta_1': 'value_' + str(i), 'meta_2': i})
        self.assertEqual(len(collection), 4)
        word_tagger = WordTagger()
        collection.create_layer(tagger=word_tagger)
        sentence_tagger = SentenceTokenizer()
        collection.create_layer(tagger=sentence_tagger)
        vabamorf_tagger = VabamorfTagger(disambiguate=False)
        collection.create_layer(tagger=vabamorf_tagger)
        # Check the collection structure (should correspond to 2.0)
        collection_columns = get_columns_of_table( \
                                    self.storage, f'{collection_name}', \
                                    only_names=True)
        self.assertListEqual(collection_columns, \
                             ['id', 'data', 'meta_1', 'meta_2'])
        struct_columns = get_columns_of_table(self.storage, \
                                              f'{collection_name}__structure', \
                                              only_names=True)
        self.assertListEqual(struct_columns, \
                             ['layer_name', 'attributes', 'ambiguous', 'parent', 'enveloping', \
                              'meta', 'layer_type', 'serialisation_module'])
        
        # Update structure to the version 4.0
        update_structure(self.storage, collection_name, '4.0')
        # Restart connection (for the update to take effect)
        self.restart_connection()
        # Check version
        collection = self.storage[collection_name]
        self.assertEqual(collection.version, '4.0')
        # Check the collection structure (should correspond to 4.0)
        collection_columns = get_columns_of_table( \
                                    self.storage, f'{collection_name}', \
                                    only_names=True)
        self.assertListEqual(collection_columns, \
                             ['id', 'data', 'hidden', 'meta_1', 'meta_2'])
        struct_columns = get_columns_of_table(self.storage, \
                                              f'{collection_name}__structure', \
                                              only_names=True)
        self.assertListEqual(struct_columns, \
                             ['layer_name', 'attributes', 'span_names', 'ambiguous', 'sparse', \
                              'parent', 'enveloping', 'meta', 'layer_type', 'serialisation_module', \
                              'layer_template'])
        # Validate collection
        self.assertEqual(len(collection), 4)
        # Validate document order and layers
        self.assertEqual(collection[0].text , 'Esimene lause. Teine lause. Kolmas lause.')
        self.assertEqual(collection[1].text , 'Teine tekst')
        self.assertEqual(collection[3].text , 'Mis kell on?')
        self.assertSetEqual( set(collection.layers), 
                             {'compound_tokens', 'tokens', 'words', 'sentences', 'morph_analysis'} )


    def test_update_v3_0_to_v4_0(self):
        # Create an old collection with version 3.0
        collection_name = get_random_collection_name()
        collection = _create_collection_with_version(self.storage, collection_name, '3.0', 
                                                     meta=OrderedDict([('meta_1', 'str'), 
                                                                       ('meta_2', 'int')]))
        # Check version
        self.storage.refresh()
        collection = self.storage[collection_name]
        self.assertEqual(collection.version, '3.0')
        # Add data to the collection
        texts = ['Esimene lause. Teine lause. Kolmas lause.',
                 'Teine tekst',
                 'Ööbik laulab. Öökull ei laula.',
                 'Mis kell on?']
        with collection.insert() as collection_insert:
            for i, t in enumerate(texts):
                text = Text(t).tag_layer(['compound_tokens'])
                collection_insert(text, meta_data={'meta_1': 'value_' + str(i), 'meta_2': i})
        self.assertEqual(len(collection), 4)
        word_tagger = WordTagger()
        collection.create_layer(tagger=word_tagger)
        sentence_tagger = SentenceTokenizer()
        collection.create_layer(tagger=sentence_tagger)
        vabamorf_tagger = VabamorfTagger(disambiguate=False)
        collection.create_layer(tagger=vabamorf_tagger)
        # Check the collection structure (should correspond to 3.0)
        collection_columns = get_columns_of_table( \
                                    self.storage, f'{collection_name}', \
                                    only_names=True)
        self.assertListEqual(collection_columns, \
                             ['id', 'data', 'meta_1', 'meta_2'])
        struct_columns = get_columns_of_table(self.storage, \
                                              f'{collection_name}__structure', \
                                              only_names=True)
        self.assertListEqual(struct_columns, \
                             ['layer_name', 'attributes', 'ambiguous', 'sparse', 'parent', \
                              'enveloping', 'meta', 'layer_type', 'serialisation_module', \
                              'layer_template'])
        
        # Update structure to the version 4.0
        update_structure(self.storage, collection_name, '4.0')
        # Restart connection (for the update to take effect)
        self.restart_connection()
        # Check version
        collection = self.storage[collection_name]
        self.assertEqual(collection.version, '4.0')
        # Check the collection structure (should correspond to 4.0)
        collection_columns = get_columns_of_table( \
                                    self.storage, f'{collection_name}', \
                                    only_names=True)
        self.assertListEqual(collection_columns, \
                             ['id', 'data', 'hidden', 'meta_1', 'meta_2'])
        struct_columns = get_columns_of_table(self.storage, \
                                              f'{collection_name}__structure', \
                                              only_names=True)
        self.assertListEqual(struct_columns, \
                             ['layer_name', 'attributes', 'span_names', 'ambiguous', 'sparse', \
                              'parent', 'enveloping', 'meta', 'layer_type', 'serialisation_module', \
                              'layer_template'])
        # Validate collection
        self.assertEqual(len(collection), 4)
        # Validate document order and layers
        self.assertEqual(collection[0].text , 'Esimene lause. Teine lause. Kolmas lause.')
        self.assertEqual(collection[1].text , 'Teine tekst')
        self.assertEqual(collection[3].text , 'Mis kell on?')
        self.assertSetEqual( set(collection.layers), 
                             {'compound_tokens', 'tokens', 'words', 'sentences', 'morph_analysis'} )
        
