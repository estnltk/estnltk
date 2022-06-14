import unittest
import random
import re

from psycopg2.sql import SQL, Identifier

from estnltk import logger
from estnltk import Text, Layer
from estnltk.converters import layer_to_dict, text_to_dict
from estnltk.storage.postgres import PostgresStorage
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
    
    def __init__(self, layer_name, module, remainder, parent_layer=None,
                       force_str_values=False):
        self.output_layer = layer_name
        self.input_layers = ['words']
        self.output_attributes = ('normalized', 'module', 'remainder')
        self.conf_param = ('module', 'remainder', 'number_regex', 'parent_layer', 
                           'force_str_values')
        self.parent_layer = parent_layer
        if self.parent_layer is not None:
            self.input_layers.append( self.parent_layer )
        self.force_str_values = force_str_values
        assert isinstance(module, int)
        assert isinstance(remainder, int)
        self.module = module
        self.remainder = remainder
        self.number_regex = re.compile('([0-9]+)')

    def _make_layer_template(self):
        return Layer(self.output_layer, attributes=self.output_attributes, 
                     text_object=None, parent=self.parent_layer)

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
                if self.force_str_values:
                    # Convert all values to strings
                    annotations['normalized'] = str(annotations['normalized'])
                    annotations['module'] = str(annotations['module'])
                    annotations['remainder'] = str(annotations['remainder'])
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

def _make_index_query( storage, collection, layer_name, only_table_ids=True ):
    layer_table_identifier = SQL("{}.{}").format( \
                             Identifier(storage.schema), 
                             Identifier(layer_table_name(collection, layer_name)))
    rows = _make_simple_query_on_table( storage, layer_table_identifier )
    if only_table_ids:
        return [ row[1] for row in rows ]
    else:
        return [ (row[0], row[1]) for row in rows ]

def _make_count_query( storage, collection, layer_name ):
    return count_rows( storage, table=layer_table_name(collection, layer_name) )



