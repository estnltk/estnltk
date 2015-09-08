======================================================================
Estnltk --- Open source tools for Estonian natural language processing
======================================================================
.. highlight:: python

Estnltk is a Python 2.7/Python 3.4 library for performing common language processing tasks in Estonian, funded by `Eesti Keeletehnoloogia Riiklik Programm`_ under the project `EKT57`_.
Estnltk is licensed under `GNU GPL version 2`_.

.. _Eesti Keeletehnoloogia Riiklik Programm: https://www.keeletehnoloogia.ee/
.. _EKT57: https://www.keeletehnoloogia.ee/et/ekt-projektid/estnltk-pythoni-teegid-eestikeelsete-vabatektside-lihtsamaks-tootlemiseks
.. _GNU GPL version 2: http://www.gnu.org/licenses/gpl-2.0.html

Quick example
=============

The best way to learn Estnltk is to start using it right away, so without further ado,
let's begin with an example on how to extract some morphological information from text and
display it as a nicely formatted `DataFrame`_ object::

    from estnltk import Text
    text = Text('Mine vanast raudteeülesõidukohast edasi ja pööra paremale, siis leiad Krokodilli!')
    text.get.word_texts.lemmas.postags.postag_descriptions.as_dataframe

::

                       word_texts               lemmas postags  postag_descriptions
    0                    Mine               minema       V             tegusõna
    1                  vanast                 vana       A  omadussõna algvõrre
    2   raudteeülesõidukohast  raudteeülesõidukoht       S             nimisõna
    3                   edasi                edasi       D             määrsõna
    4                      ja                   ja       J             sidesõna
    5                   pööra              pöörama       V             tegusõna
    6                paremale             paremale       D             määrsõna
    7                       ,                    ,       Z            lausemärk
    8                    siis                 siis       J             sidesõna
    9                   leiad               leidma       V             tegusõna
    10             Krokodilli            Krokodill       H            pärisnimi
    11                      !                    !       Z            lausemärk


Here is the same data as a dictionary::

    text.get.word_texts.lemmas.postags.postag_descriptions.as_dict

::

    {'lemmas': ['minema',
                'vana',
                'raudteeülesõidukoht',
                'edasi',
                'ja',
                'pöörama',
                'paremale',
                ',',
                'siis',
                'leidma',
                'Krokodill',
                '!'],
     'postag_descriptions': ['tegusõna',
                             'omadussõna algvõrre',
                             'nimisõna',
                             'määrsõna',
                             'sidesõna',
                             'tegusõna',
                             'määrsõna',
                             'lausemärk',
                             'sidesõna',
                             'tegusõna',
                             'pärisnimi',
                             'lausemärk'],
     'postags': ['V', 'A', 'S', 'D', 'J', 'V', 'D', 'Z', 'J', 'V', 'H', 'Z'],
     'word_texts': ['Mine',
                    'vanast',
                    'raudteeülesõidukohast',
                    'edasi',
                    'ja',
                    'pööra',
                    'paremale',
                    ',',
                    'siis',
                    'leiad',
                    'Krokodilli',
                    '!']}

.. _DataFrame: http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.html

About
=====

In recent years, several major NLP components for Estonian have become available under free open source licenses, which is an important milestone in Estonian NLP domain.

The goal of Estnltk is to become the main platform for Estonian NLP and glue together existing free components to make them easily usable.
Current situation requires the researchers to write their own interfaces to the tools, which can be very time-consuming
Also, a simple platform is a great resource for students who are interested in NLP domain.

The most important component is **vabamorf**, which is a C++ library for morphological analysis, disambiguation and synthesis [KA97]_.
For named entity recognition, **Estner library** provides necessary code and also a valuable training dataset, which is required for training the default models that come with the software [TK13]_.
Estnltk also includes **temporal time expression** (TIMEX) library [OR12]_.
The de facto library for NLP in English, the **NLTK toolkit** is also a dependency [BI06]_.

In addition to providing an API that is simple to use for software developers, Estnltk also aims to be useful for language researches and linguists in general.
The library is used to create tools for sentiment analysis, text classification and information extraction, which requires no programming knowledge once they are set up.
Including useful tools is a major goal in the future of Estnltk. See https://github.com/estnltk/ for a list of tools available.

.. [KA97] Kaalep, Heiki-Jaan. *"An Estonian morphological analyser and the impact of a corpus on its development."* Computers and the Humanities 31, no. 2 (1997): 115-133.
.. [TK13] Tkachenko, Alexander; Petmanson, Timo; Laur, Sven. *"Named Entity Recognition in Estonian."* ACL 2013 (2013): 78.
.. [OR12] Orasmaa, Siim. *"Automaatne ajaväljendite tuvastamine eestikeelsetes tekstides."* Eesti Rakenduslingvistika Ühingu aastaraamat 8 (2012): 153-169.
.. [BI06] Bird, Steven. *"NLTK: the natural language toolkit."* In Proceedings of the COLING/ACL on Interactive presentation sessions, pp. 69-72. Association for Computational Linguistics, 2006.


Tutorials
=========

.. toctree::
   :maxdepth: 3

   tutorials/installation
   tutorials/text
   tutorials/disambiguation
   tutorials/ner
   tutorials/prettyprinter
   tutorials/grammar
   tutorials/wikipedia
   tutorials/tei
   tutorials/database
   tutorials/devel
   tutorials/morf_tables

Tools for linguists
-------------------

.. toctree::
   :maxdepth: 3
   
   tutorials/textclassifier


API reference
=============

.. toctree::
   :maxdepth: 1

   api/clausesegmenter
   api/core
   api/ner
   api/teicorpus
   api/text
   api/textcleaner
   api/timex
   api/vabamorf
   api/wordnet_tagger
   api/wn

