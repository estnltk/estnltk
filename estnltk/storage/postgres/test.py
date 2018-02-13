""""
Test postgres storage functionality.

Requires .pgpass file with database connection settings in the same directory.

"""
import unittest
import random
import os

from estnltk import Text
from estnltk.storage.postgres import PostgresStorage, PgStorageException, JsonbQuery as Q


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


if __name__ == '__main__':
    unittest.main()
