"""Test postgres storage functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest

from psycopg2.errors import DuplicateSchema

from estnltk_core import Layer
from estnltk import Text
from estnltk import logger
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import LayerQuery
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import collection_table_exists
from estnltk.storage.postgres import create_collection_table
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage.postgres import drop_collection_table
from estnltk.storage.postgres import fragment_table_exists
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import count_rows
from estnltk.taggers import ParagraphTokenizer
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers import VabamorfTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgCollection(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_storage_get_collections(self):
        # Test that the collections list can be accessed
        # even before it is filled in with collections 
        self.assertTrue( len( self.storage.collections ) == 0 )

    def test_create_collection(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]

        self.assertIs(collection, self.storage[collection_name])

        self.assertFalse(collection.exists())

        collection.create()

        self.assertTrue(collection.exists())

        self.assertIs(collection, self.storage[collection_name])

        # In case of an empty collection, collection.layers should be []
        self.assertTrue(collection.layers == [])

        collection.delete()

        collection = self.storage['not_existing']
        self.assertIsInstance(collection, PgCollection)

        collection.delete()
        self.assertFalse(collection.exists())

    def test_insert(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        text_1 = Text('Esimene tekst.')
        text_2 = Text('Teine tekst')
        text_3 = Text('Kolmas tekst')

        with collection.insert() as collection_insert:
            collection_insert(text_1)
            collection_insert(text_2)
            collection_insert(text_3)

        # If no layers have been added to collection, collection.layers should be []
        self.assertTrue(collection.layers == [])

        assert len(collection) == 3

        collection.delete()

    def test_basic_collection_workflow(self):
        # insert texts -> create layers -> select texts
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        text_1 = Text('Esimene lause. Teine lause. Kolmas lause.')
        text_2 = Text('Teine tekst')
        text_1.tag_layer(['sentences'])
        text_2.tag_layer(['sentences'])

        with collection.insert() as collection_insert:
            collection_insert(text_1, key=1)
            collection_insert(text_2, key=2)

        tagger1 = VabamorfTagger(disambiguate=False)
        collection.create_layer(tagger=tagger1)

        tagger1.tag(text_1)
        tagger1.tag(text_2)

        tagger2 = ParagraphTokenizer()
        collection.create_layer(tagger=tagger2)

        tagger2.tag(text_1)
        tagger2.tag(text_2)

        # Assert that added layers appear in the collection
        self.assertTrue('tokens' in collection.layers)
        self.assertTrue('compound_tokens' in collection.layers)
        self.assertTrue('words' in collection.layers)
        self.assertTrue('sentences' in collection.layers)
        self.assertTrue('paragraphs' in collection.layers)
        self.assertTrue('morph_analysis' in collection.layers)

        for text_id, text in collection.select(layers=['compound_tokens', 'morph_analysis', 'paragraphs']):
            if text_id == 1:
                assert text == text_1, text_1.diff(text)
            elif text_id == 2:
                assert text == text_2, text_2.diff(text)

        collection.delete()

    def test_collection_getitem_and_iter(self):
        # insert texts -> create layers -> select texts
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        text_1 = Text('Esimene lause. Teine lause. Kolmas lause.')
        text_2 = Text('Teine tekst')
        text_1.tag_layer(['sentences'])
        text_2.tag_layer(['sentences'])

        with collection.insert() as collection_insert:
            collection_insert(text_1, key=1)
            collection_insert(text_2, key=2)

        tagger1 = VabamorfTagger(disambiguate=False)
        collection.create_layer(tagger=tagger1)

        tagger1.tag(text_1)
        tagger1.tag(text_2)

        tagger2 = ParagraphTokenizer()
        collection.create_layer(tagger=tagger2)

        tagger2.tag(text_1)
        tagger2.tag(text_2)

        raw_text_set = {text_1.text, text_2.text}

        # test __iter__
        result = list(collection)
        assert len(result) == 2, result
        assert {text.text for text in result} == raw_text_set, result
        for text in result:
            assert set(text.layers) == {'sentences', 'words', 'tokens', 'compound_tokens'}

        # test __getitem__
        assert collection[1].text == text_1.text
        assert collection[2].text == text_2.text
        
        # test __getitem__ and attached layers
        collection.selected_layers = ['sentences']
        # attached layers included:
        self.assertTrue('words' in collection[1].layers)
        self.assertTrue('words' in collection[2].layers)
        self.assertTrue('sentences' in collection[1].layers)
        self.assertTrue('sentences' in collection[2].layers)
        # detached layers excluded:
        self.assertTrue('morph_analysis' not in collection[1].layers)
        self.assertTrue('morph_analysis' not in collection[2].layers)
        self.assertTrue('paragraphs' not in collection[1].layers)
        self.assertTrue('paragraphs' not in collection[2].layers)

        # test __getitem__ and detached layers
        collection.selected_layers = ['morph_analysis', 'paragraphs']
        self.assertTrue('words' in collection[1].layers)
        self.assertTrue('words' in collection[2].layers)
        self.assertTrue('sentences' in collection[1].layers)
        self.assertTrue('sentences' in collection[2].layers)
        self.assertTrue('paragraphs' in collection[1].layers)
        self.assertTrue('paragraphs' in collection[2].layers)
        self.assertTrue('morph_analysis' in collection[1].layers)
        self.assertTrue('morph_analysis' in collection[2].layers)
        
        with self.assertRaises(KeyError):
            collection[5]
        with self.assertRaises(KeyError):
            next(collection['bla'])

        # result = collection[1, 'paragraphs']
        # assert isinstance(result, Layer)
        # assert result.name == 'paragraphs'

    def test_collection_selected_layers_are_unique(self):
        # Test that duplicates are removed from selected_layers
        # (this is required for correct assembling of results)
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        text_1 = Text('Esimene lause. Teine lause. Kolmas lause.')
        text_2 = Text('Teine tekst')
        text_1.tag_layer('sentences')
        text_2.tag_layer('sentences')

        with collection.insert() as collection_insert:
            collection_insert(text_1, key=1)
            collection_insert(text_2, key=2)
            
        tagger1 = VabamorfTagger(disambiguate=False)
        collection.create_layer(tagger=tagger1)
        tagger2 = ParagraphTokenizer()
        collection.create_layer(tagger=tagger2)
        # Test that a single selected layer cannot be duplicated
        collection.selected_layers = \
            ['words', 'words', 'words', 'words']
        self.assertEqual( collection.selected_layers, ['words'] )
        # Test that multiple selected layer cannot be duplicated
        collection.selected_layers = \
            ['morph_analysis', 'paragraphs', 'paragraphs', 'morph_analysis']
        self.assertEqual( collection.selected_layers, \
            ['words', 'morph_analysis', 'sentences', 'paragraphs'] )
        
        collection.delete()

    def test_create_and_drop_collection_table(self):
        collection_name = get_random_collection_name()

        create_collection_table(self.storage, collection_name)
        assert collection_table_exists(self.storage, collection_name)
        assert table_exists(self.storage, collection_name)
        drop_collection_table(self.storage, collection_name)
        assert not collection_table_exists(self.storage, collection_name)
        assert not table_exists(self.storage, collection_name)

    def test_sql_injection(self):
        normal_collection_name = get_random_collection_name()
        create_collection_table(self.storage, normal_collection_name)
        self.assertTrue(collection_table_exists(self.storage, normal_collection_name))

        injected_collection_name = "%a; drop table %s;" % (get_random_collection_name(), normal_collection_name)
        create_collection_table(self.storage, injected_collection_name)
        self.assertTrue(collection_table_exists(self.storage, injected_collection_name))
        self.assertTrue(collection_table_exists(self.storage, normal_collection_name))

        drop_collection_table(self.storage, normal_collection_name)
        drop_collection_table(self.storage, injected_collection_name)

    def test_select(self):
        not_existing_collection = self.storage['not_existing']
        with self.assertRaises(pg.PgCollectionException):
            not_existing_collection.select()

        collection = self.storage[get_random_collection_name()]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.')

            id1 = collection_insert(text1, key=1)

            text2 = Text('Mis kell on?')
            id2 = collection_insert(text2, key=2)

        id1 = 1
        id2 = 2
        # test select_by_id
        self.assertEqual(collection[id1], text1)
        self.assertEqual(collection[id2], text2)

        subcollection = collection.select()
        assert isinstance(subcollection, pg.PgSubCollection)

        # test select_all
        res = list(subcollection)

        self.assertEqual(len(res), 2)
        id_, text = res[0]
        self.assertEqual(id_, id1)
        self.assertEqual(text, text1)
        id_, text = res[1]
        self.assertEqual(id_, id2)
        self.assertEqual(text, text2)

        collection.delete()

        collection = self.storage[get_random_collection_name()]
        collection.create()

        # test select (on attached layers)
        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').tag_layer('morph_analysis')
            collection_insert(text1, key=3)
            text2 = Text('palju kell on?').tag_layer('morph_analysis')
            collection_insert(text2, key=4)
        
        res = list(collection.select(query=LayerQuery('morph_analysis', lemma='mis')))
        self.assertEqual(len(res), 1)

        res = list(collection.select(query=LayerQuery('morph_analysis', lemma='kell')))
        self.assertEqual(len(res), 2)

        res = list(collection.select(query=LayerQuery('morph_analysis', lemma='mis') | LayerQuery('morph_analysis', lemma='palju')))
        self.assertEqual(len(res), 2)

        res = list(collection.select(query=LayerQuery('morph_analysis', lemma='mis') & LayerQuery('morph_analysis', lemma='palju')))
        self.assertEqual(len(res), 0)

        res = list(collection.select(query=(LayerQuery('morph_analysis', lemma='mis') | LayerQuery('morph_analysis', lemma='palju')) &
                                           LayerQuery('morph_analysis', lemma='kell')))
        self.assertEqual(len(res), 2)

        #
        # Note: the following tests previously targeted find_fingerprint,
        #       which is a deprecated method and will be removed.
        #       But we'll keep the tests to check that the same queries
        #       can be made via select().
        #
        #q["query"] = [{'miss1', 'miss2'}, {'miss3'}]
        q = (LayerQuery(layer_name="morph_analysis", lemma="miss1") & \
             LayerQuery(layer_name="morph_analysis", lemma="miss2")) | \
             LayerQuery(layer_name="morph_analysis", lemma="miss3")
        res = list(collection.select(query = q))
        self.assertEqual(len(res), 0)

        #q["query"] = [{'miss1', 'miss2'}, {'palju'}]
        q = (LayerQuery(layer_name="morph_analysis", lemma="miss1") & \
             LayerQuery(layer_name="morph_analysis", lemma="miss2")) | \
             LayerQuery(layer_name="morph_analysis", lemma="palju")
        res = list(collection.select(query = q))
        self.assertEqual(len(res), 1)

        #q["query"] = [{'mis', 'miss2'}, {'palju'}]
        q = (LayerQuery(layer_name="morph_analysis", lemma="mis") & \
             LayerQuery(layer_name="morph_analysis", lemma="miss2")) | \
             LayerQuery(layer_name="morph_analysis", lemma="palju")
        res = list(collection.select(query = q))
        self.assertEqual(len(res), 1)

        #q["query"] = [{'mis', 'kell'}, {'miss'}]
        q = (LayerQuery(layer_name="morph_analysis", lemma="mis") & \
             LayerQuery(layer_name="morph_analysis", lemma="kell")) | \
             LayerQuery(layer_name="morph_analysis", lemma="miss")
        res = list(collection.select(query = q))
        self.assertEqual(len(res), 1)

        #q["query"] = [{'mis', 'kell'}, {'palju'}]
        q = (LayerQuery(layer_name="morph_analysis", lemma="mis") & \
             LayerQuery(layer_name="morph_analysis", lemma="kell")) | \
             LayerQuery(layer_name="morph_analysis", lemma="palju")
        res = list(collection.select(query = q))
        self.assertEqual(len(res), 2)

        #q["query"] = []
        res = list(collection.select())
        self.assertEqual(len(res), 2)

        # test keys_query
        res = list(collection.select(pg.IndexQuery(keys=[])))
        self.assertEqual(len(res), 0)

        res = list(collection.select(pg.IndexQuery(keys=[1, 3])))
        self.assertEqual(len(res), 1)

        collection.delete()


    def test_insert_fails(self):
        collection = self.storage['no_such_collection_exists']

        # If the collection does not exist, Text insertion should rise PgCollectionException
        with self.assertRaises( pg.PgCollectionException ):
            with collection.insert() as collection_insert:
                collection_insert( Text('Esimene tekst.') )

        # If the collection does not exist, adding a layer template should rise PgCollectionException
        with self.assertRaises( pg.PgCollectionException ):
            collection.add_layer( ParagraphTokenizer().get_layer_template() )

        # If the collection does not exist, creating a layer should rise PgCollectionException
        with self.assertRaises( pg.PgCollectionException ):
            collection.create_layer( tagger=ParagraphTokenizer() )

        collection.delete()


class TestLayerFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_layer_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

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

        self.assertTrue(layer_table_exists(self.storage, collection.name, layer_fragment_name))

        collection.delete()

        self.assertFalse(layer_table_exists(self.storage, collection.name, layer_fragment_name))


class TestFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

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

        def row_mapper(row):
            parent_id, layer = row
            # TODO: remove next line
            # layer.serialisation_module = 'default_v1'
            return [{'fragment': layer, 'parent_id': parent_id},
                    {'fragment': layer, 'parent_id': parent_id}]

        collection.create_fragment(fragment_name,
                                   data_iterator=collection.select().fragmented_layer(name=layer_fragment_name),
                                   row_mapper=row_mapper,
                                   create_index=False,
                                   ngram_index=None)

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

        assert fragment_table_exists(self.storage, collection.name, fragment_name)
        collection.delete_fragment(fragment_name)
        assert not fragment_table_exists(self.storage, collection.name, fragment_name)


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.schema = "test_layer"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=self.schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_layer_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

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

        collection.delete()
        self.assertFalse(layer_table_exists(self.storage, collection.name, layer1))
        self.assertFalse(layer_table_exists(self.storage, collection.name, layer2))

    def test_add_layer(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        
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
        
        # Add some annotations to the layer
        def row_mapper_x(row):
            text_id, text = row[0], row[1]
            layer = Layer('test_layer', ['attr_1', 'attr_2'], ambiguous=True)
            layer.add_annotation( (0, 3), attr_1='a', attr_2='b' )
            return RowMapperRecord( layer=layer, meta={} )

        collection.create_layer(layer_template.name,
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
        
        collection.delete()

    def test_create_layer_block(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        
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
        
        collection.delete()

    def test_layer_meta(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer1 = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer1)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.make_layer(text)
            return RowMapperRecord(layer=layer, meta={"meta_text_id": text_id, "sum": 45.5})

        collection.create_layer(layer1,
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

        collection.delete()

    def test_detached_layer_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

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
