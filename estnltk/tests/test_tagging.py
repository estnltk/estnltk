# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ..text import Text
from ..names import *


class TaggingTest(unittest.TestCase):

    def test_tagging(self):
        text = Text('Natukene teksti')

        self.assertFalse(text.is_tagged(PARAGRAPHS))
        self.assertFalse(text.is_tagged(SENTENCES))
        self.assertFalse(text.is_tagged(WORDS))
        self.assertFalse(text.is_tagged(ANALYSIS))
        self.assertFalse(text.is_tagged(LABEL))
        self.assertFalse(text.is_tagged(NAMED_ENTITIES))
        self.assertFalse(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tokenize_paragraphs()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertFalse(text.is_tagged(SENTENCES))
        self.assertFalse(text.is_tagged(WORDS))
        self.assertFalse(text.is_tagged(ANALYSIS))
        self.assertFalse(text.is_tagged(LABEL))
        self.assertFalse(text.is_tagged(NAMED_ENTITIES))
        self.assertFalse(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tokenize_sentences()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertTrue(text.is_tagged(SENTENCES))
        self.assertFalse(text.is_tagged(WORDS))
        self.assertFalse(text.is_tagged(ANALYSIS))
        self.assertFalse(text.is_tagged(LABEL))
        self.assertFalse(text.is_tagged(NAMED_ENTITIES))
        self.assertFalse(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tokenize_words()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertTrue(text.is_tagged(SENTENCES))
        self.assertTrue(text.is_tagged(WORDS))
        self.assertFalse(text.is_tagged(ANALYSIS))
        self.assertFalse(text.is_tagged(LABEL))
        self.assertFalse(text.is_tagged(NAMED_ENTITIES))
        self.assertFalse(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tag_analysis()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertTrue(text.is_tagged(SENTENCES))
        self.assertTrue(text.is_tagged(WORDS))
        self.assertTrue(text.is_tagged(ANALYSIS))
        self.assertFalse(text.is_tagged(LABEL))
        self.assertFalse(text.is_tagged(NAMED_ENTITIES))
        self.assertFalse(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tag_labels()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertTrue(text.is_tagged(SENTENCES))
        self.assertTrue(text.is_tagged(WORDS))
        self.assertTrue(text.is_tagged(ANALYSIS))
        self.assertTrue(text.is_tagged(LABEL))
        self.assertFalse(text.is_tagged(NAMED_ENTITIES))
        self.assertFalse(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tag_named_entities()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertTrue(text.is_tagged(SENTENCES))
        self.assertTrue(text.is_tagged(WORDS))
        self.assertTrue(text.is_tagged(ANALYSIS))
        self.assertTrue(text.is_tagged(LABEL))
        self.assertTrue(text.is_tagged(NAMED_ENTITIES))
        self.assertFalse(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tag_clauses()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertTrue(text.is_tagged(SENTENCES))
        self.assertTrue(text.is_tagged(WORDS))
        self.assertTrue(text.is_tagged(ANALYSIS))
        self.assertTrue(text.is_tagged(LABEL))
        self.assertTrue(text.is_tagged(NAMED_ENTITIES))
        self.assertTrue(text.is_tagged(CLAUSES))
        self.assertFalse(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

        text.tag_verb_chains()

        self.assertTrue(text.is_tagged(PARAGRAPHS))
        self.assertTrue(text.is_tagged(SENTENCES))
        self.assertTrue(text.is_tagged(WORDS))
        self.assertTrue(text.is_tagged(ANALYSIS))
        self.assertTrue(text.is_tagged(LABEL))
        self.assertTrue(text.is_tagged(NAMED_ENTITIES))
        self.assertTrue(text.is_tagged(CLAUSES))
        self.assertTrue(text.is_tagged(VERB_CHAINS))
        self.assertFalse(text.is_tagged(WORDNET))

