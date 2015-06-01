========================
Working with text basics
========================

In this tutorial, we start with Estnltk basics and introduce you to the :py:class:`~estnltk.text.Text` class.
We will take the class apart to bits and pieces and put it back together to give a good overview, what it can do for you
and how can you work with it.

Getting started
===============

One of the most important classes in Estnltk is :py:class:`~estnltk.text.Text`, which is essentally the main interface
for doing everything Estnltk is capable of. It is actually a subclass of standard ``dict`` class in Python and stores
all data relevant to the text in this form::

    from estnltk import Text

    text = Text('Tere maailm!')
    print (repr(text))

::

    {'text': 'Tere maailm!'}


You can use :py:class:`~estnltk.text.Text` instances the same way as you would use a typical ``dict`` object in Python::

    print (text['text'])

::

    Tere maailm!

Naturally, you can initiate a new instance from a dictionary::

    text2 = Text({'text': 'Tere maailm!'})
    print (text == text2)

::

    True


As the :py:class:`~estnltk.text.Text` class is essentially a dictionary, it has a number of **advantages**:

* via JSON serialization, it is easy to store texts in databases, pass it easily around with HTTP GET/PUT commands,
* simple to inspect and debug,
* simple to extend and add new layers of annotations.

Main disadvantage is that the dictionary can get quite verbose, so space can be an issue when storing large corpora with many layers of annotations.

Layers
------

A :py:class:`~estnltk.text.Text` instance can have different types of layers that hold annotations or denote
special regions of the text.
For instance, ``words`` layer defines the word tokens, ``named_entities`` layer denotes the positions of named entities etc.

There are two types of layers:

1. **simple** layer has elements that only span a single region *such as words, sentences*.
2. **multi** layer has elements that can span several regions. For example, sentence
   *"Kõrred, millel on toitunud viljasääse vastsed, jäävad õhukeseks."* has two clauses:

   a. *"Korred jäävad õhukeseks"*,
   b. *", millel on toitunud viljasääse vastsed, "* .

   Clause (a) spans multiple regions in the original text.

Both types of layers require each layer element to define ``start`` and ``end`` attributes.
Simple layer elements define ``start`` and ``end`` as integers of the range containing the element.
Multi layer elements similarily define ``start`` and ``end`` attributes, but these are lists of
respective start and end positions of the element.

Simple layer::

    from estnltk import Text
    text = Text('Kõrred, millel on toitunud viljasääse vastsed, jäävad õhukeseks.')
    text.compute_words()
    text['words']

::

    [{'end': 6, 'start': 0, 'text': 'Kõrred'},
     {'end': 7, 'start': 6, 'text': ','},
     {'end': 14, 'start': 8, 'text': 'millel'},
     {'end': 17, 'start': 15, 'text': 'on'},
     {'end': 26, 'start': 18, 'text': 'toitunud'},
     {'end': 37, 'start': 27, 'text': 'viljasääse'},
     {'end': 45, 'start': 38, 'text': 'vastsed'},
     {'end': 46, 'start': 45, 'text': ','},
     {'end': 53, 'start': 47, 'text': 'jäävad'},
     {'end': 63, 'start': 54, 'text': 'õhukeseks'},
     {'end': 64, 'start': 63, 'text': '.'}]

Each word has a ``start`` and ``end`` attribute that tells, where the word is located in the text.
In case of multi layers, we see slightly different result::

    text.compute_clauses()
    text['clauses']

::

    [{'end': [6, 64], 'start': [0, 47]},
     {'end': [46], 'start': [6]}]

We see that first clause has two spans in the text.
Although the second clause has only one span, it is also defined as a multi layer element.
Estnltk uses *either* **simple** or **multi** type for a single layer.
However, nothing stops you from mixing these two, if you wish.

In next sections, we discuss typical NLP operations you can do with Estnltk and also explain, how the results are stored in the dictionary underneath the  :py:class:`~estnltk.text.Text` instances.

Tokenization
============

One of the most basic tasks of any NLP pipeline is text and sentence tokenization.
The :py:class:`~estnltk.text.Text` class has methods :py:func:`~estnltk.text.Text.compute_sentences` and :py:func:`~estnltk.text.Text.compute_words`,
which you can call to do this explicitly.
However, there are also properties :py:attr:`~estnltk.text.Text.word_texts` and
:py:attr:`~estnltk.text.Text.sentence_texts` that do this automatically when you use them and also
give you the texts of tokenized words or sentences::


    from estnltk import Text

    text = Text('Üle oja mäele, läbi oru jõele. Ämber läks ümber.')
    print (text.word_texts)

::

    ['Üle', 'oja', 'mäele', ',', 'läbi', 'oru', 'jõele', '.', 'Ämber', 'läks', 'ümber', '.']

In order for the tokenization to happen, :py:class:`~estnltk.text.Text` instance applies the default tokenizer in
background and updates the text data::

    from pprint import pprint
    pprint (text)

