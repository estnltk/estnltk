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


def database():
    return Database('test')


class InsertTest(unittest.TestCase):

    def test_insert(self):
        db = database()
        db.delete()
        db.index(text(), id=100)
        self.assertEqual(1, db.count())
