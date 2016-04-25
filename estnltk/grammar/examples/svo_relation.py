# -*- coding: utf-8 -*-
"""Simple naive grammar that extracts subject-verb-object relations."""
from __future__ import unicode_literals, print_function, absolute_import

from ..grammar import *
from ...text import Text

subject = Postags('H', 'S', name='subject')
verb = Postags('V', name='verb')
obj = Postags('H', 'S', name='object')

phrase = Gaps(
    subject,
    verb,
    obj,
    name='phrase'
)

distant_phrase = AllGaps(
    subject,
    verb,
    obj,
    name='phrase'
)

example = '''Harju maakohus pidi alustama teisipäeval Roode ja Pentuse süüasja arutamist,
kuid lükkas istungi edasi, sest Roode hiljuti vahetunud kaitsja Natalia Lausmaa
ei olnud jõudnud kriminaalasja materjalidega tutvuda.
Lausmaa ütles, et asus kaitsja kohustusi täitma 13. augustil ja kuna süüasi on väga mahukas,
vajab ta vähemalt ühe kuu aega toimikutega tutvumiseks.
Ta tõi esile, et süüasjas on kaheksa toimikut ja 45 raamatupidamiskausta.
'''

if __name__ == '__main__':
    sentences = Text(example).split_by('clauses', 'sentences')
    for sentence in sentences:
        print ('TEXT:', sentence, ' ', ' '.join(sentence.postags))
        for m in phrase.get_matches(sentence, conflict_resolver=None):
            m = m.dict
            print ('\tGaps:', m['subject']['text'], m['verb']['text'], m['object']['text'])
        for m in distant_phrase.get_matches(sentence, conflict_resolver=None):
            m = m.dict
            print ('\tAllGaps:', m['subject']['text'], m['verb']['text'], m['object']['text'])
