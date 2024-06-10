"""Tests postgres storage & collection main functionality.

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
from estnltk.storage.postgres import PgStorageException
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import collection_table_exists
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import drop_collection_table
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import is_empty
from estnltk.taggers import ParagraphTokenizer
from estnltk.taggers import VabamorfTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgCollection(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_storage_connection(self):
        # If we try to connect to a database that does not have 
        # the schema, an exception will be thrown
        schema = "unseen_test_schema"
        with self.assertRaises( PgStorageException ):
            storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, 
                                      dbname='test_db', \
                                      create_schema_if_missing=False)
        # However, we can create the schema if we have sufficient privileges
        storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, 
                                  dbname='test_db', \
                                  create_schema_if_missing=True)
        self.assertTrue( pg.schema_exists(storage) )
        delete_schema(storage)
        storage.close()

    def test_storage_get_collections(self):
        # Test that the collections list can be accessed
        # even before it is filled in with collections 
        self.assertTrue( len( self.storage.collections ) == 0 )

    def test_create_collection(self):
        collection_name = get_random_collection_name()
        
        with self.assertRaises(KeyError):
            self.storage[collection_name]
        
        collection = self.storage.add_collection(collection_name)

        self.assertTrue(collection.exists())

        self.assertIs(collection, self.storage[collection_name])

        # In case of an empty collection, collection.layers should be []
        self.assertTrue(collection.layers == [])

        # 1st way to remove collection
        self.storage.delete_collection(collection_name)

        with self.assertRaises(KeyError):
            collection = self.storage[collection_name]
        
        self.storage.add_collection(collection_name)
        collection = self.storage[collection_name]
        self.assertTrue(collection.exists())

        # 2nd way to remove collection
        self.storage.delete_collection(collection_name)

        with self.assertRaises(KeyError):
            collection = self.storage[collection_name]

    def test_create_collection_multiple_connections(self):
        storage_1 = self.storage
        storage_2 = PostgresStorage(pgpass_file='~/.pgpass', 
                                    schema=storage_1.schema, 
                                    dbname='test_db', 
                                    create_schema_if_missing=False)
        
        collection_name = get_random_collection_name()
        
        # Check that the collection is missing at first place
        with self.assertRaises(KeyError):
            storage_1[collection_name]
        with self.assertRaises(KeyError):
            storage_2[collection_name]
        
        # Add new collection
        storage_1.add_collection(collection_name)
        
        # Check that new collection cannot be added twice
        with self.assertRaises(PgStorageException):
            storage_2.add_collection(collection_name)
        
        # Add different collection via other thread
        another_collection_name = get_random_collection_name()
        assert collection_name != another_collection_name
        storage_2.add_collection(another_collection_name)
        
        # Get collection
        collection_from_1 = storage_1[collection_name]
        collection_from_2 = storage_2[collection_name]

        # Assert existence
        self.assertTrue(collection_from_1.exists())
        self.assertTrue(collection_from_2.exists())

        self.assertIs(collection_from_1, storage_1[collection_name])
        self.assertIs(collection_from_2, storage_2[collection_name])

        # Make third connection. It should be able to retrieve
        # up-to-date status of collections table instantly
        storage_3 = PostgresStorage(pgpass_file='~/.pgpass', 
                                    schema=storage_1.schema, 
                                    dbname='test_db', 
                                    create_schema_if_missing=False)
        self.assertTrue(collection_name in storage_3.collections)
        self.assertTrue(another_collection_name in storage_3.collections)
        storage_3.close()

        # Remove collection
        storage_1.delete_collection(collection_name)

        # Assert collection is not existing any more
        self.assertFalse(collection_from_1.exists())
        self.assertFalse(collection_from_2.exists())
        
        # Assert collection is not listed in storage.collections
        self.assertFalse(collection_name in storage_1.collections)
        
        # Assert that collection is again "missing" from 1
        with self.assertRaises(KeyError):
            storage_1[collection_name]
        # And not existing in 2
        self.assertFalse(storage_2[collection_name].exists())

        # Assert that collection cannot be deleted twice
        with self.assertRaises(KeyError):
            storage_2.delete_collection(collection_from_2.name)
        
        # Test that storage_1 can proceed with insertion
        # (lock has been released)
        yet_another_collection_name = get_random_collection_name()
        assert collection_name != yet_another_collection_name
        assert another_collection_name != yet_another_collection_name
        yet_another_collection = \
            storage_1.add_collection(yet_another_collection_name)

        # Check the remaining collection
        self.assertTrue(another_collection_name in storage_2.collections)
        storage_1.refresh()
        another_collection = storage_1[another_collection_name]
        self.assertTrue(another_collection.exists())

        # Remove last collections
        storage_1.delete_collection(another_collection_name)
        storage_1.delete_collection(yet_another_collection_name)

        storage_2.close()

    def test_insert(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

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

        self.storage.delete_collection(collection.name)

    def test_collection_emptyness_check(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        # newly created collection is empty
        self.assertTrue( collection._is_empty )
        self.assertTrue( is_empty(collection.storage, collection.name) )

        with collection.insert() as collection_insert:
            collection_insert( Text('Esimene tekst.') )

        # collection is no longer empty after the insertion
        self.assertFalse( collection._is_empty )
        self.assertFalse( is_empty(collection.storage, collection.name) )

        self.storage.delete_collection(collection.name)

    def test_basic_collection_workflow(self):
        # insert texts -> create layers -> select texts
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

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

        # Assert that layers have expected types
        self.assertTrue(collection.has_layer('tokens', 'attached'))
        self.assertTrue(collection.has_layer('compound_tokens', 'attached'))
        self.assertTrue(collection.has_layer('words', 'attached'))
        self.assertTrue(collection.has_layer('sentences', 'attached'))
        self.assertTrue(collection.has_layer('paragraphs', 'detached'))
        self.assertTrue(collection.has_layer('morph_analysis', 'detached'))

        for text_id, text in collection.select(layers=['compound_tokens', 'morph_analysis', 'paragraphs']):
            if text_id == 1:
                assert text == text_1, text_1.diff(text)
            elif text_id == 2:
                assert text == text_2, text_2.diff(text)

        self.storage.delete_collection(collection.name)

    def test_collection_getitem_and_iter(self):
        # insert texts -> create layers -> select texts
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

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
        collection = self.storage.add_collection(collection_name)

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
        
        self.storage.delete_collection(collection.name)

    def test_collection_base_columns(self):
        collection_name = get_random_collection_name()
        collection = PgCollection(collection_name, self.storage, version='3.0')
        self.assertEqual( collection.structure.collection_base_columns, ['id', 'data'])
        collection_name_2 = get_random_collection_name()
        collection_2 = PgCollection(collection_name_2, self.storage, version='4.0')
        self.assertEqual( collection_2.structure.collection_base_columns, ['id', 'data', 'hidden'])

    def test_create_and_drop_collection_table(self):
        collection_name = get_random_collection_name()
        collection = PgCollection(collection_name, self.storage)
        collection.structure.create_collection_table()
        self.assertTrue( collection_table_exists(self.storage, collection_name) )
        self.assertTrue( table_exists(self.storage, collection_name) )
        drop_collection_table(self.storage, collection_name)
        self.assertFalse( collection_table_exists(self.storage, collection_name) )
        self.assertFalse( table_exists(self.storage, collection_name) )

    def test_sql_injection(self):
        normal_collection_name = get_random_collection_name()
        collection = PgCollection(normal_collection_name, self.storage)
        collection.structure.create_collection_table()
        self.assertTrue(collection_table_exists(self.storage, normal_collection_name))
        injected_collection_name = "%a; drop table %s;" % (get_random_collection_name(), normal_collection_name)
        with self.assertRaises(AssertionError):
            injected_collection = PgCollection(injected_collection_name, self.storage)
            injected_collection.structure.create_collection_table()
        if collection_table_exists(self.storage, injected_collection_name):
            drop_collection_table(self.storage, injected_collection_name)
        self.assertTrue(collection_table_exists(self.storage, normal_collection_name))
        drop_collection_table(self.storage, normal_collection_name)

    def test_select(self):
        # Test error case: try to select on non-existing collection
        # Create a collection and then remove it
        collection_name = get_random_collection_name()
        not_existing_collection = self.storage.add_collection(collection_name)
        self.storage.delete_collection(not_existing_collection.name)
        # If the collection does not exist, select should rise PgCollectionException
        with self.assertRaises(pg.PgCollectionException):
            not_existing_collection.select()

        # Test positive cases
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

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

        self.storage.delete_collection(collection.name)

        collection = self.storage.add_collection(get_random_collection_name())

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

        self.storage.delete_collection(collection.name)


    def test_insert_fails(self):
        # Test that collection operations do not work if someone 
        # has already deleted the collection
        
        # Create collection and then remove it
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        self.storage.delete_collection(collection.name)
        # If the collection does not exist, Text insertion should rise PgCollectionException
        with self.assertRaises( pg.PgCollectionException ):
            with collection.insert() as collection_insert:
                collection_insert( Text('Esimene tekst.') )

        # Create collection and then remove it
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        self.storage.delete_collection(collection.name)
        # If the collection does not exist, adding a layer template should rise PgCollectionException
        with self.assertRaises( pg.PgCollectionException ):
            collection.add_layer( ParagraphTokenizer().get_layer_template() )

        # Create collection and then remove it
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        self.storage.delete_collection(collection.name)
        # If the collection does not exist, creating a layer should rise PgCollectionException
        with self.assertRaises( pg.PgCollectionException ):
            collection.create_layer( tagger=ParagraphTokenizer() )


    def test_insert_and_select_meta(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name,
                                                 description='demo collection', 
                                                 meta={'author': 'str', 'date': 'str'})

        text_1 = Text('Esimene tekst.')
        text_1.meta['author'] = 'Niinepuu'
        text_1.meta['date']   = '1983'
        text_2 = Text('Teine tekst')
        text_2.meta['author'] = 'Kõivupuu'
        text_2.meta['date']   = '1997'
        text_3 = Text('Kolmas tekst')
        text_3.meta['author'] = 'Musumets'
        text_3.meta['date']   = '2009'

        with collection.insert() as collection_insert:
            collection_insert(text_1, meta_data=text_1.meta)
            collection_insert(text_2, meta_data=text_2.meta)
            collection_insert(text_3, meta_data=text_3.meta)
        
        self.assertEqual( len(collection), 3 )
        # Check meta columns
        self.assertEqual( collection.meta.columns, ['author', 'date'] )
        # Iterate over collection and select id, text_obj and meta
        selection = \
            list( collection.select( collection_meta=['author', 'date'] ) )
        self.assertEqual( len(selection), 3 )
        # Check meta values
        self.assertEqual( selection[0][2], \
                          {'author': 'Niinepuu', 'date': '1983'} )
        self.assertEqual( selection[1][2], \
                          {'author': 'Kõivupuu', 'date': '1997'} )
        self.assertEqual( selection[2][2], \
                          {'author': 'Musumets', 'date': '2009'} )

        # Iterate over collection and select id and meta exclusively 
        selection = list( collection.meta[0:] )
        self.assertEqual( len(selection), 3 )
        # Check meta values
        self.assertEqual( selection[0], \
                          {'author': 'Niinepuu', 'date': '1983'} )
        self.assertEqual( selection[1], \
                          {'author': 'Kõivupuu', 'date': '1997'} )
        self.assertEqual( selection[2], \
                          {'author': 'Musumets', 'date': '2009'} )
        
        self.storage.delete_collection(collection.name)


    @unittest.expectedFailure
    def test_dependent_layers_topological_sort(self):
        # Test that Text.topological_sort(...) gives same results as collection.dependent_layers(...)
        # Create input layers
        tokens = Layer(name='tokens', parent=None, enveloping=None, text_object=None)
        words = Layer(name='words', parent=None, enveloping=None, text_object=None)
        sentences = Layer(name='sentences', parent=None, enveloping='words', text_object=None)
        paragraphs = Layer(name='paragraphs', parent=None, enveloping='sentences', text_object=None)
        morph_analysis = \
            Layer(name='morph_analysis', parent='words', enveloping=None, text_object=None)
        morph_extended = \
            Layer(name='morph_extended', parent='morph_analysis', enveloping=None, text_object=None)
        syntax = Layer(name='syntax', parent='morph_extended', enveloping=None, text_object=None)
        # 1) Text.topological_sort(...)
        layers_dict = {layer.name: layer for layer in [ morph_extended, paragraphs, morph_analysis, 
                                                        sentences, syntax, words, tokens ]}
        text_obj_top_sorted_layers = Text.topological_sort( layers_dict )
        text_obj_top_sorted_layers = [layer.name for layer in text_obj_top_sorted_layers]
        self.assertListEqual( text_obj_top_sorted_layers, \
                              ['tokens', 'words', 'morph_analysis', 'morph_extended', \
                               'sentences', 'paragraphs', 'syntax'] )
        # 2) collection.dependent_layers(...)
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        # Add some documents to the collection
        with collection.insert() as collection_insert:
            collection_insert( Text('Näidislause') )
        # Add layers to collection in arbitrary order
        for layer_template in [ morph_extended, paragraphs, morph_analysis, 
                                          sentences, syntax, words, tokens ]:
            collection.add_layer( layer_template )
        collection_top_sorted_layers = \
            collection.dependent_layers( collection.layers )
        self.assertListEqual( collection_top_sorted_layers, \
                             ['words', 'morph_analysis', 'morph_extended', 'sentences', \
                              'paragraphs', 'syntax', 'tokens'] )
        self.storage.delete_collection(collection.name)
        # Currently, the two topological orderings are different,
        # so the following is expected to fail:
        self.assertListEqual(collection_top_sorted_layers, text_obj_top_sorted_layers)
        # TODO: two topological orderings need to be synchronized


if __name__ == '__main__':
    unittest.main()
