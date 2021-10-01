from estnltk.common import PACKAGE_PATH
from estnltk.helpers.logger import logger
from estnltk.helpers.progressbar import Progressbar

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

# Update serialization map: add syntax serialization module
from estnltk_core.converters.serialisation_modules.serialisation_map import layer_converter_collection
from estnltk.converters.serialisation_modules import syntax_v0

if 'syntax_v0' not in layer_converter_collection:
    layer_converter_collection['syntax_v0'] = syntax_v0
    