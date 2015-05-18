# -*- coding: utf-8 -*-
'''Temporal expression tagger.'''
from __future__ import unicode_literals, print_function

from estnltk import Tokenizer
from estnltk import PyVabamorfAnalyzer
from estnltk import TimexTagger
from pprint import pprint

tokenizer = Tokenizer()
analyzer = PyVabamorfAnalyzer()
tagger = TimexTagger()

text = ''''Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle.'''
tagged = tagger(analyzer(tokenizer(text)))

# print timex objects
pprint(tagged.timexes)


# retag with a new creation date
import datetime

tagged = tagger(tagged, creation_date=datetime.datetime(1995, 6, 10))
pprint(tagged.timexes)
