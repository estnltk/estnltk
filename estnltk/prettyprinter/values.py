# -*- coding: utf-8 -*-
"""This module defines various constants that are required by PrettyPrinter.
"""
from __future__ import unicode_literals, print_function, absolute_import


# here we define allowed aesthetics
COLOR = 'color'
BACKGROUND = 'background'
FONT = 'font'
WEIGHT = 'weight'
ITALICS = 'italics'
UNDERLINE = 'underline'
SIZE = 'size'
TRACKING = 'tracking'

# set of all aesthetics
AESTHETICS = {COLOR, BACKGROUND, FONT, WEIGHT, ITALICS, UNDERLINE, SIZE, TRACKING}

# here we define argument names for values that the user can give along with the aesthetics
COLOR_VALUE = 'color_value'
BACKGROUND_VALUE = 'background_value'
FONT_VALUE = 'font_value'
WEIGHT_VALUE = 'weight_value'
ITALICS_VALUE = 'italics_value'
UNDERLINE_VALUE = 'underline_value'
SIZE_VALUE = 'size_value'
TRACKING_VALUE = 'tracking_value'

# set of all aesthetic value arguments
VALUES = {COLOR_VALUE, BACKGROUND_VALUE, FONT_VALUE, WEIGHT_VALUE, ITALICS_VALUE, UNDERLINE_VALUE, SIZE_VALUE, TRACKING_VALUE}

# legal arguments that can be accepted by prettyprinter
LEGAL_ARGUMENTS = AESTHETICS | VALUES

# here we define mapping from aesthetic name to its value name that can be supplied by user
AES_VALUE_MAP = {
    COLOR: COLOR_VALUE,
    BACKGROUND: BACKGROUND_VALUE,
    FONT: FONT_VALUE,
    WEIGHT: WEIGHT_VALUE,
    ITALICS: ITALICS_VALUE,
    UNDERLINE: UNDERLINE_VALUE,
    SIZE: SIZE_VALUE,
    TRACKING: TRACKING_VALUE
}

# value to aesthetic mapping
VALUE_AES_MAP = dict((v, k) for k, v in AES_VALUE_MAP.items())

# here we define mapping from aesthetic names to actual CSS properties
AES_CSS_MAP = {
    COLOR: 'color',
    BACKGROUND: 'background-color',
    FONT: 'font-family',
    WEIGHT: 'font-weight',
    ITALICS: 'font-style',
    UNDERLINE: 'text-decoration',
    SIZE: 'font-size',
    TRACKING: 'letter-spacing'
}

# here we define default CSS property values
DEFAULT_VALUE_MAP = {
    COLOR: 'rgb(0, 0, 102)',
    BACKGROUND: 'rgb(102, 204, 255)',
    FONT: 'sans-serif',
    WEIGHT: 'bold',
    ITALICS: 'italic',
    UNDERLINE: 'underline',
    SIZE: '120%',
    TRACKING: '0.03em'
}