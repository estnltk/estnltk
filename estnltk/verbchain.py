# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.names import *
from estnltk.core import VERB_CHAIN_RES_PATH

from estnltk.mw_verbs.verbchain_detector import VerbChainDetector as Detector
from pprint import pprint
from .text import Text

det = Detector(resourcesPath=VERB_CHAIN_RES_PATH)

text = Text('See masin ei läinud just rikki')
text.compute_analysis()
pprint(text)
det.detectVerbChainsFromSent(text)