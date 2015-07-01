# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.

Deals with rendering Text instances as HTML.
"""
from __future__ import unicode_literals, print_function, absolute_import

try:
    from StringIO import cStringIO as StringIO
except ImportError: # Py3
    from io import StringIO

try:
    from html import escape as htmlescape
except ImportError:
    from cgi import escape as htmlescape

from estnltk import Text

class PrettyPrinter(object):
    """Class for formatting Text instances as HTML & CSS."""
    def __init__(self, **kwargs):
        self.text = kwargs['text']
        self.list = kwargs
        return

    def render(self, text):
        text = Text(text)
        file_jason = text.get.word_texts.lemmas.postag_descriptions.as_dict
        temporary = file_jason['postag_descriptions']
        descriptions = list(set(temporary))
        print(descriptions)
        for el in range(0,len(descriptions),1):
            try:
                asi = kwargs[descriptions[el]]
            except KeyError:
                asi = {'color': 'black', 'background': 'white', 'font': 'serif', 'weight': 'normal','italics': 'normal',
                     'underline': 'normal', 'size': 'normal', 'tracking': 'normal'}
            exec("self."+descriptions[el]+" = wordType(**asi)")

        return text.get.word_texts.lemmas.postag_descriptions.as_dict

    @property
    def css(self):
        """The CSS of the prettyprinter."""
        return ''

class wordType(object):
    def __init__(self, **kwargs):
        variables = {'color': 'black', 'background': 'white', 'font': 'serif', 'weight': 'normal','italics': 'normal',
                     'underline': 'normal', 'size': 'normal', 'tracking': 'normal'}
        for k,v in kwargs.items():
            variables[k] = v
        self.color = variables['color']
        self.background = variables['background']
        self.font = variables['font']
        self.weight = variables['weight']
        self.italics = variables['italics']
        self.underline = variables['underline']
        self.size = variables['size']
        self.tracking = variables['tracking']
        return

"""Current test protocols"""

kwargs = {'text': "Mis siin  praegu siin toimub?", 'asesõna': {'color': 'red', 'size': 'large'},
          'tegusõna': {'color': 'green', 'size': 'small'}}
p2 = PrettyPrinter(**kwargs)
p2Render = p2.render(p2.text)
print(p2Render['postag_descriptions'])

for tag in p2Render['postag_descriptions']:
    print()
    print(tag)
    print()
    exec("print(p2."+tag+".color)")
    exec("print(p2."+tag+".background)")
    exec("print(p2."+tag+".font)")
    exec("print(p2."+tag+".weight)")
    exec("print(p2."+tag+".italics)")
    exec("print(p2."+tag+".underline)")
    exec("print(p2."+tag+".size)")
    exec("print(p2."+tag+".tracking)")