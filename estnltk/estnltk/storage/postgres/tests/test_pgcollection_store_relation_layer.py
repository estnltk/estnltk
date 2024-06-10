"""Test that relation layers can be stored in / loaded from PgCollection.

Requires ~/.pgpass file with database connection settings to `test_db` database.
"""

import unittest
import random
import regex as re
from itertools import tee

from psycopg2.sql import SQL, Identifier

from estnltk_core import RelationLayer
from estnltk_core.taggers import RelationTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer

from estnltk import logger
from estnltk import Text
from estnltk.converters import layer_to_dict, text_to_dict

from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import count_rows
from estnltk.storage.postgres import LayerQuery
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import table_identifier


logger.setLevel('DEBUG')

def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))

# ========================================================================================


# Original source: https://docs.python.org/3/library/itertools.html#itertools.pairwise
def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

class NumberComparisonRelationsTagger(RelationTagger):
    """Tags all numbers in text and annotates relations (equal, less than, greater than) between pairs of numbers."""

    conf_param = ['regex', 'enveloping']

    def __init__(self,
                 output_layer='number_pair_comparison',
                 output_span_names=('number_a', 'number_b'),
                 output_attributes=('a', 'comp_relation', 'b'),
                 enveloping=None,
                 input_layers=()
                ):
        self.output_layer = output_layer
        self.output_span_names = output_span_names
        self.output_attributes = output_attributes
        self.enveloping = enveloping
        if isinstance(enveloping, str) and enveloping not in input_layers:
            input_layers += (enveloping, )
        self.input_layers = input_layers
        self.regex = re.compile(r'-?\d+')

    def _make_layer_template(self):
        return RelationLayer(name=self.output_layer, 
                             span_names=self.output_span_names, 
                             attributes=self.output_attributes, 
                             enveloping=self.enveloping, 
                             text_object=None)

    def _make_layer(self, text, layers, status=None):
        layer = self._make_layer_template()
        layer.text_object = text
        # Detect all numbers in text
        numbers = []
        for m in self.regex.finditer(text.text):
            start, end = m.start(), m.end()
            numbers.append( (start, end, text.text[start:end]) )
        # Make pairs and mark relations
        for a, b in pairwise(numbers):
            a_val = int(a[2])
            b_val = int(b[2])
            relation = ''
            if a_val == b_val:
                relation = 'equal'
            elif a_val > b_val:
                relation = 'greater_than'
            elif a_val < b_val:
                relation = 'less_than'
            span_a = (a[0], a[1])
            span_b = (b[0], b[1])
            if isinstance(self.enveloping, str) and self.enveloping == 'words':
                span_a = [span_a]
                span_b = [span_b]
            layer.add_annotation({ 'number_a':span_a, 'number_b':span_b, 
                                   'a' : a_val, 'comp_relation': relation, 'b': b_val } )
        return layer

# ========================================================================================

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

# ========================================================================================


