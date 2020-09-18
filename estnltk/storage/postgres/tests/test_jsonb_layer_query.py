import unittest
import random

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage, layer_table_identifier
from estnltk.storage.postgres import create_schema, delete_schema, count_rows
from estnltk.storage import postgres as pg
from estnltk.taggers import VabamorfTagger
from estnltk.finite_grammar import ngram_fingerprint, phrase_list_generator
from estnltk.storage.postgres.queries.jsonb_layer_query import JsonbLayerQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


# @TODO: Currently not working
class TestJsonbLayerQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_jsonb_layer_query(self):
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

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik')
        self.assertEqual(len(list(collection.select(query=q))), 1)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(query=q))), 1)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik') | JsonbLayerQuery(layer_name=layer1_name,
                                                                                     lemma='mis')
        self.assertEqual(len(list(collection.select(query=q))), 2)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik') & JsonbLayerQuery(layer_name=layer1_name,
                                                                                     lemma='mis')
        self.assertEqual(len(list(collection.select(query=q))), 0)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik')
        text = [text for key, text in collection.select(query=q)][0]
        self.assertTrue(layer1_name not in text.layers)

        text = list(collection.select(query=q, layers=[layer1_name]))[0][1]
        self.assertTrue(layer1_name in text.layers)

        # test with 2 layers
        layer2 = "layer2"
        layer2_table = layer2
        tagger2 = VabamorfTagger(disambiguate=True, output_layer=layer2)

        collection.create_layer(tagger=tagger2)

        q = JsonbLayerQuery(layer_name=layer2_table, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(query=q))), 1)

        text = list(collection.select(query=q, layers=[layer1_name, layer2]))[0][1]
        self.assertTrue(layer1_name in text.layers)
        self.assertTrue(layer2 in text.layers)

        collection.delete()
