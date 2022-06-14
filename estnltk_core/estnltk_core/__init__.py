# The current version of EstNLTK. Should be readable from setup.py
__version__ = '1.7.0'

from estnltk_core.common import CORE_PACKAGE_PATH

from estnltk_core.layer.annotation import Annotation
from estnltk_core.layer.base_span import BaseSpan
from estnltk_core.layer.base_span import ElementaryBaseSpan
from estnltk_core.layer.base_span import EnvelopingBaseSpan
from estnltk_core.layer.span import Span
from estnltk_core.layer.enveloping_span import EnvelopingSpan
from estnltk_core.layer.span_list import SpanList
from estnltk_core.layer.layer import Layer

from estnltk_core.taggers.tagger import Tagger
from estnltk_core.taggers.retagger import Retagger

import pandas

# Set the maximum width in characters of a column in 
# a pandas data structure. ‘None’ value means unlimited.
# (Note: assuming pandas.__version__ >= 1.0.0)
pandas.set_option('display.max_colwidth', None)

