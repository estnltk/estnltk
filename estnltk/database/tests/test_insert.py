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
        text = Text('Üle oja jõele. Läbi oru mäele. Usjas kaslane ründas künklikul maanteel tünjat Tallinnfilmi režissööri.')
        text.tag_clauses().tag_named_entities()
        return text

    def setUp(self):
        self.db = Database('test')
        self.db.delete_index()

    def test_insert_default_ids(self):
        db = self.db

        # insert the documents
        id_first = db.insert(self.first)
        id_second = db.insert(self.second)

        # check the count
        self.assertEqual(2, db.count())

        # check the document retrieval
        self.assertDictEqual(self.first, db.get(id_first))
        self.assertDictEqual(self.second, db.get(id_second))
