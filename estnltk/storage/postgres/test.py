""""
Test postgres storage functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.
"""
import unittest
import random
from collections import OrderedDict

from estnltk import logger
from estnltk import Layer
from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers import ParagraphTokenizer
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import JsonbTextQuery as Q
from estnltk.storage.postgres import JsonbLayerQuery
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import create_schema, delete_schema, count_rows
from estnltk.storage.postgres import create_collection_table
from estnltk.storage.postgres import collection_table_exists
from estnltk.storage.postgres import drop_collection_table
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import fragment_table_exists
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import build_sql_query
from estnltk.storage.postgres import PgCollection
from estnltk.storage import postgres as pg


logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgCollection(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_create_collection(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]

        self.assertFalse(collection.exists())

        collection.create()

        self.assertTrue(collection.exists())

        self.assertIs(collection, self.storage[collection_name])

        collection.delete()

        collection = self.storage['not_existing']
        self.assertIsInstance(collection, PgCollection)

        collection.delete()
        self.assertFalse(collection.exists())

    def test_basic_collection_workflow(self):
        # insert texts -> create layers -> select texts
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        text_1 = Text('Esimene lause. Teine lause. Kolmas lause.')
        text_2 = Text('Teine tekst')
        text_1.tag_layer(['sentences'])
        text_2.tag_layer(['sentences'])

        with collection.insert() as collection_insert:
            collection_insert(text_1, key=1)
            collection_insert(text_2, key=2)

        tagger1 = VabamorfTagger(disambiguate=False)
        collection.create_layer(tagger=tagger1)

        tagger1.tag(text_1)
        tagger1.tag(text_2)

        tagger2 = ParagraphTokenizer()
        collection.create_layer(tagger=tagger2)

        tagger2.tag(text_1)
        tagger2.tag(text_2)

        for text_id, text in collection.select(layers=['compound_tokens', 'morph_analysis', 'paragraphs']):
            if text_id == 1:
                assert text == text_1, text_1.diff(text)
            elif text_id == 2:
                assert text == text_2, text_2.diff(text)

    def test_collection_getitem_and_iter(self):
        # insert texts -> create layers -> select texts
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        text_1 = Text('Esimene lause. Teine lause. Kolmas lause.')
        text_2 = Text('Teine tekst')
        text_1.tag_layer(['sentences'])
        text_2.tag_layer(['sentences'])

        with collection.insert() as collection_insert:
            collection_insert(text_1, key=1)
            collection_insert(text_2, key=2)

        tagger1 = VabamorfTagger(disambiguate=False)
        collection.create_layer(tagger=tagger1)

        tagger1.tag(text_1)
        tagger1.tag(text_2)

        tagger2 = ParagraphTokenizer()
        collection.create_layer(tagger=tagger2)

        tagger2.tag(text_1)
        tagger2.tag(text_2)

        raw_text_set = {text_1.text, text_2.text}

        # test __iter__
        result = list(collection)
        assert len(result) == 2, result
        assert {text.text for text in result} == raw_text_set, result
        for text in result:
            assert set(text.layers) == {'sentences', 'words', 'tokens', 'compound_tokens'}

        # test __getitem__
        assert collection[1].text == text_1.text
        assert collection[2].text == text_2.text
        with self.assertRaises(KeyError):
            collection[5]
        with self.assertRaises(KeyError):
            next(collection['bla'])

        #result = collection[1, 'paragraphs']
        #assert isinstance(result, Layer)
        #assert result.name == 'paragraphs'

    def test_create_and_drop_collection_table(self):
        collection_name = get_random_collection_name()

        create_collection_table(self.storage, collection_name)
        assert collection_table_exists(self.storage, collection_name)
        assert table_exists(self.storage, collection_name)
        drop_collection_table(self.storage, collection_name)
        assert not collection_table_exists(self.storage, collection_name)
        assert not table_exists(self.storage, collection_name)

    def test_sql_injection(self):
        normal_collection_name = get_random_collection_name()
        create_collection_table(self.storage, normal_collection_name)
        self.assertTrue(collection_table_exists(self.storage, normal_collection_name))

        injected_collection_name = "%a; drop table %s;" % (get_random_collection_name(), normal_collection_name)
        create_collection_table(self.storage, injected_collection_name)
        self.assertTrue(collection_table_exists(self.storage, injected_collection_name))
        self.assertTrue(collection_table_exists(self.storage, normal_collection_name))

        drop_collection_table(self.storage, normal_collection_name)
        drop_collection_table(self.storage, injected_collection_name)

    def test_select_by_key(self):
        collection = self.storage[get_random_collection_name()]
        collection.create()
        self.assertRaises(PgCollectionException, lambda: collection.select_by_key(1))

        text = Text("Mingi tekst")
        with collection.insert() as collection_insert:
            collection_insert(text, 1)
        res = collection.select_by_key(1)
        self.assertEqual(text, res)
        collection.delete()

    def test_select(self):
        not_existing_collection = self.storage['not_existing']
        with self.assertRaises(pg.PgCollectionException):
            not_existing_collection.select()

        collection = self.storage[get_random_collection_name()]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.')

            id1 = collection_insert(text1, key=1)

            text2 = Text('Mis kell on?')
            id2 = collection_insert(text2, key=2)

        id1 = 1
        id2 = 2
        # test select_by_id
        self.assertEqual(collection.select_by_key(id1), text1)
        self.assertEqual(collection.select_by_key(id2), text2)

        subcollection = collection.select(order_by_key=True)
        assert isinstance(subcollection, pg.PgSubCollection)

        # test select_all
        res = list(subcollection)

        self.assertEqual(len(res), 2)
        id_, text = res[0]
        self.assertEqual(id_, id1)
        self.assertEqual(text, text1)
        id_, text = res[1]
        self.assertEqual(id_, id2)
        self.assertEqual(text, text2)

        # test select
        with collection.insert() as collection_insert:
            text1 = Text('mis kell on?').analyse('morphology')
            collection_insert(text1, key=3)
            text2 = Text('palju kell on?').analyse('morphology')
            collection_insert(text2, key=4)

        res = list(collection.select(query=Q('morph_analysis', lemma='mis')))
        self.assertEqual(len(res), 1)

        res = list(collection.select(query=Q('morph_analysis', lemma='kell')))
        self.assertEqual(len(res), 2)

        res = list(collection.select(query=Q('morph_analysis', lemma='mis') | Q('morph_analysis', lemma='palju')))
        self.assertEqual(len(res), 2)

        res = list(collection.select(query=Q('morph_analysis', lemma='mis') & Q('morph_analysis', lemma='palju')))
        self.assertEqual(len(res), 0)

        res = list(collection.select(query=(Q('morph_analysis', lemma='mis') | Q('morph_analysis', lemma='palju')) &
                                    Q('morph_analysis', lemma='kell')))
        self.assertEqual(len(res), 2)

        # test find_fingerprint
        q = {"layer": "morph_analysis", "field": "lemma", "ambiguous": True}

        q["query"] = ["mis", "palju"]  # mis OR palju
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 2)

        q["query"] = [["mis"], ["palju"]]  # mis OR palju
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 2)

        q["query"] = [["mis", "palju"]]  # mis AND palju
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 0)

        q["query"] = [{'miss1', 'miss2'}, {'miss3'}]
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 0)

        q["query"] = [{'miss1', 'miss2'}, {'palju'}]
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 1)

        q["query"] = [{'mis', 'miss2'}, {'palju'}]
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 1)

        q["query"] = [{'mis', 'kell'}, {'miss'}]
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 1)

        q["query"] = [{'mis', 'kell'}, {'palju'}]
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 2)

        q["query"] = []
        res = list(collection.find_fingerprint(q))
        self.assertEqual(len(res), 4)

        res = list(collection.select(keys=[]))
        self.assertEqual(len(res), 0)

        res = list(collection.select(keys=[1, 3]))
        self.assertEqual(len(res), 2)

        collection.delete()

    def test_build_sql_query(self):
        collection = self.storage['test_collection']

        # defaults
        sql = build_sql_query(collection)
        result = sql.as_string(self.storage.conn)
        expected = ('SELECT "test_schema"."test_collection"."id", '
                           '"test_schema"."test_collection"."data" '
                    'FROM "test_schema"."test_collection" ;')
        self.assertEqual(expected, result)

        # query
        jsonb_text_query = Q('kiht', lemma='kass')
        sql = build_sql_query(collection, query=jsonb_text_query)
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" '
            'WHERE "test_schema"."test_collection"."data"->\'layers\' @> \'[{"name": "kiht", "spans": [[{"lemma": "kass"}]]}]\' ;')
        self.assertEqual(expected, result)

        # layer_query
        sql = build_sql_query(collection,
                              layer_query={
            'layer1': JsonbLayerQuery(layer_name='layer1_table', lemma='esimene') |
                      JsonbLayerQuery(layer_name='layer1_table', lemma='teine')
        })
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection", "test_schema"."test_collection__layer1__layer" '
            'WHERE "test_schema"."test_collection"."id" = "test_schema"."test_collection__layer1__layer"."text_id" '
            'AND ("test_schema"."test_collection__layer1_table__layer".data @> \'{"spans": [[{"lemma": "esimene"}]]}\' '
            'OR "test_schema"."test_collection__layer1_table__layer".data @> \'{"spans": [[{"lemma": "teine"}]]}\') ;')
        self.assertEqual(expected, result)

        # layer_ngram_query
        q = {'indexed_layer': {"lemma": [("see", "olema")]}}
        sql = build_sql_query(collection, layer_ngram_query=q)
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection", "test_schema"."test_collection__indexed_layer__layer" '
            'WHERE "test_schema"."test_collection"."id" = "test_schema"."test_collection__indexed_layer__layer"."text_id" '
            'AND ("test_schema"."test_collection__indexed_layer__layer"."lemma" @> ARRAY[\'see-olema\']) ;')
        self.assertEqual(expected, result)

        # layers
        sql = build_sql_query(collection, layers=['layer_1'])
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data", '
            '"test_schema"."test_collection__layer_1__layer"."id", '
            '"test_schema"."test_collection__layer_1__layer"."data" '
            'FROM "test_schema"."test_collection", "test_schema"."test_collection__layer_1__layer" '
            'WHERE "test_schema"."test_collection"."id" = "test_schema"."test_collection__layer_1__layer"."text_id" ;')
        self.assertEqual(expected, result)

        # keys
        sql = build_sql_query(collection, keys=[2, 5, 9])
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" WHERE "test_schema"."test_collection"."id" = ANY(ARRAY[2,5,9]) ;')
        self.assertEqual(expected, result)

        # order_by_id
        sql = build_sql_query(collection, order_by_key=True)
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" ORDER BY "id" ;')
        self.assertEqual(expected, result)

        # collection_meta
        sql = build_sql_query(collection, collection_meta=['meta1', 'meta2'])
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data", '
                   '"test_schema"."test_collection"."meta1", "test_schema"."test_collection"."meta2" '
            'FROM "test_schema"."test_collection" ;')
        self.assertEqual(expected, result)

        # missing_layer
        sql = build_sql_query(collection, missing_layer='layer_1')
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" '
            'WHERE "id" NOT IN (SELECT "text_id" FROM "test_schema"."test_collection__layer_1__layer") ;')
        self.assertEqual(expected, result)

        # all in one
        layer_query = {'layer_2': JsonbLayerQuery(layer_name='layer1_table', lemma='esimene') |
                                  JsonbLayerQuery(layer_name='layer1_table', lemma='teine')}
        sql = build_sql_query(collection=collection,
                              query=Q('layer_1', lemma='kass'),
                              layer_query=layer_query,
                              layer_ngram_query={'layer_3': {"lemma": [("see", "olema")]}},
                              layers=['layer_4'],
                              keys=[2, 5, 9],
                              order_by_key=True,
                              collection_meta=['meta1', 'meta2'],
                              missing_layer='layer_5')

        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", '
                   '"test_schema"."test_collection"."data", '
                   '"test_schema"."test_collection"."meta1", '
                   '"test_schema"."test_collection"."meta2", '
                   '"test_schema"."test_collection__layer_4__layer"."id", '
                   '"test_schema"."test_collection__layer_4__layer"."data" '
            'FROM "test_schema"."test_collection", '
                 '"test_schema"."test_collection__layer_2__layer", '
                 '"test_schema"."test_collection__layer_3__layer", '
                 '"test_schema"."test_collection__layer_4__layer" '
            'WHERE "test_schema"."test_collection"."id" = "test_schema"."test_collection__layer_2__layer"."text_id" '
              'AND "test_schema"."test_collection"."id" = "test_schema"."test_collection__layer_3__layer"."text_id" '
              'AND "test_schema"."test_collection"."id" = "test_schema"."test_collection__layer_4__layer"."text_id" '
              'AND "test_schema"."test_collection"."data"->\'layers\' @> \'[{"name": "layer_1", "spans": [[{"lemma": "kass"}]]}]\' '
              'AND ("test_schema"."test_collection__layer1_table__layer".data @> \'{"spans": [[{"lemma": "esimene"}]]}\' '
                'OR "test_schema"."test_collection__layer1_table__layer".data @> \'{"spans": [[{"lemma": "teine"}]]}\') '
              'AND "test_schema"."test_collection"."id" = ANY(ARRAY[2,5,9]) '
              'AND ("test_schema"."test_collection__layer_3__layer"."lemma" @> ARRAY[\'see-olema\']) '
              'AND "id" NOT IN (SELECT "text_id" FROM "test_schema"."test_collection__layer_5__layer") '
            'ORDER BY "id" ;')
        self.assertEqual(expected, result)


