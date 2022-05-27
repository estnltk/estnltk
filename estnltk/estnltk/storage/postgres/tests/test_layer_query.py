import unittest
import random

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage, layer_table_identifier
from estnltk.storage.postgres import create_schema, delete_schema, count_rows
from estnltk.taggers import VabamorfTagger
from estnltk.storage.postgres.queries.layer_query import LayerQuery

from estnltk.storage.postgres.tests.test_sparse_layer import ModuleRemainderNumberTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestAttachedLayerQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_attached_layer_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.').tag_layer(['morph_analysis'])
            collection_insert(text1)

            text2 = Text('Öökull ei laula.').tag_layer(['morph_analysis'])
            collection_insert(text2)

            text3 = Text('Auto sõidab mööda teed').tag_layer(['morph_analysis'])
            collection_insert(text3)

            text4 = Text('Peakokk ei oska teed valmistada').tag_layer(['morph_analysis'])
            collection_insert(text4)

        q = LayerQuery('morph_analysis', lemma='laulma')
        self.assertEqual(len(list(collection.select(query=q))), 2)

        q = LayerQuery('morph_analysis', lemma='tee')
        self.assertEqual(len(list(collection.select(query=q))), 2)

        q = LayerQuery('morph_analysis', lemma='jooksma')
        self.assertEqual(len(list(collection.select(query=q))), 0)

        collection.delete()


class TestDetachedLayerQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_detached_layer_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
            collection_insert(text1)

            text2 = Text('Mis kell on?').tag_layer(["sentences"])
            collection_insert(text2)

        layer1_name = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer1_name)

        collection.create_layer(tagger=tagger1)

        q = LayerQuery(layer_name=layer1_name, lemma='ööbik')
        self.assertEqual(len(list(collection.select(query=q))), 1)

        q = LayerQuery(layer_name=layer1_name, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(query=q))), 1)

        q = LayerQuery(layer_name=layer1_name, lemma='ööbik') | LayerQuery(layer_name=layer1_name,
                                                                                     lemma='mis')
        self.assertEqual(len(list(collection.select(query=q))), 2)

        q = LayerQuery(layer_name=layer1_name, lemma='ööbik') & LayerQuery(layer_name=layer1_name,
                                                                                     lemma='mis')
        self.assertEqual(len(list(collection.select(query=q))), 0)

        q = LayerQuery(layer_name=layer1_name, lemma='ööbik')
        text = [text for key, text in collection.select(query=q)][0]
        self.assertTrue(layer1_name not in text.layers)

        text = list(collection.select(query=q, layers=[layer1_name]))[0][1]
        self.assertTrue(layer1_name in text.layers)

        # test with 2 layers
        layer2 = "layer2"
        layer2_table = layer2
        tagger2 = VabamorfTagger(disambiguate=True, output_layer=layer2)

        collection.create_layer(tagger=tagger2)

        q = LayerQuery(layer_name=layer2_table, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(query=q))), 1)

        text = list(collection.select(query=q, layers=[layer1_name, layer2]))[0][1]
        self.assertTrue(layer1_name in text.layers)
        self.assertTrue(layer2 in text.layers)

        collection.delete()


class TestDetachedSparseLayerQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()
        
    def test_detached_sparse_layer_query(self):
        # Test that LayerQuery successfully works with detached sparse layers
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')
        
        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(30):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )
        
        # Add sparse layers
        even_number_tagger = ModuleRemainderNumberTagger('even_numbers', 2, 0)
        fourth_number_tagger = ModuleRemainderNumberTagger('fourth_numbers', 4, 0, 
                                                            parent_layer='even_numbers')
        collection.create_layer( tagger=even_number_tagger,   sparse=True )
        collection.create_layer( tagger=fourth_number_tagger, sparse=True )
        
        # Make a small LayerQuery
        q = LayerQuery(layer_name='even_numbers', normalized=2) | \
            LayerQuery(layer_name='even_numbers', normalized=22)
        q_result = list( collection.select(query=q, layers=['even_numbers']) )
        self.assertEqual(len(q_result), 2)
        self.assertEqual( q_result[0][0], 2 )
        self.assertEqual( q_result[1][0], 22 )
        self.assertTrue( 'even_numbers' in q_result[0][1].layers )
        self.assertTrue( 'even_numbers' in q_result[1][1].layers )

        # Make a larger LayerQuery
        q = LayerQuery(layer_name='even_numbers', module=2)
        q_result = list( collection.select(query=q, 
                         layers=['even_numbers', 'fourth_numbers']) )
        self.assertEqual(len(q_result), 15)
        text_ids = []
        for (text_id, text) in q_result:
            # Assert that spare layer exists
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'fourth_numbers' in text.layers )
            text_ids.append( text_id )
        self.assertEqual(text_ids, \
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28])

        # Make a LayerQuery over a combination of sparse layers
        q = LayerQuery(layer_name='even_numbers', module=2) & \
            LayerQuery(layer_name='fourth_numbers', module=4)
        q_result = list( collection.select(query=q, 
                         layers=['even_numbers', 'fourth_numbers']) )
        text_ids = []
        for (text_id, text) in q_result:
            # Assert that spare layer exists
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'fourth_numbers' in text.layers )
            text_ids.append( text_id )
        self.assertEqual(text_ids, [0, 4, 8, 12, 16, 20, 24, 28])
        