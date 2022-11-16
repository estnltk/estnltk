import unittest
import random

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres.queries.block_query import BlockQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestBlockQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_block_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        with collection.insert() as collection_insert:
            for i in range(100):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )

        res = list( collection.select( query=BlockQuery(2, 0) ) )
        self.assertEqual( len(res), 50 )
        for doc_id, doc in res:
            self.assertTrue( doc.meta['number'] % 2 == 0 )

        res = list( collection.select( query=BlockQuery(3, 0) ) )
        self.assertEqual( len(res), 34 )
        
        self.storage.delete_collection(collection.name)
