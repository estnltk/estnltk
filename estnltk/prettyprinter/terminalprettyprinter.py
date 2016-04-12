# -*- coding: utf-8 -*-
""" A Pretty-printer class that can be used for pre-formatting (annotated) text before printing to terminal. 
    Currently, allows to preformat only one layer at time;
"""
from __future__ import unicode_literals, print_function, absolute_import

from ..text import Text
from ..names import TEXT, START, END
from .extractors import texts_simple, texts_multi


def getANSIColoredFont( color ):
    ''' Returns an ANSI escape code (a string) corresponding to switching the font
        to given color, or None, if the given color could not be associated with 
        the available colors.
        
        See also:
          https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
          http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    '''
    color = (color.replace('-','')).lower()
    #
    #   Bright colors:
    #
    if color == 'white':
        return '\033[97m'
    elif color in ['cyan', 'aqua']:
        return '\033[96m'
    elif color in ['purple', 'magneta', 'fuchsia']:
        return '\033[95m'
    elif color == 'blue':
        return '\033[94m'
    elif color in ['yellow', 'gold']:
        return '\033[93m'
    elif color in ['green', 'lime']:
        return '\033[92m'
    elif color == 'red':
        return '\033[91m'
    #
    #   Dark colors:
    #
    elif color in ['grey', 'gray', 'silver']:
        return '\033[37m'
    elif color in ['darkcyan', 'teal']:
        return '\033[36m'
    elif color in ['darkpurple', 'darkmagneta']:
        return '\033[35m'
    elif color in ['darkblue', 'navy']:
        return '\033[34m'
    elif color in ['darkyellow', 'olive']:
        return '\033[33m'
    elif color == 'darkgreen':
        return '\033[32m'
    elif color in ['darkred', 'maroon']:
        return '\033[31m'
    return None


def preformat(text, layer, markup_settings):
    ''' Preformats given text, adding a special ( ANSI-terminal compatible ) markup
        to the text elements of given layer. The markup_settings specifies how the
        annotations of the layer should be formatted, and it currently supports the 
        following visualization options:
        * 'bracket' : True -- annotations will be surrounded with brackets; This works 
                              in any terminal;
        * 'underline' : True -- annotations will be underlined; This works in ANSI 
                              compatible terminal;
        * 'color' : ('red', 'green', 'blue' etc. ) -- annotated text will be displayed in
                              given color; this works in ANSI compatible terminal;
        The method returns preformatted text as a string;
        
        Parameters
        ----------
        text: Text
           a text object. must contain layer;
        layer: str
           name of the layer that needs to be visualised;
        markup_settings: dict
           dictionary with the user-defined markup settings;
        
        Returns
        -------
        text: str
           preformatted text, where elements of the given layer have been marked up, using 
           an ANSI-terminal compatible markup;
        
    '''
    if not markup_settings or not isinstance(markup_settings, dict):
       raise Exception('Error: markup_settings should be a dict containing markup specification;')
    
    # >>> The following code borrows from estnltk.prettyprinter.marker :
    # decide which extractor to use
    # first just assume we need to use a multi layer text extractor
    extractor = lambda t: texts_multi(t, layer)
    # if user has specified his/her own callable, use it
    if hasattr(layer, '__call__'):
        extractor = layer
    elif text.is_simple(layer):
        # the given layer is simple, so use simple text extractor
        extractor = lambda t: texts_simple(t, layer)
    tags = {}
    # >>> 
    
    for elem in extractor(text):
        if elem[START] not in tags:
           tags[ elem[START] ] = ''
        endExists = False
        if elem[END] not in tags:
           tags[elem[END]] = ''
        else:
           endExists = True
        # Make start tag
        graphicFormatting = False
        # -- Underlining
        if ('u' in markup_settings and markup_settings['u']) or \
           ('underline' in markup_settings and markup_settings['underline']):
           tags[elem[START]] += '\033[4m'
           graphicFormatting = True
        colorName = markup_settings['c'] if 'c' in markup_settings else None
        colorName = markup_settings['color'] if 'color' in markup_settings else colorName
        # -- Coloring
        if colorName:
           color = getANSIColoredFont( colorName )
           if color:
               graphicFormatting = True
               tags[elem[START]] += color
        # -- Bracketing
        add_brackets = False
        if ('b' in markup_settings and markup_settings['b']) or \
           ('bracket' in markup_settings and markup_settings['bracket']):
            tags[elem[START]] += '['
            add_brackets = True
        # Make end-tag
        if add_brackets:
           # end bracket
           if not endExists:
               tags[elem[END]] += ']'
           else:
               tags[elem[END]] = ']'+tags[elem[END]]
        if graphicFormatting:
           # end formatting (resets coloring, underlining, etc.)
           if not endExists:
               tags[elem[END]] += '\033[0m'  
           else:
               tags[elem[END]] = '\033[0m'+tags[elem[END]]
    return_str = []
    for i in range( len(text[TEXT]) ):
        c = text[TEXT][i]
        if i in tags:
           return_str.append( tags[i] )
        return_str.append( c )
    if len(text[TEXT]) in tags:
        return_str.append( tags[len(text[TEXT])] )
    return ''.join(return_str)