::

    {'sentences': [{'end': 30, 'start': 0}, {'end': 48, 'start': 31}],
     'text': 'Üle oja mäele, läbi oru jõele. Ämber läks ümber.',
     'words': [{'end': 3, 'start': 0, 'text': 'Üle'},
               {'end': 7, 'start': 4, 'text': 'oja'},
               {'end': 13, 'start': 8, 'text': 'mäele'},
               {'end': 14, 'start': 13, 'text': ','},
               {'end': 19, 'start': 15, 'text': 'läbi'},
               {'end': 23, 'start': 20, 'text': 'oru'},
               {'end': 29, 'start': 24, 'text': 'jõele'},
               {'end': 30, 'start': 29, 'text': '.'},
               {'end': 36, 'start': 31, 'text': 'Ämber'},
               {'end': 41, 'start': 37, 'text': 'läks'},
               {'end': 47, 'start': 42, 'text': 'ümber'},
               {'end': 48, 'start': 47, 'text': '.'}]}

As you can see, there is now a ``words`` element in the dictionary, which is a list of dictionaries denoting ``start``
and ``end`` positions of the respective words. You also see ``sentences`` element, because sentence tokenization is a prerequisite
before word tokenization and Estnltk did this automatically on your behalf.

The :py:attr:`~estnltk.text.Text.word_texts` property does basically the same as the following snippet::

    text = Text('Üle oja mäele, läbi oru jõele. Ämber läks ümber.')
    text.compute_words() # this method applies text tokenization
    print ([text['text'][word['start']:word['end']] for word in text['words']])

::

    ['Üle', 'oja', 'mäele', ',', 'läbi', 'oru', 'jõele', '.', 'Ämber', 'läks', 'ümber', '.']

Only difference is that by using :py:attr:`~estnltk.text.Text.word_texts` property twice does not perform tokenization twice.
Second call would use the ``start`` and ``end`` attributes already stored in the :py:class:`~estnltk.text.Text` instance.


The default word tokenizer is NLTK-s `WordPunctTokenizer`_::

    from nltk.tokenize.regexp import WordPunctTokenizer
    tok = WordPunctTokenizer()
    print (tok.tokenize('Tere maailm!'))

::

    ['Tere', 'maailm', '!']

.. _WordPunctTokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.regexp.WordPunctTokenizer


Also, the default sentence tokenizer comes from NLTK::

    import nltk.data
    tok = nltk.data.load('tokenizers/punkt/estonian.pickle')
    tok.tokenize('Esimene lause. Teine lause?')

::

    ['Esimene lause.', 'Teine lause?']

In order to plug in custom tokenization functionality, you need to implement interface defined by NLTK
`StringTokenizer`_ and supply them as keyword arguments when initiating :py:class:`~estnltk.text.Text`
objects. Of course, all other NLTK tokenizers follow this interface::

    from nltk.tokenize.regexp import WhitespaceTokenizer
    from nltk.tokenize.simple import LineTokenizer

    kwargs = {
        "word_tokenizer": WhitespaceTokenizer(),
        "sentence_tokenizer": LineTokenizer()
    }

    plain = '''Hmm, lausemärgid jäävad sõnade külge. Ja laused
    tuvastatakse praegu

    reavahetuste järgi'''

    text = Text(plain, **kwargs)
    print (text.word_texts)
    print (text.sentence_texts)

.. _StringTokenizer: http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.api.StringTokenizer

::

    # words
    ['Hmm,', 'lausemärgid', 'jäävad', 'sõnade', 'külge.', 'Ja', 'laused', 'tuvastatakse', 'praegu', 'reavahetuste', 'järgi']

    # sentences
    ['Hmm, lausemärgid jäävad sõnade külge. Ja laused', 'tuvastatakse praegu', '', 'reavahetuste järgi']


After both word and sentence tokenization, a :py:class:`~estnltk.text.Text` instance looks like this::

    {'sentences': [{'end': 47, 'start': 0},
                   {'end': 67, 'start': 48},
                   {'end': 68, 'start': 68},
                   {'end': 87, 'start': 69}],
     'text': 'Hmm, lausemärgid jäävad sõnade külge. Ja laused\n'
             'tuvastatakse praegu\n'
             '\n'
             'reavahetuste järgi',
     'words': [{'end': 4, 'start': 0, 'text': 'Hmm,'},
               {'end': 16, 'start': 5, 'text': 'lausemärgid'},
               {'end': 23, 'start': 17, 'text': 'jäävad'},
               {'end': 30, 'start': 24, 'text': 'sõnade'},
               {'end': 37, 'start': 31, 'text': 'külge.'},
               {'end': 40, 'start': 38, 'text': 'Ja'},
               {'end': 47, 'start': 41, 'text': 'laused'},
               {'end': 60, 'start': 48, 'text': 'tuvastatakse'},
               {'end': 67, 'start': 61, 'text': 'praegu'},
               {'end': 81, 'start': 69, 'text': 'reavahetuste'},
               {'end': 87, 'start': 82, 'text': 'järgi'}]}

This is the full list of tokenization related properties of :py:class:`~estnltk.text.Text`:

