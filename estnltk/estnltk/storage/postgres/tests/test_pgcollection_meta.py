"""Tests PgCollectionMeta functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.
"""
import random
import unittest
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema

from estnltk import Text
from estnltk import logger

from estnltk.storage import postgres as pg
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage.postgres.collection_meta import PgCollectionMeta
from estnltk.storage.postgres.collection_meta_selection import PgCollectionMetaSelection


logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgCollectionMeta(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            # TODO: for some reason we get DuplicateSchema error. Unexpected?
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_collection_meta_columns(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), 
                                            ('text_name', 'str'),
                                            ('text_letter', 'str'),
                                            ('missing_metadata', 'str')]))
        letters = 'ABCDEFGHIJ'
        with collection.insert() as collection_insert:
            for i in range(len(letters)):
                text_str = 'See on {}. tekst.'.format(i+1)
                collection_insert( Text( text_str ), 
                                   meta_data={'text_id': i,
                                              'text_name': '{}. tekst.'.format(i+1),
                                              'text_letter': letters[i]} )
        meta = PgCollectionMeta(collection)
        # Assert metadata columns can be retrieved
        assert meta.columns == ['text_id', 'text_name', 'text_letter', 'missing_metadata']
        collection.delete()

    def test_collection_meta_select_single_index(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), 
                                            ('text_name', 'str'),
                                            ('text_letter', 'str'),
                                            ('missing_metadata', 'str')]))
        letters = 'ABCDEFGHIJ'
        with collection.insert() as collection_insert:
            for i in range(len(letters)):
                text_str = 'See on {}. tekst.'.format(i+1)
                collection_insert( Text( text_str ).tag_layer('words'), 
                                   meta_data={'text_id': i,
                                              'text_name': '{}. tekst.'.format(i+1),
                                              'text_letter': letters[i]} )
        meta = PgCollectionMeta(collection)
        
        # Select single item with all available metadata
        assert meta[0] == {'text_id': 0, 
                           'text_name': '1. tekst.', 
                           'text_letter': 'A', 
                           'missing_metadata': None}
        assert meta[9] == {'text_id': 9, 
                           'text_name': '10. tekst.', 
                           'text_letter': 'J', 
                           'missing_metadata': None}
        
        # Select single item with specific metadata
        assert meta[6, ['text_name', 'text_letter']] == \
                       {'text_name': '7. tekst.', 'text_letter': 'G'}
        assert meta[7, 'text_letter'] == {'text_letter': 'H'}
        assert meta[7, 'text_letter'] == meta[7, ['text_letter']]
        
        # Select single item w/o metadata
        assert meta[8, []] == {}
        
        collection.delete()


    def test_collection_meta_selection_from_slice(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), 
                                            ('text_name', 'str'),
                                            ('text_letter', 'str'),
                                            ('missing_metadata', 'str')]))
        letters = 'ABCDEFGHIJ'
        with collection.insert() as collection_insert:
            for i in range(len(letters)):
                text_str = 'See on {}. tekst.'.format(i+1)
                collection_insert( Text( text_str ).tag_layer('words'), 
                                   meta_data={'text_id': i,
                                              'text_name': '{}. tekst.'.format(i+1),
                                              'text_letter': letters[i]} )
        
        meta = PgCollectionMeta(collection)
        
        # Assert that slice returns iterable
        assert isinstance(meta[1:3], PgCollectionMetaSelection)
        
        # Select slice over metadata over all available metadata columns
        assert list(meta[1:3]) == [{'text_id': 1, 'text_name': '2. tekst.', 
                                    'text_letter': 'B', 'missing_metadata': None}, 
                                   {'text_id': 2, 'text_name': '3. tekst.', 
                                    'text_letter': 'C', 'missing_metadata': None}]
        assert list(meta[1:3]) == list(meta[1:3, ['text_id', 'text_name', 
                                                  'text_letter', 'missing_metadata']])
        
        # Assert that slice returns iterable
        assert isinstance( meta[5:7,['text_name','text_letter']],\
                           PgCollectionMetaSelection )
        
        # Select slice with specific metadata
        assert list(meta[5:7, ['text_name', 'text_letter'] ]) == \
                [{'text_name': '6. tekst.', 'text_letter': 'F'}, \
                 {'text_name': '7. tekst.', 'text_letter': 'G'}]
        assert list(meta[7:10, 'text_letter' ]) == \
                [{'text_letter': 'H'}, {'text_letter': 'I'}, {'text_letter': 'J'}]
        assert list(meta[7:, 'text_letter' ]) == list(meta[7:10, 'text_letter' ])
        assert list(meta[:4, ['text_name'] ]) == \
                [ {'text_name': '1. tekst.'}, {'text_name': '2. tekst.'}, 
                  {'text_name': '3. tekst.'}, {'text_name': '4. tekst.'} ]

        collection.delete()


    def test_collection_meta_selection_from_list_of_indexes(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), 
                                            ('text_name', 'str'),
                                            ('text_letter', 'str'),
                                            ('missing_metadata', 'str')]))
        letters = 'ABCDEFGHIJ'
        with collection.insert() as collection_insert:
            for i in range(len(letters)):
                text_str = 'See on {}. tekst.'.format(i+1)
                collection_insert( Text( text_str ).tag_layer('words'), 
                                   meta_data={'text_id': i,
                                              'text_name': '{}. tekst.'.format(i+1),
                                              'text_letter': letters[i]} )
        
        meta = PgCollectionMeta(collection)
        
        # Assert that list of indexes returns iterable
        assert isinstance(meta[[3,4,5]], PgCollectionMetaSelection)
        
        # Select items with all available metadata
        assert list(meta[[3,4,5]]) == [{'text_id': 3, 'text_name': '4. tekst.', 
                                        'text_letter': 'D', 'missing_metadata': None},
                                       {'text_id': 4, 'text_name': '5. tekst.', 
                                        'text_letter': 'E', 'missing_metadata': None},
                                       {'text_id': 5, 'text_name': '6. tekst.', 
                                        'text_letter': 'F', 'missing_metadata': None}]
        
        assert list(meta[[3,6]]) == [{'text_id': 3, 'text_name': '4. tekst.', 
                                      'text_letter': 'D', 'missing_metadata': None},
                                     {'text_id': 6, 'text_name': '7. tekst.', 
                                      'text_letter': 'G', 'missing_metadata': None}]
        
        # Assert that list of indexes returns iterable
        assert isinstance(meta[[3,4,5],['text_name','text_letter']], \
                          PgCollectionMetaSelection)
        
        # Select items with specific metadata
        assert list(meta[[2,8,9], ['text_name', 'text_letter']]) == \
            [{'text_name': '3. tekst.', 'text_letter': 'C'},
             {'text_name': '9. tekst.', 'text_letter': 'I'},
             {'text_name': '10. tekst.', 'text_letter': 'J'}]
        assert list(meta[[1,6,9], ['text_letter']]) == \
            [{'text_letter': 'B'}, {'text_letter': 'G'}, {'text_letter': 'J'}]
        
        collection.delete()

if __name__ == '__main__':
    unittest.main()
