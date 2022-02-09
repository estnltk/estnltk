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


class TestPgSubCollectionSample(unittest.TestCase):
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


    def _create_test_collection_of_docs(self, size=100):
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
                            collection_insert(text, meta_data={'text_id':text.meta['text_id'],\
                                                               'text_name':text.meta['text_name'] })
                            counter += 1
                        elif size == 200:
                            for adj in ['hea', 'tore']:
                                text_str = (' '.join([adj, subj, verb, obj])).capitalize()+'.'
                                text = Text( text_str ).tag_layer('sentences')
                                text.meta['text_id'] = counter+1
                                text.meta['text_name'] = 'text_{}'.format(counter+1)
                                collection_insert(text, meta_data={'text_id':text.meta['text_id'],\
                                                                   'text_name':text.meta['text_name'] })
                                counter += 1
        return collection



    def test_pgsubcollection_sample_query_based_on_simple_select(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100)
        #
        # Construction type: JOIN
        #
        # Default select with sample size approx. 5%
        res = list( collection.select().sample(5, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[1].meta['text_id'] for t in res], [20, 38, 77, 98])
        # Default select without indexes and with sample size approx. 5%
        res = list( collection.select(return_index=False).sample(5, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 4)
        self.assertTrue( type(res[0]) is Text )
        self.assertListEqual([t.meta['text_id'] for t in res], [20, 38, 77, 98])
        # Default select with collection_meta and sample size approx. 5% 
        res = list( collection.select(collection_meta=['text_id']).sample(5, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res[0]), 3)
        self.assertListEqual([t[2] for t in res], [{'text_id': 20}, {'text_id': 38}, {'text_id': 77}, {'text_id': 98}])
        #
        # Construction type: ANY
        #
        # Default select with sample size approx. 5%
        res = list( collection.select().sample(5, seed=55, method='BERNOULLI', construction='ANY') )
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[1].meta['text_id'] for t in res], [20, 38, 77, 98])
        # Default select without indexes and with sample size approx. 5%
        res = list( collection.select(return_index=False).sample(5, seed=55, method='BERNOULLI', construction='ANY') )
        self.assertEqual(len(res), 4)
        self.assertTrue( type(res[0]) is Text )
        self.assertListEqual([t.meta['text_id'] for t in res], [20, 38, 77, 98])
        # Default select with collection_meta and sample size approx. 5% 
        res = list( collection.select(collection_meta=['text_id']).sample(5, seed=55, method='BERNOULLI', construction='ANY') )
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res[0]), 3)
        self.assertListEqual([t[2] for t in res], [{'text_id': 20}, {'text_id': 38}, {'text_id': 77}, {'text_id': 98}])
        #
        # Test bigger sample sizes
        #
        # Default select with sample size approx. 25%
        res = list( collection.select().sample(25, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 27)
        self.assertEqual(len(res[0]), 2)
        expected_text_ids = [3, 12, 16, 17, 18, 20, 22, 23, 26, 32, 37, 38, 40, 48, \
                             51, 60, 66, 68, 72, 77, 79, 80, 81, 84, 93, 95, 98]
        self.assertListEqual( [t[1].meta['text_id'] for t in res], expected_text_ids )
        # Default select with sample size approx. 50%
        res = list( collection.select().sample(50, seed=555, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 44)
        self.assertEqual(len(res[0]), 2)
        expected_text_ids = [0, 2, 4, 6, 9, 10, 15, 17, 18, 21, 23, 26, 27, 28, 29, 30,\
                             33, 34, 36, 37, 41, 44, 49, 51, 52, 55, 58, 59, 60, 69, 71, \
                             75, 77, 78, 79, 80, 81, 82, 87, 88, 92, 94, 96, 99]
        self.assertListEqual( [t[0] for t in res], expected_text_ids )
        # Default select with sample size approx. 75%
        res = list( collection.select().sample(75, seed=555, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 76)
        self.assertEqual(len(res[0]), 2)
        expected_text_ids = [0, 2, 3, 4, 6, 7, 8, 9, 10, 13, 15, 16, 17, 18, 19, 20, 21, \
                             23, 26, 27, 28, 29, 30, 32, 33, 34, 36, 37, 39, 40, 41, 43, \
                             44, 45, 48, 49, 50, 51, 52, 53, 55, 56, 58, 59, 60, 62, 63, \
                             64, 66, 68, 69, 70, 71, 72, 75, 76, 77, 78, 79, 80, 81, 82, \
                             83, 84, 85, 86, 87, 88, 89, 90, 92, 94, 96, 97, 98, 99]
        self.assertListEqual( [t[0] for t in res], expected_text_ids )
        # Default select with sample size approx. 10% and no fixed seed
        res = list( collection.select().sample(10, seed=None, method='BERNOULLI', construction='JOIN') )
        # The number of selected documents will fluctuate
        # and we give it a broad approximate range
        self.assertLessEqual(0, len(res))
        self.assertGreaterEqual(10+30, len(res))
        collection.delete()



    def test_pgsubcollection_sample_query_based_on_simple_select_and_fixed_amount(self):
        # This is works with psql version 10.19, but earlier versions gave 
        # different results on the same seed values
        
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=200)
        cur_selection = collection.select()
        # Default select with sample size of approx. 15 elements
        res = list( collection.select().sample(15, amount_type='SIZE', seed=105, method='BERNOULLI') )
        self.assertEqual(len(res), 15)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[0] for t in res] , [2, 25, 28, 49, 57, 112, 124, 130, 144, 147, 154, 158, 174, 190, 198])
        # Default select with sample size of approx. 45 elements
        res = list( collection.select().sample(45, amount_type='SIZE', seed=125, method='BERNOULLI') )
        self.assertEqual(len(res), 43)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[0] for t in res] , [1, 6, 13, 17, 22, 33, 40, 41, 42, 45, 54, 55, 56, 58, 
                                                    65, 70, 78, 81, 86, 91, 94, 95, 100, 102, 117, 118, 139, 
                                                    144, 148, 155, 159, 160, 163, 165, 174, 175, 179, 180, 
                                                    187, 189, 190, 191, 197])
        collection.delete()



    def test_pgsubcollection_sample_query_reiteration(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100)
        cur_selection = collection.select()
        # Reiteration is allowed if seed is fixed:
        # Default select with sample size approx. 5%
        res1 = list( cur_selection.sample(5, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res1), 4)
        res2 = list( cur_selection.sample(5, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res2), 4)
        # Reiteration is disallowed without seed
        # Default select with sample size approx. 5% and no seed
        res3 = list( cur_selection.sample(5, seed=None, method='BERNOULLI', construction='JOIN') )
        # The number of selected documents will fluctuate
        # and we give it a broad approximate range
        self.assertLessEqual(0, len(res3))
        self.assertGreaterEqual(5+20, len(res3))
        with self.assertRaises(Exception) as exception:
            # Reiteration should rise an exception
            res4 = list( cur_selection.sample(5, seed=None, method='BERNOULLI', construction='JOIN') )
        collection.delete()



    def test_pgsubcollection_sample_query_based_on_layer_select(self):
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
        #
        # Construction type: JOIN
        # Select with 'morph_analysis' and with sample size approx. 5%
        res = list( collection.select(layers=[ vabamorf_tagger.output_layer ]).sample(5, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[1].meta['text_id'] for t in res], [20, 38, 77, 98])
        self.assertSetEqual( res[0][1].layers, { 'words', vabamorf_tagger.output_layer } )

        # Select 'morph_analysis' with collection_meta and sample size approx. 5% 
        res = list( collection.select(layers=[ vabamorf_tagger.output_layer ], \
                                      collection_meta=['text_id']).sample(5, seed=77, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 5)
        self.assertEqual(len(res[0]), 3)
        self.assertListEqual([t[2] for t in res], [{'text_id': 6}, {'text_id': 22}, {'text_id': 28}, {'text_id': 54}, {'text_id': 79}])
        for (text_id, text_obj, text_meta) in res:
            self.assertSetEqual( text_obj.layers, { 'words', vabamorf_tagger.output_layer } )
        # Select with 'morph_analysis' and with sample size approx. 25%
        res = list( collection.select(layers=[ vabamorf_tagger.output_layer ]).sample(25, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 27)
        self.assertEqual(len(res[0]), 2)
        expected_text_ids = [3, 12, 16, 17, 18, 20, 22, 23, 26, 32, 37, 38, 40, 48, \
                             51, 60, 66, 68, 72, 77, 79, 80, 81, 84, 93, 95, 98]
        self.assertListEqual( [t[1].meta['text_id'] for t in res], expected_text_ids )
        self.assertSetEqual( res[0][1].layers, { 'words', vabamorf_tagger.output_layer } )
        #
        # Construction type: ANY
        # Select with 'morph_analysis' and with sample size approx. 5%
        res = list( collection.select(layers=[ vabamorf_tagger.output_layer ]).sample(5, seed=55, method='BERNOULLI', construction='ANY') )
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[1].meta['text_id'] for t in res], [20, 38, 77, 98])
        self.assertSetEqual( res[0][1].layers, { 'words', vabamorf_tagger.output_layer } )
        # Default select with sample size approx. 10% and no fixed seed
        res = list( collection.select(layers=[ vabamorf_tagger.output_layer ]).sample(10, seed=None, method='BERNOULLI', construction='JOIN') )
        # The number of selected documents will fluctuate
        # and we give it a broad approximate range
        self.assertLessEqual(0, len(res))
        self.assertGreaterEqual(10+30, len(res))
        collection.delete()



    def test_pgsubcollection_sample_query_based_on_query_select(self):
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
        # Construction type: JOIN
        # Select with 'morph_analysis' and SliceQuery(30:80) and sample size approx. 5%
        res = list( collection.select(query=SliceQuery(30, 80), 
                                      layers=[ vabamorf_tagger.output_layer ]).sample(5, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[1].meta['text_id'] for t in res], [38, 77])
        # Construction type: default
        # Select with 'morph_analysis' and MetadataQuery(text_id=20...39) and sample size approx. 50%
        res = list( collection.select(query=MetadataQuery( {'text_id':[ str(20+i) for i in range(10) ]}, meta_type='TEXT' ), 
                                      layers=[ vabamorf_tagger.output_layer ]).sample(50, seed=55, method='BERNOULLI') )
        self.assertEqual(len(res), 6)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[1].meta['text_id'] for t in res], [20, 21, 22, 23, 26, 29])
        # Select with 'morph_analysis' and SliceQuery(25:75) and sample size approx. 10 items
        res = list( collection.select(query=SliceQuery(25, 75), 
                                      layers=[ vabamorf_tagger.output_layer ]).sample(10, amount_type = 'SIZE', seed=55, method='BERNOULLI') )
        self.assertEqual(len(res), 9)
        self.assertEqual(len(res[0]), 2)
        self.assertListEqual([t[1].meta['text_id'] for t in res], [26, 32, 37, 38, 40, 51, 66, 68, 72])
        collection.delete()
        
