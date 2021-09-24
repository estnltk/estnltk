from estnltk.core import PACKAGE_PATH
from estnltk.helpers.logger import logger
from estnltk.helpers.progressbar import Progressbar

from estnltk.layer.annotation import Annotation
from estnltk.layer.base_span import BaseSpan
from estnltk.layer.base_span import ElementaryBaseSpan
from estnltk.layer.base_span import EnvelopingBaseSpan
from estnltk.layer.span import Span
from estnltk.layer.enveloping_span import EnvelopingSpan
from estnltk.layer.span_list import SpanList
from estnltk.layer.layer import Layer
from estnltk.text import Text

from estnltk.taggers.tagger import Tagger
from estnltk.taggers.retagger import Retagger

from distutils.version import LooseVersion
import pandas

if LooseVersion(pandas.__version__) < LooseVersion('1'):
    pandas.set_option('display.max_colwidth', -1)
else:
    pandas.set_option('display.max_colwidth', None)