* :py:attr:`~estnltk.text.Text.text` - the text string itself
* :py:attr:`~estnltk.text.Text.words` - list of word dictionaries
* :py:attr:`~estnltk.text.Text.word_texts` - word texts
* :py:attr:`~estnltk.text.Text.word_starts` - word start positions
* :py:attr:`~estnltk.text.Text.word_ends` - word end positions
* :py:attr:`~estnltk.text.Text.word_spans` - word (start, end) position tuples
* :py:attr:`~estnltk.text.Text.sentence_texts` - list of sentence dictionaries
* :py:attr:`~estnltk.text.Text.sentence_texts` - list of sentence texts
* :py:attr:`~estnltk.text.Text.sentence_starts` - sentence start positions
* :py:attr:`~estnltk.text.Text.sentence_ends` - sentence end positions
* :py:attr:`~estnltk.text.Text.sentence_spans` - sentence (start, end) position pairs

Example::

    from estnltk import Text

    text = Text('Esimene lause. Teine lause')

    print (text.text)

    print (text.words)
    print (text.word_texts)
    print (text.word_starts)
    print (text.word_ends)
    print (text.word_spans)

    print (text.sentences)
    print (text.sentence_texts)
    print (text.sentence_starts)
    print (text.sentence_ends)
    print (text.sentence_spans)

Output::

    # text.text
    Esimene lause. Teine lause

    # text.words
    [{'end': 7, 'start': 0, 'text': 'Esimene'}, {'end': 13, 'start': 8, 'text': 'lause'}, {'end': 14, 'start': 13, 'text': '.'},
    {'end': 20, 'start': 15, 'text': 'Teine'}, {'end': 26, 'start': 21, 'text': 'lause'}]
    # text.word_texts
    ['Esimene', 'lause', '.', 'Teine', 'lause']
    # text.word_starts
    [0, 8, 13, 15, 21]
    # text.word_ends
    [7, 13, 14, 20, 26]
    # text.word_spans
    [(0, 7), (8, 13), (13, 14), (15, 20), (21, 26)]

    # text.sentences
    [{'end': 14, 'start': 0}, {'end': 26, 'start': 15}]
    # text.sentence_texts
    ['Esimene lause.', 'Teine lause']
    # text.sentence_starts
    [0, 15]
    # text.sentence_ends
    [14, 26]
    # text.sentence_spans
    [(0, 14), (15, 26)]

Note that if a dictionary already has ``words`` and ``sentences`` elements (or any other element that we introduce later),
accessing these elements in a newly initialized :py:class:`~estnltk.text.Text` object does not require
recomputing them::

    text = Text({'sentences': [{'end': 14, 'start': 0}, {'end': 27, 'start': 15}],
                 'text': 'Esimene lause. Teine lause.',
                 'words': [{'end': 7, 'start': 0, 'text': 'Esimene'},
                           {'end': 13, 'start': 8, 'text': 'lause'},
                           {'end': 14, 'start': 13, 'text': '.'},
                           {'end': 20, 'start': 15, 'text': 'Teine'},
                           {'end': 26, 'start': 21, 'text': 'lause'},
                           {'end': 27, 'start': 26, 'text': '.'}]})

    print (text.word_texts) # tokenization is already done, just extract words using the positions

::

    ['Esimene', 'lause', '.', 'Teine', 'lause', '.']

You should also remember this, when you have defined custom tokenizers. In such cases you can force retokenization by
calling :py:meth:`~estnltk.text.Text.compute_words` and :py:meth:`~estnltk.text.Text.compute_sentences`.

.. note:: Things to remember!

    1. ``words`` and ``sentences`` are **simple** layers.
    2. use properties to access the tokenized word/sentence texts and avoid :py:meth:`~estnltk.text.Text.compute_words` and :py:meth:`~estnltk.text.Text.compute_sentences`, unless you have a meaningful reason to use them.


Morphological analysis
======================

In linguistics, morphology is the identification, analysis, and description of the structure of a given language's morphemes and other linguistic units,
such as root words, lemmas, suffixes, parts of speech etc.
Estnltk wraps `Vabamorf`_ morphological analyzer, which can do both morphological analysis and synthesis.

.. _Vabamorf: https://github.com/Filosoft/vabamorf

Esnltk :py:class:`~estnltk.text.Text` class  properties for extracting morphological information:

* :py:attr:`~estnltk.text.Text.analysis` - raw analysis data.
* :py:attr:`~estnltk.text.Text.roots` - root forms of words.
* :py:attr:`~estnltk.text.Text.root_tokens` - for compound words, all the tokens the root is made of.
* :py:attr:`~estnltk.text.Text.lemmas` - dictionary (canonical) word forms.
* :py:attr:`~estnltk.text.Text.forms` - word form expressing the case, plurality, voice etc.
* :py:attr:`~estnltk.text.Text.endings` - word inflective suffixes.
* :py:attr:`~estnltk.text.Text.postags` - part-of-speech (POS) tags (word types).
* :py:attr:`~estnltk.text.Text.postag_descriptions` - Estonian descriptions for POS tags.
* :py:attr:`~estnltk.text.Text.descriptions` - Estonian descriptions for forms.


