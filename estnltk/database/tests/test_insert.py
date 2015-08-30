# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..database import Database
from ...text import Text
from pprint import pprint


class InsertTest(unittest.TestCase):
    @property
    def first(self):
        text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid.')
        text.tag_clauses().tag_named_entities()
        return text

    @property
    def second(self):
        text = Text(
            'Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul maanteel tünjat Tallinnfilmi režissööri.')
        text.tag_clauses().tag_named_entities()
        return text

    def setUp(self):
        self.db = Database('test')
        self.db.delete_index()

    def test_insert_default_ids(self):
        print('test_insert_default_ids')
        self.db.refresh()
        db = self.db

        # insert the documents
        id_first = db.insert(self.first)
        id_second = db.insert(self.second)

        # check the count
        self.assertEqual(2, db.count())

        # check the document retrieval
        self.assertDictEqual(self.first, db.get(id_first))
        self.assertDictEqual(self.second, db.get(id_second))


class CountTest(unittest.TestCase):
    def setUp(self):
        self.db = Database('test')
        self.db.delete_index()

    def count_test(self):
        print('count_test')
        self.db = Database('test')
        self.db.delete_index()
        self.db.refresh()
        db = self.db

        # check the count
        self.assertEqual(0, db.count())


class BulkInsertTest(unittest.TestCase):
    @property
    def first(self):
        text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid.')
        text.tag_clauses().tag_named_entities()
        return text


    @property
    def second(self):
        text = Text(
            'Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul maanteel tünjat Tallinnfilmi režissööri.')
        text.tag_clauses().tag_named_entities()
        return text


    def setUp(self):
        self.db = Database('bulk_test')
        self.db.delete_index()

    def bulk_insert(self):
        print('bulk_insert')
        # create a bulk_test database
        self.db = Database('bulk_test')
        self.db.delete_index()
        self.db.refresh()
        db = self.db

        # insert many (bulk) into db bulk_test
        print(self.first)
        print(self.second)
        text_lists = [self.first, self.second]
        # id_bulk = db.insert_many(text_lists)

        # check the document retrieval
        self.assertEqual(1, db.count())
        print("Bulk count test OK")
        # check the document retrieval
        # self.assertAlmostEquals

if __name__ == '__main__':
    unittest.main()