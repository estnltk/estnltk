# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .text import Text

import codecs
import json


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
    documents = []
    with codecs.open(fnm, 'rb', 'ascii') as f:
        line = f.readline()
        while line != '':
            documents.append(Text(json.loads(line)))
            line = f.readline()
    return documents


def write_json_corpus(documents, fnm):
    """Write a list of Text instances as JSON corpus on disk.
    A JSON corpus contains one document per line, encoded in JSON.

    Parameters
    ----------
    documents: list of estnltk.text.Text
        The documents of the corpus
    fnm: str
        The path to save the corpus.
    """
    with codecs.open(fnm, 'wb', 'ascii') as f:
        for document in documents:
            f.write(json.dumps(document))
    return documents
