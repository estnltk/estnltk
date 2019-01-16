""""
Test postgres storage functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.
"""
import unittest
import random

from estnltk import logger
from estnltk import Layer
from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.storage.postgres import PostgresStorage, PgStorageException
from estnltk.storage.postgres import JsonbTextQuery as Q
from estnltk.storage.postgres import JsonbLayerQuery
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import create_schema, delete_schema, count_rows
from estnltk.storage.postgres import create_collection_table, create_structure_table
from estnltk.storage.postgres import collection_table_exists, structure_table_exists
from estnltk.storage.postgres import drop_collection_table
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import fragment_table_exists


logger.setLevel('DEBUG')


def get_random_table_name():
    return "table_%d" % random.randint(1, 1000000)


def get_random_table_name_with_schema(schema="public"):
    return "%s.table_%d" % (schema, random.randint(1, 1000000))


class TestStorage(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_create_collection(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        self.assertFalse(col.exists())
        col.create()
        self.assertTrue(col.exists())
        col.delete()
        self.assertFalse(col.exists())

    def test_create_and_drop_collection_table(self):
        collection_name = get_random_table_name()

        create_collection_table(self.storage, collection_name)
        assert collection_table_exists(self.storage, collection_name)
        assert table_exists(self.storage, collection_name)
        drop_collection_table(self.storage, collection_name)
        assert not collection_table_exists(self.storage, collection_name)
        assert not table_exists(self.storage, collection_name)

    def test_sql_injection(self):
        normal_table = get_random_table_name()
        create_collection_table(self.storage, normal_table)
        self.assertTrue(collection_table_exists(self.storage, normal_table))

        injected_table_name = "%a; drop table %s;" % (get_random_table_name(), normal_table)
        create_collection_table(self.storage, injected_table_name)
        self.assertTrue(collection_table_exists(self.storage, injected_table_name))
        self.assertTrue(collection_table_exists(self.storage, normal_table))

        drop_collection_table(self.storage, normal_table)
        drop_collection_table(self.storage, injected_table_name)

    def test_select_by_key(self):
        collection = self.storage.get_collection(get_random_table_name())
        collection.create()
        self.assertRaises(PgStorageException, lambda: collection.select_by_key(1))

        text = Text("Mingi tekst")
        with collection.insert() as collection_insert:
            collection_insert(text, 1)
        res = collection.select_by_key(1)
        self.assertEqual(text, res)
        collection.delete()

    def test_select(self):
        collection = self.storage.get_collection(get_random_table_name())
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

        # test select_all
        res = list(collection.select(order_by_key=True))
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
        collection = self.storage.get_collection('test_collection')

        sql = collection._build_sql_query()
        result = sql.as_string(self.storage.conn)
        expected = ('SELECT "test_schema"."test_collection"."id", '
                           '"test_schema"."test_collection"."data" '
                    'FROM "test_schema"."test_collection" ;')
        self.assertEqual(expected, result)

        # query
        jsonb_text_query = Q('kiht', lemma='kass')
        sql = collection._build_sql_query(query=jsonb_text_query)
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" '
            'WHERE data->\'layers\' @> \'[{"name": "kiht", "spans": [[{"lemma": "kass"}]]}]\' ;')
        self.assertEqual(expected, result)

        # layer_query
        sql = collection._build_sql_query(layer_query={
            'layer1': JsonbLayerQuery(layer_table='layer1_table', lemma='esimene') |
                      JsonbLayerQuery(layer_table='layer1_table', lemma='teine')
        })
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data"  '
            'FROM "test_schema"."test_collection", "test_schema"."test_collection__layer1__layer" '
            'WHERE "test_schema"."test_collection"."id" = "test_schema"."test_collection__layer1__layer"."text_id" '
            'AND (layer1_table.data @> \'{"spans": [[{"lemma": "esimene"}]]}\' '
            'OR layer1_table.data @> \'{"spans": [[{"lemma": "teine"}]]}\') ;')
        self.assertEqual(expected, result)

        # layer_ngram_query
        q = {'indexed_layer': {"lemma": [("see", "olema")]}}
        sql = collection._build_sql_query(layer_ngram_query=q)
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data"  '
            'FROM "test_schema"."test_collection", "test_schema"."test_collection__indexed_layer__layer" '
            'WHERE "test_schema"."test_collection"."id" = "test_schema"."test_collection__indexed_layer__layer"."text_id" '
            'AND ("test_schema"."test_collection__indexed_layer__layer"."lemma" @> ARRAY[\'see-olema\']) ;')
        self.assertEqual(expected, result)

        # layers
        sql = collection._build_sql_query(layers=['layer_1'])
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" , '
            '"test_schema"."test_collection__layer_1__layer"."id", '
            '"test_schema"."test_collection__layer_1__layer"."data" '
            'FROM "test_schema"."test_collection", "test_schema"."test_collection__layer_1__layer" '
            'WHERE "test_schema"."test_collection"."id" = "test_schema"."test_collection__layer_1__layer"."text_id" ;')
        self.assertEqual(expected, result)

        # keys
        sql = collection._build_sql_query(keys=[2, 5, 9])
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" WHERE "test_schema"."test_collection"."id" = ANY(ARRAY[2,5,9]) ;')
        self.assertEqual(expected, result)

        # order_by_id
        sql = collection._build_sql_query(order_by_key=True)
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" ORDER BY "id" ;')
        self.assertEqual(expected, result)

        # collection_meta
        sql = collection._build_sql_query(collection_meta=['meta1', 'meta2'])
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data", '
                   '"test_schema"."test_collection"."meta1", "test_schema"."test_collection"."meta2" '
            'FROM "test_schema"."test_collection" ;')
        self.assertEqual(expected, result)

        # missing_layer
        sql = collection._build_sql_query(missing_layer='layer_1')
        result = sql.as_string(self.storage.conn)
        expected = (
            'SELECT "test_schema"."test_collection"."id", "test_schema"."test_collection"."data" '
            'FROM "test_schema"."test_collection" '
            'WHERE "id" NOT IN (SELECT "text_id" FROM "test_schema"."test_collection__layer_1__layer") ;')
        self.assertEqual(expected, result)


class TestLayerFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_layer_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def _test_create(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        lfrag1 = "layer_fragment_1"
        lfrag2 = "layer_fragment_2"

        col.old_slow_create_layer(lfrag1, data_iterator=col.select(), row_mapper=None)
        self.assertTrue(table_exists(self.storage, col.layer_name_to_table_name(lfrag1)))
        self.assertTrue(col.has_layer(lfrag1))

        col.old_slow_create_layer(lfrag2, data_iterator=col.select(), row_mapper=None)
        self.assertEqual(len(col.get_layer_names()), 2)
        self.assertTrue(lfrag1 in col.get_layer_names())
        self.assertTrue(lfrag2 in col.get_layer_names())

        col.delete_layer(lfrag1)
        self.assertFalse(table_exists(self.storage, col.layer_name_to_table_name(lfrag1)))
        self.assertFalse(col.has_layer(lfrag1))
        self.assertFalse(lfrag1 in col.get_layer_names())
        self.assertTrue(col.has_layer(lfrag2))

        col.delete()

        self.assertFalse(col.has_layer(lfrag2))
        self.assertEqual(len(col.get_layer_names()), 0)
        self.assertFalse(table_exists(self.storage, table_name))

    def test_read_write(self):
        table_name = get_random_table_name()
        collection = self.storage.get_collection(table_name)
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
                                         data_iterator=collection.select(),
                                         row_mapper=fragment_tagger)

        self.assertTrue(collection.has_layer(layer_fragment_name))

        rows = [row for row in collection.select_raw(layers=[layer_fragment_name])]
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

        collection.delete()

        self.assertFalse(
            table_exists(self.storage, collection.layer_name_to_table_name(layer_fragment_name)))


class TestFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_fragment"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_read_write(self):
        table_name = get_random_table_name()
        collection = self.storage.get_collection(table_name)
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('see on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('see on teine lause').tag_layer(["sentences"])
            collection_insert(text2)

        layer_fragment_name = "layer_fragment_1"
        tagger = VabamorfTagger(disambiguate=False, layer_name=layer_fragment_name)
        collection.old_slow_create_layer(layer_fragment_name,
                                         data_iterator=collection.select(),
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
                            data_iterator=collection.select_raw(layers=[layer_fragment_name]),
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

    def _test_create_layer(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        layer1 = "layer1"
        layer2 = "layer2"

        col.old_slow_create_layer(layer1, data_iterator=col.select(), row_mapper=None)

        self.assertTrue(table_exists(self.storage, col.layer_name_to_table_name(layer1)))
        self.assertTrue(col.has_layer(layer1))

        col.old_slow_create_layer(layer2, data_iterator=col.select(), row_mapper=None)
        self.assertEqual(len(col.get_layer_names()), 2)
        self.assertTrue(layer1 in col.get_layer_names())
        self.assertTrue(layer2 in col.get_layer_names())

        col.delete_layer(layer1)
        self.assertFalse(table_exists(self.storage, col.layer_name_to_table_name(layer1)))
        self.assertFalse(col.has_layer(layer1))
        self.assertFalse(layer1 in col.get_layer_names())
        self.assertTrue(col.has_layer(layer2))

        col.delete()

        self.assertFalse(col.has_layer(layer2))
        self.assertEqual(len(col.get_layer_names()), 0)
        self.assertFalse(table_exists(self.storage, table_name))

    def test_layer_read_write(self):
        table_name = get_random_table_name()
        collection = self.storage.get_collection(table_name)
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

        collection.old_slow_create_layer(layer1, data_iterator=collection.select(), row_mapper=row_mapper1)
        tagger1.tag(text1)
        tagger1.tag(text2)

        layer2 = "layer2"
        tagger2 = VabamorfTagger(disambiguate=False, layer_name=layer2)

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer2, data_iterator=collection.select(), row_mapper=row_mapper2)
        tagger2.tag(text1)
        tagger2.tag(text2)

        for key, text in collection.select():
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
        self.assertFalse(table_exists(self.storage, self.storage.layer_name_to_table_name(collection.name, layer1)))
        self.assertFalse(table_exists(self.storage, self.storage.layer_name_to_table_name(collection.name, layer2)))

    def test_layer_meta(self):
        table_name = get_random_table_name()
        collection = self.storage.get_collection(table_name)
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

        collection.old_slow_create_layer(layer1,
                                  data_iterator=collection.select(),
                                  row_mapper=row_mapper1,
                                  meta={"meta_text_id": "int",
                               "sum": "float"})
        layer_table = self.storage.layer_name_to_table_name(collection.name, layer1)
        self.assertTrue(table_exists(self.storage, layer_table))

        q = "SELECT text_id, meta_text_id, sum from %s.%s" % (
            self.schema, layer_table)  # col.layer_name_to_table_name(layer1)
        with self.storage.conn.cursor() as c:
            c.execute(q)
            for row in c.fetchall():
                self.assertEqual(row[0], row[1])
                self.assertAlmostEqual(row[2], 45.5)

        collection.delete()

    def test_layer_query(self):
        table_name = get_random_table_name()
        collection = self.storage.get_collection(table_name)
        collection.create()

        with collection.insert() as collection_insert:
            text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
            collection_insert(text1)

            text2 = Text('Mis kell on?').tag_layer(["sentences"])
            collection_insert(text2)

        # test ambiguous layer
        layer1 = "layer1"
        layer1_table = self.storage.layer_name_to_table_name(table_name, layer1)
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer1,
                                  data_iterator=collection.select(),
                                  row_mapper=row_mapper1)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(layer_query={layer1: q}))), 1)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik') | JsonbLayerQuery(layer_table=layer1_table,
                                                                                       lemma='mis')
        self.assertEqual(len(list(collection.select(layer_query={layer1: q}))), 2)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik') & JsonbLayerQuery(layer_table=layer1_table,
                                                                                       lemma='mis')
        self.assertEqual(len(list(collection.select(layer_query={layer1: q}))), 0)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik')
        text = [text for key, text in collection.select(layer_query={layer1: q})][0]
        self.assertTrue(layer1 not in text.layers)

        text = list(collection.select(layer_query={layer1: q}, layers=[layer1]))[0][1]
        self.assertTrue(layer1 in text.layers)

        # test with 2 layers
        layer2 = "layer2"
        layer2_table = self.storage.layer_name_to_table_name(table_name, layer2)
        tagger2 = VabamorfTagger(disambiguate=True, layer_name=layer2)

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        collection.old_slow_create_layer(layer2, data_iterator=collection.select(), row_mapper=row_mapper2)

        q = JsonbLayerQuery(layer_table=layer2_table, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(collection.select(layer_query={layer2: q}))), 1)

        text = list(collection.select(layer_query={layer2: q}, layers=[layer1, layer2]))[0][1]
        self.assertTrue(layer1 in text.layers)
        self.assertTrue(layer2 in text.layers)

    def test_layer_fingerprint_query(self):
        table_name = get_random_table_name()
        collection = self.storage.get_collection(table_name)
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

        collection.old_slow_create_layer(layer1, data_iterator=collection.select(), row_mapper=row_mapper1, create_index=True)
        collection.old_slow_create_layer(layer2, data_iterator=collection.select(), row_mapper=row_mapper2)

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
        table_name = get_random_table_name()
        collection = self.storage.get_collection(table_name)
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

        collection.old_slow_create_layer(layer1, data_iterator=collection.select(), row_mapper=row_mapper1,
                                  ngram_index={"lemma": 2})
        collection.old_slow_create_layer(layer2, data_iterator=collection.select(), row_mapper=row_mapper2,
                                  ngram_index={"partofspeech": 3})

        self.assertEqual(count_rows(self.storage, self.storage.layer_name_to_table_name(table_name, layer1)), 2)
        self.assertEqual(count_rows(self.storage, self.storage.layer_name_to_table_name(table_name, layer2)), 2)

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
