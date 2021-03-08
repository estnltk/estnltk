import unittest
import random
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema

from estnltk.storage.postgres.queries.metadata_query import MetadataQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


# Test metadata queries with meta_type = 'COLLECTION' (default)
class TestMetadataQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            # TODO: for some reason we get DuplicateSchema error. Unexpected?
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_metadata_query_str(self):
        collection = self.storage[get_random_collection_name()]
        collection.create( meta=OrderedDict([('subcorpus', 'str'), ('type', 'str')]) )

        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').tag_layer()
            meta = {}
            meta['subcorpus'] = 'argivestlused'
            meta['type'] = 'kõnekoosolek'
            collection_insert(text1, meta_data=meta)
            text2 = Text('palju kell on?').tag_layer()
            meta = {}
            meta['subcorpus'] = 'argivestlused'
            meta['type'] = 'kiirkoosolek'
            collection_insert(text2, meta_data=meta)
            text3 = Text('kus kell on?').tag_layer()
            meta = {}
            meta['subcorpus'] = 'argivestlused'
            meta['type'] = 'kõnekoosolek'
            collection_insert(text3, meta_data=meta)
            text4 = Text('kes Kell on?').tag_layer()
            meta = {}
            meta['subcorpus'] = 'ajaleheartiklid'
            meta['type'] = 'artikkel'
            collection_insert(text4, meta_data=meta)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused'} ) ) )
        self.assertEqual(len(res), 3)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused', 'type':'kõnekoosolek'}  ) ) )
        self.assertEqual(len(res), 2)

        res = list(collection.select( MetadataQuery( {'type':'kiirkoosolek'}  ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused', 'type':'artikkel'}  ) ) )
        self.assertEqual(len(res), 0)

        res = list(collection.select( MetadataQuery( {'subcorpus':'ajaleheartiklid', 'type':'artikkel'}  ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'subcorpus':['ajaleheartiklid','argivestlused']} ) ) )
        self.assertEqual(len(res), 4)
        
        res = list(collection.select( MetadataQuery( {'type':['kõnekoosolek', 'kiirkoosolek', 'artikkel']} ) ) )
        self.assertEqual(len(res), 4)

        collection.delete()

    def test_metadata_query_int(self):
        collection = self.storage[get_random_collection_name()]
        collection.create( meta=OrderedDict([('jrknr', 'int'), ('tyyp_nr', 'int')]) )

        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').tag_layer()
            meta = {}
            meta['jrknr'] = 1
            meta['tyyp_nr'] = 3
            collection_insert(text1, meta_data=meta)
            text2 = Text('palju kell on?').tag_layer()
            meta = {}
            meta['jrknr'] = 2
            meta['tyyp_nr'] = 4
            collection_insert(text2, meta_data=meta)
            text3 = Text('kus kell on?').tag_layer()
            meta = {}
            meta['jrknr'] = 3
            meta['tyyp_nr'] = 4
            collection_insert(text3, meta_data=meta)
            text4 = Text('kes Kell on?').tag_layer()
            meta = {}
            meta['jrknr'] = 4
            meta['tyyp_nr'] = 2
            collection_insert(text4, meta_data=meta)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':4} ) ) )
        self.assertEqual(len(res), 2)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':[4,3]}  ) ) )
        self.assertEqual(len(res), 3)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':[2]} ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':5} ) ) )
        self.assertEqual(len(res), 0)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':4, 'jrknr':3} ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'jrknr':[1,2,3,4]} ) ) )
        self.assertEqual(len(res), 4)

        collection.delete()


    def test_metadata_query_on_missing_metadata_columns(self):
        # Test an invalid query: MetadataQuery on a collection that misses appropriate metadata columns
        collection = self.storage[get_random_collection_name()]
        # Create a collection w/o metadata columns
        collection.create()
        
        with collection.insert() as collection_insert:
            text1 = Text("Kas kuubik kerib pinget ?").tag_layer(["sentences"])
            collection_insert(text1)
        
        # Attempt to make a MetadataQuery. This should rise an Exception
        with self.assertRaises( Exception ):
            res = list( collection.select( query = MetadataQuery( {'tyyp_nr':4, 'jrknr':3} ) ) )

        collection.delete()


# Test metadata queries with meta_type = 'TEXT'
class TestTextLevelMetadataQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            # TODO: for some reason we get DuplicateSchema error. Unexpected?
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_jsonb_metadata_query(self):
        collection = self.storage[get_random_collection_name()]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').tag_layer()
            text1.meta['subcorpus'] = 'argivestlused'
            text1.meta['type'] = 'kõnekoosolek'
            collection_insert(text1, key=3)
            text2 = Text('palju kell on?').tag_layer()
            text2.meta['subcorpus'] = 'argivestlused'
            text2.meta['type'] = 'kiirkoosolek'
            collection_insert(text2, key=4)
            text3 = Text('kus kell on?').tag_layer()
            text3.meta['subcorpus'] = 'argivestlused'
            text3.meta['type'] = 'kõnekoosolek'
            collection_insert(text3, key=5)
            text4 = Text('kes Kell on?').tag_layer()
            text4.meta['subcorpus'] = 'ajaleheartiklid'
            text4.meta['type'] = 'artikkel'
            collection_insert(text4, key=6)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused'}, 
                                                     meta_type='TEXT' ) ) )
        self.assertEqual(len(res), 3)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused', 'type':'kõnekoosolek'}, 
                                                     meta_type='TEXT' ) ) )
        self.assertEqual(len(res), 2)

        res = list(collection.select( MetadataQuery( {'type':'kiirkoosolek'}, 
                                                     meta_type='TEXT' ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused', 'type':'artikkel'}, 
                                                     meta_type='TEXT' ) ) )
        self.assertEqual(len(res), 0)

        res = list(collection.select( MetadataQuery( {'subcorpus':'ajaleheartiklid', 'type':'artikkel'}, 
                                                     meta_type='TEXT' ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'subcorpus':['ajaleheartiklid','argivestlused']}, 
                                                     meta_type='TEXT') ) )
        self.assertEqual(len(res), 4)
        
        res = list(collection.select( MetadataQuery( {'type':['kõnekoosolek', 'kiirkoosolek', 'artikkel']}, 
                                                     meta_type='TEXT') ) )
        self.assertEqual(len(res), 4)

        collection.delete()


