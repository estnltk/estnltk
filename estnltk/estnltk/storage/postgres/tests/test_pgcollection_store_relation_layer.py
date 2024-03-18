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

from estnltk import logger
from estnltk import Text
from estnltk.converters import layer_to_dict, text_to_dict

from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import count_rows


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

    conf_param = ['regex']

    def __init__(self,
                 output_layer='number_pair_comparison',
                 output_span_names=('number_a', 'number_b'),
                 output_attributes=('comp_relation',),
                 input_layers=()           
                ):
        self.output_layer = output_layer
        self.output_span_names = output_span_names
        self.output_attributes = output_attributes
        self.input_layers = input_layers
        self.regex = re.compile(r'-?\d+')

    def _make_layer_template(self):
        return RelationLayer(name=self.output_layer, 
                             span_names=self.output_span_names,
                             attributes=self.output_attributes,
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
            layer.add_annotation({ 'number_a':(a[0], a[1]), 'number_b':(b[0], b[1]), 
                                   'comp_relation': relation } )
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


class TestRelationLayerCreation(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)

        self.maxDiff = None

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_create_relation_layer_insertion(self):
        # Note: this is a smoke test about relation layer insertion
        # PostgresStorage does not fully support relation layers yet
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

        # Annotate relation layer
        rel_tagger = NumberComparisonRelationsTagger(output_layer='number_pair_comparison')
        self.assertFalse( rel_tagger.output_layer in collection.structure )
        
        collection.create_layer( tagger=rel_tagger, sparse=True )
        # Assert results (structure)
        self.assertTrue( rel_tagger.output_layer in collection.structure )
        self.assertTrue( collection.structure[rel_tagger.output_layer].get('is_relation_layer') )
        self.assertTrue( collection.is_sparse( rel_tagger.output_layer ) )
        
        # Assert 
        self.assertEqual( _make_count_query( self.storage, collection_name, 
                                             rel_tagger.output_layer ), 
                          13 )


        self.storage.delete_collection(collection.name)



if __name__ == '__main__':
    unittest.main()
