import unittest
import random

from psycopg2.sql import SQL

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage import postgres as pg
from estnltk.taggers import VabamorfTagger

from estnltk.storage.postgres.tests.test_sparse_layer import ModuleRemainderNumberTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestMissingLayerQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.schema = schema
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_missing_layer_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
            collection_insert(text1)

            text2 = Text('Mis kell on?').tag_layer(["sentences"])
            collection_insert(text2)

            text3 = Text('Auto sõidab.').tag_layer(["sentences"])
            collection_insert(text3)
            
            text4 = Text('Kägu kukub.').tag_layer(["sentences"])
            collection_insert(text4)
            
            text5 = Text('Aga kella ikka ei ole...').tag_layer(["sentences"])
            collection_insert(text5)

        layer1 = "layer1"
        layer2 = "layer2"
        layer3 = "layer3"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer1)
        tagger2 = VabamorfTagger(disambiguate=False, output_layer=layer2)
        tagger3 = VabamorfTagger(disambiguate=False, output_layer=layer3)

        collection.create_layer(tagger=tagger1)
        collection.create_layer(tagger=tagger2)
        collection.create_layer(tagger=tagger3)

        with self.storage.conn.cursor() as c:
            c.execute(SQL("DELETE FROM {}.{}__layer1__layer WHERE id = 0;").format(
                SQL(self.schema),
                SQL(collection_name)))

            c.execute(SQL("DELETE FROM {}.{}__layer3__layer WHERE id = 0 OR id = 1 OR id = 4;").format(
                SQL(self.schema),
                SQL(collection_name)))

        res = list(collection.select(query=pg.MissingLayerQuery(missing_layer=layer1)))
        self.assertEqual(len(res), 1)

        res = list(collection.select(query=pg.MissingLayerQuery(missing_layer=layer2)))
        self.assertEqual(len(res), 0)

        res = list(collection.select(query=pg.MissingLayerQuery(missing_layer=layer3)))
        self.assertEqual(len(res), 3)

        collection.delete()

    def test_missing_layer_query_on_sparse_layer(self):
        # Test that MissingLayerQuery works with sparse layers
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')
        
        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(30):
                text = Text('See on tekst number {}'.format(i))
                text.tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )

        # Add sparse layers
        even_number_tagger = ModuleRemainderNumberTagger('even_numbers', 2, 0)
        fourth_number_tagger = ModuleRemainderNumberTagger('fourth_numbers', 4, 0, 
                                                            parent_layer='even_numbers')
        collection.create_layer( tagger=even_number_tagger,  sparse=True )
        collection.create_layer( tagger=fourth_number_tagger, sparse=True )
        
        # Note: in case of sparse layers, MissingLayerQuery returns texts 
        # that had corresponding layers left empty during the annotation process 
        res = list(collection.select(query=pg.MissingLayerQuery(missing_layer='even_numbers')))
        self.assertEqual(len(res), 15)
        expected_text_ids = \
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
        self.assertEqual(expected_text_ids, [text_id for text_id, text in res])
        res = list(collection.select(query=pg.MissingLayerQuery(missing_layer='fourth_numbers')))
        self.assertEqual(len(res), 22)
        expected_text_ids = \
            [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 29]
        self.assertEqual(expected_text_ids, [text_id for text_id, text in res])
        
        res = list(collection.select(query=pg.MissingLayerQuery(missing_layer='even_numbers') &
                                           pg.MissingLayerQuery(missing_layer='fourth_numbers'),
                                     layers=['fourth_numbers']))
        expected_text_ids = \
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
        self.assertEqual(expected_text_ids, [text_id for text_id, text in res])
        for text_id, text in res:
            self.assertEqual( len(text['even_numbers']), 0 )
            self.assertEqual( len(text['fourth_numbers']), 0 )
        
        collection.delete()