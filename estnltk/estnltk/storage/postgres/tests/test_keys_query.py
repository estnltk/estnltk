import unittest
import random

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage import postgres as pg

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestKeysQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_keys_query(self):
        collection = self.storage[get_random_collection_name()]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').tag_layer('morph_analysis')
            collection_insert(text1, key=3)
            text2 = Text('palju kell on?').tag_layer('morph_analysis')
            collection_insert(text2, key=4)
            text2 = Text('kus kell on?').tag_layer('morph_analysis')
            collection_insert(text2, key=5)
            text2 = Text('kes Kell on?').tag_layer('morph_analysis')
            collection_insert(text2, key=6)

        res = list(collection.select(pg.IndexQuery(keys=[])))
        self.assertEqual(len(res), 0)

        res = list(collection.select(pg.IndexQuery(keys=[1])))
        self.assertEqual(len(res), 0)

        res = list(collection.select(pg.IndexQuery(keys=[3])))
        self.assertEqual(len(res), 1)

        res = list(collection.select(pg.IndexQuery(keys=[1, 3])))
        self.assertEqual(len(res), 1)

        res = list(collection.select(pg.IndexQuery(keys=[3, 4])))
        self.assertEqual(len(res), 2)

        res = list(collection.select(pg.IndexQuery(keys=[3, 4, 5, 6])))
        self.assertEqual(len(res), 4)

        collection.delete()
