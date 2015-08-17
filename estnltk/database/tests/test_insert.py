# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..database import Database
from ...text import Text
from pprint import pprint


def text():
    text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid.')
    text.tag_clauses().tag_named_entities()
    return text


def database(name, id):
    return Database(name, id)

#class DeleteTest(unittest.TestCase):
    # def test_delete(self):
    #     db  = database('test_delete', 100)
    #     #db.insert(100, text())
    #     #db.delete('test_delete', 100)
    #     self.assertAlmostEquals(0, db.count('test_delete'))

class InsertTest(unittest.TestCase):
    def test_insert(self):
        db = database('test_insert', 100)
        print(text())
        print(db.count('test_insert'))
        #db.delete()
        db.insert(100, text())
        self.assertEqual(1, db.count('test_insert'))