class TestPgSubCollection(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

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

    def tearDown(self):
        delete_schema(self.storage)
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

    def test_all_layers(self):
        subcollection = pg.PgSubCollection(self.collection)
        assert set(subcollection.all_layers) == {'tokens', 'compound_tokens', 'words', 'sentences', 'morph_analysis'}

    def test_sql_query_text(self):
        subcollection = self.collection.select()

        expected = ('SELECT "test_schema"."{collection_name}"."id", '
                           '"test_schema"."{collection_name}"."data" '
                    'FROM "test_schema"."{collection_name}"').format(collection_name=self.collection_name)
        assert subcollection.sql_query_text == expected

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
                                             layer_query={'morph_analysis': pg.JsonbLayerQuery('morph_analysis', lemma='esimene') |
                                                                            pg.JsonbLayerQuery('morph_analysis', lemma='ööbik') |
                                                                            pg.JsonbLayerQuery('morph_analysis', lemma='mis')
                                                          }
                                             )
        subcollection_5 = subcollection_4.select(additional_constraint=selection_criterion)
        assert isinstance(subcollection_5, pg.PgSubCollection)
        assert subcollection_5.selected_layers == ['words', 'sentences']
        assert subcollection_5 is not subcollection_4
        assert len(list(subcollection_5)) == 3

        selection_criterion = pg.WhereClause(collection=self.collection,
                                             keys=[0, 1, 2])
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
        assert meta == {'meta_1': None, 'meta_2': None}

        subcollection = pg.PgSubCollection(self.collection, meta_attributes=['meta_2'],
                                           selected_layers=['morph_analysis'], return_index=False)
        text, meta = next(iter(subcollection))
        assert text.text == 'Esimene lause. Teine lause. Kolmas lause.'
        assert set(text.layers) == {'words', 'morph_analysis'}
        assert meta == {'meta_2': None}

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

    def test_select_all(self):
        subcollection_0 = pg.PgSubCollection(self.collection)
        subcollection_1 = subcollection_0.select_all()
        assert subcollection_1 is subcollection_0
        text_id, text = next(iter(subcollection_1))
        assert text_id == 0
        assert set(text.layers) == {'sentences', 'words', 'morph_analysis', 'compound_tokens', 'tokens'}

    def test_raw_layer(self):
        subcollection = pg.PgSubCollection(self.collection)
        with self.assertRaises(NotImplementedError):
            subcollection.raw_layer()

    def test_raw_fragment(self):
        subcollection = pg.PgSubCollection(self.collection)
        with self.assertRaises(NotImplementedError):
            subcollection.raw_fragment()


class TestLayerFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_layer_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer_fragment_name = "layer_fragment_1"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer_fragment_name)

        def fragment_tagger(row):
            text_id, text = row[0], row[1]
            fragments = [RowMapperRecord(layer=tagger1.tag(text, return_layer=True), meta=None),
                         RowMapperRecord(layer=tagger1.tag(text, return_layer=True), meta=None)]
            return fragments

        collection.old_slow_create_layer(layer_fragment_name,
                                         data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                         row_mapper=fragment_tagger)

        self.assertTrue(collection.has_layer(layer_fragment_name))

        rows = [row for row in pg.select_raw(collection=collection,
                                             detached_layers=[layer_fragment_name])]
        self.assertEqual(len(rows), 4)

        text_ids = [row[0] for row in rows]
        self.assertEqual(text_ids[0], text_ids[1])
        self.assertEqual(text_ids[2], text_ids[3])
        self.assertNotEqual(text_ids[1], text_ids[2])

        layer_ids = [row[2] for row in rows]
        #self.assertEqual(len(set(layer_ids)), 4)

        texts = [row[1] for row in rows]
        self.assertTrue(isinstance(texts[0], Text))

        layers = [row[3] for row in rows]
        #self.assertTrue(isinstance(layers[0], Layer))

        self.assertTrue(layer_table_exists(self.storage, collection.name, layer_fragment_name))

        collection.delete()

        self.assertFalse(layer_table_exists(self.storage, collection.name, layer_fragment_name))


class TestFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer_fragment_name = "layer_fragment_1"
        tagger = VabamorfTagger(disambiguate=False, layer_name=layer_fragment_name)
        collection.old_slow_create_layer(layer_fragment_name,
                                         data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                         row_mapper=lambda row: [RowMapperRecord(
                                                 layer=tagger.tag(row[1], return_layer=True), meta=None)])

        self.assertTrue(collection.has_layer(layer_fragment_name))

        fragment_name = "fragment_1"

        def row_mapper(row):
            text_id, text, meta, detached_layers = row
            parent_layer = detached_layers[layer_fragment_name]['layer']
            parent_id = detached_layers[layer_fragment_name]['layer_id']
            return [{'fragment': parent_layer, 'parent_id': parent_id},
                    {'fragment': parent_layer, 'parent_id': parent_id}]

        collection.create_fragment(fragment_name,
                            data_iterator=pg.select_raw(collection=collection,
                                                        detached_layers=[layer_fragment_name]),
                            row_mapper=row_mapper,
                            create_index=False,
                            ngram_index=None)

        rows = list(collection.select_fragment_raw(fragment_name, layer_fragment_name))
        self.assertEqual(len(rows), 4)

        row = rows[0]
        self.assertEqual(len(row), 6)
        self.assertIsInstance(row[0], int)
        self.assertIsInstance(row[1], Text)
        self.assertIsInstance(row[2], int)
        self.assertIsInstance(row[3], Layer)
        self.assertIsInstance(row[4], int)
        self.assertIsInstance(row[5], Layer)

        assert fragment_table_exists(self.storage, collection.name, fragment_name)
        collection.delete_fragment(fragment_name)
        assert not fragment_table_exists(self.storage, collection.name, fragment_name)


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.schema = "test_layer"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=self.schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_layer_read_write(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer1 = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer1,
                                         data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                         row_mapper=row_mapper1)
        tagger1.tag(text1)
        tagger1.tag(text2)

        layer2 = "layer2"
        tagger2 = VabamorfTagger(disambiguate=False, layer_name=layer2)

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer2,
                                         data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                         row_mapper=row_mapper2)
        tagger2.tag(text1)
        tagger2.tag(text2)

        for key, text in collection.select(layers=['sentences']):
            self.assertTrue("sentences" in text.layers)
            self.assertTrue(layer1 not in text.layers)
            self.assertTrue(layer2 not in text.layers)

        rows = list(collection.select(layers=[layer1, layer2]))
        text1_db = rows[0][1]
        self.assertTrue(layer1 in text1_db.layers)
        self.assertTrue(layer2 in text1_db.layers)
        self.assertEqual(text1_db[layer1].lemma, text1[layer1].lemma)
        self.assertEqual(text1_db[layer2].lemma, text1[layer2].lemma)

        collection.delete()
        self.assertFalse(layer_table_exists(self.storage, collection.name, layer1))
        self.assertFalse(layer_table_exists(self.storage, collection.name, layer2))

    def test_layer_meta(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer1 = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta={"meta_text_id": text_id, "sum": 45.5})]

        collection.create_layer(layer1,
                                data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                row_mapper=row_mapper1,
                                meta={"meta_text_id": "int",
                                      "sum": "float"})
        self.assertTrue(layer_table_exists(self.storage, collection.name, layer1))

        # get_layer_meta
        layer_meta = collection.get_layer_meta(layer_name=layer1)
        assert layer_meta.to_dict() == {'id': {0: 1, 1: 2},
                                        'meta_text_id': {0: 0, 1: 1},
                                        'sum': {0: 45.5, 1: 45.5},
                                        'text_id': {0: 0, 1: 1}}, layer_meta.to_dict()

        with self.assertRaises(PgCollectionException):
            collection.get_layer_meta(layer_name='not_exists')

        assert set(collection._get_structure()[layer1]['meta']) == {'sum', 'meta_text_id'}

        collection.delete()

    def test_layer_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
            collection_insert(text1)

            text2 = Text('Mis kell on?').tag_layer(["sentences"])
            collection_insert(text2)

        # test ambiguous layer
        layer1_name = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1_name)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer1_name,
                                  data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                  row_mapper=row_mapper1)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(layer_query={layer1_name: q}))), 1)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik') | JsonbLayerQuery(layer_name=layer1_name,
                                                                                     lemma='mis')
        self.assertEqual(len(list(collection.select(layer_query={layer1_name: q}))), 2)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik') & JsonbLayerQuery(layer_name=layer1_name,
                                                                                     lemma='mis')
        self.assertEqual(len(list(collection.select(layer_query={layer1_name: q}))), 0)

        q = JsonbLayerQuery(layer_name=layer1_name, lemma='ööbik')
        text = [text for key, text in collection.select(layer_query={layer1_name: q})][0]
        self.assertTrue(layer1_name not in text.layers)

        text = list(collection.select(layer_query={layer1_name: q}, layers=[layer1_name]))[0][1]
        self.assertTrue(layer1_name in text.layers)

        # test with 2 layers
        layer2 = "layer2"
        layer2_table = layer2
        tagger2 = VabamorfTagger(disambiguate=True, layer_name=layer2)

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer2, data_iterator=collection.select(layers=['sentences', 'compound_tokens']), row_mapper=row_mapper2)

        q = JsonbLayerQuery(layer_name=layer2_table, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(layer_query={layer2: q}))), 1)

        text = list(collection.select(layer_query={layer2: q}, layers=[layer1_name, layer2]))[0][1]
        self.assertTrue(layer1_name in text.layers)
        self.assertTrue(layer2 in text.layers)

    def test_layer_fingerprint_query(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
            collection_insert(text1)

            text2 = Text('Mis kell on?').tag_layer(["sentences"])
            collection_insert(text2)

        layer1 = "layer1"
        layer2 = "layer2"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)
        tagger2 = VabamorfTagger(disambiguate=False, layer_name=layer2)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer1,
                                         data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                         row_mapper=row_mapper1, create_index=True)
        collection.old_slow_create_layer(layer2,
                                         data_iterator=collection.select(layers=['sentences', 'compound_tokens']),
                                         row_mapper=row_mapper2)

        # test one layer
        res = collection.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": ["ööbik"],
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 1)

        res = collection.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": ["ööbik"],
                "ambiguous": False
            }})
        self.assertEqual(len(list(res)), 0)

        res = collection.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": ["ööbik", "mis"],  # ööbik OR mis
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 2)

        res = collection.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": [["ööbik", "mis"]],  # ööbik AND mis
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 0)

        res = collection.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": [["ööbik", "laulma"]],  # ööbik AND laulma
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 1)

        # test multiple layers
        res = collection.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": ["ööbik"],
                "ambiguous": True
            },
            layer2: {
                "field": "lemma",
                "query": ["ööbik"],
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 1)

    def test_layer_ngramm_index(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()

        id1 = 1
        id2 = 2

        with collection.insert() as collection_insert:
            text1 = Text("Ööbik laulab puu otsas.").tag_layer(["sentences"])
            collection_insert(text1, key=id1)

            text2 = Text("Mis kell on?").tag_layer(["sentences"])
            collection_insert(text2, key=id2)

        layer1 = "layer1"
        layer2 = "layer2"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)
        tagger2 = VabamorfTagger(disambiguate=False, layer_name=layer2)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer1, data_iterator=collection.select(layers=['sentences', 'compound_tokens']), row_mapper=row_mapper1,
                                  ngram_index={"lemma": 2})
        collection.old_slow_create_layer(layer2, data_iterator=collection.select(layers=['sentences', 'compound_tokens']), row_mapper=row_mapper2,
                                  ngram_index={"partofspeech": 3})

        self.assertEqual(count_rows(self.storage, table_identifier=layer_table_identifier(self.storage, collection.name, layer1)), 2)
        self.assertEqual(count_rows(self.storage, table_identifier=layer_table_identifier(self.storage, collection.name, layer2)), 2)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("otsas", ".")]}}))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], id1)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("mis", "kell")]}}))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], id2)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("mis",)]}}))
        self.assertEqual(len(res), 1)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer1: {
                "lemma": [[("mis", "kell")],  # "mis-kell" OR "otsas-."
                          [("otsas", ".")]]
            }}))
        self.assertEqual(len(res), 2)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer1: {
                "lemma": [[("mis", "kell"),  # "mis-kell" AND "otsas-."
                           ("otsas", ".")]]
            }}))
        self.assertEqual(len(res), 0)

        # "Ööbik laulab puu otsas." ->[['H', 'S'], ['V'], ['S', 'S'], ['D', 'K', 'V', 'S'], ['Z']]
        # "Mis kell on?" -> [['P', 'P'], ['S'], ['V', 'V'], ['Z']]
        res = list(collection.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [("S", "V", "S")]}}))  # Ööbik laulab puu
        self.assertEqual(len(res), 1)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [("S", "V")]}}))  # 2-grams are also indexed
        self.assertEqual(len(res), 2)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [[("S", "V", "S")],  # "Ööbik laulab puu" OR "Mis kell on"
                                      [("P", "S", "V")]]}}))
        self.assertEqual(len(res), 2)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [[("S", "V", "S"), ("S", "D", "Z")]]}}))  # "Ööbik laulab puu" AND "puu otsas ."
        self.assertEqual(len(res), 1)

        res = list(collection.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("puu", "otsas")]},
            layer2: {"partofspeech": [("S", "V", "S")]},  # "laulma-puu-otsas"
        }))
        self.assertEqual(len(res), 1)

        res = list(collection.find_fingerprint(
            layer_ngram_query={
                layer1: {"lemma": [("mis", "kell")]}},
            layers=[layer1, layer2]
        ))
        t1 = res[0][1]
        self.assertTrue(layer1 in t1.layers)
        self.assertTrue(layer2 in t1.layers)

        collection.delete()


if __name__ == '__main__':
    unittest.main()
