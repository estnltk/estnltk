import unittest
import random

from psycopg2.errors import DuplicateSchema

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema

from estnltk.storage.postgres.queries.metadata_query import JsonbMetadataQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestJsonbMetadataQuery(unittest.TestCase):
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

        res = list(collection.select( JsonbMetadataQuery( {'subcorpus':'argivestlused'} ) ) )
        self.assertEqual(len(res), 3)

        res = list(collection.select( JsonbMetadataQuery( {'subcorpus':'argivestlused', 'type':'kõnekoosolek'} ) ) )
        self.assertEqual(len(res), 2)

        res = list(collection.select( JsonbMetadataQuery( {'type':'kiirkoosolek'} ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( JsonbMetadataQuery( {'subcorpus':'argivestlused', 'type':'artikkel'} ) ) )
        self.assertEqual(len(res), 0)

        res = list(collection.select( JsonbMetadataQuery( {'subcorpus':'ajaleheartiklid', 'type':'artikkel'} ) ) )
        self.assertEqual(len(res), 1)

        res = list(collection.select( JsonbMetadataQuery( {'subcorpus':['ajaleheartiklid','argivestlused']}) ) )
        self.assertEqual(len(res), 4)
        
        res = list(collection.select( JsonbMetadataQuery( {'type':['kõnekoosolek', 'kiirkoosolek', 'artikkel']}) ) )
        self.assertEqual(len(res), 4)

        collection.delete()