class TestRelationLayerStorage(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_create_relation_layer(self):
        # Note: this is a smoke test about relation layer insertion
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Collection version >= '4.0' is required for storing relation layers
        self.assertTrue( collection.version >= '4.0' )
        
        # Add regular (span) layers
        with collection.insert() as collection_insert:
            for i in range(15):
                if i not in [8, 10]:
                    text = Text('See on tekst number {}. Eelnes tekst number {} ja järgneb tekst {}'.format(i, i-1, i+1)).tag_layer('words')
                else:
                    text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )

        # Create non-sparse relation layer
        rel_tagger = NumberComparisonRelationsTagger(output_layer='number_pair_comparison')
        self.assertFalse( rel_tagger.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger, sparse=False )
        # Assert results (structure)
        self.assertTrue( rel_tagger.output_layer in collection.structure )
        self.assertTrue( collection.is_relation_layer( rel_tagger.output_layer ) )
        self.assertFalse( collection.is_sparse( rel_tagger.output_layer ) )
        # Assert that all layers exist (even empty ones)
        self.assertEqual( _make_count_query( self.storage, collection_name, 
                                             rel_tagger.output_layer ), 15 )

        # Create sparse relation layer via batch-processing
        rel_tagger_2 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_2')
        collection.add_layer( rel_tagger_2.get_layer_template(), sparse=True )
        collection.create_layer_block( tagger=rel_tagger_2, block=(2,0) )
        collection.create_layer_block( tagger=rel_tagger_2, block=(2,1) )
        # Assert results (structure)
        self.assertTrue( rel_tagger_2.output_layer in collection.structure )
        self.assertTrue( collection.is_relation_layer( rel_tagger_2.output_layer ) )
        self.assertTrue( collection.is_sparse( rel_tagger_2.output_layer ) )
        # Assert that all layers exist except empty ones
        self.assertEqual( _make_count_query( self.storage, collection_name, 
                                             rel_tagger_2.output_layer ), 13 )

        self.storage.delete_collection(collection.name)


    def test_access_relation_layer(self):
        # Note: this is a test about relation layer simple access
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Collection version >= '4.0' is required for storing relation layers
        self.assertTrue( collection.version >= '4.0' )
        
        # Create collection with attached layers
        rel_tagger_0 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_0')
        with collection.insert() as collection_insert:
            for i in range(15):
                # Create text with regular (span) layers
                if i not in [8, 10]:
                    text = Text('See on tekst number {}. Eelnes tekst number {} ja järgneb tekst {}'.format(i, i-1, i+1)).tag_layer('words')
                else:
                    text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                # Add attached relation layer
                rel_tagger_0.tag( text )
                assert rel_tagger_0.output_layer in text.relation_layers
                text.meta['number'] = i
                collection_insert( text )
        self.assertTrue( rel_tagger_0.output_layer in collection.structure )
        self.assertTrue( collection.is_relation_layer( rel_tagger_0.output_layer ) )

        # Simple document access on attached relation layer
        collection.selected_layers = ['words', rel_tagger_0.output_layer ]
        text_obj = collection[5]
        self.assertEqual( text_obj.layers, { 'words' } )
        self.assertEqual( text_obj.relation_layers, { rel_tagger_0.output_layer } )
        self.assertEqual( layer_to_dict( text_obj[rel_tagger_0.output_layer] ), \
            {'ambiguous': False,
             'attributes': ('a', 'comp_relation', 'b'),
             'display_order': (),
             'enveloping': None,
             'meta': {},
             'name': 'number_pair_comparison_0',
             'relations': [{'annotations': [{'a': 5, 'b': 4, 'comp_relation': 'greater_than'}],
                            'named_spans': {'number_a': (20, 21), 'number_b': (43, 44)}},
                           {'annotations': [{'a': 4, 'b': 6, 'comp_relation': 'less_than'}],
                            'named_spans': {'number_a': (43, 44), 'number_b': (62, 63)}}],
             'secondary_attributes': (),
             'serialisation_module': 'relations_v1',
             'span_names': ('number_a', 'number_b')}
        )
        text_obj = collection[8]
        self.assertEqual( collection.selected_layers, ['words', rel_tagger_0.output_layer ] )
        self.assertEqual( text_obj.layers, { 'words' } )
        self.assertEqual( text_obj.relation_layers, { rel_tagger_0.output_layer } )
        self.assertEqual( layer_to_dict( text_obj[rel_tagger_0.output_layer] ), \
            {'ambiguous': False,
             'attributes': ('a', 'comp_relation', 'b'),
             'display_order': (),
             'enveloping': None,
             'meta': {},
             'name': 'number_pair_comparison_0',
             'relations': [],
             'secondary_attributes': (),
             'serialisation_module': 'relations_v1',
             'span_names': ('number_a', 'number_b')}
        )

        # Create detached non-sparse relation layer
        rel_tagger_1 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_1')
        self.assertFalse( rel_tagger_1.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_1, sparse=False )
        self.assertTrue( rel_tagger_1.output_layer in collection.structure )

        # Simple document access on non-sparse relation layer
        collection.selected_layers = ['words', rel_tagger_1.output_layer ]
        text_obj = collection[5]
        self.assertEqual( text_obj.layers, { 'words' } )
        self.assertEqual( text_obj.relation_layers, { rel_tagger_1.output_layer } )
        self.assertEqual( layer_to_dict( text_obj[rel_tagger_1.output_layer] ), \
            {'ambiguous': False,
             'attributes': ('a', 'comp_relation', 'b'),
             'display_order': (),
             'enveloping': None,
             'meta': {},
             'name': 'number_pair_comparison_1',
             'relations': [{'annotations': [{'a': 5, 'b': 4, 'comp_relation': 'greater_than'}],
                            'named_spans': {'number_a': (20, 21), 'number_b': (43, 44)}},
                           {'annotations': [{'a': 4, 'b': 6, 'comp_relation': 'less_than'}],
                            'named_spans': {'number_a': (43, 44), 'number_b': (62, 63)}}],
             'secondary_attributes': (),
             'serialisation_module': 'relations_v1',
             'span_names': ('number_a', 'number_b')}
        )
        text_obj_2 = collection[10]
        self.assertEqual( collection.selected_layers, ['words', rel_tagger_1.output_layer ] )
        self.assertEqual( text_obj_2.layers, { 'words' } )
        self.assertEqual( text_obj_2.relation_layers, { rel_tagger_1.output_layer } )
        self.assertEqual( layer_to_dict( text_obj_2[rel_tagger_1.output_layer] ), \
            {'ambiguous': False,
             'attributes': ('a', 'comp_relation', 'b'),
             'display_order': (),
             'enveloping': None,
             'meta': {},
             'name': 'number_pair_comparison_1',
             'relations': [],
             'secondary_attributes': (),
             'serialisation_module': 'relations_v1',
             'span_names': ('number_a', 'number_b')}
        )
        
        # Create detached sparse relation layer
        rel_tagger_2 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_2')
        self.assertFalse( rel_tagger_2.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_2, sparse=True )
        self.assertTrue( rel_tagger_2.output_layer in collection.structure )
        
        # Simple document access on sparse relation layer
        collection.selected_layers = ['words', rel_tagger_2.output_layer ]
        text_obj_3 = collection[8]
        self.assertEqual( collection.selected_layers, ['words', rel_tagger_2.output_layer ] )
        self.assertEqual( text_obj_3.layers, { 'words' } )
        self.assertEqual( text_obj_3.relation_layers, { rel_tagger_2.output_layer } )
        self.assertEqual( layer_to_dict( text_obj_3[rel_tagger_2.output_layer] ), \
            {'ambiguous': False,
             'attributes': ('a', 'comp_relation', 'b'),
             'display_order': (),
             'enveloping': None,
             'meta': {},
             'name': 'number_pair_comparison_2',
             'relations': [],
             'secondary_attributes': (),
             'serialisation_module': 'relations_v1',
             'span_names': ('number_a', 'number_b')}
        )
        text_obj_4 = collection[9]
        self.assertEqual( collection.selected_layers, ['words', rel_tagger_2.output_layer ] )
        self.assertEqual( text_obj_4.layers, { 'words' } )
        self.assertEqual( text_obj_4.relation_layers, { rel_tagger_2.output_layer } )
        self.assertEqual( layer_to_dict( text_obj_4[rel_tagger_2.output_layer] ), \
            {'ambiguous': False,
             'attributes': ('a', 'comp_relation', 'b'),
             'display_order': (),
             'enveloping': None,
             'meta': {},
             'name': 'number_pair_comparison_2',
             'relations': [{'annotations': [{'a': 9,
                                             'b': 8,
                                             'comp_relation': 'greater_than'}],
                            'named_spans': {'number_a': (20, 21), 'number_b': (43, 44)}},
                           {'annotations': [{'a': 8,
                                             'b': 10,
                                             'comp_relation': 'less_than'}],
                            'named_spans': {'number_a': (43, 44), 'number_b': (62, 64)}}],
             'secondary_attributes': (),
             'serialisation_module': 'relations_v1',
             'span_names': ('number_a', 'number_b')}
        )
        
        self.storage.delete_collection(collection.name)


    def test_select_relation_layer(self):
        # Note: this is a test about relation layer select / iteration
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Collection version >= '4.0' is required for storing relation layers
        self.assertTrue( collection.version >= '4.0' )
        
        # Create collection with attached layers
        rel_tagger_0 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_0')
        with collection.insert() as collection_insert:
            for i in range(15):
                # Create text with regular (span) layers
                if i not in [8, 10]:
                    text = Text('See on tekst number {}. Eelnes tekst number {} ja järgneb tekst {}'.format(i, i-1, i+1)).tag_layer('words')
                else:
                    text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                # Add attached relation layer
                rel_tagger_0.tag( text )
                assert rel_tagger_0.output_layer in text.relation_layers
                text.meta['number'] = i
                collection_insert( text )
        self.assertTrue( rel_tagger_0.output_layer in collection.structure )
        
        # Create detached non-sparse relation layer enveloping 'words'
        rel_tagger_1 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_1',\
                                                       enveloping='words')
        self.assertFalse( rel_tagger_1.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_1, sparse=False )
        self.assertTrue( rel_tagger_1.output_layer in collection.structure )
        
        # Create detached sparse relation layer enveloping 'words'
        rel_tagger_2 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_2',\
                                                       enveloping='words')
        self.assertFalse( rel_tagger_2.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_2, sparse=True )
        self.assertTrue( rel_tagger_2.output_layer in collection.structure )

        # Create detached sentences layer
        sent_tagger = SentenceTokenizer()
        collection.create_layer( tagger=sent_tagger )
        
        # Select attached relation layer
        text_count = 0
        for text_id, text_obj in collection.select(layers=('words', rel_tagger_0.output_layer)):
            self.assertEqual( text_obj.layers, { 'words' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_0.output_layer } )
            if text_id not in [8, 10]:
                self.assertEqual( len(text_obj[rel_tagger_0.output_layer]), 2 )
            else:
                self.assertEqual( len(text_obj[rel_tagger_0.output_layer]), 0 )
            text_count += 1
        self.assertEqual( text_count, 15 )

        # Select detached non-sparse relation layer
        text_count = 0
        for text_id, text_obj in collection.select(layers=(rel_tagger_1.output_layer, 'sentences')):
            self.assertEqual( text_obj.layers, { 'words', 'sentences' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_1.output_layer } )
            self.assertEqual( text_obj[rel_tagger_1.output_layer].enveloping, 'words' )
            if text_id not in [8, 10]:
                self.assertEqual( len(text_obj[rel_tagger_1.output_layer]), 2 )
            else:
                self.assertEqual( len(text_obj[rel_tagger_1.output_layer]), 0 )
            text_count += 1
        self.assertEqual( text_count, 15 )

        # Select detached sparse relation layer
        text_count = 0
        for text_id, text_obj in collection.select(layers=(rel_tagger_2.output_layer, 'sentences')):
            self.assertEqual( text_obj.layers, { 'words', 'sentences' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_2.output_layer } )
            self.assertEqual( text_obj[rel_tagger_2.output_layer].enveloping, 'words' )
            if text_id not in [8, 10]:
                self.assertEqual( len(text_obj[rel_tagger_2.output_layer]), 2 )
            else:
                self.assertEqual( len(text_obj[rel_tagger_2.output_layer]), 0 )
            text_count += 1
        self.assertEqual( text_count, 15 )

        # Select detached sparse relation layer, skip text objects with empty layers
        text_count = 0
        for text_id, text_obj in collection.select(layers=(rel_tagger_2.output_layer, 'sentences'), \
                                                           keep_all_texts=False):
            self.assertTrue( text_id not in [8, 10] )
            self.assertEqual( text_obj.layers, { 'words', 'sentences' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_2.output_layer } )
            self.assertEqual( text_obj[rel_tagger_2.output_layer].enveloping, 'words' )
            self.assertEqual( len(text_obj[rel_tagger_2.output_layer]), 2 )
            text_count += 1
        self.assertEqual( text_count, 13 )

        self.storage.delete_collection(collection.name)


    def test_select_relation_layer_with_layer_query(self):
        # Note: this is a test about relation layer selection with layer query
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Collection version >= '4.0' is required for storing relation layers
        self.assertTrue( collection.version >= '4.0' )
        
        # Create collection with attached layers
        rel_tagger_0 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_0')
        with collection.insert() as collection_insert:
            for i in range(15):
                # Create text with regular (span) layers
                if i not in [8, 10]:
                    text = Text('See on tekst number {}. Eelnes tekst number {} ja järgneb tekst {}'.format(i, i-1, i+1)).tag_layer('words')
                else:
                    text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                # Add attached relation layer
                rel_tagger_0.tag( text )
                assert rel_tagger_0.output_layer in text.relation_layers
                text.meta['number'] = i
                collection_insert( text )
        self.assertTrue( rel_tagger_0.output_layer in collection.structure )

        # Create detached non-sparse relation layer enveloping 'words'
        rel_tagger_1 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_1',\
                                                       enveloping='words')
        self.assertFalse( rel_tagger_1.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_1, sparse=False )
        self.assertTrue( rel_tagger_1.output_layer in collection.structure )

        # Select attached relation layer
        text_count = 0
        for text_id, text_obj in collection.select(layers=('words', rel_tagger_0.output_layer),
                                                   query=LayerQuery(rel_tagger_0.output_layer, a=1) |
                                                         LayerQuery(rel_tagger_0.output_layer, b=1) ):
            self.assertEqual( text_obj.layers, { 'words' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_0.output_layer } )
            self.assertEqual( len(text_obj[rel_tagger_0.output_layer]), 2 )
            text_count += 1
        self.assertEqual( text_count, 3 )
        text_count = 0
        for text_id, text_obj in collection.select(layers=('words', rel_tagger_0.output_layer),
                                                   query=LayerQuery(rel_tagger_0.output_layer, a=10) |
                                                         LayerQuery(rel_tagger_0.output_layer, b=10) ):
            self.assertEqual( text_obj.layers, { 'words' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_0.output_layer } )
            self.assertEqual( len(text_obj[rel_tagger_0.output_layer]), 2 )
            text_count += 1
        self.assertEqual( text_count, 2 )

        # Create detached sentences layer
        sent_tagger = SentenceTokenizer()
        collection.create_layer( tagger=sent_tagger )

        # Select detached non-sparse relation layer
        text_count = 0
        for text_id, text_obj in collection.select(layers=(rel_tagger_1.output_layer, 'sentences'),
                                                   query=LayerQuery(rel_tagger_1.output_layer, a=1) |
                                                         LayerQuery(rel_tagger_1.output_layer, b=1) ):
            self.assertEqual( text_obj.layers, { 'words', 'sentences' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_1.output_layer } )
            self.assertEqual( len(text_obj[rel_tagger_1.output_layer]), 2 )
            text_count += 1
        self.assertEqual( text_count, 3 )
        text_count = 0
        for text_id, text_obj in collection.select(layers=('words', rel_tagger_1.output_layer, 'sentences'),
                                                   query=LayerQuery(rel_tagger_1.output_layer, a=8) |
                                                         LayerQuery(rel_tagger_1.output_layer, b=8) ):
            self.assertEqual( text_obj.layers, { 'words', 'sentences' } )
            self.assertEqual( text_obj.relation_layers, { rel_tagger_1.output_layer } )
            self.assertEqual( len(text_obj[rel_tagger_1.output_layer]), 2 )
            text_count += 1
        self.assertEqual( text_count, 2 )
        
        self.storage.delete_collection(collection.name)


    def test_delete_relation_layer(self):
        # Note: this is a test about deletion of detached relation layer
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Collection version >= '4.0' is required for storing relation layers
        self.assertTrue( collection.version >= '4.0' )
        
        # Create collection with attached layers
        with collection.insert() as collection_insert:
            for i in range(15):
                # Create text with regular (span) layers
                if i not in [8, 10]:
                    text = Text('See on tekst number {}. Eelnes tekst number {} ja järgneb tekst {}'.format(i, i-1, i+1)).tag_layer('compound_tokens')
                else:
                    text = Text('See on tekst number {}'.format(i)).tag_layer('compound_tokens')
                text.meta['number'] = i
                collection_insert( text )

        # Create detached words layer
        words_tagger = WordTagger()
        collection.create_layer( tagger=words_tagger )
        
        # Create detached non-sparse relation layer
        rel_tagger_1 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_1')
        self.assertFalse( rel_tagger_1.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_1, sparse=False )
        self.assertTrue( rel_tagger_1.output_layer in collection.structure )
        
        # Create detached sparse relation layer enveloping 'words'
        rel_tagger_2 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_2',\
                                                       enveloping='words')
        self.assertFalse( rel_tagger_2.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_2, sparse=True )
        self.assertTrue( rel_tagger_2.output_layer in collection.structure )
        
        # Remove layer created by rel_tagger_1
        self.assertTrue( rel_tagger_1.output_layer in collection.structure )
        collection.delete_layer( rel_tagger_1.output_layer, cascade=False )
        self.assertFalse( rel_tagger_1.output_layer in collection.structure )
        
        # Remove layers created by words_tagger & rel_tagger_2
        self.assertTrue( rel_tagger_2.output_layer in collection.structure )
        self.assertTrue( words_tagger.output_layer in collection.structure )
        collection.delete_layer( words_tagger.output_layer, cascade=True )
        self.assertFalse( rel_tagger_2.output_layer in collection.structure )
        self.assertFalse( words_tagger.output_layer in collection.structure )
        
        self.storage.delete_collection(collection.name)


    def test_export_relation_layer(self):
        # Note: this is a test about exporting relation layer's relations into a separate table
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
        # Collection version >= '4.0' is required for storing relation layers
        self.assertTrue( collection.version >= '4.0' )
        
        # Create collection with attached layers
        rel_tagger_0 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_0')
        with collection.insert() as collection_insert:
            for i in range(15):
                # Create text with regular (span) layers
                if i not in [8, 10]:
                    text = Text('See on tekst number {}. Eelnes tekst number {} ja järgneb tekst {}'.format(i, i-1, i+1)).tag_layer('words')
                else:
                    text = Text('See on tekst number {}'.format(i)).tag_layer('words')
                # Add attached relation layer
                rel_tagger_0.tag( text )
                assert rel_tagger_0.output_layer in text.relation_layers
                text.meta['number'] = i
                collection_insert( text )
        self.assertTrue( rel_tagger_0.output_layer in collection.structure )

        # Create detached non-sparse relation layer enveloping 'words'
        rel_tagger_1 = NumberComparisonRelationsTagger(output_layer='number_pair_comparison_1',\
                                                       enveloping='words')
        self.assertFalse( rel_tagger_1.output_layer in collection.structure )
        collection.create_layer( tagger=rel_tagger_1, sparse=False )
        self.assertTrue( rel_tagger_1.output_layer in collection.structure )
        
        #
        # 1) Export attached rel_tagger_0.output_layer with all the attributes
        #
        collection.export_layer( rel_tagger_0.output_layer, attributes=['a', 'comp_relation', 'b'] )
        table_name='{}__{}__export'.format(collection_name, rel_tagger_0.output_layer)
        assert table_exists(self.storage, table_name)
        # Validate exported annotations
        exported_table_identifier = \
            table_identifier(storage=self.storage, table_name=table_name)
        table_entries = _make_simple_query_on_table( self.storage, exported_table_identifier )
        expected_entries = \
            [(1, 0, 0, 20, 21, 43, 45, '0', 'greater_than', '-1'),
             (2, 0, 1, 43, 45, 63, 64, '-1', 'less_than', '1'),
             (3, 1, 0, 20, 21, 43, 44, '1', 'greater_than', '0'),
             (4, 1, 1, 43, 44, 62, 63, '0', 'less_than', '2'),
             (5, 2, 0, 20, 21, 43, 44, '2', 'greater_than', '1'),
             (6, 2, 1, 43, 44, 62, 63, '1', 'less_than', '3'),
             (7, 3, 0, 20, 21, 43, 44, '3', 'greater_than', '2'),
             (8, 3, 1, 43, 44, 62, 63, '2', 'less_than', '4'),
             (9, 4, 0, 20, 21, 43, 44, '4', 'greater_than', '3'),
             (10, 4, 1, 43, 44, 62, 63, '3', 'less_than', '5'),
             (11, 5, 0, 20, 21, 43, 44, '5', 'greater_than', '4'),
             (12, 5, 1, 43, 44, 62, 63, '4', 'less_than', '6'),
             (13, 6, 0, 20, 21, 43, 44, '6', 'greater_than', '5'),
             (14, 6, 1, 43, 44, 62, 63, '5', 'less_than', '7'),
             (15, 7, 0, 20, 21, 43, 44, '7', 'greater_than', '6'),
             (16, 7, 1, 43, 44, 62, 63, '6', 'less_than', '8'),
             (17, 9, 0, 20, 21, 43, 44, '9', 'greater_than', '8'),
             (18, 9, 1, 43, 44, 62, 64, '8', 'less_than', '10'),
             (19, 11, 0, 20, 22, 44, 46, '11', 'greater_than', '10'),
             (20, 11, 1, 44, 46, 64, 66, '10', 'less_than', '12'),
             (21, 12, 0, 20, 22, 44, 46, '12', 'greater_than', '11'),
             (22, 12, 1, 44, 46, 64, 66, '11', 'less_than', '13'),
             (23, 13, 0, 20, 22, 44, 46, '13', 'greater_than', '12'),
             (24, 13, 1, 44, 46, 64, 66, '12', 'less_than', '14'),
             (25, 14, 0, 20, 22, 44, 46, '14', 'greater_than', '13'),
             (26, 14, 1, 44, 46, 64, 66, '13', 'less_than', '15')]
        assert table_entries == expected_entries 
        
        #
        # 2) Export attached rel_tagger_1.output_layer with all the attributes
        #
        collection.export_layer( rel_tagger_1.output_layer, attributes=['a', 'comp_relation', 'b'] )
        table_name='{}__{}__export'.format(collection_name, rel_tagger_1.output_layer)
        assert table_exists(self.storage, table_name)
        # Validate exported annotations
        exported_table_identifier_2 = \
            table_identifier(storage=self.storage, table_name=table_name)
        table_entries_2 = _make_simple_query_on_table( self.storage, exported_table_identifier_2 )
        assert table_entries_2 == expected_entries 
        
        self.storage.delete_collection(collection.name)


if __name__ == '__main__':
    unittest.main()
