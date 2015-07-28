# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'
import re
from .wikiextra import balancedSlicer
section = {'title': 'Nimi', 'text': "[[File:example.jpg|frameless|border|caption]]\n[[Pilt:Darius I the Great's inscription.jpg|pisi|[[Dareios I|Dareios I]] [[Behistuni raidkiri]], millel mainitakse Armeeniat. [[6. sajand eKr]].]] Kohanimi &quot;Armeenia&quot; pärineb [[Armeenia mägismaa]]l praeguse [[Malatya]] lähedal paiknenud piirkonna ''Armi-'' [[hurri keel|hurrikeelsest]] nimest. [[Aramea keeled|Aramea]] kuju ''ˊarmǝn-āiē'' [[File:shiitaaku.jpg|frameless|border|caption]] vahendusel läks [[File:shiitaaku.jpg|frameless|border|caption]] see üle [[vanapärsia keel]]de ning esineb [[lokatiiv]]ivormis\n''Arminiyaiy'' kuus korda[[File:shiiccctaaku.jpg|frameless|border|caption]] [[Behistuni raidkiri|Behistuni raidkirjal]] [[6. sajand eKr|6. sajandist eKr]].&lt;ref&gt;R. Schmitt. [http://www.iranica.com/articles/armenia-i ARMENIA and IRAN i. Armina, Achaemenid province.], ''Encyclopædia Iranica'', arhiveeritud aadressil [http://www.webcitation.org/659qWLMs7]&lt;/ref&gt; Teistel andmetel on see nimi moodustatud Armeenia mägismaal elanud rahva armeenide (''arim'') nimest.&lt;ref name='Pospelov'&gt;[[Jevgeni Pospelov|Поспелов Е. М.]] ''Географические названия мира: Топонимический словарь'', М.: Русские словари 1998, lk 160, ISBN 5-89216-029-7&lt;/ref&gt;. [[Vanakreeka keel]]es võttis nimi kuju Ἀρμενία&lt;ref&gt;Фасмер М. [http://dic.academic.ru/dic.nsf/vasmer/35265/армения ''Этимологический словарь русского языка'', [[Progress|Прогресс]] 1964, kd 1, lk 87: &quot;Арме́ния, vanakreeks sõnast Ἀρμενία. Juba vanapärsia ''Armaniya-'', ''Armina-'' 'Armeenia'; vt Бартоломэ, Air. Wb. 197; Хюбшман, IF 16, 205. Vt армяни́н.''&lt;/ref&gt;. Seda nime mainis esmakordselt [[Hekataios]] Mileetoselt.\n\n [[File:Gamma phage.png|pisi|[[Bakteriofaagid]]e hulka kuuluv [[viirus]]]] Enne nime Ἀρμένιοι levikut kitsuti [[armeenlased|armeenlasi]] vanakreeka keeles Μελιττήνιοι&lt;ref name=&quot;Дьяконов1981&quot;/&gt;.\n\nArmeenia [[armeenia keel|armeeniakeelne]] nimi on Հայք (''Hajkh''). [[5. sajand]]i ajaloolase [[Movses Khorenatsi]] järgi andis selle Armeenia legendaarne patriarh [[Hajk]], kelle järglase [[Aram]]i, [[Urartu]] kuninga nimest sündis omakorda nimi ''Armeenia''.&lt;ref&gt;[http://www.vehi.net/istoriya/armenia/khorenaci/01.html Мовсес Хоренаци &quot;История Армении&quot;], arhiveeritud [http://www.webcitation.org/659qX7URz]&lt;/ref&gt; Legendi järgi lõi Hajk [[2492 eKr]] lahingus [[Assüüria]] kuningat [[Bel]]i ning hiljem moodustas esimese Armeenia riigi. See aasta on [[vanaarmeenia ajaarvamine|Vanaarmeenia ajaarvamise]] algusaasta. [[File:example.jpg|frameless|border|caption]] Teine versioon seostab seda nimetust [[Ḫajaša]] riigiga&lt;ref&gt;Hrach K. Martirosyan. ''Etymological dictionary of the Armenian inherited lexicon'', Brill Academic Publishers 2009, lk 382–385, ISBN 978-90-04-17337-8&lt;/ref&gt;. Kolmanda versiooni järgi pärineb see praeguse [[Malatya]] [[urartu keel|urartukeelsest]] nimest ''Ḫāti''&lt;ref name=&quot;Дьяконов1981&quot;&gt;[[Igor Djakonov|Дьяконов И. М.]] ''Малая Азия и Армения около 600 г. до н.э. и северные походы вавилонских царей''. – ''[[Vestnik Drevnei Istorii|Вестник древней истории]]'', 1981, nr 2, lk 34—63.&lt;/ref&gt;&lt;ref&gt;A. E. Redgate. ''The Armenians'', Oxford: Blackwell 1998, lk  24, ISBN 0-631-14372-6&lt;/ref&gt;.\n\nKeskajal asendus armeenia kohanimejärelliide ''-kh'' pärsia keelest laenatud järelliitega ''[[-stan]]''.&lt;ref&gt;Капанцян Г. ''Хайаса--колыбель армян: этногенез армян и их начальная история'', Изд-во Академии наук Армянской ССР 1947, lk 10 [http://books.google.co.uk/books?id=HDRIAAAAMAAJ&amp;q=%5B%D1%85%D0%B0%D0%B9%D0%B0%D1%81%D1%82%D0%B0%D0%BD+%D1%81%D1%83%D1%84%D1%84%D0%B8%D0%BA%D1%81%5D&amp;dq=%5B%D1%85%D0%B0%D0%B9%D0%B0%D1%81%D1%82%D0%B0%D0%BD+%D1%81%D1%83%D1%84%D1%84%D0%B8%D0%BA%D1%81%5D&amp;source=bl&amp;ots=m1mrKyyoYt&amp;sig=Nja4qrhSWUqWYfSfvuMzMeqZETg&amp;hl=ru&amp;sa=X&amp;ei=uFIqUJqfDKKo0QWUiIEI&amp;redir_esc=y Google'i raamat]&lt;/ref&gt; ja Armeeniat hakati kutsuma Հայաստան (''Hajastan'').\n"}
from pprint import pprint
from .internalLink import urlBegin, findBalanced, addIntLinks
from .externalLink import addExternalLinks, ExtLinkBracketedRegex
from .wikiextra import balancedSlicer
from .cleaner import dropSpans

