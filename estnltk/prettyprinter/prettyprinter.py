# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.
Deals with rendering Text instances as HTML.
"""
from __future__ import unicode_literals, print_function, absolute_import

from .values import AESTHETICS, VALUES, AES_VALUE_MAP, DEFAULT_VALUE_MAP, LEGAL_ARGUMENTS
from .templates import get_mark_css
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

        Keyword arguments
        -----------------
        color: str
            Layer that corresponds to color aesthetic.
        background: str
            Layer that corresponds to background.
        ...

        color_value: str or list
            The alternative value for the color.
        background_value: str or list
            The background value for the color.
        """
        assert_legal_arguments(kwargs)
        self.__aesthetics, self.__values = parse_arguments(kwargs)
        self.__rules = dict((aes, create_rules(aes, values)) for aes, values in zip(self.aesthetics, self.values))

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
        """Get the CSS of the PrettyPrinter."""
        css_list = []
        for aes in self.aesthetics:
            css_list.extend(get_mark_css(aes, self.values[aes]))
        return '\n'.join(css_list)

    def render(self, text, add_header=False):
        # TODO: lisada boolean parameeter, millega saab headeri/footeri lisamist kontrollida
        # vaikimisi võiks kood headerit mitte lisada (nagu preagu lihtsalt return html)
        return mark_text(text, self.aesthetics)
        '''add_format = False
        html, css_layers = mark_text(text, self.aesthetics, self.values)
        final_content = []
        final_content.append(HEADER)
        final_content.append(self.css(css_layers))
        final_content.append(MIDDLE + "\t\t\t" + html)
        final_content.append("\n\t\t" + "</p>")
        final_content.append("\n" + FOOTER)
        #return "".join(final_content)
        if add_format == True:
            return "".join(final_content)
        else:
            return html'''

