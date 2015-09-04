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
        self.db = Database('test_insert')
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


class BulkInsertTest(unittest.TestCase):

    def test_bulk_insert(self):
        print('bulk_insert')
        # create a bulk_test database
        self.db = Database('bulk_test')
        self.db.delete_index()
        self.db.refresh()
        db = self.db

        # insert many (bulk) into db bulk_test
        it = InsertTest()
        text_lists = [it.first, it.second]
        id_bulk = db.bulk_insert(text_lists)
        print(id_bulk)

        # check the document retrieval
        self.assertEqual(2, db.count())
        print("Bulk count test OK")

class SearchTest(unittest.TestCase):

    def test_search_keyword_documents(self):
        self.db = Database('test')
        keywords = ["Aegna"]
        search = Database.keyword_documents(self.db, keywords=keywords)
        print(search)
