import unittest
import random

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema, count_rows
from estnltk.storage import postgres as pg

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


# @TODO: Currently not working
class TestLayerNgramQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_layer_ngram_query(self):
        collection = self.storage[get_random_collection_name()]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Teeme ühe naljaka katse').tag_layer(['morph_analysis'])
            collection_insert(text1, meta_data=text1.meta)

            text2 = Text('Joome õhtul teed').tag_layer(['morph_analysis'])
            collection_insert(text2, meta_data=text2.meta)

            text3 = Text('Sõidan autoga tee peal').tag_layer(['morph_analysis'])
            collection_insert(text3, meta_data=text3.meta)

        res = list(collection.find_fingerprint(layer_ngram_query=pg.LayerNgramQuery({
            'morph_analysis': {"lemma": [("sõitma", "auto")]}})))
        self.assertEqual(len(res), 3)

        res = list(collection.find_fingerprint(layer_ngram_query=pg.LayerNgramQuery({
            'morph_analysis': {"lemma": ["auto"]}})))
        print(res)
        self.assertEqual(len(res), 3)

        collection.delete()
