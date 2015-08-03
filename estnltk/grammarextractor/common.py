# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape


try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
