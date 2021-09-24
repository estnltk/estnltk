from estnltk_core.common import CORE_PACKAGE_PATH

from estnltk_core.layer.annotation import Annotation
from estnltk_core.layer.base_span import BaseSpan
from estnltk_core.layer.base_span import ElementaryBaseSpan
from estnltk_core.layer.base_span import EnvelopingBaseSpan
from estnltk_core.layer.span import Span
from estnltk_core.layer.enveloping_span import EnvelopingSpan
from estnltk_core.layer.span_list import SpanList
from estnltk_core.layer.layer import Layer
from estnltk_core.text import Text

from estnltk_core.taggers.tagger import Tagger
from estnltk_core.taggers.retagger import Retagger

from distutils.version import LooseVersion
import pandas

if LooseVersion(pandas.__version__) < LooseVersion('1'):
    pandas.set_option('display.max_colwidth', -1)
else:
    pandas.set_option('display.max_colwidth', None)
