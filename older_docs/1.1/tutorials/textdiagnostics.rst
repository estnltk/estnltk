====================================
Detecting invalid characters in text
====================================

Often, during preprocessing of text files, we wish to check if the files satisfy certain assumptions.
One such possible requirement is check if the files contain characters that can be handled by our application.
For example, an application assuming Estonian input might not work with Cyrillic characters.
In such cases, it is necessary to detect invalid input.

Estnltk provides :class:`estnltk.textdiagnostics.TextDiagnostics` class, that compares input texts against a predefined set of allowed characters.
The class can be used for detecting invalid input and also to provide basic overview of "wrong" characters.


Predefined alphabets
====================

The module contains some predefined alphabets that can be used::

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

There are also alphabets for Estonian and Russian (named respectively `ESTONIAN` and `RUSSIAN`) that include also whitespace, digits and punctuation.
There are also lowercase and uppercase variants containing just letters: `EST_ALPHA_LOWER`, `EST_ALPHA_UPPER`, `RUS_ALPHA_LOWER`, `RUS_ALPHA_UPPER`.


Basic usage
===========

The default alphabet of the :class:`estnltk.textdiagnostics.TextDiagnostics` class is Estonian additionally containing whitespace, digits and punctuation.
`is_valid(text)` method can be used to check, if the text contains only allowed characters in the alphabet::

    >>> td = TextDiagnostics()
    >>> td.is_valid('Segan suhkrut malbelt tassis, kus nii armsalt aurab tee.')
    True
    >>> td.is_valid('Дождь, звонкой пеленой наполнил небо майский дождь.')
    False
    >>> td_ru = TextDiagnostics(RUSSIAN)
    >>> td_ru.is_valid('Дождь, звонкой пеленой наполнил небо майский дождь.')
    True


Overview of invalid characters
==============================

The `report(texts, n_examples=10, context_size=10, f=sys.stdout)` method can be used to analyze a set of texts and print out the counts of invalid characters with examples.

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
