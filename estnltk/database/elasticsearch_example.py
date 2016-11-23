# -*- coding:utf-8 -*-
from __future__ import print_function, absolute_import

from estnltk.database import elastic

from ..text import Text

try:
    index = elastic.create_index('example_index')
except:
    index = elastic.connect('example_index')

index.save(Text(
    "See on dokument. See on dokumendi teine lause. Need kõik salvestatakse eraldi objektidena, mille tüüp on 'sentence'"))

for sentence in index.sentences():
    print(sentence.lemmas)
