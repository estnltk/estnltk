""""
Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.
"""

import unittest
import random
from collections import OrderedDict

from estnltk import logger
from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.storage import postgres as pg


logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgSubCollectionFragments(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = pg.PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        pg.create_schema(self.storage)

        self.collection_name = get_random_collection_name()
        self.collection = self.storage[self.collection_name]
        self.collection.create(meta=OrderedDict([('meta_1', 'str'), ('meta_2', 'int')]))

        texts = ['Esimene lause. Teine lause. Kolmas lause.',
                 'Teine tekst',
                 'Ööbik laulab. Öökull ei laula.',
                 'Mis kell on?']

        with self.collection.insert() as collection_insert:
            for i, t in enumerate(texts):
                text = Text(t).tag_layer(['compound_tokens'])
                collection_insert(text, meta_data={'meta_1': 'value_' + str(i), 'meta_2': i})

        word_tagger = WordTagger()
        self.collection.create_layer(tagger=word_tagger)

        sentence_tagger = SentenceTokenizer()
        self.collection.create_layer(tagger=sentence_tagger)

        vabamorf_tagger = VabamorfTagger(disambiguate=False)
        self.collection.create_layer(tagger=vabamorf_tagger)

        self.subcollection = pg.PgSubCollection(self.collection,
                                                selected_layers=['sentences', 'morph_analysis'],
                                                meta_attributes=['meta_1', 'meta_2'])

    def tearDown(self):
        pg.delete_schema(self.storage)
        self.storage.close()

    def test_init(self):
        subcollectionfragments = pg.PgSubCollectionFragments(collection=self.collection,
                                                             selection_criterion=None,
                                                             fragmented_layer='words',
                                                             progressbar=None,
                                                             return_index=True)