See :ref:`postag_table`, :ref:`nounform_table` and :ref:`verbform_table` for more detailed information.


Property aggregation
--------------------

Before we continue with morphological analysis, we introduce a way to put together various information in
a simple way.
Often you want to extract various information, such as words, lemmas, postags and put them together such that
you could easily access all of them.
Estnltk has :py:class:`~estnltk.text.ZipBuilder` class, which can compile together properties you need and then
format them in various ways.
First, you can initiate the builder on a Text object by calling :py:attr:`~estnltk.text.Text.get` attribute and
then chain together the attributes you wish to have.
Last step is telling the format you want the data to appear.

You can think of this process as building a sentence: **get <item_1> <item_2> ... <item_n> as <format>**.
Output formats include Pandas `DataFrame`_::

    from estnltk import Text
    text = Text('Usjas kaslane ründas künklikul maastikul tünjat Tallinnfilmi režissööri')
    text.get.word_texts.postags.postag_descriptions.as_dataframe

::

             word_texts postags  postag_descriptions
    0         Usjas       A  omadussõna algvõrre
    1       kaslane       S             nimisõna
    2        ründas       V             tegusõna
    3     künklikul       A  omadussõna algvõrre
    4     maastikul       S             nimisõna
    5        tünjat       A  omadussõna algvõrre
    6  Tallinnfilmi       H            pärisnimi
    7    režissööri       S             nimisõna

.. _DataFrame: http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.html

A list of tuples::

    text.get.word_texts.postags.postag_descriptions.as_zip

::

    [('Usjas', 'A', 'omadussõna algvõrre'),
     ('kaslane', 'S', 'nimisõna'),
     ('ründas', 'V', 'tegusõna'),
     ('künklikul', 'A', 'omadussõna algvõrre'),
     ('maastikul', 'S', 'nimisõna'),
     ('tünjat', 'A', 'omadussõna algvõrre'),
     ('Tallinnfilmi', 'H', 'pärisnimi'),
     ('režissööri', 'S', 'nimisõna')]

A list of lists::

    text.get.word_texts.postags.postag_descriptions.as_list

::

    [['Usjas',
      'kaslane',
      'ründas',
      'künklikul',
      'maastikul',
      'tünjat',
      'Tallinnfilmi',
      'režissööri'],
     ['A', 'S', 'V', 'A', 'S', 'A', 'H', 'S'],
     ['omadussõna algvõrre',
      'nimisõna',
      'tegusõna',
      'omadussõna algvõrre',
      'nimisõna',
      'omadussõna algvõrre',
      'pärisnimi',
      'nimisõna']]

A dictionary::

    text.get.word_texts.postags.postag_descriptions.as_dict

::

    {'postag_descriptions': ['omadussõna algvõrre',
                             'nimisõna',
                             'tegusõna',
                             'omadussõna algvõrre',
                             'nimisõna',
                             'omadussõna algvõrre',
                             'pärisnimi',
                             'nimisõna'],
     'postags': ['A', 'S', 'V', 'A', 'S', 'A', 'H', 'S'],
     'word_texts': ['Usjas',
                    'kaslane',
                    'ründas',
                    'künklikul',
                    'maastikul',
                    'tünjat',
                    'Tallinnfilmi',
                    'režissööri']}


All the properties can be given also as a list, which can be convinient in some situations::

    text.get(['word_texts', 'postags', 'postag_descriptions']).as_dataframe

::

         word_texts postags  postag_descriptions
    0         Usjas       A  omadussõna algvõrre
    1       kaslane       S             nimisõna
    2        ründas       V             tegusõna
    3     künklikul       A  omadussõna algvõrre
    4     maastikul       S             nimisõna
    5        tünjat       A  omadussõna algvõrre
    6  Tallinnfilmi       H            pärisnimi
    7    režissööri       S             nimisõna


.. note:: Estnltk does not stop the programmer doing wrong things

    You can chain together any :py:class:`~estnltk.text.Text` property, but only thing you must take care of is that
    all the properties act on same unit of data. So, when you mix sentence and word properties, you get either an error
    or malformed output.


Word analysis
-------------

After doing morphological analysis, ideally only one unambiguous dictionary containing all the raw data is generated.
However, sometimes the disambiguator cannot really eliminate all ambiguity and you get multiple analysis variants::

    from estnltk import Text
    text = Text('mõeldud')
    print (text.analysis)

::

    {'text': 'mõeldud',
     'words': [{'analysis': [{'clitic': '',
                              'ending': '0',
                              'form': '',
                              'lemma': 'mõeldud',
                              'partofspeech': 'A',
                              'root': 'mõel=dud',
                              'root_tokens': ['mõeldud']},
                             {'clitic': '',
                              'ending': '0',
                              'form': 'sg n',
                              'lemma': 'mõeldud',
                              'partofspeech': 'A',
                              'root': 'mõel=dud',
                              'root_tokens': ['mõeldud']},
                             {'clitic': '',
                              'ending': 'd',
                              'form': 'pl n',
                              'lemma': 'mõeldud',
                              'partofspeech': 'A',
                              'root': 'mõel=dud',
                              'root_tokens': ['mõeldud']},
                             {'clitic': '',
                              'ending': 'dud',
                              'form': 'tud',
                              'lemma': 'mõtlema',
                              'partofspeech': 'V',
                              'root': 'mõtle',
                              'root_tokens': ['mõtle']}],
                'end': 7,
                'start': 0,
                'text': 'mõeldud'}]}

