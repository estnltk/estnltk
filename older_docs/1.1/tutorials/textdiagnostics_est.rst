====================================
Sobimatute sümbolite tuvastamine
====================================

Sageli on enne tekstide töötlust tarvis kontrollida, kas need rahuldavad mingeid nõudeid.
Näiteks ei pruugi eesti keelt töötlevad rakendused osata analüüsida kirillitsas tekste, kuna eeldavad, et sisendtekst sisaldab vaid eesti keele tähemärke.
Seetõttu on tarvis kuidagi eristada analüüsitavaid tekste mitteanalüüsitavatest.

`Estnltk` klass :class:`estnltk.textdiagnostics.TextDiagnostics` võimaldab sisendteksti võrrelda eeldefineeritud lubatud sümbolite hulgaga, et tuvastada, kas potentsiaalselt võiks tegu olla mitteanalüüsitava tekstiga. 
Samuti pakub klass ülevaatet "probleemsetest" sümbolitest.


Eeldefineeritud sõnastikud
==========================

Moodul sisaldab järgmisi eeldefineeritud sõnastikke::

    >>> from estnltk.textdiagnostics import *
    >>> print (EST_ALPHA)
    abcdefghijklmnoprsšzžtuvõäöüxyzABCDEFGHIJKLMNOPRSŠZŽTUVÕÄÖÜXYZ
    >>> print (RUS_ALPHA)
    абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ
    >>> print (PUNCTUATION)
    !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~–
    >>> print (DIGITS)
    0123456789
    >>> WHITESPACE
    '\t\n\x0b\x0c\r '
    >>>

Samuti on moodulis eesti ja vene tähestikud, mis sisaldavad tühikuid, numbreid ja punktuatsiooni (`ESTONIAN` and `RUSSIAN`).
Lisaks leiduvad ka eraldi suur- ja väiketähti sisaldavad tähestikud eesti ja vene keelele: `EST_ALPHA_LOWER`, `EST_ALPHA_UPPER`, `RUS_ALPHA_LOWER`, `RUS_ALPHA_UPPER`.


Põhikasutus
===========

Vaikimisi kasutab :class:`estnltk.textdiagnostics.TextDiagnostics` klass eesti tähestikku, milles lisaks eesti tähtedele ka tühikud, numbrid ja punktuatsioon.
Meetodi `is_valid(text)` abil saab kontrollida, kas sisendsõne sisaldab vaid tähestikus olevaid sümboleid::

    >>> td = TextDiagnostics()
    >>> td.is_valid('Segan suhkrut malbelt tassis, kus nii armsalt aurab tee.')
    True
    >>> td.is_valid('Дождь, звонкой пеленой наполнил небо майский дождь.')
    False
    >>> td_ru = TextDiagnostics(RUSSIAN)
    >>> td_ru.is_valid('Дождь, звонкой пеленой наполнил небо майский дождь.')
    True


Ülevaade sobimatutest sümbolitest
===================================

Meetodi `report(texts, n_examples=10, context_size=10, f=sys.stdout)` abil saab analüüsida etteantud listis olevaid tekste ning leida, millised on sobimatud sümbolid. Meetod väljastab sobimatute sümbolite esinemissagedused ja -näited.

    >>> texts = ['Kokkuvõte ja soovitused: magada rahulikult.',
    ...          'Kokkuvōte ja soovitused: pole.',
    ...          'Diameeter ø 25cm',
    ...          'Mõōgad ja kilbid']
    >>> 
    >>> td.report(texts)
    Analyzed 4 texts.
    Invalid characters and their counts:
    "ō" 2
    "ø" 1
    For character "ō", found 2 occurrences.
    Examples:
    example 1: Kokkuvōte ja soo
    example 2: Mõōgad ja ki
    For character "ø", found 1 occurrences.
    Examples:
    example 1: Diameeter ø 25cm
