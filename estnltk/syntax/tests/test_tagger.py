# -*- coding: utf-8 -*-
"""
TODO: syntax tagger module needs tons of testing, because there are a lot of things that can break.
"""
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ...text import Text
from ..tagger import SyntaxTagger

t = '''Kes tasa sõuab, see võibolla jõuab kaugele, kui tema aerud ära ei mädane.
See teine lause on siin niisama.
Kuid mis siin ikka pikalt mõtiskleda, on nende asjadega nagu on.'''

tagger = SyntaxTagger()
text = Text(t)
text.tag_analysis()
tagger.tag_text(text)


class SyntaxTaggerTest(unittest.TestCase):

    def test_noop(self):
        tagger.tag_text(text)