The word "mõeldud" has quite a lot ambiguity as it can be interpreted either as a *verb* or *adjective*. Adjective
version itself can be though of as singular or plural and with different suffixes.

This ambiguity also affects how properties work.
In this case, there are two lemmas and when accessing :py:attr:`~estnltk.text.Text.lemmas` property, estnltk
displays both unique cases, sorted alphabetically and separated by a pipe::

    print (text.lemmas)
    print (text.postags)

::

    ['mõeldud|mõtlema']
    ['A|V']


Now, we have already seen that morphological data is added to word level dictionary under element ``analysis``. Let's also
look at a single analysis dictionary element for word "raudteejaamadelgi"::

    Text('raudteejaamadelgi').analysis

::

    {'clitic': 'gi', # In Estonian, -gi and -ki suffixes
     'ending': 'del', # word suffix without clitic
     'form': 'pl ad', # word form, in this case plural and adessive (alalütlev) case
     'lemma': 'raudteejaam', # the dictionary form of the word
     'partofspeech': 'S', # POS tag, in this case substantive
     'root': 'raud_tee_jaam', # root form (same as lemma, but verbs do not have -ma suffix)
                              # also has compound word markers and optional phonetic markers
     'root_tokens': ['raud', 'tee', 'jaam']} # for compund word roots, a list of simple roots the compound is made of


Human-readable descriptions
---------------------------

:py:class:`~estnltk.text.Text` class has properties :py:attr:`~estnltk.text.Text.postag_descriptions` and
:py:attr:`~estnltk.text.Text.descriptions`, which give Estonian descriptions respectively to POS tags and word forms::

    from estnltk import Text
    text = Text('Usjas kaslane ründas künklikul maastikul tünjat Tallinnfilmi režissööri')

    text.get.word_texts.postags.postag_descriptions.as_dataframe

::

    text.get.word_texts.postags.postag_descriptions.as_dataframe
         word_texts postags  postag_descriptions
    0         Usjas       A  omadussõna algvõrre
    1       kaslane       S             nimisõna
    2        ründas       V             tegusõna
    3     künklikul       A  omadussõna algvõrre
    4     maastikul       S             nimisõna
    5        tünjat       A  omadussõna algvõrre
    6  Tallinnfilmi       H            pärisnimi
    7    režissööri       S             nimisõna

::

    text.get.word_texts.forms.descriptions.as_dataframe

::

         word_texts  forms                                       descriptions
    0         Usjas   sg n                        ainsus nimetav (nominatiiv)
    1       kaslane   sg n                        ainsus nimetav (nominatiiv)
    2        ründas      s  kindel kõneviis lihtminevik 3. isik ainsus akt...
    3     künklikul  sg ad                        ainsus alalütlev (adessiiv)
    4     maastikul  sg ad                        ainsus alalütlev (adessiiv)
    5        tünjat   sg p                         ainsus osastav (partitiiv)
    6  Tallinnfilmi   sg g                          ainsus omastav (genitiiv)
    7    režissööri   sg p                         ainsus osastav (partitiiv)


Also, see :ref:`nounform_table`, :ref:`verbform_table` and :ref:`postag_table` that contains detailed information
with examples about the morphological attributes.

Analysis options & phonetic information
---------------------------------------

By default, estnltk does not add phonetic information to analyzed word roots, but this functionality can be changed.
Here are all the options that can be given to the :py:class:`~estnltk.text.Text` class that will affect the
analysis results:

* disambiguate: boolean (default: True)
    Disambiguate the output and remove incosistent analysis.
* guess: boolean (default: True)
     Use guessing in case of unknown words
* propername: boolean (default: True)
    Perform additional analysis of proper names.
* compound: boolean (default: True)
    Add compound word markers to root forms.
* phonetic: boolean (default: False)
    Add phonetic information to root forms.

::

    from estnltk import Text
    print (Text('tosinkond palki sai oma palga', phonetic=True, compound=False).roots)

::

    ['t?os]in~k<ond', 'p<al]k', 's<aa', 'oma', 'p<alk']


See :ref:`phonetic_markers` for more information.


Morphological synthesis
=======================

The reverse operation of morphological analysis is synthesis. That is, given the dictionary form of the word
and some options, generating all possible inflections that match given criteria.

Estnltk has function :py:func:`~estnltk.vabamorf.morf.synthesize`, which accepts these parameters:

1. word dictionary form (lemma).
2. word form (see :ref:`nounform_table` and :ref:`verbform_table`).
3. *(optional)* POS tag (see :ref:`postag_table`).
4. *(optional)* hint, essentially a prefix filter.

Let's generate plural genitive forms for lemma "palk" (in English a *paycheck* and a *log*)::

    from estnltk import synthesize
    synthesize('palk', 'pl g')

