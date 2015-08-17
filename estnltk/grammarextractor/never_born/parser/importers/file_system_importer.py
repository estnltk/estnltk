# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os
import os.path
import codecs
from .importer import Importer
from ...exceptions import GrammarImportError


class FileSystemImporter(Importer):
    """FileSystemImporter tries to load grammar files from specified search path."""

    def __init__(self, paths):
        """Initialize FileSystemImporter.

        Parameters
        ----------
        paths: list of str
            A search path for the grammars. The paths are traversed in the order they are given here.
        """
        self.__paths = paths

    def import_grammar(self, grammarname):
        """Try to loada grammar text with given name from filesystem.
        First, it tries to load the grammar from working directory and then continues
        for search path.

        Example
        -------
        Assume your working dir is /home/user/myproject
        and you have specified following include paths:
        /grammars
        /home/user/grammars

        and you look for a grammar named common.numerics

        The algorithm will search following locations for the file `numerics`:

        /home/user/myproject/common/numerics
        /grammars/common/numerics
        /home/user/grammars/common/numerics

        Parameters
        ----------
        grammarname: str
            The dots in the grammar name indicate the folder separators.

        Returns
        -------
        str
            The grammar text.
        """

        fnm = os.path.join(*grammarname.split('.'))
        paths = [os.getcwd()] + self.__paths
        for path in paths:
            full_path = os.path.join(path, fnm)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                with codecs.open(full_path, 'rb', 'utf-8') as f:
                    return f.read()
        raise GrammarImportError('Grammar {0} not found!'.format(grammarname))

