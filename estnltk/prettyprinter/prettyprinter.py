# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.
Deals with rendering Text instances as HTML.
"""
from __future__ import unicode_literals, print_function, absolute_import

from .values import AESTHETICS, VALUES, AES_VALUE_MAP, DEFAULT_VALUE_MAP, LEGAL_ARGUMENTS
from .templates import get_mark_css, HEADER, MIDDLE, FOOTER, DEFAULT_MARK_CSS
from .marker import mark_text
from .rules import create_rules

from cached_property import cached_property
import six


def assert_legal_arguments(kwargs):
    """Assert that PrettyPrinter arguments are correct.

    Raises
    ------
    ValueError
        In case there are unknown arguments or a single layer is mapped to more than one aesthetic.
    """
    seen_layers = set()
    for k, v in kwargs.items():
        if k not in LEGAL_ARGUMENTS:
            raise ValueError('Illegal argument <{0}>!'.format(k))
        if k in AESTHETICS:
            if v in seen_layers:
                raise ValueError('Layer <{0}> mapped for more than a single aesthetic!'.format(v))
            seen_layers.add(v)
        if k in VALUES:
            if not isinstance(v, six.string_types) and not isinstance(v, list):
                raise ValueError('Value <{0}> must be either string or list'.format(k))
            if isinstance(v, list):
                if len(v) == 0:
                    raise ValueError('Rules cannot be empty list')
                for rule_matcher, rule_value in v:
                    if not isinstance(rule_matcher, six.string_types) or not isinstance(rule_value, six.string_types):
                        raise ValueError('Rule tuple elements must be strings')


def parse_arguments(kwargs):
    """Function that parses PrettyPrinter arguments.
    Detects which aesthetics are mapped to which layers
    and collects user-provided values.

    Parameters
    ----------
    kwargs: dict
        The keyword arguments to PrettyPrinter.

    Returns
    -------
    dict, dict
        First dictionary is aesthetic to layer mapping.
        Second dictionary is aesthetic to user value mapping.
    """
    aesthetics = {}
    values = {}
    for aes in AESTHETICS:
        if aes in kwargs:
            aesthetics[aes] = kwargs[aes]
            val_name = AES_VALUE_MAP[aes]
            # map the user-provided CSS value or use the default
            values[aes] = kwargs.get(val_name, DEFAULT_VALUE_MAP[aes])
    return aesthetics, values


class PrettyPrinter(object):
    """Class for formatting Text instances as HTML & CSS."""

    def __init__(self, **kwargs):
        """Initialize a new PrettyPrinter class.

        Parameters
        ----------
        color: str or callable
            Layer that corresponds to color aesthetic.
        background: str or callable
            Layer that corresponds to background.
        ...

        color_value: str or list
            The alternative value for the color.
        background_value: str or list
            The background value for the color.
        """
        assert_legal_arguments(kwargs)
        self.__aesthetics, self.__values = parse_arguments(kwargs)
        self.__rules = dict((aes, create_rules(aes, self.values[aes])) for aes in self.aesthetics)

    @cached_property
    def aesthetics(self):
        """Mapping of aesthetics mapped to layers."""
        return self.__aesthetics

    @cached_property
    def values(self):
        """Mapping of aesthetic values."""
        return self.__values

    @cached_property
    def rules(self):
        return self.__rules

    @cached_property
    def css(self):
        """Returns
        -------
        str
            The CSS.
        """
        css_list = [DEFAULT_MARK_CSS]
        for aes in self.aesthetics:
            css_list.extend(get_mark_css(aes, self.values[aes]))
        #print('\n'.join(css_list))
        return '\n'.join(css_list)

    def render(self, text, add_header=False):
        """Render the HTML.

        Parameters
        ----------
        add_header: boolean (default: False)
            If True, add HTML5 header and footer.

        Returns
        -------
        str
            The rendered HTML.
        """

        html = mark_text(text, self.aesthetics, self.rules)
        html = html.replace('\n', '<br/>')
        if add_header:
            html = '\n'.join([HEADER, self.css, MIDDLE, html, FOOTER])
        #print('\n'.join((HEADER, self.css, MIDDLE, html, FOOTER)))
        return html


