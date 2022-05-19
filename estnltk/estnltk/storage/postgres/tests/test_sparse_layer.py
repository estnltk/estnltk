import unittest
import random
import re

from psycopg2.sql import SQL, Identifier

from estnltk import logger
from estnltk import Text, Layer
from estnltk.converters import layer_to_dict
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import count_rows
from estnltk.taggers import Tagger
from estnltk.taggers import SentenceTokenizer, ParagraphTokenizer

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class ModuleRemainderNumberTagger(Tagger):
    '''Tagger for detecting numbers that match criterion: number % module = remainder'''
    
    def __init__(self, layer_name, module, remainder):
        self.output_layer = layer_name
        self.input_layers = ['words']
        self.output_attributes = ('normalized', 'module', 'remainder')
        self.conf_param = ('module', 'remainder', 'number_regex')
        assert isinstance(module, int)
        assert isinstance(remainder, int)
        self.module = module
        self.remainder = remainder
        self.number_regex = re.compile('([0-9]+)')

    def _make_layer_template(self):
        return Layer(self.output_layer, attributes=self.output_attributes, text_object=None)

    def _make_layer(self, text, layers, status):
        layer = self._make_layer_template()
        layer.text_object = text
        for match in self.number_regex.finditer(text.text):
            m_start  = match.start(1)
            m_end    = match.end(1)
            m_text   = match.group(1)
            m_normalized = int(m_text)
            if m_normalized % self.module == self.remainder:
                annotations = {'normalized':m_normalized, 
                               'module': self.module,
                               'remainder': self.remainder}
                layer.add_annotation( (m_start, m_end), **annotations )
        return layer


def _make_simple_query_on_table( storage, table_identifier ):
    query = SQL('SELECT * FROM {}').format( table_identifier )
    rows = []
    with storage.conn.cursor() as cursor:
        try:
            cursor.execute( query )
        except:
            raise
        for row in cursor.fetchall():
            rows.append( row )
    return rows


def _make_index_query_on_layer( storage, collection, layer_name, only_table_ids=True ):
    layer_table_identifier = SQL("{}.{}").format( \
                               Identifier(storage.schema), 
                               Identifier(layer_table_name(collection, layer_name)))
    rows = _make_simple_query_on_table( storage, layer_table_identifier )
    if only_table_ids:
        return [ row[1] for row in rows ]
    else:
        return [ (row[0], row[1]) for row in rows ]


class TestSparseLayerCreation(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_create_sparse_layer_structure(self):
        collection_name = get_random_collection_name()
        # Create collection with 3.0 structure
        collection = PgCollection(collection_name, self.storage, version='3.0')
        self.storage._load()
        self.storage._collections[collection_name] = collection
        collection.create()

        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(10):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )
        # Assert settings
        self.assertTrue( 'words' in collection.layers )
        self.assertFalse( collection.is_sparse('words') )
        
        # Add sparse layers
        sent_tokenizer = SentenceTokenizer()
        para_tokenizer = ParagraphTokenizer()
        collection.add_layer( sent_tokenizer.get_layer_template(), sparse=True )
        collection.add_layer( para_tokenizer.get_layer_template(), sparse=True )
        # Assert settings
        self.assertTrue( sent_tokenizer.output_layer in collection.layers )
        self.assertTrue( collection.is_sparse( sent_tokenizer.output_layer ) )
        self.assertTrue( para_tokenizer.output_layer in collection.layers )
        self.assertTrue( collection.is_sparse( para_tokenizer.output_layer ) )
        # Check that layer templates are available
        # as json
        self.assertEqual( collection.get_sparse_layer_template(sent_tokenizer.output_layer, as_json=True), 
                          '{"name": "sentences", "attributes": [], "secondary_attributes": [], '+\
                          '"parent": null, "enveloping": "words", "ambiguous": false, '+\
                          '"serialisation_module": null, "meta": {}, "spans": []}' )
        # as Layer objects
        self.assertEqual( layer_to_dict(collection.get_sparse_layer_template(para_tokenizer.output_layer, as_json=False)), 
                          {'ambiguous': False,
                           'attributes': (),
                           'enveloping': 'sentences',
                           'meta': {},
                           'name': 'paragraphs',
                           'parent': None,
                           'secondary_attributes': (),
                           'serialisation_module': None,
                           'spans': []} )
        collection.delete()


    def test_create_sparse_layer_insertion(self):
        collection_name = get_random_collection_name()
        # Create collection with 3.0 structure
        collection = PgCollection(collection_name, self.storage, version='3.0')
        self.storage._load()
        self.storage._collections[collection_name] = collection
        collection.create()
        
        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(30):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )

        # Annotate sparse layer #1        
        odd_number_tagger = ModuleRemainderNumberTagger('odd_numbers', 2, 1)
        collection.create_layer( tagger=odd_number_tagger, sparse=True )
        # Assert results
        self.assertTrue( collection.is_sparse( odd_number_tagger.output_layer ) )
        rows = count_rows( self.storage, 
                           table=layer_table_name(collection_name, 
                                                  odd_number_tagger.output_layer) )
        self.assertEqual( rows, 15 )
        self.assertEqual( _make_index_query_on_layer( self.storage, collection_name, 
                                                      odd_number_tagger.output_layer,
                                                      only_table_ids=True),
                          [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29] )

        # Annotate sparse layer #2
        fourth_number_tagger = ModuleRemainderNumberTagger('fourth_numbers', 4, 0)
        collection.add_layer( fourth_number_tagger.get_layer_template(), sparse=True )
        collection.create_layer_block( fourth_number_tagger, (2, 0) )
        collection.create_layer_block( fourth_number_tagger, (2, 1) )
        # Assert results
        self.assertTrue( collection.is_sparse( fourth_number_tagger.output_layer ) )
        rows = count_rows( self.storage, 
                           table=layer_table_name(collection_name, 
                                                  fourth_number_tagger.output_layer) )
        self.assertEqual( rows, 8 )
        self.assertEqual( _make_index_query_on_layer( self.storage, collection_name, 
                                                      fourth_number_tagger.output_layer,
                                                      only_table_ids=True),
                          [0, 4, 8, 12, 16, 20, 24, 28] )

        collection.delete()