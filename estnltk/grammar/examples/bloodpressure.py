# -*- coding: utf-8 -*-
"""Example grammar that extracts blood pressures."""
from __future__ import unicode_literals, print_function, absolute_import

from ..grammar import *
from ...text import Text
from ...prettyprinter import PrettyPrinter

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

unit = IRegex('mm[ -/]?hg', name='unit')

bp_measurement = Union(
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
RR 130/80 mmHg. Patsient rahulik.
RR 120 / 80 mmHg
RR 120 mm/Hg , fr 76 xminutis
V/R115/100 mm Hg
RR 106/70 mmhg
'''

if __name__ == '__main__':
    text = Text(example)
    #print ('Text:')
    #print (text.text)

    # just print the matches
    #print ('Matches:')
    #matches = bp_measurement.get_matches(text)
    #for match in matches:
    #    pprint(match.dict)

    # annotate the text and print it as html
    bp_measurement.annotate(text)
    pp = PrettyPrinter(background='bloodpressure', color='systolic', italics='diastolic', font='unit')

    html = pp.render(text, add_header=True)
    print (html)
