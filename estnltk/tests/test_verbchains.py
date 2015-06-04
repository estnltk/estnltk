# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text


class VerbchainTest(unittest.TestCase):

    def test_verbchain(self):
        text = Text('Kass, suur ja must, ei jooksnud üle tee.')
        phrase = Text('ei jooksnud')
        phrase.compute_verb_chains()
        text.compute_verb_chains()
        phrases = text.split_by('verb_chains')
        self.assertEqual(len(phrases), 1)
