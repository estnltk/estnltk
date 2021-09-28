# -*- coding: utf-8 -*-

import unittest
from ..morf import analyze, disambiguate

# EINO SANTANEN. Muodon vanhimmat
# http://luulet6lgendus.blogspot.com/
sentences = '''KÕIGE VANEM MUDEL

Pimedas luusivad robotid,
originaalsed tšehhi robotid kahekümnendatest.
Robota! kisendavad nad, uhked originaalsed robotid,
hüüdes iseenda nime.
Robota! möirgavad nad, naftasegused elukad,
hiiglase vaimusünnitised, robotid:
kurvameelsetena kauguses,
ebamäärastena kauguses,
mattudes vastuoludesse,
muutudes peaaegu julmaks oma õiglusejanus.
Robota! Kui päike pageb monoliitide kohalt,
tähistavad nad vägisi
öö salajast geomeetriat.
Õudne on inimesel vaadata
neid metsikuid mudeleid.

Kuuntele, romantiikkaa, 2002'''.split('\n')


class TestDisambiguator(unittest.TestCase):
    """Test the separate disambiguate function
    against the built in disambiguate=True function.

    Both must work the same."""

    def test_disambiguator(self):
        for sentence in sentences:
            an_with = analyze(sentence)
            an_without = analyze(sentence, disambiguate=False)
            disamb = disambiguate(an_without)
            self.assertListEqual(an_with, disamb)

