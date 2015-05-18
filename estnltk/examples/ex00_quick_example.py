"""
Documentation quick example code.
"""
from __future__ import unicode_literals, print_function, absolute_import

from estnltk import Text
from pprint import pprint

text = Text('Mine vanast raudteeülesõidukohast edasi ja pööra paremale, siis leiad Krokodilli!')
text.get.word_texts.lemmas.postags.postag_descriptions.as_dataframe

text.get.word_texts.lemmas.postags.postag_descriptions.as_dict
