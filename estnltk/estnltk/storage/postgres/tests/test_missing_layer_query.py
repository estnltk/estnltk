import unittest
import random

from psycopg2.sql import SQL

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage import postgres as pg
from estnltk.taggers import VabamorfTagger

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
