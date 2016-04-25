# -*- coding: utf-8 -*-
"""Module for reading extracted wikipedia articles.
"""
from __future__ import unicode_literals, print_function, absolute_import
from ..text import Text


def as_text(article):
    """Convert a Wikipedia article to Text object.
    Concatenates the sections in wikipedia file and rearranges other information so it
    can be interpreted as a Text object.

    Links and other elements with start and end positions are annotated
    as layers.

    Parameters
    ----------
    article: dict
        The wikipedia article (deserialized JSON).

    Returns
    -------
    estnltk.text.Text
        The Text object.
    """
    pass


def read_article(fnm):
    """Read a Wikipedia article.

    Parameters
    ----------
    fnm: str
        The path of the file.

    Returns
    -------
    estnltk.text.Text
        The article as a Text object.
    """
    pass


def yield_corpus(path):
    """Yield all articles from a Wikipedia corpus.

    Parameters
    ----------
    path: str
        The directory containing .json files of articles.

    Returns
    -------
    generator of text
    """
    pass

