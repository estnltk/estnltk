import unittest
import random

from estnltk import Text
from estnltk import get_logger_with_tqdm_handler
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema
from estnltk.storage import postgres as pg

logger = get_logger_with_tqdm_handler('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestIndexAndSliceQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_index_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').tag_layer('words')
            collection_insert(text1, key=3)
            text2 = Text('palju kell on?').tag_layer('words')
            collection_insert(text2, key=4)
            text2 = Text('kus kell on?').tag_layer('words')
            collection_insert(text2, key=5)
            text2 = Text('kes Kell on?').tag_layer('words')
            collection_insert(text2, key=6)

        res = list(collection.select(pg.IndexQuery(keys=[])))
        self.assertEqual(len(res), 0)

        res = list(collection.select(pg.IndexQuery(keys=[1])))
        self.assertEqual(len(res), 0)

        res = list(collection.select(pg.IndexQuery(keys=[3])))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['mis kell on?'] )

        res = list(collection.select(pg.IndexQuery(keys=[1, 3])))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['mis kell on?'] )

        res = list(collection.select(pg.IndexQuery(keys=[3, 4])))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['mis kell on?', 'palju kell on?'] )

        res = list(collection.select(pg.IndexQuery(keys=[3, 4, 5, 6])))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['mis kell on?', 'palju kell on?',
                                          'kus kell on?', 'kes Kell on?'] )

        self.storage.delete_collection(collection.name)


    def test_slice_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').tag_layer('words')
            collection_insert(text1, key=1)
            text2 = Text('palju kell on?').tag_layer('words')
            collection_insert(text2, key=2)
            text2 = Text('kus kell on?').tag_layer('words')
            collection_insert(text2, key=3)
            text2 = Text('kes Kell on?').tag_layer('words')
            collection_insert(text2, key=4)
            text2 = Text('kas kell on relevantne?').tag_layer('words')
            collection_insert(text2, key=5)

        res = list(collection.select(pg.SliceQuery(start=1, stop=1)))
        self.assertEqual(len(res), 0)

        res = list(collection.select(pg.SliceQuery(start=1, stop=2)))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['mis kell on?'] )

        res = list(collection.select(pg.SliceQuery(start=2, stop=4)))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['palju kell on?', 'kus kell on?'] )

        res = list(collection.select(pg.SliceQuery(start=3, stop=None)))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['kus kell on?', 'kes Kell on?', \
                                          'kas kell on relevantne?'] )

        res = list(collection.select(pg.SliceQuery(start=None, stop=3)))
        res_texts = [text_obj.text for tid, text_obj in res]
        self.assertListEqual( res_texts, ['mis kell on?', 'palju kell on?'] )

        self.storage.delete_collection(collection.name)