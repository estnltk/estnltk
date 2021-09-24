import unittest
import random
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema

from estnltk import logger
from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import create_schema, delete_schema

from estnltk.storage.postgres.queries.metadata_query import MetadataQuery
from estnltk.storage.postgres.queries.slice_query import SliceQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgSubCollectionPermutate(unittest.TestCase):
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


    def _create_test_collection_of_docs( self, size=100 ):
        assert size in [100, 200], '(!) Unexpected test collection size: {}'.format(size)
        # Create a test collection
        collection = self.storage[get_random_collection_name()]
        collection.create(meta=OrderedDict([('text_id', 'int'), ('text_name', 'str')]))
        # Populate collection with test sentences
        logger.debug('Creating a collection of {} texts:'.format(size))
        subj_words = ['kiisumiisu', 'vanahärra', 'vanama', 'neiu', 'tuttav']
        verb_words = ['loeb', 'keedab', 'kasvatab', 'kiigutab', 'organiseerib']
        obj_words = ['raamatut', 'ruutmeetreid', 'kartuleid', 'kohvrit']
        with collection.insert() as collection_insert:
            counter = 0
            for subj in subj_words:
                for verb in verb_words:
                    for obj in obj_words:
                        if size == 100:
                            text_str = (' '.join([subj, verb, obj])).capitalize()+'.'
                            text = Text( text_str ).tag_layer('sentences')
                            text.meta['text_id'] = counter+1
                            text.meta['text_name'] = 'text_{}'.format(counter+1)
                            text.meta['mod_2'] = str( 1 + (counter % 2) )
                            text.meta['mod_3'] = str( 1 + (counter % 3) )
                            collection_insert(text, meta_data={'text_id':text.meta['text_id'],\
                                                               'text_name':text.meta['text_name'] })
                            counter += 1
                        elif size == 200:
                            for adj in ['hea', 'tore']:
                                text_str = (' '.join([adj, subj, verb, obj])).capitalize()+'.'
                                text = Text( text_str ).tag_layer('sentences')
                                text.meta['text_id'] = counter+1
                                text.meta['text_name'] = 'text_{}'.format(counter+1)
                                text.meta['mod_2'] = str( 1 + (counter % 2) )
                                text.meta['mod_3'] = str( 1 + (counter % 3) )
                                collection_insert(text, meta_data={'text_id':text.meta['text_id'],\
                                                                   'text_name':text.meta['text_name'] })
                                counter += 1
        return collection

    ##  
    ##  Notes about testing functionalities based on PostgreSQL's SETSEED() and RANDOM():
    ##   -- we cannot test for concrete sequences of documents, because 
    ##      even if the seed is fixed, random gives different results
    ##      depending on server's platform (Windows or Linux);
    ##   -- this issue can be resolved by migrating to PostgreSQL's
    ##      version 12.0 (or beyond), which provides uniform behaviour
    ##      for SETSEED() / RANDOM() across platforms;
    ##

    def test_pgsubcollection_permutate_based_on_simple_select_and_query_constraints(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100)
        
        # Permutate simple select (seed 0.0)
        seed_0_results_1 = list( collection.select().permutate(seed=0.0) )
        self.assertEqual(len(seed_0_results_1), 100)
        self.assertEqual(len(seed_0_results_1[0]), 2)
        text_ids = [text_id for text_id, _ in seed_0_results_1]
        self.assertTrue( len(seed_0_results_1), len(set(text_ids)) )
        # Check that the order "appears randomized"
        self.assertFalse( text_ids[:5] == [0,1,2,3,4] )

        # Permutate simple select wo return_index (seed 0.5)
        seed_0_5_results_1 = list( collection.select(return_index=False).permutate(seed=0.5) )
        self.assertEqual(len(seed_0_5_results_1), 100)
        self.assertTrue( type(seed_0_5_results_1[0]) is Text )
        text_ids = [text.meta['text_id'] for text in seed_0_5_results_1]
        self.assertTrue( len(seed_0_5_results_1), len(set(text_ids)) )
        
        # Permutate simple select with metadata (seed 0.0)
        seed_0_results_2 = list( collection.select(collection_meta=['text_id', 'text_name']).permutate(seed=0.0) )
        self.assertEqual(len(seed_0_results_2), 100)
        self.assertEqual(len(seed_0_results_2[0]), 3)
        
        # Check that fixed seeds gave the same results
        # 1) text_ids
        text_ids_1 = [text_id for text_id, _    in seed_0_results_1]
        text_ids_2 = [text_id for text_id, _, _ in seed_0_results_2]
        self.assertListEqual( text_ids_1[:10], text_ids_2[:10])
        self.assertListEqual( text_ids_1[-10:], text_ids_2[-10:])
        # 2) text_ids + meta
        text_ids_and_meta_1 = [ {'text_id': tid+1, 'text_name': 'text_{}'.format(tid+1)} for (tid, text) in seed_0_results_1 ]
        text_ids_and_meta_2 = [ meta for (tid, text, meta) in seed_0_results_2 ]
        self.assertListEqual( text_ids_and_meta_1[:5], text_ids_and_meta_2[:5] )
        self.assertListEqual( text_ids_and_meta_1[-5:], text_ids_and_meta_2[-5:] )

        # Permutate select with metadata constraining query (seed 0.25)
        seed_0_5_results_2 = list( collection.select(query=MetadataQuery({'mod_2':'2'}, meta_type='TEXT') ).permutate(seed=0.25) )
        self.assertEqual(len(seed_0_5_results_2), 50)
        self.assertEqual(len(seed_0_5_results_2[0]), 2)
        text_ids = [text_id for text_id, _ in seed_0_5_results_2]
        self.assertTrue( len(seed_0_5_results_2), len(set(text_ids)) )
        # Validate mod_2 values
        for text_id, text_obj in seed_0_5_results_2:
            self.assertTrue( text_obj.meta['mod_2'] == '2' )
        
        collection.delete()



    def test_pgsubcollection_permutate_based_on_layer_select(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100)
        # Add morph_analysis as a detached layer
        vabamorf_tagger = VabamorfTagger(disambiguate=False)
        def vabamorf_row_mapper(row):
            text_id, text = row[0], row[1]
            status = {}
            layer = vabamorf_tagger.make_layer(text=text, status=status)
            return RowMapperRecord(layer=layer, meta=status)
        data_iterator = collection.select( layers=['words', 'sentences', 'compound_tokens'] )
        collection.create_layer(layer_name = vabamorf_tagger.output_layer, 
                                data_iterator = data_iterator, 
                                row_mapper = vabamorf_row_mapper, 
                                tagger=None, mode='overwrite')
        
        # Select 'morph_analysis' with permutation (seed -0.25)
        seed_0_25_results_1 = list( collection.select(layers=[ vabamorf_tagger.output_layer ]).permutate(seed=-0.25) )
        self.assertEqual(len(seed_0_25_results_1), 100)
        self.assertEqual(len(seed_0_25_results_1[0]), 2)
        for text_id, text_obj in seed_0_25_results_1:
            self.assertTrue( 0 <= text_id and text_id < 100 )
            self.assertTrue( vabamorf_tagger.output_layer in text_obj.layers )
            self.assertTrue( 'words' in text_obj.layers )
        text_ids_1 = [text_id for text_id, _ in seed_0_25_results_1]
        # Check that the order "appears randomized"
        self.assertFalse( text_ids_1[:5] == [0,1,2,3,4] )

        # Select slice of documents from 25 to 75 with 'morph_analysis' and permutate (seed -0.25)
        seed_0_25_results_2 = list( collection.select(query=SliceQuery(25,75), \
                                    layers=[ vabamorf_tagger.output_layer ]).permutate(seed=-0.25) )
        self.assertEqual(len(seed_0_25_results_2), 50)
        self.assertEqual(len(seed_0_25_results_2[0]), 2)
        text_ids_2 = [text_id for text_id, _ in seed_0_25_results_2]
        self.assertTrue( len(seed_0_25_results_2), len(set(text_ids_2)) )
        for text_id, text_obj in seed_0_25_results_2:
            self.assertTrue( 25 <= text_id and text_id < 75 )
            self.assertTrue( vabamorf_tagger.output_layer in text_obj.layers )
            self.assertTrue( 'words' in text_obj.layers )

        # Select 'morph_analysis' with permutation (seed -0.25)
        seed_0_25_results_3 = list( collection.select(layers=[ vabamorf_tagger.output_layer ]).permutate(seed=-0.25) )
        text_ids_3 = [text_id for text_id, _ in seed_0_25_results_3]
        # Check that fixed seeds gave the same results
        self.assertListEqual( text_ids_1[:10], text_ids_3[:10])
        self.assertListEqual( text_ids_1[-10:], text_ids_3[-10:])

        # Permutate without seed
        res = list( collection.select().permutate() )
        self.assertEqual(len(res), 100)
        self.assertEqual(len(res[0]), 2)
        text_ids = [text_id for text_id, _ in res]
        self.assertTrue( len(res), len(set(text_ids)) )
        
        collection.delete()

