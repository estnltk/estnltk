import unittest
import pytest
import random
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema, UniqueViolation

from estnltk import logger
from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import create_schema, delete_schema

from estnltk.storage.postgres.queries.slice_query import SliceQuery
from estnltk.storage.postgres import PgCollectionException

from estnltk.storage.postgres.tests.test_sparse_layer import ModuleRemainderNumberTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgSubCollectionCreateLayer(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)
        self.maxDiff = None

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def test_subcollection_create_layer(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')

        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(200):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )
        
        # 1) Make a selection and create layer
        odd_number_tagger = ModuleRemainderNumberTagger('odd_numbers', 2, 1)
        collection.select(query=SliceQuery(0, 25) | \
                                SliceQuery(125, 150)).create_layer(odd_number_tagger)
        # Assert the layer has been created and it's sparse
        self.assertTrue( collection.has_layer( odd_number_tagger.output_layer ) )
        self.assertTrue( collection.is_sparse( odd_number_tagger.output_layer ) )
        # Assert the layer's content: select texts with only non-empty layers
        res = list(collection.select(layers=['odd_numbers'], keep_all_texts=False))
        expected_text_ids = \
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 125, 127, 129, 131, 133, \
             135, 137, 139, 141, 143, 145, 147, 149]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res])
        for text_id, text in res:
            self.assertTrue( odd_number_tagger.output_layer in text.layers )
            self.assertEqual( len(text[odd_number_tagger.output_layer]), 1 )

        # 2) Make a selection and create child layer (with keep_all_texts=True)
        third_number_tagger = ModuleRemainderNumberTagger('third_numbers', 3, 0,
                                    parent_layer=odd_number_tagger.output_layer )
        collection.select(query=SliceQuery(25, 75) | \
                                SliceQuery(100, 150)).create_layer(third_number_tagger)
        # Assert the layer has been created and it's sparse
        self.assertTrue( collection.has_layer( third_number_tagger.output_layer ) )
        self.assertTrue( collection.is_sparse( third_number_tagger.output_layer ) )
        # Assert the layer's content: select texts with only non-empty layers
        res = list(collection.select(layers=['third_numbers'], keep_all_texts=False))
        for text_id, text in res:
            self.assertTrue( odd_number_tagger.output_layer in text.layers )
            self.assertTrue( third_number_tagger.output_layer in text.layers )
            self.assertEqual( len(text[odd_number_tagger.output_layer]), 1 )
            self.assertEqual( len(text[third_number_tagger.output_layer]), 1 )
        expected_text_ids = \
            [129, 135, 141, 147]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res])

        # 3) Make a selection and create child layer (with keep_all_texts=False)
        third_number_tagger2 = ModuleRemainderNumberTagger('third_numbers_2', 3, 0,
                                    parent_layer=odd_number_tagger.output_layer )
        collection.select(query=SliceQuery(25, 75) |  \
                                SliceQuery(100, 150), \
                                keep_all_texts=False).create_layer(third_number_tagger2)
        # Assert the layer has been created and it's sparse
        self.assertTrue( collection.has_layer( third_number_tagger2.output_layer ) )
        self.assertTrue( collection.is_sparse( third_number_tagger2.output_layer ) )
        # Assert the layer's content: select texts with only non-empty layers
        res = list(collection.select(layers=['third_numbers_2'], keep_all_texts=False))
        for text_id, text in res:
            self.assertTrue( odd_number_tagger.output_layer in text.layers )
            self.assertTrue( third_number_tagger2.output_layer in text.layers )
            self.assertEqual( len(text[odd_number_tagger.output_layer]), 1 )
            self.assertEqual( len(text[third_number_tagger2.output_layer]), 1 )
        expected_text_ids = \
            [129, 135, 141, 147]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res])
        
        # 4) Continue creating layers (mode='append')
        collection.select(query=SliceQuery(50, 75) | \
                                SliceQuery(100, 125)).create_layer(odd_number_tagger, 
                                                                   mode='append')
        collection.select(query=SliceQuery(0, 25) |  \
                                SliceQuery(100, 125), \
                                keep_all_texts=False).create_layer(third_number_tagger2, 
                                                                   mode='append')
        # Assert the layer's content: select texts with only non-empty layers
        res1 = list(collection.select(layers=['odd_numbers'], keep_all_texts=False))
        expected_text_ids = \
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 51, 53, 55, 57, 59, 61, 63, \
             65, 67, 69, 71, 73, 101, 103, 105, 107, 109, 111, 113, 115, 117, 119,  \
             121, 123, 125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, 147, 149]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res1])
        res2 = list(collection.select(layers=['third_numbers_2'], keep_all_texts=False))
        expected_text_ids = \
            [3, 9, 15, 21, 105, 111, 117, 123, 129, 135, 141, 147]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res2])
        
        # 5) Test error situations: 

        layer_len_before = \
            len(list(collection.select(layers=['odd_numbers'], keep_all_texts=False)))
        
        # trying to insert texts with the same id twice (mode="new")
        selectionX = collection.select(query=SliceQuery(0, 25), layers=['words'])
        with pytest.raises(PgCollectionException):
            # PgCollectionException: can't create 'odd_numbers' layer, the layer 
            # already exists
            selectionX.create_layer(odd_number_tagger)
        
        layer_len_after1 = \
            len(list(collection.select(layers=['odd_numbers'], keep_all_texts=False)))
        self.assertEqual( layer_len_before, layer_len_after1 )
        
        # trying to insert texts with the same id twice (mode="append")
        with pytest.raises(UniqueViolation):
            # psycopg2.errors.UniqueViolation: duplicate key value violates unique 
            # constraint "collection_XXXXXX__odd_numbers__layer_pkey"
            selectionX.create_layer(odd_number_tagger, mode='append')
        
        layer_len_after2 = \
            len(list(collection.select(layers=['odd_numbers'], keep_all_texts=False)))
        self.assertEqual( layer_len_before, layer_len_after2 )
        
        collection.delete()


    def test_subcollection_create_layer_block(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')

        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(200):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )

        # 1) Make a selection and create layer
        odd_number_tagger = ModuleRemainderNumberTagger('odd_numbers', 2, 1)
        collection.add_layer( odd_number_tagger.get_layer_template(), sparse=True )
        selection1 = collection.select(query=SliceQuery(0, 50))
        selection1.create_layer_block(odd_number_tagger, (3, 0))
        selection1.create_layer_block(odd_number_tagger, (3, 1))
        selection1.create_layer_block(odd_number_tagger, (3, 2))
        # Assert the layer has been created and it's sparse
        self.assertTrue( collection.has_layer( odd_number_tagger.output_layer ) )
        self.assertTrue( collection.is_sparse( odd_number_tagger.output_layer ) )
        selection2 = collection.select(query=SliceQuery(75, 100), layers=['words'])
        selection2.create_layer_block(odd_number_tagger, (2, 0))
        selection2.create_layer_block(odd_number_tagger, (2, 1))
        # Assert the layer's content: 
        res = list(collection.select(layers=['odd_numbers'], keep_all_texts=False))
        expected_text_ids = \
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, \
             35, 37, 39, 41, 43, 45, 47, 49, 75, 77, 79, 81, 83, 85, 87, 89, \
             91, 93, 95, 97, 99]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res])

        # 2) Make a selection and create child layer (with keep_all_texts=True)
        fifth_number_tagger = ModuleRemainderNumberTagger('fifth_numbers', 5, 0,
                                    parent_layer=odd_number_tagger.output_layer )
        collection.add_layer( fifth_number_tagger.get_layer_template(), sparse=True )
        selection3 = collection.select(query=SliceQuery(0, 50))
        selection3.create_layer_block(fifth_number_tagger, (3, 0))
        selection3.create_layer_block(fifth_number_tagger, (3, 1))
        selection3.create_layer_block(fifth_number_tagger, (3, 2))
        selection4 = collection.select(query=SliceQuery(150, 200), layers=['words'])
        selection4.create_layer_block(fifth_number_tagger, (2, 0))
        selection4.create_layer_block(fifth_number_tagger, (2, 1))
        # Assert the layer's content: 
        res = list(collection.select(layers=['fifth_numbers'], keep_all_texts=False))
        expected_text_ids = \
            [5, 15, 25, 35, 45]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res])
        for text_id, text in res:
            self.assertTrue( odd_number_tagger.output_layer in text.layers )
            self.assertTrue( fifth_number_tagger.output_layer in text.layers )
            self.assertEqual( len(text[odd_number_tagger.output_layer]), 1 )
            self.assertEqual( len(text[fifth_number_tagger.output_layer]), 1 )

        # 3) Make a selection and create child layer (with keep_all_texts=False)
        fifth_number_tagger2 = ModuleRemainderNumberTagger('fifth_numbers_2', 5, 0,
                                    parent_layer=odd_number_tagger.output_layer )
        collection.add_layer( fifth_number_tagger2.get_layer_template(), sparse=True )
        selection5 = collection.select(query=SliceQuery(0, 25), keep_all_texts=False)
        selection5.create_layer_block(fifth_number_tagger2, (2, 0))
        selection5.create_layer_block(fifth_number_tagger2, (2, 1))
        selection6 = collection.select(query=SliceQuery(25, 50), layers=['words'], 
                                       keep_all_texts=False)
        selection6.create_layer_block(fifth_number_tagger2, (3, 0))
        selection6.create_layer_block(fifth_number_tagger2, (3, 1))
        selection6.create_layer_block(fifth_number_tagger2, (3, 2))
        # Assert the layer's content: 
        res = list(collection.select(layers=['fifth_numbers_2'], keep_all_texts=False))
        expected_text_ids = \
            [5, 15, 25, 35, 45]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res])
        for text_id, text in res:
            self.assertTrue( odd_number_tagger.output_layer in text.layers )
            self.assertTrue( fifth_number_tagger2.output_layer in text.layers )
            self.assertEqual( len(text[odd_number_tagger.output_layer]), 1 )
            self.assertEqual( len(text[fifth_number_tagger2.output_layer]), 1 )

        # 4) Continue creating layers (mode='append')
        selection7 = collection.select(query=SliceQuery(150, 200), layers=['words'])
        selection7.create_layer_block(odd_number_tagger, (2, 0), mode='append')
        selection7.create_layer_block(odd_number_tagger, (2, 1), mode='append')
        selection8 = collection.select(query=SliceQuery(150, 200), layers=['words'], 
                                       keep_all_texts=False)
        selection8.create_layer_block(fifth_number_tagger2, (3, 0), mode='append')
        selection8.create_layer_block(fifth_number_tagger2, (3, 1), mode='append')
        selection8.create_layer_block(fifth_number_tagger2, (3, 2), mode='append')
        res1 = list(collection.select(layers=['odd_numbers'], keep_all_texts=False))
        expected_text_ids = \
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 
             37, 39, 41, 43, 45, 47, 49, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 
             95, 97, 99, 151, 153, 155, 157, 159, 161, 163, 165, 167, 169, 171, 
             173, 175, 177, 179, 181, 183, 185, 187, 189, 191, 193, 195, 197, 199]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res1])
        res2 = list(collection.select(layers=['fifth_numbers_2'], keep_all_texts=False))
        expected_text_ids = \
            [5, 15, 25, 35, 45, 155, 165, 175, 185, 195]
        self.assertListEqual(expected_text_ids, [text_id for text_id, text in res2])
        
        # 5) Test error situations: 

        layer_len_before = \
            len(list(collection.select(layers=['odd_numbers'], keep_all_texts=False)))
        
        # trying to insert texts with the same id twice (mode="new")
        selectionX = collection.select(query=SliceQuery(150, 200), layers=['words'])
        with pytest.raises(UniqueViolation):
            # psycopg2.errors.UniqueViolation: duplicate key value violates unique 
            # constraint "collection_XXXXXX__odd_numbers__layer_pkey"
            selectionX.create_layer_block(odd_number_tagger, (2, 0))
            selectionX.create_layer_block(odd_number_tagger, (2, 1))
        layer_len_after1 = \
            len(list(collection.select(layers=['odd_numbers'], keep_all_texts=False)))
        self.assertEqual( layer_len_before, layer_len_after1 )
        
        # trying to insert texts with the same id twice (mode="append")
        selectionX.create_layer_block(odd_number_tagger, (2, 0), mode='append')
        selectionX.create_layer_block(odd_number_tagger, (2, 1), mode='append')
        # nothing should have happened: we should have same amount of tagged texts
        layer_len_after2 = \
            len(list(collection.select(layers=['odd_numbers'], keep_all_texts=False)))
        self.assertEqual( layer_len_before, layer_len_after2 )

        collection.delete()


if __name__ == '__main__':
    unittest.main()