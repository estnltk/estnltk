import unittest
import pytest
import random
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema

from estnltk import logger
from estnltk import Text
from estnltk.taggers import VabamorfTagger, SentenceTokenizer
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import create_schema, delete_schema

from estnltk.storage.postgres.queries.metadata_query import MetadataQuery

from estnltk.storage.postgres.tests.test_sparse_layer import ModuleRemainderNumberTagger

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


def get_server_version():
    schema = "test_schema"
    storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
    # https://www.psycopg.org/docs/connection.html#connection.server_version
    version = storage.conn.server_version
    storage.close()
    return version


class TestPgSubCollectionSampleFromLayer(unittest.TestCase):
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


    def _create_test_collection_of_docs(self, size=25, detached_sentences=False):
        assert size in [25, 100], '(!) Unexpected test collection size: {}'.format(size)
        # Create a test collection
        collection = self.storage[get_random_collection_name()]
        collection.create(meta=OrderedDict([('text_id', 'int'), ('text_name', 'str')]))
        # Populate collection with test sentences
        logger.debug('Creating a collection of {} texts:'.format(size))
        subj_words = ['kiisumiisu', 'vanahärra', 'vanama', 'neiu', 'tuttav', \
                      'filharmoonik', 'sahin', 'kärbes', 'teleskoop', 'võsalendur',\
                      'kapsauss', 'klaverijalg', 'sugulane', 'viiuldaja', 'temake', \
                      'kvantarvuti', 'puhvet', 'kuldlõige', 'proua', 'kahvel', \
                      'peremees', 'kaalujälgija', 'lõkats', 'vintraud', 'vahvel']
        if size == 100:
            new_subj_words = subj_words[:]
            for adj in ['hea', 'tore', 'ilus']:
                for subj in subj_words:
                    new_subj_words.append( adj+' '+subj )
            subj_words = new_subj_words
        verb_words = ['loeb', 'keedab', 'kasvatab', 'kiigutab', 'organiseerib']
        obj_words = ['raamatut', 'ruutmeetreid', 'kartuleid', 'kohvrit', 'distantsõpet']
        with collection.insert() as collection_insert:
            doc_counter = 0
            sent_counter = 0
            for subj in subj_words:
                subj_text = []
                # Generate sentences for the text
                for verb in verb_words:
                    for obj in obj_words:
                        text_str = (' '.join([subj, verb, obj])).capitalize()+'.'
                        subj_text.append( text_str )
                        sent_counter += 1
                # Create Text obj
                if not detached_sentences:
                    text = Text( '\n\n'.join(subj_text) ).tag_layer('sentences')
                else:
                    text = Text( '\n\n'.join(subj_text) ).tag_layer('words')
                text.meta['text_id'] = doc_counter+1
                text.meta['text_name'] = 'text_{}'.format(doc_counter+1)
                text.meta['text_actor'] = subj
                text.meta['mod_2'] = str( 1 + (doc_counter % 2) )
                text.meta['mod_3'] = str( 1 + (doc_counter % 3) )
                collection_insert(text, meta_data={'text_id':text.meta['text_id'],\
                                                   'text_name':text.meta['text_name'] })
                doc_counter += 1
        if detached_sentences:
            # Add sentences as a detached layer
            sent_tokenizer = SentenceTokenizer()
            def sent_tokenizer_row_mapper(row):
                text_id, text = row[0], row[1]
                status = {}
                layer = sent_tokenizer.make_layer(text=text, status=status)
                return RowMapperRecord(layer=layer, meta=status)
            data_iterator = collection.select( layers=['words', 'compound_tokens'] )
            collection.create_layer(layer_name = sent_tokenizer.output_layer, 
                                    data_iterator = data_iterator, 
                                    row_mapper = sent_tokenizer_row_mapper, 
                                    tagger=None, mode='overwrite')
        logger.debug('Created test collection with {} docs and {} sentences.'.format(doc_counter,sent_counter))
        return collection

    ##  
    ##  Notes about testing functionalities based on PostgreSQL's SETSEED() and RANDOM():
    ##   -- at the moment, we cannot test for concrete sequences of 
    #       documents, because even if the seed is fixed, random gives 
    #       different results depending on server's platform (Windows 
    #       or Linux);
    ##   -- this issue can be resolved by migrating to PostgreSQL's
    ##      version 12.0 (or beyond), which provides uniform behaviour
    ##      for SETSEED() / RANDOM() across platforms;
    ##

    def test_pgsubcollection_sample_from_attached_layer_based_on_simple_select(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100, detached_sentences=False)
        
        #
        # amount_type='PERCENTAGE' (default)
        #
        # Default select sentences with sample size approx. 5% (seed -0.7)
        res_seed_0_7_1 = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 5, seed=-0.7) )
        self.assertLessEqual(40, len(res_seed_0_7_1))
        self.assertGreaterEqual(70, len(res_seed_0_7_1))
        self.assertEqual(len(res_seed_0_7_1[0]), 2)
        sent_locations = []
        for (doc_id, dok) in res_seed_0_7_1:
            self.assertTrue( 'sentences' in dok.layers )
            self.assertTrue( 'words' in dok.layers )
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        self.assertLessEqual(25, len(sent_locations))
        self.assertGreaterEqual(250, len(sent_locations))
        
        # Default select sentences with collection_meta sample size approx. 25% (seed 0.1)
        res_seed_0_1_1 = list( collection.select(layers=['sentences'], collection_meta=['text_id']).sample_from_layer('sentences', 25, seed=0.1) )
        self.assertLessEqual(70, len(res_seed_0_1_1))
        self.assertGreaterEqual(100, len(res_seed_0_1_1))
        self.assertEqual(len(res_seed_0_1_1[0]), 3)
        for (doc_id, dok, meta) in res_seed_0_1_1:
            self.assertTrue( 'text_id' in meta )
            self.assertTrue( 1 <= meta['text_id'] and meta['text_id'] <= 100 )

        # Default select sentences with collection_meta and return_index=False sample size approx. 75% (seed 0.0)
        res_seed_00_1 = list( collection.select(layers=['sentences'], return_index=False, collection_meta=['text_id']).sample_from_layer('sentences', 75, seed=0.0) )
        self.assertLessEqual(90, len(res_seed_00_1))
        self.assertGreaterEqual(100, len(res_seed_00_1))
        self.assertEqual(len(res_seed_00_1[0]), 2)
        sent_locations = []
        for (doc_id, (dok, text_meta)) in enumerate(res_seed_00_1):
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        self.assertLessEqual(1600, len(sent_locations))
        self.assertGreaterEqual(2000, len(sent_locations))

        # Check that repeating a query with the same seed gives the same result as before
        # Default select sentences with sample size approx. 5% (seed -0.7)
        res_seed_0_7_2 = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 5, seed=-0.7) )
        self.assertEqual(len(res_seed_0_7_2[0]), 2)
        sent_locations_1 = []
        for (doc_id, dok) in res_seed_0_7_1:
            for sent in dok['sentences']:
                sent_locations_1.append( (doc_id, sent.start, sent.end) )
        sent_locations_2 = []
        for (doc_id, dok) in res_seed_0_7_2:
            for sent in dok['sentences']:
                sent_locations_2.append( (doc_id, sent.start, sent.end) )
        self.assertListEqual( sent_locations_1, sent_locations_2 )
        
        # Check that repeating a query with the same seed gives the same result as before
        # Default select sentences with collection_meta sample size approx. 25% (seed 0.1)
        res_seed_0_1_2 = list( collection.select(layers=['sentences'], collection_meta=['text_id']).sample_from_layer('sentences', 25, seed=0.1) )
        self.assertLessEqual(70, len(res_seed_0_1_2))
        self.assertGreaterEqual(100, len(res_seed_0_1_2))
        self.assertEqual(len(res_seed_0_1_2[0]), 3)
        sent_locations_1 = []
        for (doc_id, dok, meta) in res_seed_0_1_1:
            for sent in dok['sentences']:
                sent_locations_1.append( (doc_id, sent.start, sent.end) )
        sent_locations_2 = []
        for (doc_id, dok, meta) in res_seed_0_1_2:
            for sent in dok['sentences']:
                sent_locations_2.append( (doc_id, sent.start, sent.end) )
        self.assertListEqual( sent_locations_1, sent_locations_2 )


        #
        # amount_type='SIZE'
        #
        # Default select sentences with sample size roughly 100-150 sentences (seed -0.5)
        res_0_5__1 = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 150, amount_type='SIZE', seed=-0.5) )
        self.assertLessEqual(40, len(res_0_5__1))
        self.assertGreaterEqual(100, len(res_0_5__1))
        self.assertEqual(len(res_0_5__1[0]), 2)

        # Default select sentences with return_index=False and sample size roughly 1500 sentences (seed 0.0)
        res_00_1 = list( collection.select(layers=['sentences'], return_index=False).sample_from_layer('sentences', 1500, amount_type='SIZE', seed=0.0) )
        self.assertLessEqual(50, len(res_00_1))
        self.assertGreaterEqual(100, len(res_00_1))
        self.assertTrue( type(res_00_1[0]) is Text )
        sent_locations = []
        for (doc_id, dok) in enumerate(res_00_1):
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        self.assertLessEqual(1200, len(sent_locations))
        self.assertGreaterEqual(1700, len(sent_locations))
        
        # Check that repeating a query with the same seed gives the same result as before
        # Default select sentences with sample size roughly 100-150 sentences (seed -0.5)
        res_0_5__2 = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 150, amount_type='SIZE', seed=-0.5) )
        self.assertEqual(len(res_0_5__1), len(res_0_5__2))
        sent_locations_1 = []
        for (doc_id, dok) in res_0_5__1:
            for sent in dok['sentences']:
                sent_locations_1.append( (doc_id, sent.start, sent.end) )
        sent_locations_2 = []
        for (doc_id, dok) in res_0_5__2:
            for sent in dok['sentences']:
                sent_locations_2.append( (doc_id, sent.start, sent.end) )
        self.assertListEqual( sent_locations_1, sent_locations_2 )

        # Test sampling without seed. 
        # Default select sentences with sample size roughly 1000 sentences
        res = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 1000, amount_type='SIZE') )
        # Note: the results can fluctuate quite much, so we give it a broad range
        self.assertLessEqual(15, len(res))
        self.assertGreaterEqual(100, len(res))
        self.assertEqual(len(res[0]), 2)
        sent_locations = []
        for (doc_id, dok) in res:
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        # Note: the results can fluctuate quite much, so we give it a broad range
        self.assertLessEqual(250, len(sent_locations))
        self.assertGreaterEqual(1750, len(sent_locations))
        
        collection.delete()


    def test_pgsubcollection_sample_from_detached_layer_based_on_simple_select(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100, detached_sentences=True)
        
        # amount_type='PERCENTAGE' (default)
        # Default select sentences with sample size approx. 5% (seed -0.25)
        res_0_25__1 = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 5, seed=-0.25) )
        self.assertLessEqual(30, len(res_0_25__1))
        self.assertGreaterEqual(70, len(res_0_25__1))
        self.assertEqual(len(res_0_25__1[0]), 2)

        # Default select sentences with return_index=False and with sample size approx. 50%
        res = list( collection.select(layers=['sentences'], return_index=False).sample_from_layer('sentences', 50, seed=-0.25) )
        self.assertEqual(len(res), 100)
        self.assertTrue( type(res[0]) is Text )
        sent_locations = []
        for (doc_id, dok) in enumerate(res):
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        self.assertLessEqual(1000, len(sent_locations))
        self.assertGreaterEqual(1500, len(sent_locations))

        # Check that repeating a query with the same seed gives the same result as before
        # Default select sentences with sample size approx. 5% (seed -0.25)
        res_0_25__2 = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 5, seed=-0.25) )
        self.assertEqual(len(res_0_25__1), len(res_0_25__2))
        self.assertEqual(len(res_0_25__2[0]), 2)
        sent_locations_1 = []
        for (doc_id, dok) in res_0_25__1:
            for sent in dok['sentences']:
                sent_locations_1.append( (doc_id, sent.start, sent.end) )
        sent_locations_2 = []
        for (doc_id, dok) in res_0_25__2:
            for sent in dok['sentences']:
                sent_locations_2.append( (doc_id, sent.start, sent.end) )
        self.assertListEqual( sent_locations_1, sent_locations_2 )

        #
        # amount_type='SIZE'
        #
        # Default select sentences with collection_meta and return_index=False sample size roughly 1000 sentences (seed 0.5)
        res_0_5__1 = list( collection.select(layers=['sentences'], return_index=False, collection_meta=['text_id']).sample_from_layer('sentences', 1000, amount_type='SIZE', seed=0.5) )
        self.assertLessEqual(70, len(res_0_5__1))
        self.assertGreaterEqual(100, len(res_0_5__1))
        self.assertEqual(len(res_0_5__1[0]), 2)
       
        # Test sampling without seed. 
        # Default select sentences with sample size roughly 50%
        res = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 50) )
        # Note: the results can fluctuate quite much, so we give it a broad range
        self.assertLessEqual(10, len(res))
        self.assertGreaterEqual(100, len(res))
        self.assertEqual(len(res[0]), 2)
        sent_locations = []
        for (doc_id, dok) in res:
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        # Note: the results can fluctuate quite much, so we give it a broad range
        self.assertLessEqual(500, len(sent_locations))
        self.assertGreaterEqual(2000, len(sent_locations))

        # Check that repeating a query with the same seed gives the same result as before
        # Default select sentences with collection_meta and return_index=False sample size roughly 1000 sentences (seed 0.5)
        res_0_5__2 = list( collection.select(layers=['sentences'], return_index=False, collection_meta=['text_id']).sample_from_layer('sentences', 1000, amount_type='SIZE', seed=0.5) )
        sent_locations_1 = []
        for (doc_id, (dok, text_meta)) in enumerate(res_0_5__1):
            for sent in dok['sentences']:
                sent_locations_1.append( (doc_id, sent.start, sent.end) )
        sent_locations_2 = []
        for (doc_id, (dok, text_meta)) in enumerate(res_0_5__2):
            for sent in dok['sentences']:
                sent_locations_2.append( (doc_id, sent.start, sent.end) )
        self.assertListEqual( sent_locations_1, sent_locations_2 )

        collection.delete()



    def test_pgsubcollection_sample_from_detached_layer_based_on_metadata_select(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100, detached_sentences=True)
        
        # amount_type='PERCENTAGE' (default)
        # Default select where mod_2=2 (every second document) with sentences sample size approx. 25% (seed 0.0)
        res_00__1 = list( collection.select(layers=['sentences'],
                                            query=MetadataQuery({'mod_2':'2'}, meta_type='TEXT')).sample_from_layer('sentences', 25, seed=0.0) )
        self.assertEqual(len(res_00__1[0]), 2)
        sent_locations = []
        for (doc_id, dok) in res_00__1:
            self.assertTrue( dok.meta['mod_2'] == '2' )
            self.assertTrue( 'sentences' in dok.layers )
            self.assertTrue( 'words' in dok.layers )
        
        # Default select where mod_3=3 (every third document) with return_index=False and sentences sample size approx. 75% (seed 0.5)
        res = list( collection.select(layers=['sentences'],
                                      query=MetadataQuery({'mod_3':'3'}, meta_type='TEXT'),
                                      return_index=False).sample_from_layer('sentences', 75, seed=0.5) )
        self.assertLessEqual(30, len(res))
        self.assertGreaterEqual(40, len(res))
        self.assertTrue( type(res[0]) is Text )
        for (doc_id, dok) in enumerate(res):
            self.assertTrue( dok.meta['mod_3'] == '3' )
            self.assertTrue( 'sentences' in dok.layers )
            self.assertTrue( 'words' in dok.layers )
        
        # Check that repeating a query with the same seed gives the same result as before
        # Default select where mod_2=2 (every second document) with sentences sample size approx. 25% (seed 0.0)
        res_00__2 = list( collection.select(layers=['sentences'],
                                            query=MetadataQuery({'mod_2':'2'}, meta_type='TEXT')).sample_from_layer('sentences', 25, seed=0.0) )
        self.assertEqual(len(res_00__1), len(res_00__2))
        sent_locations_1 = []
        for (doc_id, dok) in res_00__1:
            self.assertTrue( dok.meta['mod_2'] == '2' )
            for sent in dok['sentences']:
                sent_locations_1.append( (doc_id, sent.start, sent.end) )
        sent_locations_2 = []
        for (doc_id, dok) in res_00__2:
            self.assertTrue( dok.meta['mod_2'] == '2' )
            for sent in dok['sentences']:
                sent_locations_2.append( (doc_id, sent.start, sent.end) )
        self.assertListEqual( sent_locations_1, sent_locations_2 )
        
        collection.delete()


    # This test can only be launched on server versions where SETSEED() / RANDOM() 
    # behaviour has been fixed across the platforms (so, we get same results everywhere)
    @pytest.mark.skipif(get_server_version() < 120000,
                        reason="PostgreSQL server version >= 12.0 is required for this test")
    def test_pgsubcollection_sample_from_sparse_layer(self):
        # Test that sampling works with sparse layers
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        # Assert structure version 3.0+ (required for sparse layers)
        self.assertGreaterEqual(collection.version , '3.0')
        
        # Add regular (non-sparse) layers
        with collection.insert() as collection_insert:
            for i in range(200):
                text = Text('See on tekst number {}'.format(i))
                text.tag_layer('words')
                text.meta['number'] = i
                collection_insert( text )
        
        # Add sparse layers
        even_number_tagger = ModuleRemainderNumberTagger('even_numbers', 2, 0)
        fourth_number_tagger = ModuleRemainderNumberTagger('fourth_numbers', 4, 0, 
                                                            parent_layer='even_numbers')
        collection.create_layer( tagger=even_number_tagger,  sparse=True )
        collection.create_layer( tagger=fourth_number_tagger, sparse=True )
        
        # Select a sample from sparse layer (~5 %)
        # Caveat: we get less than expected
        res = list( collection.select(layers=['even_numbers']).sample_from_layer('even_numbers', 5, seed=0.0) )
        annotation_locations = []
        for (doc_id, dok) in res:
            for span in dok['even_numbers']:
                annotation_locations.append( (doc_id, span.start, span.end) )
        self.assertListEqual( [t[0] for t in res], [0, 168] )
        self.assertListEqual( annotation_locations, [(0, 20, 21), (168, 20, 23)] )
        
        # Select a sample from sparse layer (~25 %)
        # Caveat: we get less than expected
        res = list( collection.select(layers=['even_numbers']).sample_from_layer('even_numbers', 25, seed=0.0) )
        annotation_locations = []
        for (doc_id, dok) in res:
            for span in dok['even_numbers']:
                annotation_locations.append( (doc_id, span.start, span.end) )
        self.assertListEqual( [t[0] for t in res],  [0, 2, 6, 24, 50, 98, 124, 136, 138] )
        self.assertListEqual( annotation_locations, [(0, 20, 21), (2, 20, 21), (6, 20, 21), 
                                                     (24, 20, 22), (50, 20, 22), (98, 20, 22), 
                                                     (124, 20, 23), (136, 20, 23), (138, 20, 23)] )
        
        # Select a sample from sparse layer (~25 %) with keep_all_texts=False
        # The result should not change
        res = list( collection.select(layers=['even_numbers'], keep_all_texts=False).sample_from_layer('even_numbers', 25, seed=0.0) )
        annotation_locations = []
        for (doc_id, dok) in res:
            for span in dok['even_numbers']:
                annotation_locations.append( (doc_id, span.start, span.end) )
        self.assertListEqual( [t[0] for t in res],  [0, 2, 6, 24, 50, 98, 124, 136, 138] )
        self.assertListEqual( annotation_locations, [(0, 20, 21), (2, 20, 21), (6, 20, 21), 
                                                     (24, 20, 22), (50, 20, 22), (98, 20, 22), 
                                                     (124, 20, 23), (136, 20, 23), (138, 20, 23)] )

        # Select a sample from another sparse layer (~~50 %)
        # Caveat: we get less than expected
        res = list( collection.select(layers=['fourth_numbers']).sample_from_layer('fourth_numbers', 50, seed=0.0) )
        annotation_locations = []
        for (doc_id, dok) in res:
            for span in dok['even_numbers']:
                annotation_locations.append( (doc_id, span.start, span.end) )
        self.assertEqual(len(res), 25)
        self.assertListEqual( [t[0] for t in res], 
            [0, 4, 8, 12, 20, 40, 44, 48, 68, 76, 84, 92, 96, 112,
             116, 124, 132, 136, 140, 144, 152, 164, 168, 172, 184] )
        self.assertListEqual( [len(t[1]['fourth_numbers']) for t in res], 
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] )
        self.assertListEqual( [len(t[1]['even_numbers']) for t in res], 
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] )

        collection.delete()


