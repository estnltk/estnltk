# -*- coding: utf-8 -*-
"""
1. võimaldada parameetritele color_value, background_value anda väärtuseks ühe sõne asemel tervet reeglite listi.
1.a reeglid oleksid paarid (regulaaravaldis, css_väärtus)
1.b kui N on reeglite listi pikkus, siis peaks genereerima N erinevat CSS-i klassi, näiteks background_0, background_1, ..., background_N .
1.c neid regulaaravaldisi võiks siis by default matchida elementide tekstidel.

2. võimaldada color, background, ... argumendiks võtta kihi nime asemel hoopis funktsiooni, mis näiteks suudaks teha nii, et reeglite liste saab matchida lemmade, postagide jmt. Kasutajale mõeldes tuleks enamikule estnltk-s olevatele kihtide atribuutidele vastavad helper funktsioonid ka valmis teha.

3. dokumenteerida PrettyPrinteri klass.

4. kirjutada dokumentatsiooni juhend prettyprinteri kasutamiseks.

"""
from __future__ import unicode_literals, print_function, absolute_import

import unittest
from ...text import Text
from ..prettyprinter import PrettyPrinter
from ..extractors import postags


class SimpleTest(unittest.TestCase):

    @property
    def text(self):
        text = Text('Nimisõnad värvitakse')
        return text.tag_analysis()

    @property
    def rules(self):
        return [
            ('Nimisõnad', 'green'),
            ('värvitakse', 'blue')
        ]

    @property
    def expected(self):
        return '<mark class="background_0">Nimisõnad</mark> <mark class="background_1">värvitakse</mark>'

    def test_postag_rules(self):
        text = self.text

        pp = PrettyPrinter(background='words', background_value=self.rules)
        html = pp.render(text, False)

        self.assertEqual(self.expected, html)


class ComplexTest(unittest.TestCase):

    @property
    def text(self):
        text = Text('Suured kollased kõrvad ja')
        return text.tag_analysis()

    @property
    def rules(self):
        return [
            ('A', 'blue'),
            ('S', 'green')
        ]

    @property
    def expected(self):
        return '<mark class="background_0">Suured</mark> <mark class="background_0">kollased</mark> <mark class="background_1">kõrvad</mark> ja'

    def test_postag_rules(self):
        text = self.text

        pp = PrettyPrinter(background=postags, background_value=self.rules)
        html = pp.render(text)

        self.assertEqual(self.expected, html)
