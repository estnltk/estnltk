"""Test pgcollection's detached layer functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest

from estnltk_core import Layer
from estnltk import Text
from estnltk import get_logger_with_tqdm_handler
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import LayerQuery
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import count_rows
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import CollectionMultiLayerInserter

from estnltk.taggers import TokensTagger
from estnltk.taggers import CompoundTokenTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer


logger = get_logger_with_tqdm_handler('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))



class TestCollectionMultiLayerInserter(unittest.TestCase):
    def setUp(self):
        self.schema = "test_layer"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=self.schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_collection_multi_layer_inserter_smoke(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        # Insert plain text objects into the collection
        with collection.insert() as collection_insert:
            collection_insert(Text('see on esimene lause'))
            collection_insert(Text('see on teine lause'))
            collection_insert(Text('see on kolmas lausung'))

        # Create applicable taggers, fetch layer names and templates
        taggers = [TokensTagger(), CompoundTokenTagger(), WordTagger(), SentenceTokenizer()]
        insertable_layers = [t.output_layer for t in taggers]
        layer_templates = [t.get_layer_template() for t in taggers]
        # Create layer tables
        for layer_template in layer_templates:
            collection.add_layer( layer_template=layer_template )
        # Validate layer tables
        for layer_template in layer_templates:
            self.assertTrue( collection.has_layer(layer_template.name, 'detached') )
            self.assertTrue( layer_table_exists(self.storage, collection.name, layer_template.name) )
            self.assertTrue( layer_template.name in collection.layers )
            initial_rows = count_rows( self.storage, 
                                       table=layer_table_name(collection.name, layer_template.name) )
            self.assertEqual( initial_rows, 0 )

        # Use CollectionMultiLayerInserter to add multiple layers at once
        with CollectionMultiLayerInserter(collection, insertable_layers, \
                                          sparse_layers=['compound_tokens']) as multi_layer_insert:
            # Iterate over collection, retrieve Texts and add new layers
            for key, text in collection.select():
                # Add target layers via taggers
                for target_layer, tagger in zip(insertable_layers, taggers):
                    tagger.tag( text )
                    multi_layer_insert.insert( text[target_layer], key )
        
        # Assert that layers have been inserted
        for layer_template in layer_templates:
            inserted_rows = count_rows( self.storage, 
                                        table=layer_table_name(collection.name, layer_template.name) )
            if layer_template.name != 'compound_tokens':
                self.assertEqual( inserted_rows, 3 )
            else:
                self.assertEqual( inserted_rows, 0 )



if __name__ == '__main__':
    unittest.main()
