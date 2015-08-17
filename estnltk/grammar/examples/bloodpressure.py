# -*- coding: utf-8 -*-
"""Example grammar that extracts blood pressures."""
from __future__ import unicode_literals, print_function, absolute_import

from ..grammar import *
from ...text import Text

from pprint import pprint

opt_space = Regex('\s*')

bp_name = Union(
    Regex('RR'),
    Regex('V/?R'),
    Lemmas('vererõhk'))

systolic = Regex('\d\d\d?', name='systolic')
diastolic = Regex('\d\d\d?', name='diastolic')

value = Union(
    Concatenation(
        systolic,
        opt_space,
        Regex('/'),
        opt_space,
        diastolic),
    systolic
)

unit = IRegex('mm[ -/]?hg')

bp_expression = Union(
    Concatenation(
        bp_name,
        opt_space,
        value,
        opt_space,
        unit
    ),
    Concatenation(
        bp_name,
        opt_space,
        value
    ),
    name='bloodpressure'
)

example = '''22.05.2000 - Patsient niisama.
RR 130/80 mmHg. Kontakti patsiendiga ei saa
RR 120 / 80 mmHg
kõrvalkahinateta , RR mmHg , fr 76 xminutis
RR 115/100 mm Hg
RR 106/70 mmhg
'''

if __name__ == '__main__':
    text = Text(example)
    print (text.text)
    matches = bp_expression.get_matches(text)
    for match in matches:
        pprint (match.dict)
