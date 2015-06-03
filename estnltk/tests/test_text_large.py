# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest
import os
from pprint import pprint

from ..text import Text
from ..teicorpus import parse_tei_corpus
from ..core import AA_PATH

docs = parse_tei_corpus(os.path.join(AA_PATH, 'tea_AA_00_1.tasak.xml'))
plain = docs[5].text

text = Text(plain)
pprint(text)