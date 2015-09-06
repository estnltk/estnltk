# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.
Deals with rendering Text instances as HTML.
"""
from __future__ import unicode_literals, print_function, absolute_import

from .values import AESTHETICS, AES_VALUE_MAP, DEFAULT_VALUE_MAP, LEGAL_ARGUMENTS
from .templates import get_mark_css, HEADER, MIDDLE, FOOTER, MARK_CSS, OPENING_MARK, CLOSING_MARK
from .marker import mark_text, css_layers

from cached_property import cached_property


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

        Keyword arguments
        -----------------
        color: str
            Layer that corresponds to color aesthetic.
        background: str
            Layer that corresponds to background.
        ...

        color_value: str
            The alternative value for the color.
        background_value: str
            The background value for the color.
        """
        assert_legal_arguments(kwargs)
        self.__aesthetics, self.__values = parse_arguments(kwargs)

    @cached_property
    def aesthetics(self):
        """Mapping of aesthetics mapped to layers."""
        return self.__aesthetics

    @cached_property
    def values(self):
        """Mapping of aesthetic values."""
        return self.__values

    @cached_property
    def css(self):
        """Get the CSS of the PrettyPrinter."""
        css_list = []
        print(self.values)
        for tag, value in css_layers.items():
            mark_css = get_mark_css(tag, value)
            css_list.append(mark_css)
        return "\t\t"+'\n'.join(css_list)

    def render(self, text):
        html = mark_text(text, self.aesthetics, self.values)
        alist = []
        alist.append(HEADER)
        alist.append(self.css)
        alist.append(MIDDLE + "\t\t\t" + html)
        alist.append("\n\t\t" + "<\p>")
        alist.append("\n" + FOOTER)
        print("".join(alist))
        return html
