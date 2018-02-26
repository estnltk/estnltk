""""
Test postgres storage functionality.

Requires .pgpass file with database connection settings in the same directory.

"""
import unittest
import random
import os

from estnltk.layer import Layer

from estnltk.spans import Span

from estnltk import Text
from estnltk.converters.dict_importer import dict_to_layer
from estnltk.taggers import VabamorfTagger
from estnltk.storage.postgres import PostgresStorage, PgStorageException, JsonbQuery as Q
from estnltk.finite_grammar import layer_to_graph


def get_random_table_name():
    return "table_%d" % random.randint(1, 1000000)


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.storage = PostgresStorage(pgpass_file=os.path.join(os.path.dirname(__file__), '.pgpass'))

    def tearDown(self):
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
        res = list(col.find_fingerprint('morph_analysis', 'lemma', [{'miss1', 'miss2'}, {'miss3'}]))
        self.assertEqual(len(res), 0)

        res = list(col.find_fingerprint('morph_analysis', 'lemma', [{'miss1', 'miss2'}, {'palju'}]))
        self.assertEqual(len(res), 1)

        res = list(col.find_fingerprint('morph_analysis', 'lemma', [{'mis', 'miss2'}, {'palju'}]))
        self.assertEqual(len(res), 1)

        res = list(col.find_fingerprint('morph_analysis', 'lemma', [{'mis', 'kell'}, {'miss'}]))
        self.assertEqual(len(res), 1)

        res = list(col.find_fingerprint('morph_analysis', 'lemma', [{'mis', 'kell'}, {'palju'}]))
        self.assertEqual(len(res), 2)

        res = list(col.find_fingerprint('morph_analysis', 'lemma', []))
        self.assertEqual(len(res), 4)

        col.delete()


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.storage = PostgresStorage(pgpass_file=os.path.join(os.path.dirname(__file__), '.pgpass'))

    def tearDown(self):
        self.storage.close()

    def test_create_layer(self):
        table_name = get_random_table_name()
        col = self.storage.get_collection(table_name)
        col.create()

        layer1 = "layer1"
        layer2 = "layer2"

        col.create_layer(layer1, callable=None)
        self.assertTrue(self.storage.table_exists("%s__%s" % (table_name, layer1)))
        self.assertTrue(col.has_layer(layer1))

        col.create_layer(layer2, callable=None)
        self.assertEqual(len(col.get_layer_names()), 2)
        self.assertTrue(layer1 in col.get_layer_names())
        self.assertTrue(layer2 in col.get_layer_names())

        col.delete_layer(layer1)
        self.assertFalse(self.storage.table_exists("%s__%s" % (table_name, layer1)))
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
        col.create_layer(layer1, callable=lambda t: tagger1.tag(t, return_layer=True))
        tagger1.tag(text1)
        tagger1.tag(text2)

        layer2 = "layer2"
        tagger2 = VabamorfTagger(disambiguate=False, layer_name=layer2)
        col.create_layer(layer2, callable=lambda t: tagger2.tag(t, return_layer=True))
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


if __name__ == '__main__':
    unittest.main()
