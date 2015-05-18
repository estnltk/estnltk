"""
Documentation quick example code.
"""
from __future__ import unicode_literals, print_function, absolute_import

from estnltk import Text
from pprint import pprint

text = Text('''Tuleb minna vanast raudteeülesõidukohast edasi ja pöörata paremale.''')
pprint(list(zip(text.word_texts, text.lemmas, text.postags, text.forms)))