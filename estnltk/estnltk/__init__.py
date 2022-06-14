# The current version of EstNLTK. Should be readable from setup.py
__version__ = '1.7.0'

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

from estnltk_core.taggers.tagger import Tagger
from estnltk_core.taggers.retagger import Retagger

from estnltk.text import Text

import pandas

# Set the maximum width in characters of a column in 
# a pandas data structure. ‘None’ value means unlimited.
# (Note: assuming pandas.__version__ >= 1.0.0)
pandas.set_option('display.max_colwidth', None)

# Update global serialization registry: add syntax & legacy serialization modules
from estnltk_core.converters.serialisation_registry import SERIALISATION_REGISTRY
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.converters.serialisation_modules import legacy_v0

if 'syntax_v0' not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY['syntax_v0'] = syntax_v0
if 'legacy_v0' not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY['legacy_v0'] = legacy_v0

from estnltk.downloader import download, get_resource_paths
