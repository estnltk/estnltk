# -*- coding: utf-8 -*-
"""Module defining the pattern matching logic of rules."""
from __future__ import unicode_literals, print_function, absolute_import

import regex as re
import six


class Rules(object):
    """A collection of rules that define which CSS class should be
    used to mark a particular element of an layer."""

    def __init__(self, default_css_class=None):
        """Initiante empty set of rules.

        Parameters
        ----------
        default_css_class: str or None
            The css class that should be returned when no rules match.
        """
        self.__patterns = []
        self.__css_classes = []
        self.__default = default_css_class

    def add_rule(self, pattern, css_class):
        """Add a new rule.

        Parameters
        ----------
        pattern: str
            Pattern that is compiled to a regular expression.
        css_class: str
            The class that will corresponds to given pattern.
        """
        #print('adding rule <{0}> <{1}>'.format(pattern, css_class))
        self.__patterns.append(re.compile(pattern, flags=re.U | re.M))
        self.__css_classes.append(css_class)

    def get_css_class(self, value):
        """Return the css class of first pattern that matches given value.
        If no rules match, the default css class will be returned (see the constructor)
        """
        #print ('get_css_class for {0}'.format(value))
        for idx, pattern in enumerate(self.__patterns):
            if pattern.match(value) is not None:
                #print ('matched rule {0} and returning {1}'.format(idx, self.__css_classes[idx]))
                return self.__css_classes[idx]
        return self.__default


def create_rules(aes, value):
    """Create a Rules instance for a single aesthetic value.

    Parameter
    ---------
    aes: str
        The name of the aesthetic
    value: str or list
        The value associated with any aesthetic
    """
    if isinstance(value, six.string_types):
        return Rules(aes)
    else:
        rules = Rules()
        for idx, (pattern, css_value) in enumerate(value):
            rules.add_rule(pattern, '{0}_{1}'.format(aes, idx))
        return rules

