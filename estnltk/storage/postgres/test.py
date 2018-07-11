""""
Test postgres storage functionality.

Requires .pgpass file with database connection settings in the same directory.

"""
import unittest
import random
import os

from estnltk import Layer
from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.storage.postgres import PostgresStorage, PgStorageException, JsonbTextQuery as Q, JsonbLayerQuery, \
    RowMapperRecord


def get_random_table_name():
    return "table_%d" % random.randint(1, 1000000)


def get_random_table_name_with_schema(schema="public"):
    return "%s.table_%d" % (schema, random.randint(1, 1000000))


class TestStorage(unittest.TestCase):
    def setUp(self):
        schema = "test_storage_schema"
        self.storage = PostgresStorage(pgpass_file=os.path.join(os.path.dirname(__file__), '.pgpass'), schema=schema)
        self.storage.create_schema()

    def tearDown(self):
        self.storage.delete_schema()
        self.storage.close()

    def test_create_collection(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        self.assertFalse(col.exists())
        col.create()
        self.assertTrue(col.exists())
        col.delete()
        self.assertFalse(col.exists())

    def test_sql_injection(self):
        normal_table = get_random_table_name()
        self.storage.create_table(normal_table)
        self.assertTrue(self.storage.table_exists(normal_table))

        injected_table_name = "%a; drop table %s;" % (get_random_table_name(), normal_table)
        self.storage.create_table(injected_table_name)
        self.assertTrue(self.storage.table_exists(injected_table_name))
        self.assertTrue(self.storage.table_exists(normal_table))

        self.storage.drop_table(normal_table)
        self.storage.drop_table(injected_table_name)

    def test_select_by_key(self):
        col = self.storage.get_collection(get_random_table_name())
        col.create()
        self.assertRaises(PgStorageException, lambda: col.select_by_key(1))

        text = Text("Mingi tekst")
        col.insert(text, 1)
        res = col.select_by_key(1)
        self.assertEqual(text, res)
        col.delete()

    def test_select(self):
        col = self.storage.get_collection(get_random_table_name())
        col.create()

        text1 = Text('Ööbik laulab.')
        id1 = col.insert(text1)

        text2 = Text('Mis kell on?')
        id2 = col.insert(text2)

        # test select_by_id
        self.assertEqual(col.select_by_key(id1), text1)
        self.assertEqual(col.select_by_key(id2), text2)

        # test select_all
        res = list(col.select(order_by_key=True))
        self.assertEqual(len(res), 2)
        id_, text = res[0]
        self.assertEqual(id_, id1)
        self.assertEqual(text, text1)
        id_, text = res[1]
        self.assertEqual(id_, id2)
        self.assertEqual(text, text2)

        # test select
        text1 = Text('mis kell on?').analyse('morphology')
        col.insert(text1)
        text2 = Text('palju kell on?').analyse('morphology')
        col.insert(text2)

        res = list(col.select(query=Q('morph_analysis', lemma='mis')))
        self.assertEqual(len(res), 1)

        res = list(col.select(query=Q('morph_analysis', lemma='kell')))
        self.assertEqual(len(res), 2)

        res = list(col.select(query=Q('morph_analysis', lemma='mis') | Q('morph_analysis', lemma='palju')))
        self.assertEqual(len(res), 2)

        res = list(col.select(query=Q('morph_analysis', lemma='mis') & Q('morph_analysis', lemma='palju')))
        self.assertEqual(len(res), 0)

        res = list(col.select(query=(Q('morph_analysis', lemma='mis') | Q('morph_analysis', lemma='palju')) &
                                    Q('morph_analysis', lemma='kell')))
        self.assertEqual(len(res), 2)

        # test find_fingerprint
        q = {"layer": "morph_analysis", "field": "lemma", "ambiguous": True}

        q["query"] = ["mis", "palju"]  # mis OR palju
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 2)

        q["query"] = [["mis"], ["palju"]]  # mis OR palju
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 2)

        q["query"] = [["mis", "palju"]]  # mis AND palju
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 0)

        q["query"] = [{'miss1', 'miss2'}, {'miss3'}]
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 0)

        q["query"] = [{'miss1', 'miss2'}, {'palju'}]
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 1)

        q["query"] = [{'mis', 'miss2'}, {'palju'}]
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 1)

        q["query"] = [{'mis', 'kell'}, {'miss'}]
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 1)

        q["query"] = [{'mis', 'kell'}, {'palju'}]
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 2)

        q["query"] = []
        res = list(col.find_fingerprint(q))
        self.assertEqual(len(res), 4)

        res = list(col.select(keys=[]))
        self.assertEqual(len(res), 0)

        res = list(col.select(keys=[1, 3]))
        self.assertEqual(len(res), 2)

        col.delete()


class TestLayerFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_layer_fragment"
        self.storage = PostgresStorage(pgpass_file=os.path.join(os.path.dirname(__file__), '.pgpass'),
                                       schema=schema)
        self.storage.create_schema()

    def tearDown(self):
        self.storage.delete_schema()
        self.storage.close()

    def test_create(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        lfrag1 = "layer_fragment_1"
        lfrag2 = "layer_fragment_2"

        col.create_layer(lfrag1, data_iterator=col.select(), row_mapper=None)
        self.assertTrue(self.storage.table_exists(col.layer_name_to_table_name(lfrag1)))
        self.assertTrue(col.has_layer(lfrag1))

        col.create_layer(lfrag2, data_iterator=col.select(), row_mapper=None)
        self.assertEqual(len(col.get_layer_names()), 2)
        self.assertTrue(lfrag1 in col.get_layer_names())
        self.assertTrue(lfrag2 in col.get_layer_names())

        col.delete_layer(lfrag1)
        self.assertFalse(self.storage.table_exists(col.layer_name_to_table_name(lfrag1)))
        self.assertFalse(col.has_layer(lfrag1))
        self.assertFalse(lfrag1 in col.get_layer_names())
        self.assertTrue(col.has_layer(lfrag2))

        col.delete()

        self.assertFalse(col.has_layer(lfrag2))
        self.assertEqual(len(col.get_layer_names()), 0)
        self.assertFalse(self.storage.table_exists(table_name))

    def test_read_write(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        text1 = Text('see on esimene lause').tag_layer(["sentences"])
        col.insert(text1)
        text2 = Text('see on teine lause').tag_layer(["sentences"])
        col.insert(text2)

        layer_fragment_name = "layer_fragment_1"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer_fragment_name)

        def fragment_tagger(row):
            text_id, text = row[0], row[1]
            fragments = [RowMapperRecord(layer=tagger1.tag(text, return_layer=True), meta=None),
                         RowMapperRecord(layer=tagger1.tag(text, return_layer=True), meta=None)]
            return fragments

        col.create_layer(layer_fragment_name,
                         data_iterator=col.select(),
                         row_mapper=fragment_tagger)
        tagger1.tag(text1)
        tagger1.tag(text2)

        self.assertTrue(col.has_layer(layer_fragment_name))

        rows = [row for row in col.select_raw(layers=[layer_fragment_name])]
        self.assertEqual(len(rows), 4)

        text_ids = [row[0] for row in rows]
        self.assertEqual(text_ids[0], text_ids[1])
        self.assertEqual(text_ids[2], text_ids[3])
        self.assertNotEqual(text_ids[1], text_ids[2])

        layer_ids = [row[2] for row in rows]
        self.assertEqual(len(set(layer_ids)), 4)

        texts = [row[1] for row in rows]
        self.assertTrue(isinstance(texts[0], Text))

        layers = [row[3] for row in rows]
        self.assertTrue(isinstance(layers[0], Layer))

        col.delete()

        self.assertFalse(
            self.storage.table_exists(col.layer_name_to_table_name(layer_fragment_name)))


class TestFragment(unittest.TestCase):
    def setUp(self):
        schema = "test_fragment"
        self.storage = PostgresStorage(pgpass_file=os.path.join(os.path.dirname(__file__), '.pgpass'),
                                       schema=schema)
        self.storage.create_schema()

    def tearDown(self):
        self.storage.delete_schema()
        self.storage.close()

    def test_create(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        layer_fragment_name = "layer_fragment_1"
        col.create_layer(layer_fragment_name,
                         data_iterator=col.select(),
                         row_mapper=None)

        fragment_name = "fragment_1"

        def row_mapper(row):
            text_id, text = row[0], row[1]
            fragments = [text[layer_fragment_name],
                         text[layer_fragment_name]]
            return fragments

        col.create_fragment(fragment_name,
                            data_iterator=col.select_raw(layers=[layer_fragment_name]),
                            row_mapper=row_mapper,
                            create_index=False,
                            ngram_index=None)

        self.assertTrue(self.storage.table_exists(col.fragment_name_to_table_name(fragment_name)))
        self.assertTrue(col.has_fragment(fragment_name))
        self.assertTrue(fragment_name in col.get_fragment_names())

        col.delete_fragment(fragment_name)

        self.assertFalse(self.storage.table_exists(col.fragment_name_to_table_name(fragment_name)))
        self.assertFalse(col.has_fragment(fragment_name))
        self.assertFalse(fragment_name in col.get_fragment_names())

        col.delete()

    def test_read_write(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        text1 = Text('see on esimene lause').tag_layer(["sentences"])
        col.insert(text1)
        text2 = Text('see on teine lause').tag_layer(["sentences"])
        col.insert(text2)

        layer_fragment_name = "layer_fragment_1"
        tagger = VabamorfTagger(disambiguate=False, layer_name=layer_fragment_name)
        col.create_layer(layer_fragment_name,
                         data_iterator=col.select(),
                         row_mapper=lambda row: [RowMapperRecord(layer=tagger.tag(row[1], return_layer=True),
                                                                 meta=None)])

        self.assertTrue(col.has_layer(layer_fragment_name))

        fragment_name = "fragment_1"

        def row_mapper(row):
            text_id, text, parent_id, parent_layer = row[0], row[1], row[2], row[3]
            fragments = [RowMapperRecord(layer=parent_layer, meta=None),
                         RowMapperRecord(layer=parent_layer, meta=None)]
            return fragments

        col.create_fragment(fragment_name,
                            data_iterator=col.select_raw(layers=[layer_fragment_name]),
                            row_mapper=row_mapper,
                            create_index=False,
                            ngram_index=None)

        rows = list(col.select_fragment_raw(fragment_name, layer_fragment_name))
        self.assertEqual(len(rows), 4)

        row = rows[0]
        self.assertEqual(len(row), 6)
        self.assertIsInstance(row[0], int)
        self.assertIsInstance(row[1], Text)
        self.assertIsInstance(row[2], int)
        self.assertIsInstance(row[3], Layer)
        self.assertIsInstance(row[4], int)
        self.assertIsInstance(row[5], Layer)


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.schema = "test_layer"
        self.storage = PostgresStorage(pgpass_file=os.path.join(os.path.dirname(__file__), '.pgpass'),
                                       schema=self.schema)
        self.storage.create_schema()

    def tearDown(self):
        self.storage.delete_schema()
        self.storage.close()

    def test_create_layer(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        layer1 = "layer1"
        layer2 = "layer2"

        col.create_layer(layer1, data_iterator=col.select(), row_mapper=None)

        self.assertTrue(self.storage.table_exists(col.layer_name_to_table_name(layer1)))
        self.assertTrue(col.has_layer(layer1))

        col.create_layer(layer2, data_iterator=col.select(), row_mapper=None)
        self.assertEqual(len(col.get_layer_names()), 2)
        self.assertTrue(layer1 in col.get_layer_names())
        self.assertTrue(layer2 in col.get_layer_names())

        col.delete_layer(layer1)
        self.assertFalse(self.storage.table_exists(col.layer_name_to_table_name(layer1)))
        self.assertFalse(col.has_layer(layer1))
        self.assertFalse(layer1 in col.get_layer_names())
        self.assertTrue(col.has_layer(layer2))

        col.delete()

        self.assertFalse(col.has_layer(layer2))
        self.assertEqual(len(col.get_layer_names()), 0)
        self.assertFalse(self.storage.table_exists(table_name))

    def test_layer_read_write(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        text1 = Text('see on esimene lause').tag_layer(["sentences"])
        col.insert(text1)
        text2 = Text('see on teine lause').tag_layer(["sentences"])
        col.insert(text2)

        layer1 = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        col.create_layer(layer1, data_iterator=col.select(), row_mapper=row_mapper1)
        tagger1.tag(text1)
        tagger1.tag(text2)

        layer2 = "layer2"
        tagger2 = VabamorfTagger(disambiguate=False, layer_name=layer2)

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        col.create_layer(layer2, data_iterator=col.select(), row_mapper=row_mapper2)
        tagger2.tag(text1)
        tagger2.tag(text2)

        for key, text in col.select():
            self.assertTrue("sentences" in text.layers)
            self.assertTrue(layer1 not in text.layers)
            self.assertTrue(layer2 not in text.layers)

        rows = list(col.select(layers=[layer1, layer2]))
        text1_db = rows[0][1]
        self.assertTrue(layer1 in text1_db.layers)
        self.assertTrue(layer2 in text1_db.layers)
        self.assertEqual(text1_db[layer1].lemma, text1[layer1].lemma)
        self.assertEqual(text1_db[layer2].lemma, text1[layer2].lemma)

        col.delete()
        self.assertFalse(self.storage.table_exists(self.storage.layer_name_to_table_name(col.table_name, layer1)))
        self.assertFalse(self.storage.table_exists(self.storage.layer_name_to_table_name(col.table_name, layer2)))

    def test_layer_meta(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        text1 = Text('see on esimene lause').tag_layer(["sentences"])
        col.insert(text1)
        text2 = Text('see on teine lause').tag_layer(["sentences"])
        col.insert(text2)

        layer1 = "layer1"
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta={"meta_text_id": text_id, "sum": 45.5})]

        col.create_layer(layer1,
                         data_iterator=col.select(),
                         row_mapper=row_mapper1,
                         meta={"meta_text_id": "int",
                               "sum": "float"})
        layer_table = self.storage.layer_name_to_table_name(col.table_name, layer1)
        self.assertTrue(self.storage.table_exists(layer_table))

        q = "SELECT text_id, meta_text_id, sum from %s.%s" % (
            self.schema, layer_table)  # col.layer_name_to_table_name(layer1)
        with self.storage.conn.cursor() as c:
            c.execute(q)
            for row in c.fetchall():
                self.assertEqual(row[0], row[1])
                self.assertAlmostEqual(row[2], 45.5)

        col.delete()

    def test_layer_query(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
        id1 = col.insert(text1)

        text2 = Text('Mis kell on?').tag_layer(["sentences"])
        id2 = col.insert(text2)

        # test ambiguous layer
        layer1 = "layer1"
        layer1_table = self.storage.layer_name_to_table_name(table_name, layer1)
        tagger1 = VabamorfTagger(disambiguate=False, layer_name=layer1)

        def row_mapper1(row):
            text_id, text = row[0], row[1]
            layer = tagger1.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        col.create_layer(layer1,
                         data_iterator=col.select(),
                         row_mapper=row_mapper1)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(col.select(layer_query={layer1: q}))), 1)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik') | JsonbLayerQuery(layer_table=layer1_table,
                                                                                       lemma='mis')
        self.assertEqual(len(list(col.select(layer_query={layer1: q}))), 2)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik') & JsonbLayerQuery(layer_table=layer1_table,
                                                                                       lemma='mis')
        self.assertEqual(len(list(col.select(layer_query={layer1: q}))), 0)

        q = JsonbLayerQuery(layer_table=layer1_table, lemma='ööbik')
        text = [text for key, text in col.select(layer_query={layer1: q})][0]
        self.assertTrue(layer1 not in text.layers)

        text = list(col.select(layer_query={layer1: q}, layers=[layer1]))[0][1]
        self.assertTrue(layer1 in text.layers)

        # test with 2 layers
        layer2 = "layer2"
        layer2_table = self.storage.layer_name_to_table_name(table_name, layer2)
        tagger2 = VabamorfTagger(disambiguate=True, layer_name=layer2)

        def row_mapper2(row):
            text_id, text = row[0], row[1]
            layer = tagger2.tag(text, return_layer=True)
            return [RowMapperRecord(layer=layer, meta=None)]

        col.create_layer(layer2, data_iterator=col.select(), row_mapper=row_mapper2)

        q = JsonbLayerQuery(layer_table=layer2_table, lemma='ööbik', form='sg n')
        self.assertEqual(len(list(col.select(layer_query={layer2: q}))), 1)

        text = list(col.select(layer_query={layer2: q}, layers=[layer1, layer2]))[0][1]
        self.assertTrue(layer1 in text.layers)
        self.assertTrue(layer2 in text.layers)

    def test_layer_fingerprint_query(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        text1 = Text('Ööbik laulab.').tag_layer(["sentences"])
        id1 = col.insert(text1)

        text2 = Text('Mis kell on?').tag_layer(["sentences"])
        id2 = col.insert(text2)

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

        col.create_layer(layer1, data_iterator=col.select(), row_mapper=row_mapper1, create_index=True)
        col.create_layer(layer2, data_iterator=col.select(), row_mapper=row_mapper2)

        # test one layer
        res = col.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": ["ööbik"],
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 1)

        res = col.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": ["ööbik"],
                "ambiguous": False
            }})
        self.assertEqual(len(list(res)), 0)

        res = col.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": ["ööbik", "mis"],  # ööbik OR mis
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 2)

        res = col.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": [["ööbik", "mis"]],  # ööbik AND mis
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 0)

        res = col.find_fingerprint(layer_query={
            layer1: {
                "field": "lemma",
                "query": [["ööbik", "laulma"]],  # ööbik AND laulma
                "ambiguous": True
            }})
        self.assertEqual(len(list(res)), 1)

        # test multiple layers
        res = col.find_fingerprint(layer_query={
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
        col = self.storage.get_collection(table_name)
        col.create()

        text1 = Text("Ööbik laulab puu otsas.").tag_layer(["sentences"])
        id1 = col.insert(text1)

        text2 = Text("Mis kell on?").tag_layer(["sentences"])
        id2 = col.insert(text2)

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

        col.create_layer(layer1, data_iterator=col.select(), row_mapper=row_mapper1,
                         ngram_index={"lemma": 2})
        col.create_layer(layer2, data_iterator=col.select(), row_mapper=row_mapper2,
                         ngram_index={"partofspeech": 3})

        self.assertEqual(self.storage.count_rows(self.storage.layer_name_to_table_name(table_name, layer1)), 2)
        self.assertEqual(self.storage.count_rows(self.storage.layer_name_to_table_name(table_name, layer2)), 2)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("otsas", ".")]}}))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], id1)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("mis", "kell")]}}))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], id2)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("mis",)]}}))
        self.assertEqual(len(res), 1)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer1: {
                "lemma": [[("mis", "kell")],  # "mis-kell" OR "otsas-."
                          [("otsas", ".")]]
            }}))
        self.assertEqual(len(res), 2)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer1: {
                "lemma": [[("mis", "kell"),  # "mis-kell" AND "otsas-."
                           ("otsas", ".")]]
            }}))
        self.assertEqual(len(res), 0)

        # "Ööbik laulab puu otsas." ->[['H', 'S'], ['V'], ['S', 'S'], ['D', 'K', 'V', 'S'], ['Z']]
        # "Mis kell on?" -> [['P', 'P'], ['S'], ['V', 'V'], ['Z']]
        res = list(col.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [("S", "V", "S")]}}))  # Ööbik laulab puu
        self.assertEqual(len(res), 1)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [("S", "V")]}}))  # 2-grams are also indexed
        self.assertEqual(len(res), 2)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [[("S", "V", "S")],  # "Ööbik laulab puu" OR "Mis kell on"
                                      [("P", "S", "V")]]}}))
        self.assertEqual(len(res), 2)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer2: {"partofspeech": [[("S", "V", "S"), ("S", "D", "Z")]]}}))  # "Ööbik laulab puu" AND "puu otsas ."
        self.assertEqual(len(res), 1)

        res = list(col.find_fingerprint(layer_ngram_query={
            layer1: {"lemma": [("puu", "otsas")]},
            layer2: {"partofspeech": [("S", "V", "S")]},  # "laulma-puu-otsas"
        }))
        self.assertEqual(len(res), 1)

        res = list(col.find_fingerprint(
            layer_ngram_query={
                layer1: {"lemma": [("mis", "kell")]}},
            layers=[layer1, layer2]
        ))
        t1 = res[0][1]
        self.assertTrue(layer1 in t1.layers)
        self.assertTrue(layer2 in t1.layers)

        col.delete()


if __name__ == '__main__':
    unittest.main()