::

    ['palkade', 'palkide']


We can hint the synthesizer so that it outputs only inflections that match prefix *palka*::

    synthesize('palk', 'pl g', hint='palka')

::

    ['palkade']


For fun, here is some demo code for synthesizing all forms of any given noun (See :ref:`nounform_table`)::

    from estnltk import synthesize
    import pandas

    cases = [
        ('n', 'nimetav'),
        ('g', 'omastav'),
        ('p', 'osastav'),
        ('ill', 'sisseütlev'),
        ('in', 'seesütlev'),
        ('el', 'seestütlev'),
        ('all', 'alaleütlev'),
        ('ad', 'alalütlev'),
        ('abl', 'alaltütlev'),
        ('tr', 'saav'),
        ('ter', 'rajav'),
        ('es', 'olev'),
        ('ab', 'ilmaütlev'),
        ('kom', 'kaasaütlev')]

    def synthesize_all(word):
        case_rows = []
        sing_rows = []
        plur_rows = []
        for case, name in cases:
            case_rows.append(name)
            sing_rows.append(', '.join(synthesize(word, 'sg ' + case, 'S')))
            plur_rows.append(', '.join(synthesize(word, 'pl ' + case, 'S')))
        return pandas.DataFrame({'case': case_rows, 'singular': sing_rows, 'plural': plur_rows}, columns=['case', 'singular', 'plural'])

    synthesize_all('kuusk')

::

              case  singular             plural
    0      nimetav     kuusk             kuused
    1      omastav     kuuse           kuuskede
    2      osastav    kuuske  kuuski, kuuskesid
    3   sisseütlev  kuusesse        kuuskedesse
    4    seesütlev    kuuses          kuuskedes
    5   seestütlev   kuusest         kuuskedest
    6   alaleütlev   kuusele         kuuskedele
    7    alalütlev    kuusel          kuuskedel
    8   alaltütlev   kuuselt         kuuskedelt
    9         saav   kuuseks         kuuskedeks
    10       rajav   kuuseni         kuuskedeni
    11        olev   kuusena         kuuskedena
    12   ilmaütlev   kuuseta         kuuskedeta
    13  kaasaütlev   kuusega         kuuskedega

Let's try something funny as well::

    synthesize_all('luuslang-lendur')

^_^::

              case             singular                                       plural
    0      nimetav      luuslang-lendur                            luuslang-lendurid
    1      omastav     luuslang-lenduri                           luuslang-lendurite
    2      osastav    luuslang-lendurit                           luuslang-lendureid
    3   sisseütlev  luuslang-lendurisse  luuslang-lendureisse, luuslang-lenduritesse
    4    seesütlev    luuslang-lenduris      luuslang-lendureis, luuslang-lendurites
    5   seestütlev   luuslang-lendurist    luuslang-lendureist, luuslang-lenduritest
    6   alaleütlev   luuslang-lendurile    luuslang-lendureile, luuslang-lenduritele
    7    alalütlev    luuslang-lenduril      luuslang-lendureil, luuslang-lenduritel
    8   alaltütlev   luuslang-lendurilt    luuslang-lendureilt, luuslang-lenduritelt
    9         saav   luuslang-lenduriks    luuslang-lendureiks, luuslang-lenduriteks
    10       rajav   luuslang-lendurini    luuslang-lendureini, luuslang-lenduriteni
    11        olev   luuslang-lendurina    luuslang-lendureina, luuslang-lenduritena
    12   ilmaütlev   luuslang-lendurita                         luuslang-lenduriteta
    13  kaasaütlev   luuslang-lenduriga                         luuslang-lenduritega


Correcting spelling
===================

Many applications can benefit from spellcheck functionality, which flags incorrect words and also
provides suggestions.
Estnltk Text class has properties :py:attr:`~estnltk.text.Text.spelling`, that tells which words are correctly spelled
and :py:attr:`~estnltk.text.Text.spelling_suggestions`, which lists suggestions for incorrect words::

    from estnltk import Text
    text = Text('Vikastes lausetes on trügivigasid!')

    text.get.word_texts.spelling.spelling_suggestions.as_dataframe

::

         word_texts spelling  spelling_suggestions
    0      Vikastes    False  [Vigastes, Vihastes]
    1      lausetes     True                    []
    2            on     True                    []
    3  trügivigasid    False        [trükivigasid]
    4             !     True                    []

There is also property :py:attr:`~estnltk.text.Text.spellcheck_results`, that gives both spelling and suggestions
together.
This is more efficient than calling :py:attr:`~estnltk.text.Text.spelling` and :py:attr:`~estnltk.text.Text.spelling_suggestions` separately::

    text.spellcheck_results

::

    [{'spelling': False,
      'suggestions': ['Vigastes', 'Vihastes'],
      'text': 'Vikastes'},
     {'spelling': True, 'suggestions': [], 'text': 'lausetes'},
     {'spelling': True, 'suggestions': [], 'text': 'on'},
     {'spelling': False, 'suggestions': ['trükivigasid'], 'text': 'trügivigasid'},
     {'spelling': True, 'suggestions': [], 'text': '!'}]


