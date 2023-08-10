"""Test pgcollection's detached layer functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest

from estnltk_core import Layer
from estnltk import Text
from estnltk import logger
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import LayerQuery
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import count_rows
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers import VabamorfTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))



class TestDetachedLayer(unittest.TestCase):
    def setUp(self):
        self.schema = "test_layer"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=self.schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_layer_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer1 = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer1)

        collection.create_layer(tagger=tagger1)

        tagger1.tag(text1)
        tagger1.tag(text2)

        layer2 = "layer2"
        tagger2 = VabamorfTagger(disambiguate=False, output_layer=layer2)

        collection.create_layer(tagger=tagger2)

        tagger2.tag(text1)
        tagger2.tag(text2)

        self.assertTrue(collection.has_layer('words', 'attached'))
        self.assertTrue(collection.has_layer('sentences', 'attached'))
        self.assertTrue(collection.has_layer(layer1, 'detached'))
        self.assertTrue(collection.has_layer(layer2, 'detached'))

        for key, text in collection.select(layers=['sentences']):
            self.assertTrue("sentences" in text.layers)
            self.assertTrue(layer1 not in text.layers)
            self.assertTrue(layer2 not in text.layers)

        rows = list(collection.select(layers=[layer1, layer2]))
        text1_db = rows[0][1]
        self.assertTrue(layer1 in text1_db.layers)
        self.assertTrue(layer2 in text1_db.layers)
        self.assertEqual(text1_db[layer1].lemma, text1[layer1].lemma)
        self.assertEqual(text1_db[layer2].lemma, text1[layer2].lemma)

        self.storage.delete_collection(collection.name)
        self.assertFalse(layer_table_exists(self.storage, collection.name, layer1))
        self.assertFalse(layer_table_exists(self.storage, collection.name, layer2))

    def test_add_layer(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Test case 1: Add layer from user-defined layer template
        layer_template = Layer('test_layer', ['attr_1', 'attr_2'], ambiguous=True)

        # Test that add_layer() cannot be applied on an empty collection
        with self.assertRaises(pg.PgCollectionException):
            collection.add_layer( layer_template )
        
        # Add some documents to the collection
        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer('words')
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer('words')
            collection_insert(text2)
        
        # Add layer from the template (creates an empty layer)
        collection.add_layer( layer_template )
       
        self.assertTrue( layer_table_exists(self.storage, collection.name, layer_template.name) )
        self.assertTrue( layer_template.name in collection.layers )
        
        # If the layer already exists, adding a layer template should rise PgCollectionException
        with self.assertRaises( pg.PgCollectionException ):
            collection.add_layer( layer_template )
        
        # Add some annotations to the layer
        def row_mapper_x(row):
            text_id, text = row[0], row[1]
            layer = Layer('test_layer', ['attr_1', 'attr_2'], ambiguous=True)
            layer.add_annotation( (0, 3), attr_1='a', attr_2='b' )
            return RowMapperRecord( layer=layer, meta={} )

        collection.create_layer(layer_template=layer_template,
                                data_iterator=collection.select(),
                                row_mapper=row_mapper_x,
                                mode='overwrite')
        
        # Check added data
        res = collection.select( query = LayerQuery(layer_template.name, attr_1='a') )
        self.assertEqual(len(list(res)), 2)
        
        # 2) Add layer from Tagger's layer template
        sent_tokenizer = SentenceTokenizer()
        layer_template_2 = sent_tokenizer.get_layer_template()
        collection.add_layer( layer_template_2 )
        
        self.assertTrue( layer_table_exists(self.storage, collection.name, layer_template_2.name) )
        self.assertTrue( layer_template_2.name in collection.layers )
        
        collection.create_layer(tagger=sent_tokenizer, mode='overwrite')
        
        self.storage.delete_collection(collection.name)

    def test_delete_detached_layers(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        with collection.insert() as collection_insert:
            collection_insert(Text('see on esimene lause'))
            collection_insert(Text('see on teine lause'))

        tokens = Layer(name='tokens', parent=None, enveloping=None, text_object=None)
        words = Layer(name='words', parent=None, enveloping=None, text_object=None)
        sentences = Layer(name='sentences', parent=None, enveloping='words', text_object=None)
        paragraphs = Layer(name='paragraphs', parent=None, enveloping='sentences', text_object=None)
        morph_analysis = \
            Layer(name='morph_analysis', parent='words', enveloping=None, text_object=None)
        morph_extended = \
            Layer(name='morph_extended', parent='morph_analysis', enveloping=None, text_object=None)
        syntax = Layer(name='syntax', parent='morph_extended', enveloping=None, text_object=None)
        # Add detached layers to the collection
        for layer in [tokens, words, sentences, paragraphs, morph_analysis, morph_extended, syntax]:
            collection.add_layer(layer)
        # Delete layers that have no (explicit) dependencies
        self.assertListEqual( collection.layers, \
            ['tokens', 'words', 'sentences', 'paragraphs', 'morph_analysis', 'morph_extended', 'syntax'])
        collection.delete_layer('tokens')
        self.assertListEqual( collection.layers, \
            ['words', 'sentences', 'paragraphs', 'morph_analysis', 'morph_extended', 'syntax'])
        collection.delete_layer('paragraphs')
        self.assertListEqual( collection.layers, \
            ['words', 'sentences', 'morph_analysis', 'morph_extended', 'syntax'])
        # Layer that has dependencies can't be deleted by default
        with self.assertRaises(PgCollectionException):
            collection.delete_layer('morph_extended')
        self.assertListEqual( collection.layers, \
            ['words', 'sentences', 'morph_analysis', 'morph_extended', 'syntax'])
        # However, it can be deleted with cascade=True
        collection.delete_layer('morph_extended', cascade=True)
        self.assertListEqual( collection.layers, ['words', 'sentences', 'morph_analysis'])
        collection.delete_layer('words', cascade=True)
        self.assertListEqual( collection.layers, [])

        self.storage.delete_collection(collection.name)

    def test_create_layer_block(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Add some documents to the collection
        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer('words')
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer('words')
            collection_insert(text2)
            text3 = Text('ja see paistab olevat kolmas').tag_layer('words')
            collection_insert(text3)
            text4 = Text('üks lause veel siia lõppu').tag_layer('words')
            collection_insert(text4)
            text5 = Text('ja veel üks').tag_layer('words')
            collection_insert(text5)
        
        # Add layer from Tagger's layer template
        sent_tokenizer = SentenceTokenizer()
        layer_template = sent_tokenizer.get_layer_template()
        collection.add_layer( layer_template )
        
        self.assertTrue( layer_table_exists(self.storage, collection.name, layer_template.name) )
        self.assertTrue( layer_template.name in collection.layers )
        initial_rows = count_rows( self.storage, 
                                   table=layer_table_name(collection.name, layer_template.name) )
        self.assertEqual( initial_rows, 0 )

        # Tag the first block
        collection.create_layer_block( sent_tokenizer, (2, 0) )
        inserted_rows = count_rows( self.storage, 
                                    table=layer_table_name(collection.name, layer_template.name))
        self.assertEqual( inserted_rows, 3 )
        # Tag the second block
        collection.create_layer_block( sent_tokenizer, (2, 1) )
        inserted_rows = count_rows( self.storage, 
                                    table=layer_table_name(collection.name, layer_template.name) )
        self.assertEqual( inserted_rows, 5 )
        
        for key, text in collection.select(layers=['sentences']):
            self.assertTrue("sentences" in text.layers)
            self.assertEqual( len(text['sentences']), 1 )
        
        self.storage.delete_collection(collection.name)

    def test_layer_meta(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer1 = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer1)
        layer_template=tagger1.get_layer_template()

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.make_layer(text)
            return RowMapperRecord(layer=layer, meta={"meta_text_id": text_id, "sum": 45.5})

        collection.create_layer(layer_template=layer_template,
                                data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                row_mapper=row_mapper1,
                                meta={"meta_text_id": "int",
                                      "sum": "float"})
        self.assertTrue(layer_table_exists(self.storage, collection.name, layer1))

        # get_layer_meta
        layer_meta = collection.get_layer_meta(layer_name=layer1)
        assert layer_meta.to_dict() == {'id': {0: 0, 1: 1},
                                        'meta_text_id': {0: 0, 1: 1},
                                        'sum': {0: 45.5, 1: 45.5},
                                        'text_id': {0: 0, 1: 1}}, layer_meta.to_dict()

        with self.assertRaises(PgCollectionException):
            collection.get_layer_meta(layer_name='not_exists')

        assert set(collection.structure[layer1]['meta']) == {'sum', 'meta_text_id'}

        self.storage.delete_collection(collection.name)

    def test_detached_layer_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
            collection_insert(text1)

            text2 = Text('Mis kell on?').tag_layer(["sentences"])
            collection_insert(text2)

        layer1 = "layer1"
        layer2 = "layer2"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer1)
        tagger2 = VabamorfTagger(disambiguate=False, output_layer=layer2)

        collection.create_layer(tagger=tagger1)
        collection.create_layer(tagger=tagger2)

        #
        # Note: the following tests previously targeted find_fingerprint,
        #       which is a deprecated method and will be removed.
        #       But we'll keep the tests to check that the same queries
        #       can be made via select().
        #
        # test one layer
        # "query": ["ööbik"]
        res = collection.select( query = LayerQuery(layer1, lemma="ööbik") )
        self.assertEqual(len(list(res)), 1)

        # "query": ["ööbik", "mis"],  # ööbik OR mis
        res = collection.select( query = LayerQuery(layer1, lemma="ööbik") | 
                                         LayerQuery(layer1, lemma="mis") )
        self.assertEqual(len(list(res)), 2)

        # "query": [["ööbik", "mis"]],  # ööbik AND mis
        res = collection.select( query = LayerQuery(layer1, lemma="ööbik") & 
                                         LayerQuery(layer1, lemma="mis") )
        self.assertEqual(len(list(res)), 0)

        # "query": [["ööbik", "laulma"]],  # ööbik AND laulma
        res = collection.select( query = LayerQuery(layer1, lemma="ööbik") & 
                                         LayerQuery(layer1, lemma="laulma") )
        self.assertEqual(len(list(res)), 1)

        # test multiple layers
        # layer1: "query": ["ööbik"]; layer2: "query": ["ööbik"];
        res = collection.select( query = LayerQuery(layer1, lemma="ööbik") & 
                                         LayerQuery(layer2, lemma="ööbik") )
        self.assertEqual(len(list(res)), 1)


if __name__ == '__main__':
    unittest.main()
