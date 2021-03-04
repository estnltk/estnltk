""""
Test postgres storage functionality.

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


class TestPgSubCollection(unittest.TestCase):
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
        not_existing_collection = self.storage['not_existing']
        with self.assertRaises(pg.PgCollectionException):
            pg.PgSubCollection(not_existing_collection)

        subcollection = pg.PgSubCollection(self.collection)
        assert subcollection.collection is self.collection
        assert subcollection.selected_layers == []
        assert subcollection.meta_attributes == ()
        assert subcollection.progressbar is None
        assert subcollection.return_index is True

        with self.assertRaises(TypeError):
            pg.PgSubCollection(self.collection, selection_criterion='')

    def test_selected_layers(self):
        subcollection = pg.PgSubCollection(self.collection)
        assert subcollection.selected_layers == []

        with self.assertRaises(pg.PgCollectionException):
            subcollection.selected_layers = ['not_existing_layer']

        subcollection.selected_layers = ['sentences', 'tokens']
        assert set(subcollection.selected_layers) == {'tokens', 'words', 'sentences'}

        subcollection.selected_layers = ['tokens']
        assert set(subcollection.selected_layers) == {'tokens'}

    def test_layers(self):
        assert set(self.subcollection.layers) == {'tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'}

    def test_detached_layers(self):
        assert self.subcollection.detached_layers == ['words', 'sentences', 'morph_analysis']

    def test_fragmented_layers(self):
        with self.assertRaises(NotImplementedError):
            self.subcollection.fragmented_layers

    def test_sql_query_text(self):
        subcollection = self.collection.select()

        expected = ('SELECT "test_schema"."{collection_name}"."id", '
                           '"test_schema"."{collection_name}"."data" '
                    'FROM "test_schema"."{collection_name}" '
                    'ORDER BY "test_schema"."{collection_name}"."id"').format(collection_name=self.collection_name)
        assert subcollection.sql_query_text == expected

    def test_sql_count_query_text(self):
        subcollection = self.collection.select()

        expected = ('SELECT count(*) FROM (SELECT "test_schema"."{collection_name}"."id", '
                                                 '"test_schema"."{collection_name}"."data" '
                                          'FROM "test_schema"."{collection_name}" '
                                          'ORDER BY "test_schema"."{collection_name}"."id") AS a'
                    ).format(collection_name=self.collection_name)
        logger.debug( str(subcollection.sql_count_query_text) )
        assert subcollection.sql_count_query_text == expected

    def test_select(self):
        subcollection_0 = self.collection.select()

        subcollection_1 = subcollection_0.select()
        assert isinstance(subcollection_1, pg.PgSubCollection)
        assert subcollection_1.selected_layers == []
        assert subcollection_1 is subcollection_0

        subcollection_2 = subcollection_1.select(selected_layers=['sentences'])
        assert isinstance(subcollection_2, pg.PgSubCollection)
        assert subcollection_2.selected_layers == ['words', 'sentences']
        assert subcollection_2 is subcollection_1

        subcollection_3 = subcollection_2.select()
        assert isinstance(subcollection_3, pg.PgSubCollection)
        assert subcollection_3.selected_layers == ['words', 'sentences']
        assert subcollection_3 is subcollection_2

        subcollection_4 = subcollection_3.select(additional_constraint=pg.WhereClause(self.collection))
        assert isinstance(subcollection_4, pg.PgSubCollection)
        assert subcollection_4.selected_layers == ['words', 'sentences']
        assert subcollection_4 is not subcollection_3
        assert len(list(subcollection_4)) == 4

        selection_criterion = pg.WhereClause(collection=self.collection,
                                             query=pg.LayerQuery(layer_name='morph_analysis', lemma='esimene') | \
                                                   pg.LayerQuery(layer_name='morph_analysis', lemma='ööbik') | \
                                                   pg.LayerQuery(layer_name='morph_analysis', lemma='mis')
                                             )
        subcollection_5 = subcollection_4.select(additional_constraint=selection_criterion)
        assert isinstance(subcollection_5, pg.PgSubCollection)
        assert subcollection_5.selected_layers == ['words', 'sentences']
        assert subcollection_5 is not subcollection_4
        assert len(list(subcollection_5)) == 3

        selection_criterion = pg.WhereClause(collection=self.collection,
                                             query=pg.IndexQuery(keys=[0, 1, 2]))
        subcollection_6 = subcollection_5.select(additional_constraint=selection_criterion)
        assert isinstance(subcollection_6, pg.PgSubCollection)
        assert subcollection_6.selected_layers == ['words', 'sentences']
        assert subcollection_6 is not subcollection_5
        assert len(list(subcollection_6)) == 2

    def test_iter(self):
        collection = self.storage[self.collection.name + '_new']
        collection.create()
        subcollection = pg.PgSubCollection(collection)
        collection.delete()
        with self.assertRaises(pg.PgCollectionException):
            next(iter(subcollection))

        subcollection = pg.PgSubCollection(self.collection, meta_attributes=['meta_1', 'meta_2'])
        text_id, text, meta = next(iter(subcollection))
        assert text_id == 0
        assert text.text == 'Esimene lause. Teine lause. Kolmas lause.'
        assert set(text.layers) == set()
        assert meta == {'meta_1': 'value_0', 'meta_2': 0}

        subcollection = pg.PgSubCollection(self.collection, meta_attributes=['meta_2'],
                                           selected_layers=['morph_analysis'], return_index=False)
        text, meta = next(iter(subcollection))
        assert text.text == 'Esimene lause. Teine lause. Kolmas lause.'
        assert set(text.layers) == {'words', 'morph_analysis'}
        assert meta == {'meta_2': 0}

        subcollection = pg.PgSubCollection(self.collection, progressbar='ascii')
        result = list(subcollection)
        assert len(result) == 4
        text_id, text = result[0]
        assert text_id == 0
        assert text.text == 'Esimene lause. Teine lause. Kolmas lause.'
        assert set(text.layers) == set()

        subcollection = pg.PgSubCollection(self.collection, progressbar='unicode')
        result = list(subcollection)
        assert len(result) == 4
        text_id, text = result[0]
        assert text_id == 0
        assert text.text == 'Esimene lause. Teine lause. Kolmas lause.'
        assert set(text.layers) == set()

        subcollection = pg.PgSubCollection(self.collection, progressbar='notebook')
        result = list(subcollection)
        assert len(result) == 4
        text_id, text = result[0]
        assert text_id == 0
        assert text.text == 'Esimene lause. Teine lause. Kolmas lause.'
        assert set(text.layers) == set()

        subcollection = pg.PgSubCollection(self.collection, progressbar='undefined')
        with self.assertRaises(ValueError):
            next(iter(subcollection))

    def test_head(self):
        subcollection = pg.PgSubCollection(self.collection)

        head = list(subcollection.head(0))
        assert head == []

        head = list(subcollection.head(2))
        assert len(head) == 2
        assert head[0][1].text == 'Esimene lause. Teine lause. Kolmas lause.'
        assert head[1][1].text == 'Teine tekst'

        head = list(subcollection.head(20))
        assert len(head) == 4

    def test_tail(self):
        subcollection = pg.PgSubCollection(self.collection)

        tail = list(subcollection.tail(0))
        assert tail == []
        
        tail = list(subcollection.tail(2))
        assert len(tail) == 2
        assert tail[0][1].text == 'Ööbik laulab. Öökull ei laula.'
        assert tail[1][1].text == 'Mis kell on?'

        tail = list(subcollection.tail(20))
        assert len(tail) == 4

    def test_select_all(self):
        subcollection_0 = pg.PgSubCollection(self.collection)
        subcollection_1 = subcollection_0.select_all()
        assert subcollection_1 is subcollection_0
        text_id, text = next(iter(subcollection_1))
        assert text_id == 0
        assert set(text.layers) == {'sentences', 'words', 'morph_analysis', 'compound_tokens', 'tokens'}

    def test_detached_layer(self):
        sub_collection_layer = self.subcollection.detached_layer('words')
        self.assertIsInstance(sub_collection_layer, pg.PgSubCollectionLayer)

    def test_fragmented_layer(self):
        sub_collection_fragments = self.subcollection.fragmented_layer('words')
        self.assertIsInstance(sub_collection_fragments, pg.PgSubCollectionFragments)
