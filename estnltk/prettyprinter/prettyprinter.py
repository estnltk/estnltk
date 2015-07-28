# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.

Deals with rendering Text instances as HTML.

TODO: ülesande 2.a jaoks teha unittestid
TODO: kuigi estnltk ise seda praegu 100% ei järgi, proovime koodi stiili teha
      Pythoni tavade järgi: https://www.python.org/dev/peps/pep-0008/
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
import sys
sys.path.insert(0, '/path/to/estnltk/estnltk/prettyprinter')
import Templates

class PrettyPrinter(object):
    """Class for formatting Text instances as HTML & CSS."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        # TODO: ülesande 2.a (aesteetikute ja kihtide mappingu parsimine) võiks enne edasi liikumist valmis teha, kuna see aitab läbi mõelda kuidas koodi paremini struktureerida

    @property
    def css(self):
        """The CSS of the prettyprinter"""

        font = {'small':'20', 'normal':'30', 'large':'40'}
        spacing = {'small':'1', 'normal':'2', 'large':'4'}

        cssList = []
        cssList.append(Templates.CssHeader())

        for el in self.kwargs:
            cssTemporary = StringIO()
            if el == 'color':
                cssTemporary.write('mark.'+el+' {\n\tcolor: '+self.kwargs.get(el, 'default value')+';\n')
            elif el == 'background':
                cssTemporary.write('mark.'+el+' {\n\tbackground-color: '+self.kwargs.get(el, 'default value')+';\n')
            elif el == 'font':
                cssTemporary.write('mark.'+el+' {\n\tfont-family: '+self.kwargs.get(el, 'default value')+';\n')
            elif el == 'weight':
                cssTemporary.write('mark.'+el+' {\n\tfont-weight: '+self.kwargs.get(el, 'default value')+';\n')
            elif el == 'italics':
                cssTemporary.write('mark.'+el+' {\n\tfont-style: '+self.kwargs.get(el, 'default value')+';\n')
            elif el == 'underline':
                cssTemporary.write('mark.'+el+' {\n\tfont-decoration: '+self.kwargs.get(el, 'default value')+';\n')
            elif el == 'size':
                cssTemporary.write('mark.'+el+' {\n\tfont-size: '+font[self.kwargs.get(el, 'default value')]+';\n')
            elif el == 'tracking':
                cssTemporary.write('mark.'+el+' {\n\tletter-spacing: '+spacing[self.kwargs.get(el, 'default value')]+';\n')
            cssTemporary.write('}\n')
            cssList.append(cssTemporary.getvalue())
            cssTemporary.close()
        cssContent = "\n".join(cssList)
        return cssContent

    def createHTML(self, text):
        # TODO: märkus. CSS klasside genereerimisel tuleb hiljem arvestada ka seda, et erinevad märgendused võivad kattuda, näiteks teksti värv ja taustavärv. Selliste juhtude lahendamiseks peaks olema üks CSS klass iga aesteetik-väärtuse paari jaoks.

        originalValue = str(text)
        htmlContent = StringIO()
        htmlContent.write(Templates.Header())
        htmlContent.write(self.css)
        htmlContent.write(Templates.Middle())
        text.tokenize_words()

        a="\t\t\t<mark "

        for key in self.kwargs:
            a+='class=\"'+key+'\"'+', '
        a = a[:-2]

        for el in range(len(text['words'])):
            htmlContent.write(a+'>'+originalValue[text['words'][el]['start']:text['words'][el]['end']]+'</mark>\n')

        htmlContent.write('\t\t</p>\n')
        htmlContent.write(Templates.Footer())
        content = htmlContent.getvalue()
        htmlContent.close()

        return content

    def render(self, inputText):
        # TODO: tähelepanek, et siin meetodis tuleb kindlasti abstraheerida konkreetsed kihid
        text = Text(inputText)
        content = StringIO()
        content.write(self.createHTML(text))
        html = content.getvalue()
        content.close()
        print(html)

a = PrettyPrinter(background = 'Red', size = 'large')
PrettyPrinter.render(a, "Mis asi see siin on nüüd praegu?")