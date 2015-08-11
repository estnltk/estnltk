# -*- coding: utf-8 -*-
"""
Estnltk prettyprinter module.

Deals with rendering Text instances as HTML.

TODO: ülesande 2.a jaoks teha unittestid
TODO: kuigi estnltk ise seda praegu 100% ei järgi, proovime koodi stiili teha
      Pythoni tavade järgi: https://www.python.org/dev/peps/pep-0008/
"""
from __future__ import unicode_literals, print_function, absolute_import

#import sys
#sys.path.insert(0, '/path/to/estnltk/prettyprinter')

from .values import AESTHETICS, AES_VALUE_MAP, DEFAULT_VALUE_MAP, LEGAL_ARGUMENTS
from .templates import get_mark_css

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
        for aes in self.aesthetics:
            mark_css = get_mark_css(aes, self.values[aes])
            css_list.append(mark_css)
        return '\n'.join(css_list)


"""
    @property
    def css(self):

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
"""

#pp = PrettyPrinter(background = 'annotations')
#pp.render(text)

# üks tähelepanek veel, et võiksid kasutada Pythoni koodistiili standarti:
# https://www.python.org/dev/peps/pep-0008/
#
# peamine erinevus on see, et meetodiNimed muutuvad meetodi_nimedeks
