# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .text import Text

import codecs
import json


def yield_json_corpus(fnm):
    """Function to read a JSON corpus from a file.
    A JSON corpus contains one document per line, encoded in JSON.
    Each line is yielded after it is read.

    Parameters
    ----------
    fnm: str
        The filename of the corpus.

    Returns
    -------
    generator of Text
    """
    with codecs.open(fnm, 'rb', 'ascii') as f:
        line = f.readline()
        while line != '':
            yield Text(json.loads(line))
            line = f.readline()


def read_json_corpus(fnm):
    """Function to read a JSON corpus from a file.
    A JSON corpus contains one document per line, encoded in JSON.

    Parameters
    ----------
    fnm: str
        The filename of the corpus.

    Returns
    -------
    list of Text
    """
    return [text for text in yield_json_corpus(fnm)]


def write_json_corpus(documents, fnm):
    """Write a lisst of Text instances as JSON corpus on disk.
    A JSON corpus contains one document per line, encoded in JSON.

    Parameters
    ----------
    documents: iterable of estnltk.text.Text
        The documents of the corpus
    fnm: str
        The path to save the corpus.
    """
    with codecs.open(fnm, 'wb', 'ascii') as f:
        for document in documents:
            f.write(json.dumps(document) + '\n')
    return documents