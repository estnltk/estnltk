# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text

class TimexTest(unittest.TestCase):

    def test_tag_separately(self):
        text = self.document
        self.assertListEqual(text.timexes, self.timexes)

    @property
    def document(self):
        return Text('3. detsembril 2014 oli näiteks ilus ilm. Aga kaks päeva varem jälle ei olnud.')

    @property
    def timexes(self):
        return [{'end': 18,
                  'id': 0,
                  'start': 0,
                  'temporal_function': False,
                  'text': '3. detsembril 2014',
                  'tid': 't1',
                  'type': 'DATE',
                  'value': '2014-12-03'},
                 {'anchor_id': 0,
                  'anchor_tid': 't1',
                  'end': 61,
                  'id': 1,
                  'start': 45,
                  'temporal_function': True,
                  'text': 'kaks päeva varem',
                  'tid': 't2',
                  'type': 'DATE',
                  'value': '2014-12-01'}]