imageRegEx = re.compile(r'\[\[(Pilt|File|Image)\:.+?\]\]', re.IGNORECASE)

def imageParser(sectionObj):
    """return a sectionObj with image data added
         [
       {
             image_url = "http://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/R%C3%B5uge_Suurj%C3%A4rv_2011_10.jpg/1024px-R%C3%B5uge_Suurj%C3%A4rv_2011_10.jpg"
             text: "Rõuge Suurjärv on Eesti sügavaim järv (38 m)."
             links: [ ...] // sama loogika nagu sektsiooni tasemel lingid.
             links: [ ...] // sama loogika nagu sektsiooni tasemel lingid.
       }
   ]"""
    text = ''
    lastEnd = 0
    ends = []
    text = sectionObj['text']
    imageStarts = [x.start() for x in imageRegEx.finditer(text)]
    if imageStarts:
        images =  []
        for start in imageStarts:

            imgText, end = balancedSlicer(text[start:])
            end = start + end
            ends.append(end)

            #imgText = image.group(0).replace('[[', '').replace(']]', '')
            img =  {'text':imgText}
            imgText = imgText.split('|')

            #t= imgText[-1].replace(']]', '')
            t = imgText[-1][:-2]
            url = urlBegin + imgText[0].replace(' ', '_').replace('[[', '')
            img['text'] = t
            img['url'] = url

            if ExtLinkBracketedRegex.search(t):
                img = addExternalLinks(img)

            intlinks = [x for x in findBalanced(t, openDelim='[[', closeDelim=']]')]

            if intlinks:
                img = addIntLinks(img)

            images.append(img)


        sectionObj['images'] = images
        spans = []
        for i, j in zip(imageStarts, ends):
            spans.append((i, j))

        sectionObj['text'] = dropSpans(spans, text)
    return sectionObj


if __name__ == '__main__':
    with open("armeenia.txt", encoding='utf-8') as f:
        data = f.read()

    print(imageParser({'text' : data}))

    """
    imageRegEx = re.compile(r'\[\[(Pilt|File)\:.+')
    imagesIter = imageRegEx.finditer(section['text'])
    imagesMatches = []
    for image in imagesIter:
        if ExtLinkBracketedRegex.search(v):
        pprint(image.group())
        imagetag = balancedSlicer(image.group())

        u = {}
        pieces = imagetag.split('|')
        #FIXME:brakes if links or options use |
        url = pieces[0][2:]
        text = pieces[-1][:-2]
        u['url'] = url
        u['text'] = text
        u['links'] = None
        #TODO:Links
        imagesMatches.append(u)
        print(imagetag)
        print(u)
    section['images'] = imagesMatches
    print(section)"""