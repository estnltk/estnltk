import unittest
import random

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage.postgres.queries.jsonb_text_query import JsonbTextQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestJsonbTextQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_jsonb_text_query(self):
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

        q = JsonbTextQuery('morph_analysis', lemma='laulma')
        self.assertEqual(len(list(collection.select(query=q))), 2)

        q = JsonbTextQuery('morph_analysis', lemma='tee')
        self.assertEqual(len(list(collection.select(query=q))), 2)

        q = JsonbTextQuery('morph_analysis', lemma='jooksma')
        self.assertEqual(len(list(collection.select(query=q))), 0)

        collection.delete()
