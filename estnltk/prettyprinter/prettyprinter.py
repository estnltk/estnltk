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

    def create_HTML(self, text, annotations):
        # TODO: märkus. CSS klasside genereerimisel tuleb hiljem arvestada ka seda, et erinevad märgendused võivad kattuda, näiteks teksti värv ja taustavärv. Selliste juhtude lahendamiseks peaks olema üks CSS klass iga aesteetik-väärtuse paari jaoks.

        annotations = annotations
        originalValue = str(text)
        htmlContent = StringIO()
        htmlContent.write(templates.header())
        htmlContent.write(self.css)
        htmlContent.write(templates.middle())
        text.tokenize_words()

        a = "\t\t\t<mark"

        for key in self.kwargs:
                a+=' class=\"'+key+'\"'+', '
        a = a[:-2]

        b = "\t\t\t<mark"
        written = False

        for el in range(len(text['words'])):
            for nr in range(len(annotations)):
                if text['words'][el]['start'] >= annotations[nr]['start'] and text['words'][el]['end'] <= annotations[nr]['end']:
                    htmlContent.write(a + '>' + originalValue[text['words'][el]['start']:text['words'][el]['end']] + '</mark>\n')
                    written = True
            if written == False:
                htmlContent.write(b + '>' + originalValue[text['words'][el]['start']:text['words'][el]['end']] + '</mark>\n')
            else:
                written = False

        htmlContent.write('\t\t</p>\n')
        htmlContent.write(templates.footer())
        content = htmlContent.getvalue()
        htmlContent.close()

        return content

    def render(self, inputText):
        # TODO: tähelepanek, et siin meetodis tuleb kindlasti abstraheerida konkreetsed kihid
        text = Text(inputText['text'])
        annotations = inputText['annotations']
        content = StringIO()
        content.write(self.create_HTML(text, annotations))
        html = content.getvalue()
        content.close()
        print(html)

text = Text({
    'text': 'Selles tekstis on mitu märgendust, üks siin ja teine on siin',
    'annotations': [
        {'start': 35,
         'end': 43},
        {'start': 47,
         'end': 60
         }
    ]
})

pp = PrettyPrinter(background = 'annotations')
pp.render(text)

# lihtne näide, mida ma ise silmas pidasin


#pp = PrettyPrinter(background='annotations')
#pp.render(text)

# tulemus peaks olema midagi sellist:
"""
...
<style>
    mark.background {
        background-color:blue;
    }
</style>
...
<p>
    Selles tekstis on mitu märgendust, <mark class="background">üks siin</mark> ja <mark class="background">teine on siin</mark>
</p>
...
"""

# üks tähelepanek veel, et võiksid kasutada Pythoni koodistiili standarti:
# https://www.python.org/dev/peps/pep-0008/
#
# peamine erinevus on see, et meetodiNimed muutuvad meetodi_nimedeks