import unittest
import random
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema

from estnltk import logger
from estnltk import Text
from estnltk.taggers import VabamorfTagger, SentenceTokenizer
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage import postgres as pg

from estnltk.storage.postgres.queries.metadata_query import JsonbMetadataQuery
from estnltk.storage.postgres.queries.slice_query import SliceQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


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



    def test_pgsubcollection_sample_from_attached_layer_based_on_simple_select(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100, detached_sentences=False)
        
        # Default select sentences with sample size approx. 5%
        res = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 5, seed=-0.7) )
        self.assertEqual(len(res), 57)
        self.assertEqual(len(res[0]), 2)
        sent_locations = []
        for (doc_id, dok) in res:
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        self.assertEqual( len(sent_locations), 101 )
        self.assertListEqual( sent_locations[:5], [(0,86,110),(0,766,803),(1,83,106),(10,491,519),(10,652,684)] )
        
        # Default select sentences with sample size approx. 25%
        res = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 25, seed=0.1) )
        self.assertEqual(len(res), 100)
        self.assertEqual(len(res[0]), 2)
        sent_locations = []
        for (doc_id, dok) in res:
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        self.assertEqual( len(sent_locations), 846 )
        self.assertListEqual( sent_locations[:5], [(0, 0, 25), (0, 86, 110), (0, 112, 141), (0, 327, 360), (0, 557, 585)] )
        self.assertListEqual( sent_locations[-7:], [(98, 644, 680), (98, 801, 836), (99, 28, 58), (99, 89, 114), (99, 212, 241), (99, 506, 540), (99, 542, 573)] )
        
        # Default select sentences with sample size approx. 55 sentences
        with self.assertRaises(NotImplementedError) as exception:
            res = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 55, amount_type='SIZE', seed=0) )

        collection.delete()


    def test_pgsubcollection_sample_from_detached_layer_based_on_simple_select(self):
        # Create testing collection
        collection = self._create_test_collection_of_docs(size=100, detached_sentences=True)
        
        # Default select sentences with sample size approx. 5%
        res = list( collection.select(layers=['sentences']).sample_from_layer('sentences', 5, seed=-0.25) )
        self.assertEqual(len(res), 52)
        self.assertEqual(len(res[0]), 2)
        sent_locations = []
        for (doc_id, dok) in res:
            for sent in dok['sentences']:
                sent_locations.append( (doc_id, sent.start, sent.end) )
        self.assertEqual( len(sent_locations), 93 )
        self.assertListEqual( sent_locations[:5],  [(0, 424, 457), (0, 557, 585), (1, 508, 537), (1, 709, 740), (1, 742, 778)] )
        self.assertListEqual( sent_locations[-5:], [(96, 72, 105), (96, 178, 212), (96, 644, 681), (97, 148, 176), (97, 755, 788)] )

        collection.delete()

