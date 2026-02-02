"""Test pgcollection's detached layer functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest

from typing import MutableMapping, List, Tuple

from psycopg2.sql import SQL, Identifier

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
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import count_rows
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import CollectionMultiLayerInserter

from estnltk_core.taggers import MultiLayerTagger

from estnltk.taggers import TokensTagger
from estnltk.taggers import CompoundTokenTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer


logger = get_logger_with_tqdm_handler('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))

class TextSegmentationMultiTagger(MultiLayerTagger):
    '''Multitagger for adding text segmentation layers ("tokens", "compound_tokens", "words", "sentences").'''
    
    conf_param = ['taggers']
    
    def __init__(self, output_layers=["tokens", "compound_tokens", "words", "sentences"]):
        assert isinstance(output_layers, list) and len(output_layers) > 0
        self.taggers = [TokensTagger(), CompoundTokenTagger(), WordTagger(), SentenceTokenizer()]
        verified_output_layers = []
        verified_output_layers_to_attributes = {}
        for layer in output_layers:
            tagger_found = False
            for tagger in self.taggers:
                if layer == tagger.output_layer:
                    tagger_found = True
                    break
            if not tagger_found:
                raise ValueError(f'(!) No tagger found for creating layer: ', layer)
            if layer not in verified_output_layers:
                verified_output_layers.append( layer )
                verified_output_layers_to_attributes[ layer ] = tagger.output_attributes
        input_layers = []
        for output_layer in verified_output_layers:
            for tagger in self.taggers:
                if output_layer == tagger.output_layer:
                    for required_layer in tagger.input_layers:
                        if (required_layer not in input_layers and \
                            required_layer not in verified_output_layers):
                               input_layers.append( required_layer )
        self.input_layers = input_layers
        self.output_layers = verified_output_layers
        self.output_layers_to_attributes = verified_output_layers_to_attributes

    def _make_layer_templates(self) -> MutableMapping[str,Layer]:
        # Create layer templates
        layer_templates = dict()
        for layer in self.output_layers:
            for tagger in self.taggers:
                if layer == tagger.output_layer:
                    layer_templates[layer] = tagger.get_layer_template()
                    break
        return layer_templates

    def _make_layers(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> MutableMapping[str,Layer]:
        output_layers = dict()
        temp_layers = layers.copy()
        for layer in self.output_layers:
            for tagger in self.taggers:
                if layer == tagger.output_layer:
                    output_layers[layer] = tagger.make_layer(text, temp_layers)
                    temp_layers[layer] = output_layers[layer]
                    break
        return output_layers


def _count_layer_rows( storage, collection, layer_name ):
    return count_rows( storage, table=layer_table_name(collection.name, layer_name) )

def _get_inserted_text_ids(storage, collection, layer_name):
    table_identifier = layer_table_identifier(storage, collection.name, layer_name )
    query = SQL('SELECT text_id FROM {}').format(table_identifier)
    rows = []
    with storage.conn.cursor() as cursor:
        try:
            cursor.execute( query )
        except:
            raise
        for row in cursor.fetchall():
            rows.append( row[0] )
    return rows


class TestCollectionMultiLayerInserter(unittest.TestCase):
    def setUp(self):
        self.schema = "test_layer"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=self.schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_collection_multi_layer_inserter(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        # Insert plain text objects into the collection
        with collection.insert() as collection_insert:
            collection_insert(Text('see on esimene lause'))
            collection_insert(Text('see on teine lause'))
            collection_insert(Text('see on kolmas lausung'))

        # Create applicable multi-layer tagger, fetch layer names and templates
        multi_tagger = TextSegmentationMultiTagger(output_layers=["tokens", "compound_tokens",
                                                                  "words", "sentences"])
        insertable_layers = multi_tagger.output_layers
        layer_templates = [template for layer, template in (multi_tagger.get_layer_templates()).items()]
        # Create layer tables
        for layer_template in layer_templates:
            collection.add_layer( layer_template=layer_template )
        # Validate layer tables
        for layer_template in layer_templates:
            self.assertTrue( collection.has_layer(layer_template.name, 'detached') )
            self.assertTrue( layer_table_exists(self.storage, collection.name, layer_template.name) )
            self.assertTrue( layer_template.name in collection.layers )
            initial_rows = _count_layer_rows( self.storage, collection, layer_template.name )
            self.assertEqual( initial_rows, 0 )
        
        # Use CollectionMultiLayerInserter to add multiple layers at once
        with CollectionMultiLayerInserter(collection, insertable_layers, \
                                          sparse_layers=['compound_tokens']) as multi_layer_insert:
            # Iterate over collection, retrieve Texts and add new layers
            for key, text in collection.select():
                # Create layers via multi_tagger
                multi_tagger.tag( text )
                for target_layer in insertable_layers:
                    # Insert layers
                    multi_layer_insert.insert( text[target_layer], key )
        
        # Assert that layers have been inserted
        for layer_template in layer_templates:
            inserted_rows = _count_layer_rows( self.storage, collection, layer_template.name )
            if layer_template.name != 'compound_tokens':
                self.assertEqual( inserted_rows, 3 )
            else:
                self.assertEqual( inserted_rows, 0 )


    def test_create_layers_with_multitagger_smoke(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        # Insert plain text objects into the collection
        with collection.insert() as collection_insert:
            collection_insert(Text('see on esimene lause'))
            collection_insert(Text('see on teine lause'))
            collection_insert(Text('see on kolmas lausung'))
        
        multi_tagger_1 = TextSegmentationMultiTagger(output_layers=["tokens", "compound_tokens"])
        # Create layer tables 1
        for layer in multi_tagger_1.output_layers:
            layer_template = multi_tagger_1.get_layer_templates()[layer]
            collection.add_layer( layer_template=layer_template )
            initial_rows = _count_layer_rows( self.storage, collection, layer_template.name )
            self.assertEqual( initial_rows, 0 )
        
        # Fill in layer tables 1
        collection.create_layers( multi_tagger_1 )
        
        # Validate created layers 1
        for layer in multi_tagger_1.output_layers:
            inserted_text_ids = _get_inserted_text_ids(self.storage, collection, layer)
            self.assertEqual( len(inserted_text_ids), 3 )
            self.assertListEqual( inserted_text_ids, [0, 1, 2] )
        
        multi_tagger_2 = TextSegmentationMultiTagger(output_layers=["words", "sentences"])
        # Create layer tables 2
        for layer in multi_tagger_2.output_layers:
            layer_template = multi_tagger_2.get_layer_templates()[layer]
            collection.add_layer( layer_template=layer_template )
            initial_rows = _count_layer_rows( self.storage, collection, layer_template.name )
            self.assertEqual( initial_rows, 0 )
        
        # Fill in layer tables 2
        collection.create_layers( multi_tagger_2 )

        # Validate created layers 1
        for layer in multi_tagger_2.output_layers:
            inserted_text_ids = _get_inserted_text_ids(self.storage, collection, layer)
            self.assertEqual( len(inserted_text_ids), 3 )
            self.assertListEqual( inserted_text_ids, [0, 1, 2] )


    def test_create_layers_with_multitagger_block_wise(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        # Insert plain text objects into the collection
        with collection.insert() as collection_insert:
            collection_insert(Text('see on esimene lause'))
            collection_insert(Text('see on teine lause'))
            collection_insert(Text('see on kolmas lausung'))
            collection_insert(Text('see on neljas ja viimane kutsung'))
        
        multi_tagger_1 = TextSegmentationMultiTagger(output_layers=["tokens", "compound_tokens"])
        # Create layer tables 1
        for layer in multi_tagger_1.output_layers:
            layer_template = multi_tagger_1.get_layer_templates()[layer]
            collection.add_layer( layer_template=layer_template )
            initial_rows = _count_layer_rows( self.storage, collection, layer_template.name )
            self.assertEqual( initial_rows, 0 )
        
        # Fill in layer tables 1 block 1
        collection.create_layers( multi_tagger_1, block=(2,0) )
        
        # Validate created layers 1 block 1
        for layer in multi_tagger_1.output_layers:
            inserted_text_ids = _get_inserted_text_ids(self.storage, collection, layer)
            self.assertEqual( len(inserted_text_ids), 2 )
            self.assertListEqual( inserted_text_ids, [0, 2] )
        
        # Fill in layer tables 1 block 2
        collection.create_layers( multi_tagger_1, block=(2,1) )

        # Validate created layers 1 block 2
        for layer in multi_tagger_1.output_layers:
            inserted_text_ids = _get_inserted_text_ids(self.storage, collection, layer)
            self.assertEqual( len(inserted_text_ids), 4 )
            self.assertListEqual( inserted_text_ids, [0, 2, 1, 3] )


if __name__ == '__main__':
    unittest.main()
