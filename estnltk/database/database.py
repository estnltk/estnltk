# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import


class Database(object):

    def regex_query(self, regex, layer=None):
        """Find all Text documents that match given regular expression.

        Parameters
        ----------
        layer: str
            The layer to search the text from (for example words, sentences, clauses, verb_phrases etc).
            If layer is None (default), then use the full document text for search.

        Returns
        -------
        Iterable of {"text": document, "matches": layer}
        """
        pass

    def keyword_query(self, regex):
        pass
