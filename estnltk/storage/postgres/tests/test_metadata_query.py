import unittest
import random
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema, count_rows
from estnltk.storage import postgres as pg

from estnltk.storage.postgres.queries.metadata_query import MetadataQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))

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

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused'}, collection ) ) )
        self.assertEqual(len(res), 3)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused', 'type':'kõnekoosolek'}, collection  ) ) )
        self.assertEqual(len(res), 2)

        res = list(collection.select( MetadataQuery( {'type':'kiirkoosolek'}, collection  ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'subcorpus':'argivestlused', 'type':'artikkel'}, collection  ) ) )
        self.assertEqual(len(res), 0)

        res = list(collection.select( MetadataQuery( {'subcorpus':'ajaleheartiklid', 'type':'artikkel'}, collection  ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'subcorpus':['ajaleheartiklid','argivestlused']}, collection ) ) )
        self.assertEqual(len(res), 4)
        
        res = list(collection.select( MetadataQuery( {'type':['kõnekoosolek', 'kiirkoosolek', 'artikkel']}, collection ) ) )
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

        res = list(collection.select( MetadataQuery( {'tyyp_nr':4}, collection ) ) )
        self.assertEqual(len(res), 2)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':[4,3]}, collection  ) ) )
        self.assertEqual(len(res), 3)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':[2]}, collection  ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':5}, collection  ) ) )
        self.assertEqual(len(res), 0)

        res = list(collection.select( MetadataQuery( {'tyyp_nr':4, 'jrknr':3}, collection  ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( MetadataQuery( {'jrknr':[1,2,3,4]}, collection ) ) )
        self.assertEqual(len(res), 4)

        collection.delete()
