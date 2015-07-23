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


class PrettyPrinter(object):
    """Class for formatting Text instances as HTML & CSS."""

    def __init__(self, **kwargs):
        self.text = kwargs['text']
        self.list = kwargs # TODO: self.list asemel võiks olla self.kwargs
        # TODO: ülesande 2.a (aesteetikute ja kihtide mappingu parsimine) võiks enne edasi liikumist
        # valmis teha, kuna see aitab läbi mõelda kuidas koodi paremini struktureerida

        # TODO: HEADER ja FOOTER lihtsuse mõttes tõsta klassist välja mooduli tasemele või
        # isegi eraldi moodulisse, näiteks teha moodul nimega templates.py ja sealt need importida
        self.HEADER = """<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="prettyprinter.css">
        <meta charset="utf-8">
        <title>PrettyPrinter</title>
    </head>
    <body>\n"""
        self.FOOTER = """\t</body>\n</html>"""
        # TODO: return pole vajalik kuna vaikimisi ilma returnita meetodid alati väljastavad None
        # (sama tähelepanek ka allpool olevate meetodite kohta)
        return

    def render(self, text):
        #Jagamiseks kasutan praegu jsoni infot, kui tahan hiljem lisada kihi vormingu, siis selle plaanin htmli kihis eraldi ifiga välja tuua
        # TODO: tähelepanek, et siin meetodis tuleb kindlasti abstraheerida konkreetsed kihid
        text = Text(text)
        file_json = text.get.word_texts.lemmas.postag_descriptions.as_dict
        # print(file_json)
        temporary = file_json['postag_descriptions']
        # TODO: märgendamine võiks töötada kihtide start/end positsioonide peal.
        # kuigi sõnatasemel on praegune näide küll lihtsam, siis üld
        descriptions = list(set(temporary))
        dictionary = {}
        for el in range(0,len(descriptions),1):
            try:
                asi = kwargs[descriptions[el]]
            except KeyError:
                asi = {}
            dictionary[descriptions[el]] = asi
        self.properties = dictionary
        # TODO: render meetod peaks väljastama stringi HTML sisuga, põhimõtteliselt mida createHTMl teeb,
        # aga ilma eraldi faili kirjutamata
        return text.get.word_texts.lemmas.postag_descriptions.as_dict

    @property
    def css(self):
        """The CSS of the prettyprinter"""
        rendered = self.render(self.text)
        # TODO: märkus, css renderdamine ei tohiks sõltuda tekstist
        postags = list(set(rendered['postag_descriptions']))
        #cssContent on nö base values, miskipärast pidin backgroundi eraldi dubleerima, et see töötaks iga sõnatüübi juures
        # TODO: suured eeldefineeritud mallid/tekstiblokid võiks tõsta mooduli tasemele või eraldi moodulisse (nt templates.py)
        cssContent = """p {
    color: black;
    background-color: white;
    font-family: "Times New Roman", Times, serif;
    font-weight: normal;
    font-style: normal;
    text-decoration: none;
    font-size: 30px;
    letter-spacing: 2px;
    }\n"""
        #Erinevad fonti suuruse ja tähevahede väärtused vastavalt small, normal ja large
        font = {'small':'20', 'normal':'30', 'large':'40'}
        spacing = {'small':'1', 'normal':'2', 'large':'4'}

        #siin genereeritakse kõik erinevad mark tüübi väärtused. Näeb natukene ebaotstarbekas välja, kuid katab 100% juhtudest.
        #Kui sul on ettepanekuid parendamiseks, siis ootan huviga
        # TODO: kas try/except on IndexErrori tuvastamiseks?
        # sel juhul võib teha seda if direktiiviga, nt
        # if el in postags:
        #      cssContent ...
        # või default väärtuse saamiseks kasutada
        #    mydict.get('key', default_value)

        # TODO: += stringide liitmisel võiks asendada stringIO klassiga või siis
        # panna stringi osad listi ning kasutada join meetodit nende ühendamiseks.
        # += teeb iga kord tervest juba koostatud sõnest koopia ning on ebaefektiivne
        for el in range(len(postags)):
            try:
                cssContent += 'mark.'+postags[el]+' {\n'
            except:
                pass
            try:
                cssContent += '\tcolor: '+self.properties[postags[el]]['color']+';\n'
            except:
                pass
            try:
                cssContent += '\tbackground-color: '+self.properties[postags[el]]['background']+';\n'
            except:
                cssContent += '\tbackground-color: white;\n'
            try:
                cssContent += '\tfont-family: "Times New Roman", Times, '+self.properties[postags[el]]['font']+';\n'
            except:
                pass
            try:
                cssContent += '\tfont-weight: '+self.properties[postags[el]]['weight']+';\n'
            except:
                pass
            try:
                cssContent += '\tfont-style: '+self.properties[postags[el]]['weight']+';\n'
            except:
                pass
            try:
                cssContent += '\ttext-decoration: '+self.properties[postags[el]]['underline']+';\n'
            except:
                pass
            try:
                cssContent += '\tfont-size: '+font[self.properties[postags[el]]['size']]+'px;\n'
            except:
                pass
            try:
                cssContent += '\tletter-spacing: '+spacing[self.properties[postags[el]]['spacing']]+'px;\n'
            except:
                pass
            cssContent += '}\n'

        file = open('prettyprinter.css', 'w')
        file.write(cssContent)
        file.close()
        return

    def createHTML(self):
        #Kogu vormistus on tehtud mark funktsiooni abil, kus erinevad sõnatüübid on mark.sõnatüüp abil kättesaadavad.
        #<stile> tüüpi vormistust ma ei kasutanud, kuna mark tundus otstarbekam(saab automaatselt genereerida igale sõnatüübile)
        # TODO: märkus. CSS klasside genereerimisel tuleb hiljem arvestada ka seda, et erinevad märgendused võivad kattuda,
        # näiteks teksti värv ja taustavärv. Selliste juhtude lahendamiseks peaks olema üks CSS klass iga aesteetik-väärtuse paari jaoks.

        # TODO: märkus. testimiseks ei pea faili kirjutamist tegema otse koodis, vaid võib ka lihtsalt trükkide ekraanile
        # sõne, ning käsurealt see suunata mõnda faili.

        rendered = self.render(self.text)
        words = rendered['word_texts']
        postags = rendered['postag_descriptions']
        htmlContent = "\t\t<p>\n"
        for el in range(len(words)):
            htmlContent += '\t\t\t<mark class=\"'+postags[el]+'\">'+words[el]+'</mark>\n'
        htmlContent += '\t\t</p>\n'
        file = open('prettyprinter.HTML', 'w')
        file.write(self.HEADER)
        file.write(htmlContent)
        file.write(self.FOOTER)
        file.close()
        self.css
        return

"""Current test protocols"""
#Testi koht, sellisel kujul peaks olema info sõnatüüpide ja nende vormingu kohta. Sel/järgmisel nädalal teen juurde funktsiooni, mis kasutaja info muudab selliseks dictionaryks
kwargs = {'text': "Mis siin  praegu siin toimub?", 'asesõna': {'color': 'red', 'size': 'large'},
          'tegusõna': {'color': 'green', 'background':'white', 'size': 'small'}}
p2 = PrettyPrinter(**kwargs)
p2Render = p2.render(p2.text)
p2.createHTML()

"""
#print(p2Render['word_texts'])
#print(p2Render['postag_descriptions'])
#print(p2.properties)

for tag in list(set(p2Render['postag_descriptions'])):
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
    exec("print(p2."+tag+".tracking)")"""
