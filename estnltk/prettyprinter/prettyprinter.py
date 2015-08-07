# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.

Deals with rendering Text instances as HTML.

TODO: ülesande 2.a jaoks teha unittestid
TODO: kuigi estnltk ise seda praegu 100% ei järgi, proovime koodi stiili teha
      Pythoni tavade järgi: https://www.python.org/dev/peps/pep-0008/
"""
from __future__ import unicode_literals, print_function, absolute_import
#from estnltk.prettyprinter.templates import cssHeader, middle, header, footer

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
sys.path.insert(0, '/path/to/estnltk/prettyprinter')
import templates

# muutsin seda, sest sain importerrori:
#TODO from . import templates

# Parem on koodi käivitada estnltk juurkataloogist, nt.
# python -m estnltk.prettyprinter.prettyprinter
#
# siis pole tarvis sys.path muutujat muuta, mis pole ka alati hea mõte
# PyCharmis saab ka run configurationis seda teha kui working directory panna estnltk juureks
# ning käivitamise käsk anna -m argumendina. Ainus puudus, et nii ei saa debugida.

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
        cssList.append(templates.cssHeader())

        for key, value in self.kwargs.items():
            cssTemporary = StringIO()

            if key == 'color':
                cssTemporary.write('mark.'+key+' {\n\tcolor: '+templates.safe_get(textFormat[value], key, 'default value')+';\n')
            elif key == 'background':
                cssTemporary.write('mark.'+key+' {\n\tbackground-color: '+templates.safe_get(textFormat[value], key, 'default value')+';\n')
            elif key == 'font':
                cssTemporary.write('mark.'+key+' {\n\tfont-family: '+templates.safe_get(textFormat[value], key, 'default value')+';\n')
            elif key == 'weight':
                cssTemporary.write('mark.'+key+' {\n\tfont-weight: '+templates.safe_get(textFormat[value], key, 'default value')+';\n')
            elif key == 'italics':
                cssTemporary.write('mark.'+key+' {\n\tfont-style: '+templates.safe_get(textFormat[value], key, 'default value')+';\n')
            elif key == 'underline':
                cssTemporary.write('mark.'+key+' {\n\tfont-decoration: '+templates.safe_get(textFormat[value], key, 'default value')+';\n')
            elif key == 'size':
                cssTemporary.write('mark.'+key+' {\n\tfont-size: '+font[templates.safe_get(textFormat[value], key, 'default value')]+';\n')
            elif key == 'tracking':
                cssTemporary.write('mark.'+key+' {\n\tletter-spacing: '+spacing[templates.safe_get(textFormat[value], key, 'default value')]+';\n')
            cssTemporary.write('}\n')
            cssList.append(cssTemporary.getvalue())
            cssTemporary.close()
        cssContent = "\n".join(cssList)
        return cssContent

    def create_html(self, inputText):
        text = Text(inputText['text'])
        annots = []

        for el in inputText:
            if el != 'text' and el!= 'textFormat':
                annots.append(el)
        global textFormat

        textFormat = inputText['textFormat']
        letters = list(inputText['text'])
        htmlContent = StringIO()
        htmlContent.write(templates.header())
        htmlContent.write(self.css)
        htmlContent.write(templates.middle())
        text.tokenize_words()

        a = "\t\t\t<mark"
        b = "\t\t\t<mark>"
        temporaryValue = []
        stringBeingWritten = ""
        helpfulDictionary = {}
        element = 0

        for el in annots:
            for occurrance in range(len(inputText[el])):
                while element < len(letters):
                    if element >= inputText[el][occurrance]['start'] and element <= inputText[el][occurrance]['end']:
                        if helpfulDictionary.get(element, 'pass') != 'pass':
                            for previousValue in helpfulDictionary[element]:
                                temporaryValue.append(previousValue)
                            temporaryValue.append(el)
                            helpfulDictionary[element] = temporaryValue
                            temporaryValue = []
                        else:
                            temporaryValue.append(el)
                            helpfulDictionary[element] = temporaryValue
                            temporaryValue = []
                    element += 1
                element = 0
        print(helpfulDictionary)

        while element < len(letters):
            if element in helpfulDictionary:
                a += ' class="'
                for property in helpfulDictionary[element]:
                    for key, value in self.kwargs.items():
                        if value ==property:
                            a += key + ' '
                a = a[:len(a)-1] + '">'
                htmlContent.write(a)
                a = "\t\t\t<mark"
                while True:
                    stringBeingWritten += letters[element]
                    if element + 1 in helpfulDictionary and helpfulDictionary[element] == helpfulDictionary[element + 1]:
                        element += 1
                    else:
                        stringBeingWritten += '</mark>\n'
                        htmlContent.write(stringBeingWritten)
                        stringBeingWritten = ""
                        break
                element += 1
            else:
                htmlContent.write(b)
                while True:
                    stringBeingWritten += letters[element]
                    if element + 1 not in helpfulDictionary:
                        element += 1
                    else:
                        stringBeingWritten += '</mark>\n'
                        htmlContent.write(stringBeingWritten)
                        stringBeingWritten = ""
                        break
                element += 1

        htmlContent.write('\t\t</p>\n')
        htmlContent.write(templates.footer())
        content = htmlContent.getvalue()
        htmlContent.close()

        return content

    def render(self, inputText):
        # TODO: tähelepanek, et siin meetodis tuleb kindlasti abstraheerida konkreetsed kihid
        content = StringIO()
        content.write(self.create_html(inputText))
        html = content.getvalue()
        content.close()
        print(html)
"""
    def create_HTML(self, inputText):
        # TODO: märkus. CSS klasside genereerimisel tuleb hiljem arvestada ka seda, et erinevad märgendused võivad kattuda, näiteks teksti värv ja taustavärv. Selliste juhtude lahendamiseks peaks olema üks CSS klass iga aesteetik-väärtuse paari jaoks.
        text = Text(inputText['text'])
        annots = []
        for el in inputText:
            if el != 'text' and el!= 'textFormat':
                annots.append(el)
        global textFormat
        textFormat = inputText['textFormat']

        letters = list(inputText['text'])
        print(letters)

        htmlContent = StringIO()
        htmlContent.write(templates.header())
        htmlContent.write(self.css)
        htmlContent.write(templates.middle())
        text.tokenize_words()

        a = "\t\t\t<mark"
        b = "\t\t\t<mark>"
        writtenMarked = False
        tempBoolean = False
        el=0
        temporaryHTML = ""
        previous = ""
        breakVariable = False

        while el < len(letters):
            for annot in annots:
                if breakVariable == True:
                    breakVariable = False
                    break
                for nr in range(len(inputText[annot])):
                    if el >= len(letters):
                        breakVariable = True
                        break
                    if el >= inputText[annot][nr]['start'] and el <= inputText[annot][nr]['end']:
                        while el <= inputText[annot][nr]['end'] and el < len(letters):
                            if annot != previous:
                                for key, value in self.kwargs.items():
                                    if value == annot:
                                        a+=' class=\"'+key+'\"'+', '
                                a = a[:-2]
                                htmlContent.write(a + '>' + letters[el])
                                previous = annot
                                writtenMarked = True
                                el += 1
                            else:
                                htmlContent.write(letters[el])
                                el += 1
                    else:
                        if nr == len(inputText[annot])-1:
                            if writtenMarked == True:
                                writtenMarked =False
                                htmlContent.write('</mark>\n')
                            if previous != 'null':
                                htmlContent.write(b + letters[el])
                            else:
                                htmlContent.write(letters[el])
                        el += 1
        htmlContent.write('\t\t</p>\n')
        htmlContent.write(templates.footer())
        content = htmlContent.getvalue()
        htmlContent.close()

        return content
"""

text = Text({
    'text': 'Selles tekstis on mitu märgendust, üks siin ja teine on siin',
    'annotations': [
        {'start': 35,
         'end': 43},
        {'start': 47,
         'end': 60
         }
    ],
    'word': [
        {'start': 0,
        'end': 5
        }
    ],
    'textFormat': {'annotations':
        {'background': 'blue'},
        'word': {'weight': 'bold'}
    }
})

pp = PrettyPrinter(background = 'annotations', weight = 'word')
pp.render(text)

# üks tähelepanek veel, et võiksid kasutada Pythoni koodistiili standarti:
# https://www.python.org/dev/peps/pep-0008/
#
# peamine erinevus on see, et meetodiNimed muutuvad meetodi_nimedeks