Last, there is function :py:meth:`~estnltk.text.Text.fix_spelling`, that replaces incorrect words with first
suggestion in the list. It is very naive, but it may be handy::

    print(text.fix_spelling())

::

    Vigastes lausetes on trükivigasid!


Detecting invalid characters
============================

Often, during preprocessing of text files, we wish to check if the files satisfy certain assumptions.
One such possible requirement is check if the files contain characters that can be handled by our application.
For example, an application assuming Estonian input might not work with Cyrillic characters.
In such cases, it is necessary to detect invalid input.

Predefined alphabets
--------------------

Estnltk has predefined alphabets for Estonian and Russian, that can be combined with various punctuation and whitespace::

    from estnltk import EST_ALPHA, RUS_ALPHA, DIGITS, WHITESPACE, PUNCTUATION, ESTONIAN, RUSSIAN

Estonian alphabet (EST_ALPHA)::

    abcdefghijklmnoprsšzžtuvwõäöüxyzABCDEFGHIJKLMNOPRSŠZŽTUVWÕÄÖÜXYZ

Russian alphabet (RUS_ALPHA)::

    абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ

Standard punctuation (PUNCTUATION)::

    !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~–

Digits::

    0123456789

Whitespace::

    ' \t\n\r\x0b\x0c'

Estonian combined with punctuation and whitespace::

    'abcdefghijklmnoprsšzžtuvwõäöüxyzABCDEFGHIJKLMNOPRSŠZŽTUVWÕÄÖÜXYZ0123456789 \t\n\r\x0b\x0c!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~–'

Russian combined with punctuation and whitespace::

    'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0123456789 \t\n\r\x0b\x0c!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~–'


Detecting characters
--------------------

By default, Estnltk assumes Estonian alphabet with whitespace and punctuation, but you can supply :py:class:`~estnltk.textclearner.TextCleaner`
instances with other dictionaries to a Text instance::

    from estnltk import Text, TextCleaner, RUSSIAN
    td_ru = TextCleaner(RUSSIAN)

    et_plain = 'Segan suhkrut malbelt tassis, kus nii armsalt aurab tee.'
    ru_plain = 'Дождь, звонкой пеленой наполнил небо майский дождь.'

    et_correct = Text(et_plain)
    et_invalid = Text(ru_plain)
    ru_correct = Text(ru_plain, text_cleaner=td_ru)
    ru_invalid = Text(et_plain, text_cleaner=td_ru)

Now you can use :py:meth:`~estnltk.text.Text.is_valid` method to check if the text contains only characters defined in the alphabet::

    et_correct.is_valid()
    et_invalid.is_valid()

::

    True
    False

::

    ru_correct.is_valid()
    ru_invalid.is_valid()

::

    True
    False


In addition to checking just for correctness, we might want to get the list of invalid characters::

    from estnltk import Text

    text = Text('Esmaspäeval (27.04) liikus madalrōhkkond Pōhjalahelt Soome kohale.¶')
    print (text.invalid_characters)

::

    ¶ō

Surprisingly, in addition to ``¶`` we also see character ``ō`` as invalid.
Well, the reason is that is not the correct ``õ``.

.. note:: Different Unicode characters

    * ō latin small letter o with macron (U+014D)
    * õ latin small letter o with tilde (U+00F5)

It is really hard to distinguish the difference visually, but in case we are indexing the text, we fail to find it
via search later if we assume it used correct character ``õ``.

So, let's replace the wrong ``ō`` and remove other invalid characters using method :py:meth:`~estnltk.text.Text.clean`::

    text = text.replace('ō', 'õ').clean()
    print (text)
    print (text.is_valid())

::

    Esmaspäeval (27.04) liikus madalrõhkkond Põhjalahelt Soome kohale.
    True


Searching, replacing and splitting
==================================

Estnltk :py:class:`~estnltk.text.Text` class mimics the behaviour of some string functions for convenience:
:py:meth:`~estnltk.text.Text.capitalize`,
:py:meth:`~estnltk.text.Text.count`,
:py:meth:`~estnltk.text.Text.endswith`,
:py:meth:`~estnltk.text.Text.find`,
:py:meth:`~estnltk.text.Text.index`,
:py:meth:`~estnltk.text.Text.isalnum`,
:py:meth:`~estnltk.text.Text.isalpha`,
:py:meth:`~estnltk.text.Text.isdigit`,
:py:meth:`~estnltk.text.Text.islower`,
:py:meth:`~estnltk.text.Text.isspace`,
:py:meth:`~estnltk.text.Text.istitle`,
:py:meth:`~estnltk.text.Text.isupper`,
:py:meth:`~estnltk.text.Text.lower`,
:py:meth:`~estnltk.text.Text.lstrip`,
:py:meth:`~estnltk.text.Text.replace`,
:py:meth:`~estnltk.text.Text.rfind`,
:py:meth:`~estnltk.text.Text.rindex`,
:py:meth:`~estnltk.text.Text.rstrip`,
:py:meth:`~estnltk.text.Text.startswith`,
:py:meth:`~estnltk.text.Text.strip`.

