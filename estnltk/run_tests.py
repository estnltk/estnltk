# -*- coding: utf-8 -*-
"""Shortcut script for running all unit tests in Estnltk."""
from __future__ import unicode_literals, print_function, absolute_import

import unittest

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('estnltk.tests')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
