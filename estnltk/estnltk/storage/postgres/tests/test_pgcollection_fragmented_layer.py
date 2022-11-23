"""Test pgcollection's fragmented layer functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest

from estnltk_core import Layer
from estnltk import Text
from estnltk import logger
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import table_exists
from estnltk.taggers import VabamorfTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestLayerFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_layer_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer_fragment_name = "layer_fragment_1"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer_fragment_name)

        def fragmenter(layer):
            # layer.serialisation_module = 'default_v1'
            return [layer, layer]

        collection.create_fragmented_layer(tagger=tagger1, fragmenter=fragmenter)

        self.assertTrue(collection.has_layer(layer_fragment_name))
        self.assertTrue(collection.has_layer(layer_fragment_name, 'fragmented'))
        self.assertFalse(collection.has_layer(layer_fragment_name, 'detached'))

        # One does not simply select a fragmented layer
        with self.assertRaises(TypeError):
            collection.selected_layers = [layer_fragment_name]
        
        # Assert that fragmented layers cannot be selected in the subcollection
        with self.assertRaises(TypeError):
            collection.select(layers=['sentences', layer_fragment_name])
        pg_subcollection = collection.select(layers=['sentences'])
        with self.assertRaises(TypeError):
            pg_subcollection.select(selected_layers=[layer_fragment_name, 'sentences'])

        # Try an illegal insert: insert Text object after a fragmented layer has been added
        with self.assertRaises(pg.PgCollectionException):
            with collection.insert() as collection_insert:
                collection_insert.insert(Text('üks tekst').tag_layer("sentences"))

        rows = list(collection.select().fragmented_layer(name=layer_fragment_name))

        assert len(rows) == 4
        text_ids = [row[0] for row in rows]
        self.assertEqual(text_ids[0], text_ids[1])
        self.assertEqual(text_ids[2], text_ids[3])
        self.assertNotEqual(text_ids[1], text_ids[2])

        for row in rows:
            assert len(row) == 2, row
            assert isinstance(row[0], int), row
            assert isinstance(row[1], Layer), row
            assert row[1].text_object is None

        self.assertTrue(layer_table_exists(self.storage, collection.name, layer_fragment_name, layer_type='fragmented'))

        self.storage.delete_collection(collection.name)

        self.assertFalse(layer_table_exists(self.storage, collection.name, layer_fragment_name, layer_type='fragmented'))


class TestFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer_fragment_name = "layer_fragment_1"
        tagger = VabamorfTagger(disambiguate=False, output_layer=layer_fragment_name)

        collection.create_layer(tagger=tagger)

        self.assertTrue(collection.has_layer(layer_fragment_name))

        fragment_name = "fragment_1"
        fragment_layer_template = tagger.get_layer_template()
        fragment_layer_template.name = fragment_name

        def row_mapper(row):
            parent_id, layer = row
            # TODO: remove next line
            # layer.serialisation_module = 'default_v1'
            layer.name = fragment_name
            return [{'fragment': layer, 'parent_id': parent_id},
                    {'fragment': layer, 'parent_id': parent_id}]

        collection.create_fragmented_layer(layer_template=fragment_layer_template,
                                           data_iterator=collection.select().fragmented_layer(name=layer_fragment_name),
                                           row_mapper=row_mapper,
                                           create_index=False,
                                           ngram_index=None)

        self.assertTrue(collection.has_layer(fragment_name, 'fragmented'))
        self.assertFalse(collection.has_layer(fragment_name, 'detached'))

        rows = list(collection.select_fragment_raw(fragment_name, layer_fragment_name))
        self.assertEqual(len(rows), 4)

        row = rows[0]
        self.assertEqual(len(row), 6)
        self.assertIsInstance(row[0], int)
        self.assertIsInstance(row[1], Text)
        self.assertIsInstance(row[2], int)
        self.assertIsInstance(row[3], Layer)
        self.assertIsInstance(row[4], int)
        self.assertIsInstance(row[5], Layer)

        assert layer_table_exists(self.storage, collection.name, fragment_name, layer_type='fragmented')
        collection.delete_layer(fragment_name)
        assert not layer_table_exists(self.storage, collection.name, fragment_name, layer_type='fragmented')



if __name__ == '__main__':
    unittest.main()