However, if the method modifies the string, such as :py:meth:`~estnltk.text.Text.strip`, the method returns a new :py:class:`~estnltk.text.Text`
instance, invalidating all computed attributes such as the start and end positions as a result of tokenization. These
attributes won't be copied to the resulting string. However, all the original keyword arguments are passed to the new copy.

Here is an example showing few of these methods at work::

    from estnltk import Text

    text = Text('        TERE MAAILM  ').strip().capitalize().replace('maailm', 'estnltk!')
    print (text)

::

    Tere estnltk!


Splitting
---------

A more important concept is splitting text into smaller pieces in order to work with them independently.
For example, we might want to process the text on sentence at a time.


Temporal expression (TIMEX) tagging
===================================

Temporal expressions tagger identifies temporal expressions (timexes) in text and normalizes these expressions, providing corresponding calendrical dates and times.
The program outputs an annotation in a format similar to TimeML's TIMEX3 (more detailed description can be found in `annotation guidelines`_, which are currently only in Estonian).

.. _annotation guidelines: https://github.com/soras/EstTimeMLCorpus/blob/master/docs-et/ajav2ljendite_m2rgendamine_06.pdf?raw=true

The :py:class:`~estnltk.text.Text` class has property :py:attr:`~estnltk.text.Text.timexes`, which returns a list of time expressions found in the text::

    from estnltk import Text
    from pprint import pprint

    text = Text('Järgmisel kolmapäeval, kõige hiljemalt kell 18.00 algab viiepäevane koosolek, mida korraldatakse igal aastal')
    pprint(text.timexes)


The output is a list of four dictionaries, each representing an timex found in text::

    [{'end': 21,
      'id': 0,
      'start': 0,
      'temporal_function': True,
      'text': 'Järgmisel kolmapäeval',
      'tid': 't1',
      'type': 'DATE',
      'value': '2015-06-03'},
     {'anchor_id': 0,
      'anchor_tid': 't1',
      'end': 49,
      'id': 1,
      'start': 39,
      'temporal_function': True,
      'text': 'kell 18.00',
      'tid': 't2',
      'type': 'TIME',
      'value': '2015-06-03T18:00'},
     {'end': 67,
      'id': 2,
      'start': 56,
      'temporal_function': False,
      'text': 'viiepäevane',
      'tid': 't3',
      'type': 'DURATION',
      'value': 'P5D'},
     {'end': 108,
      'id': 3,
      'quant': 'EVERY',
      'start': 97,
      'temporal_function': True,
      'text': 'igal aastal',
      'tid': 't4',
      'type': 'SET',
      'value': 'P1Y'}]


There are a number of mandatory attributes present in the dictionaries:

* **start, end** - the expression start and end positions in the text.
* **tid** - TimeML format *id* of the expression.
* **id** - the zero-based *id* of the expressions, matches the position of the respective dictionary in the resulting list.
* **temporal_function** - *true*, if the expression is relative and exact date has to be computed from anchor points.
* **type** - according to TimeML, four types of temporal expressions are distinguished:
    * *DATE expressions*, e.g. *järgmisel kolmapäeval* (*on next Wednesday*)
    * *TIME expressions*, e.g. *kell 18.00* (*at 18.00 o’clock*)
    * *DURATIONs*, e.g. *viis päeva* (*five days*)
    * *SETs of times*, e.g. *igal aastal* (*on every year*)

The **value** is a mandatory attribute containing the semantics and has four possible formats:

1. Date and time **yyyy-mm-ddThh:mm**
    * *yyyy* - year (4 digits)
    * *mm* - month (01-12)
    * *dd* - day (01-31)
2. Week-based **yyyy-Wnn-wdThh:mm**
    * *nn* - the week of the year (01-53)
    * *wd* - day of the week (1-7, where 1 denotes Monday).
3. Time based **Thh:mm**
4. Time span **Pn1Yn2Mn3Wn4DTn5Hn6M**
    ni denotes a value and Y (year), M (month), W (week), D (day), H (hours), M (minutes) denotes respective time granularity.


Formats (1) and (2) are used with DATE, TIME and SET types.
Format (1) is always preferred if both (1) and (2) can be used.
Format (3) is used in cases it is impossible to extract the date.
Format (4) is used is used in time span expressions.

In addition, there are dedicated markers for special time notions:

1. Different times of the day
    * *MO* - morning - hommik
    * *AF* - afternoon - pärastlõuna
    * *EV* - evening - õhtu
    * *NI* - night - öö
    * *DT* - daytime - päevane aeg

2. Weekends/workdays
    * *WD* - workday - tööpäev
    * *WE* - weekend - nädalalõpp

3. Seasons
    * *SP* - spring - kevad
    * *SU* - summer - suvi
    * *FA* - fall - sügis
    * *WI* - winter - talv

4. Quarters
    * *Q1, Q2, Q3, Q4*
    * *QX* - unknown/unspecified quarter


TIMEX examples
--------------

TODO: add here a sufficiently large number of examples with tabulated output