class TestSparseLayerCreation(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)
        self.maxDiff = None

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_create_sparse_layer_structure(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')

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
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')
        
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
        self.assertEqual( _make_count_query( self.storage, collection_name, 
                                             odd_number_tagger.output_layer ), 
                          15 )
        self.assertListEqual( _make_index_query( self.storage, collection_name, 
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
        self.assertEqual( _make_count_query( self.storage, collection_name, 
                                             fourth_number_tagger.output_layer ), 
                          8 )
        self.assertListEqual( _make_index_query( self.storage, collection_name, 
                                             fourth_number_tagger.output_layer,
                                             only_table_ids=True),
                          [0, 4, 8, 12, 16, 20, 24, 28] )

        collection.delete()


class TestSparseLayerSelection(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)
        self.maxDiff = None

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_collection_select_by_key_on_sparse_layers(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')

        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(30):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )

        # Annotate sparse layers
        odd_number_tagger = ModuleRemainderNumberTagger('odd_numbers', 2, 1)
        fifth_number_tagger = ModuleRemainderNumberTagger('fifth_numbers', 5, 0)
        collection.create_layer( tagger=odd_number_tagger, sparse=True )
        collection.create_layer( tagger=fifth_number_tagger, sparse=True )
        # Check results
        self.assertEqual( _make_count_query( self.storage, collection_name, 
                                             odd_number_tagger.output_layer ), 15 )
        self.assertEqual( _make_count_query( self.storage, collection_name, 
                                             fifth_number_tagger.output_layer ), 6 )
        
        # Test selection of a single document #1
        collection.selected_layers=['words', 'odd_numbers', 'fifth_numbers']
        text1 = collection[0]
        expected_text_dict_1 = \
            {'layers': [{'ambiguous': False,
                         'attributes': ('normalized', 'module', 'remainder'),
                         'enveloping': None,
                         'meta': {},
                         'name': 'fifth_numbers',
                         'parent': None,
                         'secondary_attributes': (),
                         'serialisation_module': None,
                         'spans': [{'annotations': [{'module': 5,
                                                     'normalized': 0,
                                                     'remainder': 0}],
                                    'base_span': (20, 21)}]},
                        {'ambiguous': False,
                         'attributes': ('normalized', 'module', 'remainder'),
                         'enveloping': None,
                         'meta': {},
                         'name': 'odd_numbers',
                         'parent': None,
                         'secondary_attributes': (),
                         'serialisation_module': None,
                         'spans': []},
                        {'ambiguous': True,
                         'attributes': ('normalized_form',),
                         'enveloping': None,
                         'meta': {},
                         'name': 'words',
                         'parent': None,
                         'secondary_attributes': (),
                         'serialisation_module': None,
                         'spans': [{'annotations': [{'normalized_form': None}],
                                    'base_span': (0, 3)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (4, 6)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (7, 12)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (13, 19)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (20, 21)}]}],
             'meta': {'number': 0},
             'text': 'See on tekst number 0'}
        self.assertEqual( text_to_dict(text1), expected_text_dict_1 )
        # Test that selection also works after changing the order of selected layers
        collection.selected_layers=['odd_numbers', 'words', 'fifth_numbers']
        text11 = collection[0]
        self.assertTrue( 'odd_numbers' in text11.layers )
        self.assertTrue( 'words' in text11.layers )
        self.assertTrue( 'fifth_numbers' in text11.layers )
        collection.selected_layers=['odd_numbers', 'fifth_numbers', 'words']
        text12 = collection[0]
        self.assertTrue( 'odd_numbers' in text12.layers )
        self.assertTrue( 'words' in text12.layers )
        self.assertTrue( 'fifth_numbers' in text12.layers )
        
        # Test selection of a single document #2
        text2 = collection[4]
        expected_text_dict_2 = \
            {'layers': [{'ambiguous': False,
                         'attributes': ('normalized', 'module', 'remainder'),
                         'enveloping': None,
                         'meta': {},
                         'name': 'fifth_numbers',
                         'parent': None,
                         'secondary_attributes': (),
                         'serialisation_module': None,
                         'spans': []},
                        {'ambiguous': False,
                         'attributes': ('normalized', 'module', 'remainder'),
                         'enveloping': None,
                         'meta': {},
                         'name': 'odd_numbers',
                         'parent': None,
                         'secondary_attributes': (),
                         'serialisation_module': None,
                         'spans': []},
                        {'ambiguous': True,
                         'attributes': ('normalized_form',),
                         'enveloping': None,
                         'meta': {},
                         'name': 'words',
                         'parent': None,
                         'secondary_attributes': (),
                         'serialisation_module': None,
                         'spans': [{'annotations': [{'normalized_form': None}],
                                    'base_span': (0, 3)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (4, 6)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (7, 12)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (13, 19)},
                                   {'annotations': [{'normalized_form': None}],
                                    'base_span': (20, 21)}]}],
             'meta': {'number': 4},
             'text': 'See on tekst number 4'}
        self.assertEqual( text_to_dict(text2), expected_text_dict_2 )
        
        # Add more detached layers
        sent_tokenizer = SentenceTokenizer()
        para_tokenizer = ParagraphTokenizer()
        collection.create_layer( tagger=sent_tokenizer )
        collection.create_layer( tagger=para_tokenizer )
        
        # Test selecting all texts one by one
        odd_number_annotations = 0
        fifth_number_annotations = 0
        collection.selected_layers=['words', 'odd_numbers', 'sentences', \
                                    'fifth_numbers', 'paragraphs']
        for i in range( len(collection) ):
            text = collection[i]
            # Check that all layers are present
            for selected_layer in collection.selected_layers:
                self.assertTrue( selected_layer in text.layers )
            odd_number_annotations += \
                len( text[odd_number_tagger.output_layer] )
            fifth_number_annotations += \
                len( text[fifth_number_tagger.output_layer] )
        self.assertEqual( odd_number_annotations, 15 )
        self.assertEqual( fifth_number_annotations, 6 )
        
        collection.delete()



    def test_collection_default_select_on_sparse_layers(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')
        
        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(30):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )
        # Add sparse layers
        even_number_tagger = ModuleRemainderNumberTagger('even_numbers', 2, 0)
        sixth_number_tagger = ModuleRemainderNumberTagger('sixth_numbers', 6, 0)
        collection.create_layer( tagger=even_number_tagger, sparse=True )
        collection.create_layer( tagger=sixth_number_tagger, sparse=True )
        
        # Try iteration over different kinds of orderings of non-sparse and sparse layer selection
        for text_id, text in collection.select(layers=['words', 'sixth_numbers', 'even_numbers']):
            # Assert that both sparse and non-spare layers exist
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )
        for text_id, text in collection.select(layers=['sixth_numbers', 'words', 'even_numbers']):
            # Assert that both sparse and non-spare layers exist
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )
        for text_id, text in collection.select(layers=['sixth_numbers', 'even_numbers', 'words']):
            # Assert that both sparse and non-spare layers exist
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )        
        
        # Iteration over non-sparse and sparse layers with validation
        text_ids_with_even_sparse_layers = []
        text_ids_with_sixth_sparse_layers = []
        all_texts_iterated = 0
        for text_id, text in collection.select(layers=['sixth_numbers', 'words', 'even_numbers']):
            # Assert that both sparse and non-spare layers exist
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )
            # Collect even layers
            if len( text['even_numbers'] ) > 0:
                self.assertEqual( len(text['even_numbers']), 1 )
                text_ids_with_even_sparse_layers.append( text_id )
            # Collect sixth layers
            if len( text['sixth_numbers'] ) > 0:
                self.assertEqual( len(text['sixth_numbers']), 1 )
                text_ids_with_sixth_sparse_layers.append( text_id )
            all_texts_iterated += 1
        # Check that all texts were seen
        self.assertEqual( all_texts_iterated, 30 )
        # Check that only even texts had an 'even_numbers' layer
        self.assertListEqual( text_ids_with_even_sparse_layers, \
                          [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28] )
        # Check that only sixth texts had a 'sixth_numbers' layer
        self.assertListEqual( text_ids_with_sixth_sparse_layers, \
                          [0, 6, 12, 18, 24] )
        
        # Add a sparse layer that depends on another sparse layer
        fourth_number_tagger = ModuleRemainderNumberTagger('fourth_numbers', 4, 0, 
                                                            parent_layer='even_numbers')
        collection.add_layer( fourth_number_tagger.get_layer_template(), sparse=True )
        collection.create_layer_block( fourth_number_tagger, (2, 0) )
        collection.create_layer_block( fourth_number_tagger, (2, 1) )

        all_texts_iterated = 0
        text_ids_with_fourth_sparse_layers = []
        for text_id, text in collection.select(layers=['fourth_numbers', 'sixth_numbers', 'words']):
            # Assert that all selected layers are present
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'fourth_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )
            # Assert that the dependency layer is also present
            self.assertTrue( 'even_numbers' in text.layers )
            # Collect fourth layers
            if len( text['fourth_numbers'] ) > 0:
                # Check parent layer
                self.assertEqual( len(text['even_numbers']), 1 )
                # Check child layer
                self.assertEqual( len(text['fourth_numbers']), 1 )
                # Record text_id
                text_ids_with_fourth_sparse_layers.append( text_id )
            all_texts_iterated += 1
        # Check that all texts were seen
        self.assertEqual( all_texts_iterated, 30 )
        # Check that only fourth texts had an 'fourth_numbers' layer
        self.assertListEqual( text_ids_with_fourth_sparse_layers, \
                              [0, 4, 8, 12, 16, 20, 24, 28] )
        
        collection.delete()


    def test_collection_inner_join_select_on_sparse_layers(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')
        
        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(30):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )
        # Add sparse layers
        even_number_tagger = ModuleRemainderNumberTagger('even_numbers', 2, 0)
        sixth_number_tagger = ModuleRemainderNumberTagger('sixth_numbers', 6, 0)
        collection.create_layer( tagger=even_number_tagger, sparse=True )
        collection.create_layer( tagger=sixth_number_tagger, sparse=True )

        # Case 0: Select sparse layer with the default join: left outer join
        all_texts_iterated = 0
        collected_text_ids = []
        for text_id, text in collection.select(layers=['words', 'even_numbers'],
                                               keep_all_texts=True):
            # Assert that both sparse and non-spare layers exist and have items
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertGreaterEqual( 1, len(text['even_numbers']) )
            collected_text_ids.append( text_id )
            all_texts_iterated += 1
        # Check results
        self.assertEqual( all_texts_iterated, 30 )
        self.assertListEqual( collected_text_ids, \
                          [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29] )
        
        # Case 1: Select sparse layer with inner join
        all_texts_iterated = 0
        collected_text_ids = []
        for text_id, text in collection.select(layers=['words', 'even_numbers'],
                                               keep_all_texts=False):
            # Assert that both sparse and non-spare layers exist and have items
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertEqual( len(text['even_numbers']), 1 )
            collected_text_ids.append( text_id )
            all_texts_iterated += 1
        # Check results
        self.assertEqual( all_texts_iterated, 15 )
        self.assertListEqual( collected_text_ids, \
                          [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28] )

        # Case 2: Select two sparse layers with inner join
        all_texts_iterated = 0
        collected_text_ids = []
        for text_id, text in collection.select(layers=['words', 'sixth_numbers', 'even_numbers'],
                                               keep_all_texts=False):
            # Assert that both sparse and non-spare layers exist and have items
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )
            self.assertEqual( len(text['even_numbers']), 1 )
            self.assertEqual( len(text['sixth_numbers']), 1 )
            collected_text_ids.append( text_id )
            all_texts_iterated += 1

        # Check results
        self.assertEqual( all_texts_iterated, 5 )
        self.assertListEqual( collected_text_ids, [0, 6, 12, 18, 24] )

        # Case 3: Select head of two sparse layers with inner join
        all_texts_iterated = 0
        collected_text_ids = []
        for text_id, text in collection.select(layers=['words', 'sixth_numbers', 'even_numbers'],
                                               keep_all_texts=False).head(3):
            # Assert that both sparse and non-spare layers exist and have items
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )
            self.assertEqual( len(text['even_numbers']), 1 )
            self.assertEqual( len(text['sixth_numbers']), 1 )
            collected_text_ids.append( text_id )
            all_texts_iterated += 1

        # Check results
        self.assertEqual( all_texts_iterated, 3 )
        self.assertListEqual( collected_text_ids, [0, 6, 12] )

        # Case 4: Select tail of two sparse layers with inner join
        all_texts_iterated = 0
        collected_text_ids = []
        for text_id, text in collection.select(layers=['words', 'sixth_numbers', 'even_numbers'],
                                               keep_all_texts=False).tail(2):
            # Assert that both sparse and non-spare layers exist and have items
            self.assertTrue( 'words' in text.layers )
            self.assertTrue( 'even_numbers' in text.layers )
            self.assertTrue( 'sixth_numbers' in text.layers )
            self.assertEqual( len(text['even_numbers']), 1 )
            self.assertEqual( len(text['sixth_numbers']), 1 )
            collected_text_ids.append( text_id )
            all_texts_iterated += 1

        # Check results
        self.assertEqual( all_texts_iterated, 2 )
        self.assertListEqual( collected_text_ids, [18, 24] )

        collection.delete()


    def test_select_sparse_subcollection_layers(self):
        # Test that PgSubCollectionLayer handles sparse layers properly
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')
        
        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(30):
                text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )
        # Add sparse layers
        even_number_tagger = ModuleRemainderNumberTagger('even_numbers', 2, 0)
        sixth_number_tagger = ModuleRemainderNumberTagger('sixth_numbers', 6, 0)
        collection.create_layer( tagger=even_number_tagger, sparse=True )
        collection.create_layer( tagger=sixth_number_tagger, sparse=True )
        
        # Default case: select a layer for every text, include empty layers
        all_texts = 0
        texts_with_nonempty_layers = []
        for text_id, layer in collection.select(layers=['even_numbers']).\
                                         detached_layer('even_numbers'):
            if len(layer) > 0:
                texts_with_nonempty_layers.append( text_id )
            all_texts += 1
        self.assertEqual( all_texts, 30 )
        self.assertListEqual( texts_with_nonempty_layers, \
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28] )

        # Optimized case: select only filled sparse layers, skip empty ones
        all_texts = 0
        texts_with_nonempty_layers = []
        for text_id, layer in collection.select(layers=['sixth_numbers'], \
                                         keep_all_texts=False).\
                                         detached_layer('sixth_numbers'):
            self.assertEqual( len(layer), 1 )
            texts_with_nonempty_layers.append( text_id )
            all_texts += 1
        self.assertEqual( all_texts, 5 )
        self.assertListEqual( texts_with_nonempty_layers, \
                              [0, 6, 12, 18, 24] )

        collection.delete()
        

if __name__ == '__main__':
    unittest.main()