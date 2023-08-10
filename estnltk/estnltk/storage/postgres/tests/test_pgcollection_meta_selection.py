"""Test PgCollectionMetaSelection functionality.

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
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres.collection_meta_selection import PgCollectionMetaSelection


logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgCollectionMetaSelection(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def test_collection_meta_selection_from_single_index(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection( collection_name, 
                          meta=OrderedDict([('text_id', 'int'), 
                                            ('text_name', 'str'),
                                            ('text_letter', 'str'),
                                            ('missing_metadata', 'str')]) )
        letters = 'ABCDEFGHIJ'
        with collection.insert() as collection_insert:
            for i in range(len(letters)):
                text_str = 'See on {}. tekst.'.format(i+1)
                collection_insert( Text( text_str ), 
                                   meta_data={'text_id': i,
                                              'text_name': '{}. tekst.'.format(i+1),
                                              'text_letter': letters[i]} )

        # Selecting nothing should return an empty list
        selected = list(PgCollectionMetaSelection(collection))
        assert selected == []
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[]))
        assert selected == []

        # Select single item with all available metadata
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[0]))
        assert selected == [(0, {'text_id': 0, 'text_name': '1. tekst.', 
                                 'text_letter': 'A', 
                                 'missing_metadata': None})]

        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[9]))
        assert selected == [(9, {'text_id': 9, 'text_name': '10. tekst.', 
                                 'text_letter': 'J', 
                                 'missing_metadata': None})]
        # ... meta without indexes
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[0],
                                                  return_index=False))
        assert selected == [{'text_id': 0, 'text_name': '1. tekst.', 
                             'text_letter': 'A', 
                             'missing_metadata': None}]
        
        # Select single item with specific metadata
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[6],
                                                  selected_attributes=['text_name',
                                                                       'text_letter']))
        assert selected == [(6, {'text_name': '7. tekst.', 'text_letter': 'G'})]
        
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[7],
                                                  selected_attributes=['text_letter']))
        assert selected == [(7, {'text_letter': 'H'})]
        # ... meta without indexes
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[6],
                                                  selected_attributes=['text_name',
                                                                       'text_letter'],
                                                  return_index=False))
        assert selected == [{'text_name': '7. tekst.', 'text_letter': 'G'}]

        # Select single item w/o metadata
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[8],
                                                  selected_attributes=[]))
        assert selected == [(8, {})]
        # ... meta without indexes
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[8],
                                                  selected_attributes=[],
                                                  return_index=False))
        assert selected == [{}]
        
        self.storage.delete_collection(collection.name)


    def test_collection_meta_selection_from_slice(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection( collection_name, 
                          meta=OrderedDict([('text_id', 'int'), 
                                            ('text_name', 'str'),
                                            ('text_letter', 'str'),
                                            ('missing_metadata', 'str')]) )
        letters = 'ABCDEFGHIJ'
        with collection.insert() as collection_insert:
            for i in range(len(letters)):
                text_str = 'See on {}. tekst.'.format(i+1)
                collection_insert( Text( text_str ), 
                                   meta_data={'text_id': i,
                                              'text_name': '{}. tekst.'.format(i+1),
                                              'text_letter': letters[i]} )

        # Select slice over metadata over all available metadata columns
        selected1 = list(PgCollectionMetaSelection(collection, 
                                                  selected_slice=slice(1,3)))
        assert selected1 == [(1, {'text_id': 1, 'text_name': '2. tekst.', 
                                  'text_letter': 'B', 'missing_metadata': None}), 
                             (2, {'text_id': 2, 'text_name': '3. tekst.', 
                                  'text_letter': 'C', 'missing_metadata': None})]
        selected2 = list(PgCollectionMetaSelection(collection, 
                                                   selected_slice=slice(1,3),
                                                   selected_attributes=['text_id',
                                                        'text_name', 'text_letter',
                                                        'missing_metadata']))
        assert selected2 == selected1
        # ... meta without indexes
        selected3 = list(PgCollectionMetaSelection(collection, 
                                                   selected_slice=slice(1,3),
                                                   return_index=False))
        assert selected3 == [{'text_id': 1, 'text_name': '2. tekst.', 
                             'text_letter': 'B', 'missing_metadata': None}, 
                             {'text_id': 2, 'text_name': '3. tekst.', 
                              'text_letter': 'C', 'missing_metadata': None}]
        # Select slice with specific metadata
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_slice=slice(5,7),
                                                  selected_attributes=['text_name',
                                                                       'text_letter']))
        assert selected == [(5, {'text_name': '6. tekst.', 'text_letter': 'F'}), \
                            (6, {'text_name': '7. tekst.', 'text_letter': 'G'})]
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_slice=slice(7,10),
                                                  selected_attributes=['text_letter']))
        assert selected == [(7, {'text_letter': 'H'}), 
                            (8, {'text_letter': 'I'}), 
                            (9, {'text_letter': 'J'})]
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_slice=slice(4),
                                                  selected_attributes=['text_name']))
        assert selected == [(0, {'text_name': '1. tekst.'}), 
                            (1, {'text_name': '2. tekst.'}), 
                            (2, {'text_name': '3. tekst.'}),
                            (3, {'text_name': '4. tekst.'})]
        # ... meta without indexes
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_slice=slice(5,7),
                                                  selected_attributes=['text_name',
                                                                       'text_letter'],
                                                  return_index=False))
        assert selected == [{'text_name': '6. tekst.', 'text_letter': 'F'}, \
                            {'text_name': '7. tekst.', 'text_letter': 'G'}]
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_slice=slice(4),
                                                  selected_attributes=['text_name'],
                                                  return_index=False))
        assert selected == [{'text_name': '1. tekst.'}, 
                            {'text_name': '2. tekst.'}, 
                            {'text_name': '3. tekst.'},
                            {'text_name': '4. tekst.'}]
        self.storage.delete_collection(collection.name)


    def test_collection_meta_selection_from_list_of_indexes(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection( collection_name, 
                          meta=OrderedDict([('text_id', 'int'), 
                                            ('text_name', 'str'),
                                            ('text_letter', 'str'),
                                            ('missing_metadata', 'str')]) )
        letters = 'ABCDEFGHIJ'
        with collection.insert() as collection_insert:
            for i in range(len(letters)):
                text_str = 'See on {}. tekst.'.format(i+1)
                collection_insert( Text( text_str ), 
                                   meta_data={'text_id': i,
                                              'text_name': '{}. tekst.'.format(i+1),
                                              'text_letter': letters[i]} )

        # Select items with all available metadata
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[3,4,5]))
        assert selected == [(3, {'text_id': 3, 'text_name': '4. tekst.', 
                                 'text_letter': 'D', 'missing_metadata': None}),
                            (4, {'text_id': 4, 'text_name': '5. tekst.', 
                                 'text_letter': 'E', 'missing_metadata': None}),
                            (5, {'text_id': 5, 'text_name': '6. tekst.', 
                                 'text_letter': 'F', 'missing_metadata': None})]
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[3,6]))
        assert selected == [(3, {'text_id': 3, 'text_name': '4. tekst.', 
                                 'text_letter': 'D', 'missing_metadata': None}),
                            (6, {'text_id': 6, 'text_name': '7. tekst.', 
                                 'text_letter': 'G', 'missing_metadata': None})]
        # ... meta without indexes
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[3,4,5],
                                                  return_index=False))
        assert selected == [{'text_id': 3, 'text_name': '4. tekst.', 
                             'text_letter': 'D', 'missing_metadata': None}, 
                            {'text_id': 4, 'text_name': '5. tekst.', 
                             'text_letter': 'E', 'missing_metadata': None}, 
                            {'text_id': 5, 'text_name': '6. tekst.', 
                             'text_letter': 'F', 'missing_metadata': None}]
        
        # Select items with specific metadata
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[2,8,9],
                                                  selected_attributes=['text_name',
                                                                       'text_letter']))
        assert selected == [(2, {'text_name': '3. tekst.', 'text_letter': 'C'}),
                            (8, {'text_name': '9. tekst.', 'text_letter': 'I'}),
                            (9, {'text_name': '10. tekst.', 'text_letter': 'J'})]
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[1,6,9],
                                                  selected_attributes=['text_letter']))
        assert selected == [(1, {'text_letter': 'B'}), 
                            (6, {'text_letter': 'G'}), 
                            (9, {'text_letter': 'J'})]
        # ... meta without indexes
        selected = list(PgCollectionMetaSelection(collection, 
                                                  selected_indexes=[2,8,9],
                                                  selected_attributes=['text_name',
                                                                       'text_letter'],
                                                  return_index=False))
        assert selected == [{'text_name': '3. tekst.', 'text_letter': 'C'},
                            {'text_name': '9. tekst.', 'text_letter': 'I'},
                            {'text_name': '10. tekst.', 'text_letter': 'J'}]
        self.storage.delete_collection(collection.name)

if __name__ == '__main__':
    unittest.main()
