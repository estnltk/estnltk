=================
Working with text
=================

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
    text.tokenize_words()
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

    text.tag_clauses()
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
The :py:class:`~estnltk.text.Text` class has methods
:py:func:`~estnltk.text.Text.tokenize_paragraphs`,
:py:func:`~estnltk.text.Text.tokenize_sentences` and :py:func:`~estnltk.text.Text.tokenize_words`,
which you can call to do this explicitly.
However, there are also properties :py:attr:`~estnltk.text.Text.word_texts`,
:py:attr:`~estnltk.text.Text.sentence_texts` and :py:attr:`~estnltk.text.Text.paragraph_texts`
that do this automatically when you use them and also
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

    {'paragraphs': [{'end': 48, 'start': 0}],
     'sentences': [{'end': 30, 'start': 0}, {'end': 48, 'start': 31}],
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
and ``end`` positions of the respective words. You also see ``sentences`` and ``paragraphs`` elements,
because sentence and paragraph tokenization is a prerequisite
before word tokenization and Estnltk did this automatically on your behalf.

The :py:attr:`~estnltk.text.Text.word_texts` property does basically the same as the following snippet::

    text = Text('Üle oja mäele, läbi oru jõele. Ämber läks ümber.')
    text.tokenize_words() # this method applies text tokenization
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
* :py:attr:`~estnltk.text.Text.paragraph_texts` - paragraph texts
* :py:attr:`~estnltk.text.Text.paragraph_starts` - paragraph start positions
* :py:attr:`~estnltk.text.Text.paragraph_ends` - paragraph end positions
* :py:attr:`~estnltk.text.Text.paragraph_spans` - paragraph (start, end) position pairs

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

Note that if a dictionary already has ``words``, ``sentences`` or ``paragraphs`` elements (or any other element that we introduce later),
accessing these elements in a newly initialized :py:class:`~estnltk.text.Text` object does not require
recomputing them::

    text = Text({'paragraphs': [{'end': 27, 'start': 0}],
                 'sentences': [{'end': 14, 'start': 0}, {'end': 27, 'start': 15}],
                 'text': 'Esimene lause. Teine lause.',
                 'words': [{'end': 7, 'start': 0, 'text': 'Esimene'},
                           {'end': 13, 'start': 8, 'text': 'lause'},
                           {'end': 14, 'start': 13, 'text': '.'},
                           {'end': 20, 'start': 15, 'text': 'Teine'},
                           {'end': 26, 'start': 21, 'text': 'lause'},
                           {'end': 27, 'start': 26, 'text': '.'}]}
    )

    print (text.word_texts) # tokenization is already done, just extract words using the positions

::

    ['Esimene', 'lause', '.', 'Teine', 'lause', '.']

You should also remember this, when you have defined custom tokenizers. In such cases you can force retokenization by
calling
:py:meth:`~estnltk.text.Text.tokenize_words`,
:py:meth:`~estnltk.text.Text.tokenize_sentences`
or :py:meth:`~estnltk.text.Text.tokenize_words`.

.. note:: Things to remember!

    1. ``words``, ``sentences`` and ``paragraphs`` are **simple** layers.
    2. use properties to access the tokenized word/sentence texts and avoid :py:meth:`~estnltk.text.Text.tokenize_words`, :py:meth:`~estnltk.text.Text.tokenize_sentences` or :py:meth:`~estnltk.text.Text.tokenize_paragraphs`, unless you have a meaningful reason to use them (for example, preparing documents for indexing in a database).


Morphological analysis
======================

In linguistics, morphology is the identification, analysis, and description of the structure of a given language's morphemes and other linguistic units,
such as root words, lemmas, suffixes, parts of speech etc.
Estnltk wraps `Vabamorf`_ morphological analyzer, which can do both morphological analysis and synthesis.

.. _Vabamorf: https://github.com/Filosoft/vabamorf

Esnltk :py:class:`~estnltk.text.Text` class properties for extracting morphological information:

* :py:attr:`~estnltk.text.Text.analysis` - raw analysis data.
* :py:attr:`~estnltk.text.Text.roots` - root forms of words.
* :py:attr:`~estnltk.text.Text.root_tokens` - for compound words, all the tokens the root is made of.
* :py:attr:`~estnltk.text.Text.lemmas` - dictionary (canonical) word forms.
* :py:attr:`~estnltk.text.Text.forms` - word form expressing the case, plurality, voice etc.
* :py:attr:`~estnltk.text.Text.endings` - word inflective suffixes.
* :py:attr:`~estnltk.text.Text.postags` - part-of-speech (POS) tags (word types).
* :py:attr:`~estnltk.text.Text.postag_descriptions` - Estonian descriptions for POS tags.
* :py:attr:`~estnltk.text.Text.descriptions` - Estonian descriptions for forms.

These properties call :py:func:`~estnltk.text.Text.tag_analysis` method in background, which also
call :py:func:`~estnltk.text.Text.tokenize_paragraphs`, :py:func:`~estnltk.text.Text.tokenize_sentences` and :py:func:`~estnltk.text.Text.tokenize_words` as
word tokenization is required in order add morphological analysis.
Morphological analysis adds extra information to ``words`` layer, which we'll explain in following sections.

See :ref:`postag_table`, :ref:`nounform_table` and :ref:`verbform_table` for more detailed information
about various analysis tags.


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
    all the properties act on same layer/unit data. So, when you mix sentence and word properties, you get either an error
    or malformed output.


Word analysis
-------------

Morphological analysis is performed with method :py:func:`~estnltk.text.Text.tag_analysis`
and is invoked by accessing any property requiring this.
In such case, also methods :py:func:`~estnltk.text.Text.tokenize_paragraphs`, :py:func:`~estnltk.text.Text.tokenize_sentences` and :py:func:`~estnltk.text.Text.tokenize_words` are called as word and sentence tokenization is required in order add morphological analysis.
Morphological analysis adds extra information to ``words`` layer, which we'll explain below.

After doing morphological analysis, ideally only one unambiguous dictionary containing all the raw data is generated.
However, sometimes the disambiguator cannot really eliminate all ambiguity and you get multiple analysis variants::

    from estnltk import Text
    text = Text('mõeldud')
    text.tag_analysis()

::

    {'sentences': [{'end': 7, 'start': 0}],
     'text': 'mõeldud',
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

The word *mõeldud* has quite a lot ambiguity as it can be interpreted either as a *verb* or *adjective*. Adjective
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

    {'clitic': 'gi',                         # In Estonian, -gi and -ki suffixes
     'ending': 'del',                        # word suffix without clitic
     'form': 'pl ad',                        # word form, in this case plural and adessive (alalütlev) case
     'lemma': 'raudteejaam',                 # the dictionary form of the word
     'partofspeech': 'S',                    # POS tag, in this case substantive
     'root': 'raud_tee_jaam',                # root form (same as lemma, but verbs do not have -ma suffix)
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

.. note:: Things to remember about morphological analysis!

    1. Morphological analysis is stored in ``analysis`` attribute of each word.
    2. Morphological analysis is in ``words`` layer.
    3. Use :py:class:`~estnltk.text.ZipBuilder` class simplify data retrieval.
    4. If you write something that needs better performance, access the :py:class:`~estnltk.text.Text` directly as a dictionary,
       because when using properties, one loop per property is executed.

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
It is recommended to use these methods in case the text does not have any layers.

Here is an example showing few of these methods at work::

    from estnltk import Text

    text = Text('        TERE MAAILM  ').strip().capitalize().replace('maailm', 'estnltk!')
    print (text)

::

    Tere estnltk!


Splitting by layers
-------------------

A more important concept is splitting text into smaller pieces in order to work with them independently.
For example, we might want to process the text one sentence at a time.
Estnltk has :py:meth:`~estnltk.text.Text.split_by` method, that takes one parameter: the layer defining the splits::

    from estnltk import Text
    from pprint import pprint
    text = Text('Esimene lause. Teine lause. Kolmas lause.')
    for sentence in text.split_by('sentences'):
        pprint(sentence)

::

    {'paragraphs': [],
     'sentences': [{'end': 14, 'start': 0}],
     'text': 'Esimene lause.'}
    {'paragraphs': [],
     'sentences': [{'end': 12, 'start': 0}],
     'text': 'Teine lause.'}
    {'paragraphs': [],
     'sentences': [{'end': 13, 'start': 0}],
     'text': 'Kolmas lause.'}


An example with **multi** layer::

    from estnltk import Text

    text = Text('Kõrred, millel on toitunud viljasääse vastsed, jäävad õhukeseks.')
    for clause in text.split_by('clauses'):
        print (clause)

::

    Kõrred jäävad õhukeseks.
    , millel on toitunud viljasääse vastsed,


.. note:: Things to remember!

    1. The resulting sentences are also :py:class:`~estnltk.text.Text` instances.
    2. **Simple** layer elements that do not belong entirely to a single split, **are discarded**!
    3. **Multi** layer element regions that do not belong entirely to a single split, **are discarded**!
    4. **Multi** layer elements will end up in several splits, if spans of the element are distributed in several splits.
    5. Start and end positions defining the layer element locations are modified so they align with the split they are moved into.
    6. Splitting only deals with ``start`` and ``end`` attributes of layer elements.
       Other attributes are not modified and are copied as they are.
    7. **Multi** layer split texts are by default separated with a space character ' '.

Splitting with regular expressions
----------------------------------

Sometimes it can be useful to split the text using regular expressions::

    from estnltk import Text
    text = Text('Pidage meeles, et <red font>teete kodused tööd kõik ära</red font>, muidu tuleb pahandus!')
    text.split_by_regex('<red font>.*?</red font>')

::

    [{'text': 'Pidage meeles, et '}, {'text': ', muidu tuleb pahandus!'}]

By default, the matched regions are discarded and used as separators.
This can be changed by using ``gaps=False`` argument that reverses the behaviour::

    text.split_by_regex('<red font>.*?</red font>', gaps=False)

::

    [{'text': '<red font>teete kodused tööd kõik ära</red font>'}]


Dividing elements by layers
---------------------------

In addition to splitting, we use a term *dividing* if we actually do not want :py:class:`~estnltk.text.Text` instances as the result.
Instead, we may just want to access the words, one sentence at a time, having the reference to the original instance.
Estnltk has :py:meth:`~estnltk.text.Text.divide` method, that takes two parameters: the element to divide into bins, the element that defines the bins::

    from estnltk import Text

    text = Text('Esimene lause. Teine lause.')
    for sentence in text.divide('words', 'sentences'):
        for word in sentence:
            word['new_attribute'] = 'Estnltk greets the word ' + word['text']
    print(text)

::

    {'paragraphs': [{'end': 27, 'start': 0}],
     'sentences': [{'end': 14, 'start': 0}, {'end': 27, 'start': 15}],
     'text': 'Esimene lause. Teine lause.',
     'words': [{'end': 7,
                'new_attribute': 'Estnltk greets the word Esimene',
                'start': 0,
                'text': 'Esimene'},
               {'end': 13,
                'new_attribute': 'Estnltk greets the word lause',
                'start': 8,
                'text': 'lause'},
               {'end': 14,
                'new_attribute': 'Estnltk greets the word .',
                'start': 13,
                'text': '.'},
               {'end': 20,
                'new_attribute': 'Estnltk greets the word Teine',
                'start': 15,
                'text': 'Teine'},
               {'end': 26,
                'new_attribute': 'Estnltk greets the word lause',
                'start': 21,
                'text': 'lause'},
               {'end': 27,
                'new_attribute': 'Estnltk greets the word .',
                'start': 26,
                'text': '.'}]}


The :py:meth:`~estnltk.text.Text.divide` method is useful for

1. adding new attributes to existing elements/layers in the text
2. keeping the original `start` and `end` positions when

.. note:: Nota bene!

    The original references are lost in elements having ``start`` and ``end`` positions in **multi layer format**.
    The reason is that multi layer elements can span regions that end up in different splits/divisions, thus invalidating the ``start`` and ``end`` attributes.
    Updating the invalidated attributes requires modifying them, which we cannot do as this would also modify the original element.
    Thus, instead a copy is made of the element, the attributes are updated, and the element is returned.

Temporal expression (TIMEX) tagging
===================================

Temporal expressions tagger identifies temporal expressions (timexes) in text and normalizes these expressions, providing corresponding calendrical dates and times.
The current version of the temporal expressions tagger is tuned for processing news texts (so the quality of the analysis may be suboptimal in other domains).
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
      'value': '2015-06-17'},
     {'anchor_id': 0,
      'anchor_tid': 't1',
      'end': 49,
      'id': 1,
      'start': 39,
      'temporal_function': True,
      'text': 'kell 18 . 00',
      'tid': 't2',
      'type': 'TIME',
      'value': '2015-06-17T18:00'},
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
* **type** - following the TimeML specification, four types of temporal expressions are distinguished:
    * *DATE expressions*, e.g. *järgmisel kolmapäeval* (*on next Wednesday*)
    * *TIME expressions*, e.g. *kell 18.00* (*at 18 o’clock*)
    * *DURATIONs*, e.g. *viis päeva* (*five days*)
    * *SETs of times*, e.g. *igal aastal* (*on every year*)
* **temporal_function** - boolean value indicating whether the semantics of the expression are relative to the context. 
    * For DATE and TIME expressions:
        * *True* indicates that the expression is relative and semantics have been computed by heuristics;
        * *False* indicates that the expression is absolute and semantics haven't been computed by heuristics;
    * For DURATION expressions, *temporal_function* is mostly *False*, except for vague durations;
    * For SET expressions, *temporal_function* is always *True*;

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


Document creation date
----------------------

Relative temporal expressions often depend on document creation date, which can be supplied as ``creation_date`` parameter.
If no ``creation_date`` argument is passed, it is set as the date the code is run (June 8, 2015 in the example)::

    from estnltk import Text
    Text('Täna on ilus ilm').timexes

::

    [{'end': 4,
      'id': 0,
      'start': 0,
      'temporal_function': True,
      'text': 'Täna',
      'tid': 't1',
      'type': 'DATE',
      'value': '2015-06-08'}]


However, when passing ``creation_date=datetime.datetime(1986, 12, 21)``::

    import datetime
    Text('Täna on ilus ilm', creation_date=datetime.datetime(1986, 12, 21)).timexes

We see that word "today" (*täna*) refers to to December 21, 1986::

    [{'end': 4,
      'id': 0,
      'start': 0,
      'temporal_function': True,
      'text': 'Täna',
      'tid': 't1',
      'type': 'DATE',
      'value': '1986-12-21'}]

TIMEX examples
--------------

Here are some examples of temporal expressions and fields that the tagger can extract.
The document creation date is fixed to Dec 21, 1986 in the examples below.
See `annotation guidelines`_ for more detailed explanations.

.. _annotation guidelines: https://github.com/soras/EstTimeMLCorpus/blob/master/docs-et/ajav2ljendite_m2rgendamine_06.pdf?raw=true


========================================================================= ============================= ======== ================= ==========
Example                                                                   Temporal expression           Type     Value             Modifier
========================================================================= ============================= ======== ================= ==========
Järgmisel reedel                                                          Järgmisel reedel              DATE     1986-12-26
2004. aastal                                                              2004. aastal                  DATE     2004
esmaspäeva hommikul                                                       esmaspäeva hommikul           TIME     1986-12-15TMO
järgmisel reedel kell 14.00                                               järgmisel reedel kell 14. 00  TIME     1986-12-26T14:00
neljapäeviti                                                              neljapäeviti                  SET      XXXX-WXX-XX
hommikuti                                                                 hommikuti                     SET      XXXX-XX-XXTMO
selle kuu alguses                                                         selle kuu alguses             DATE     1986-12           START
1990ndate lõpus                                                           1990ndate lõpus               DATE     199               END
VI sajandist e.m.a                                                        VI sajandist e.m.a            DATE     BC05
kolm tundi                                                                kolm tundi                    DURATION PT3H
viis kuud                                                                 viis kuud                     DURATION P5M
kaks minutit                                                              kaks minutit                  DURATION PT2M
teisipäeviti                                                              teisipäeviti                  SET      XXXX-WXX-XX
kolm päeva igas kuus                                                      kolm päeva                    DURATION P3D
kolm päeva igas kuus                                                      igas kuus                     SET      P1M
Ühel kenal päeval                                                         päeval                        TIME     TDT
Ühel märtsikuu päeval                                                     märtsikuu                     DATE     1987-03
Ühel märtsikuu päeval                                                     päeval                        TIME     TDT
hiljuti                                                                   hiljuti                       DATE     PAST_REF
tulevikus                                                                 tulevikus                     DATE     FUTURE_REF
2009. aasta alguses                                                       2009. aasta alguses           DATE     2009              START
juuni alguseks 2007. aastal                                               juuni alguseks                DATE     1986-06           START
juuni alguseks 2007. aastal                                               2007. aastal                  DATE     2007
2009. aasta esimesel poolel                                               2009. aasta esimesel poolel   DATE     2009              FIRST_HALF
umbes 4 aastat                                                            umbes 4 aastat                DURATION P4Y               APPROX
peaaegu 4 aastat                                                          peaaegu 4 aastat              DURATION P4Y               LESS_THAN
12-15 märts 2009                                                          12-                           DATE     2009-03-12
12-15 märts 2009                                                          15 märts 2009                 DATE     2009-03-15
12-15 märts 2009                                                                                        DURATION PXXD
eelmise kuu lõpus                                                         eelmise kuu lõpus             DATE     1986-11           END
2004. aasta suvel                                                         2004. aasta suvel             DATE     2004-SU
Detsembris oli keskmine temperatuur kaks korda madalam kui kuu aega varem Detsembris                    DATE     1986-12
Detsembris oli keskmine temperatuur kaks korda madalam kui kuu aega varem kuu aega varem                DATE     1986-11
neljapäeval, 17. juunil                                                   neljapäeval , 17. juunil      DATE     1986-06-17
täna, 100 aastat tagasi                                                   täna                          DATE     1986-12-21
täna, 100 aastat tagasi                                                   100 aastat tagasi             DATE     1886
neljapäeva öösel vastu reedet                                             neljapäeva öösel vastu reedet TIME     1986-12-19TNI
aasta esimestel kuudel                                                    aasta                         DATE     XXXX
viimase aasta jooksul                                                     viimase aasta jooksul         DURATION P1Y
viimase aasta jooksul                                                                                   DATE     1985
viimase kolme aasta jooksul                                               viimase kolme aasta jooksul   DURATION P3Y
viimase kolme aasta jooksul                                                                             DATE     1983
varasemad aastad, hilisemad aastad                                        varasemad aastad              DATE     PAST_REF
varasemad aastad, hilisemad aastad                                        aastad                        DURATION PXY
viie-kuue aasta pärast, kahe-kolme aasta tagune                           aasta pärast                  DATE     1987
viie-kuue aasta pärast, kahe-kolme aasta tagune                           aasta tagune                  DATE     1985
aastaid tagasi                                                            aastaid tagasi                DATE     PAST_REF
aastate pärast                                                            aastate pärast                DATE     FUTURE_REF
========================================================================= ============================= ======== ================= ==========


Tagging clauses
===============

Basic usage
--------------

A simple sentence, also called an independent clause, typically contains a finite verb, and expresses a complete thought.
However, natural language sentences can also be long and complex, consisting of two or more clauses joined together.
The clause structure can be made even more complex due to embedded clauses, which divide their parent clauses into two halves::

    from estnltk import Text
    text = Text('Mees, keda seal kohtasime, oli tuttav ja teretas meid.')
    text.get.word_texts.clause_indices.clause_annotations.as_dataframe

The clause annotations define embedded clauses and clause boundaries.
Additionally, each word in a sentence is associated with a clause index::

       word_texts  clause_indices     clause_annotations
    0        Mees               0                   None
    1           ,               1  embedded_clause_start
    2        keda               1                   None
    3        seal               1                   None
    4   kohtasime               1                   None
    5           ,               1    embedded_clause_end
    6         oli               0                   None
    7      tuttav               0                   None
    8          ja               0        clause_boundary
    9     teretas               2                   None
    10       meid               2                   None
    11          .               2                   None

Clause annotation information is stored in ``words`` layer as ``clause_index`` and ``clause_annotation`` attributes::

    {'analysis': [{'clitic': '',
                   'ending': '0',
                   'form': 'sg n',
                   'lemma': 'mees',
                   'partofspeech': 'S',
                   'root': 'mees',
                   'root_tokens': ['mees']}],
     'clause_index': 0,
     'end': 4,
     'start': 0,
     'text': 'Mees'}

    {'analysis': [{'clitic': '',
                   'ending': '',
                   'form': '',
                   'lemma': ',',
                   'partofspeech': 'Z',
                   'root': ',',
                   'root_tokens': [',']}],
     'clause_annotation': 'embedded_clause_start',
     'clause_index': 1,
     'end': 5,
     'start': 4,
     'text': ','}

Clause indices and annotations can be explicitly tagged with method :py:meth:`~estnltk.text.Text.tag_clause_annotations`.

Property :py:attr:`~estnltk.text.Text.clause_texts` can be used to see the full clauses themselves::

    text.clause_texts

::

    ['Mees oli tuttav ja', ', keda seal kohtasime,', 'teretas meid.']

Method :py:meth:`~estnltk.text.Text.tag_clauses` can be used create a special ``clauses`` multilayer,
that lists character-level indices of start and end positions of clause regions::

    text.tag_clauses()
    text['clauses']

::

    [{'end': [4, 40], 'start': [0, 27]},
     {'end': [26], 'start': [4]},
     {'end': [54], 'start': [41]}]


It might be useful to process each clause of the sentence independently::

    for clause in text.split_by('clauses'):
        print (clause.text)

::

    Mees oli tuttav ja
    , keda seal kohtasime,
    teretas meid.

The 'ignore_missing_commas' mode
----------------------------------

Because commas are important clause delimiters in Estonian, the quality of the clause segmentation may suffer due to accidentially missing commas in the input text. To address this issue, the clause segmenter can be initialized in a mode in which the program tries to be less sensitive to missing commas while detecting clause boundaries.

Example::

    from estnltk import ClauseSegmenter
    from estnltk import Text
    
    segmenter = ClauseSegmenter( ignore_missing_commas=True )
    text = Text('Keegi teine ka siin ju kirjutas et ütles et saab ise asjadele järgi minna aga vastust seepeale ei tulnudki.', clause_segmenter = segmenter)
    
    for clause in text.split_by('clauses'):
        print (clause.text)
    
will produce following output::

    Keegi teine ka siin ju kirjutas
    et ütles
    et saab ise asjadele järgi minna
    aga vastust seepeale ei tulnudki.
    
Note that this mode is experimental and compared to the basic mode, it may introduce additional incorrect clause boundaries, although it also improves clause boundary detection in texts with (a lot of) missing commas.


Verb chain tagging
==================

Verb chain tagger identifies multiword verb units from text.
The current version of the program aims to detect following verb chain constructions:

* basic main verbs:

  * (affirmative) single non-*olema* main verbs (example: Pidevalt **uurivad** asjade seisu ka hollandlased);
  * (affirmative) single *olema* main verbs (e.g. Raha **on** alati vähe) and two word *olema* verb chains (**Oleme** sellist kino ennegi **näinud**);
  * negated main verbs: *ei/ära/pole/ega* + verb (e.g. Helistasin korraks Carmenile, kuid ta **ei vastanud.**);

* verb chain extensions:

  * verb + verb : the chain is extended with an infinite verb if the last verb of the chain subcategorizes for it, e.g. the verb *kutsuma* is extended with *ma*-verb arguments (for example: Kevadpäike **kutsub** mind **suusatama**) and the verb *püüdma* is extended with *da*-verb arguments (Aita **ei püüdnudki** Leenat **mõista**);
  * verb + nom/adv + verb : the last verb of the chain is extended with nominal/adverb arguments which subcategorize for an infinite verb, e.g. the verb *otsima* forms a multiword unit with the nominal *võimalust* which, in turn, takes infinite *da*-verb as an argument (for example: Seepärast **otsisimegi võimalust** kusagilt mõned ilvesed **hankida**);

Verb chains are stored as a simple layer named ``verb_chains``::

    from estnltk import Text
    text = Text('Ta oleks pidanud sinna minema, aga ei läinud.')
    text.verb_chains

::

    [{'analysis_ids': [[0], [0], [0]],
      'clause_index': 0,
      'end': 29,
      'mood': 'condit',
      'morph': ['V_ks', 'V_nud', 'V_ma'],
      'other_verbs': False,
      'pattern': ['ole', 'verb', 'verb'],
      'phrase': [1, 2, 4],
      'pol': 'POS',
      'roots': ['ole', 'pida', 'mine'],
      'start': 3,
      'tense': 'past',
      'voice': 'personal'},
     {'analysis_ids': [[0], [3]],
      'clause_index': 1,
      'end': 44,
      'mood': 'indic',
      'morph': ['V_neg', 'V_nud'],
      'other_verbs': False,
      'pattern': ['ei', 'verb'],
      'phrase': [7, 8],
      'pol': 'NEG',
      'roots': ['ei', 'mine'],
      'start': 35,
      'tense': 'imperfect',
      'voice': 'personal'}]


Following is a brief description of the attributes:

* ``analysis_ids`` - the indices of analysis ids of the words in the phrase of this chain.
* ``clause_index`` - the clause id this chain was tagged in.
* ``mood``  - mood of the finite verb. Possible values: *'indic'* (indicative), *'imper'* (imperative), *'condit'* (conditional), *'quotat'* (quotative) or *'??'* (undetermined);
* ``morph`` - for each word in the chain, lists its morphological features: part of speech tag and form (in one string, separated by '_', and multiple variants of the pos/form are separated by '/');
* ``other_verbs`` - boolean, marks whether there are other verbs in the context, which can be potentially added to the verb chain; if ``True``,then it is uncertain whether the chain is complete or not;
* ``pattern`` - the general pattern of the chain: for each word in the chain, lists whether it is *'ega'*, *'ei'*, *'ära'*, *'pole'*, *'ole'*, *'&'* (conjunction: ja/ning/ega/või), *'verb'* (verb different than *'ole'*) or *'nom/adv'* (nominal/adverb);
* ``phrase`` - the word indices of the sentence that make up the verb chain phrase.
* ``pol`` - grammatical polarity of the finite verb. Possible values: *'POS'*, *'NEG'* or *'??'*. *'NEG'* means that the chain begins with a negation word *ei/pole/ega/ära*; *'??'* is reserved for cases where it is uncertain whether *ära* forms a negated verb chain or not;
* ``roots`` - for each word in the chain, lists its corresponding 'root' value from the morphological analysis;
* ``tense`` - tense of the finite verb. Possible values depend on the mood value. Tenses of indicative: *'present'*, *'imperfect'*, *'perfect'*, *'pluperfect'*; tense of imperative: *'present'*; tenses of conditional and quotative: *'present'* and *'past'*. Additionally, the tense may remain undetermined (*'??'*).
* ``voice`` - voice of the finite verb. Possible values: *'personal'*, *'impersonal'*, *'??'* (undetermined).

Note that the words in the verb chain are ordered by the order of the grammatical relations (the order which may not coincide with the word order in text).
The first word is the finite verb (main verb) of the clause (except in case of the negation constructions, where the first word is typically a negation word), and each following word is governed by the previous word in the chain.
An exception: the chain may end with a conjunction of two infinite verbs (general pattern *verb & verb*), in this case, both infinite verbs can be considered as being governed by the preceding word in the chain.


Estonian wordnet
================

Estonian WordNet API provides means to query Estonian WordNet.
WordNet is a network of synsets, in which synsets are collections of synonymous words and are connected to other synsets via relations.
For example, the synset which contains the word "koer" ("dog") has a generalisation via hypernymy relation in the form of synset which contains the word "koerlane" ("canine").

Estonian WordNet contains synsets with different types of part-of-speech: *adverbs, adjectives, verbs* and *nouns*.

===============  ===============
Part of speech   API equivalent
===============  ===============
Adverb           wn.ADV
Adjective        wn.ADJ
Noun             wn.NOUN
Verb             wn.VERB
===============  ===============

Given API is on most parts in conformance with NLTK WordNet's API (http://www.nltk.org/howto/wordnet.html).
However, there are some differences due to different structure of the WordNets.

* Lemma classes' relations return empty sets. Reason: In Estonian WordNet relations are only between synsets.
* No verb frames. Reason: No information on verb frames.
* Only path, Leacock-Chodorow and Wu-Palmer similarities. No information on Information Content.

Existing relations:

*antonym, be_in_state, belongs_to_class, causes, fuzzynym, has_holo_location, has_holo_madeof, has_holo_member,
has_holo_part, has_holo_portion, has_holonym, has_hyperonym, has_hyponym, has_instance, has_mero_location,
has_mero_madeof, has_mero_member, has_mero_part, has_mero_portion, has_meronym, has_subevent, has_xpos_hyperonym,
has_xpos_hyponym, involved, involved_agent, involved_instrument, involved_location, involved_patient, involved_target_direction,
is_caused_by, is_subevent_of, near_antonym, near_synonym, role, role_agent, role_instrument, role_location, role_patient,
role_target_direction, state_of, xpos_fuzzynym, xpos_near_antonym, xpos_near_synonym .*


Wordnet API
-----------

Before anything else, let's import the module::

    from estnltk.wordnet import wn


The most common use for the API is to query synsets.
Synsets can be queried in several ways.
The easiest way is to query all the synsets which match some conditions.
For that we can either use::

    wn.all_synsets()

which returns all the synsets there are or::

    wn.all_synsets(pos=wn.ADV)

which returns all the synset of which part of speech is "adverb".
We can also query synsets by providing a lemma and a part of speech using::

    wn.synsets("koer",pos=wn.VERB)

::

    []

By neglecting "pos", it matches once again all the synsets with "koer" as lemma::

    wn.synsets("koer")

::

    [Synset('koer.n.01'), Synset('kaak.n.01')]

The API allows to query synset's details. For example, we can retrieve name and pos::

    synset = wn.synset("king.n.01")
    synset.name

::

    'king.n.01'

::

    synset.pos

::

    'n'

We can also query definition and examples::

    synset.definition()

::

    'jalalaba kattev kontsaga jalats, mis ei ulatu pahkluust kõrgemale'

::

    synset.examples()

::

    [u'Jalad hakkasid katkistes kingades k\xfclmetama.']


Relations
---------
We can also query related synsets.
There are relations, for which there are specific methods::

    synset.hypernyms()

::

    [Synset('jalats.n.01')]

::

    synset.hyponyms()

::

    [Synset('peoking.n.01'), Synset('rihmking.n.01'), Synset('lapseking.n.01')]

::

    synset.meronyms()

::

    []

::

    synset.holonyms()

::

    []

More specific relations can be queried with a universal method::

    synset = wn.synset('jäätis.n.01')
    synset.get_related_synsets('fuzzynym')

::

    [Synset('jäätisemüüja.n.01'), Synset('jäätisekauplus.n.01'), Synset('jäätisekampaania.n.01'), Synset('jäätisekohvik.n.01')]


Similarities
------------

We can measure distance or similarity between two synsets in several ways.
For calculating similarity, we provide path, Leacock-Chodorow and Wu-Palmer similarities::

    synset = wn.synset('jalats.n.01')
    target_synset = wn.synset('kinnas.n.01')
    synset.path_similarity(target_synset)

::

    0.33

::

    synset.lch_similarity(target_synset)

::

    2.159484249353372

::

    synset.wup_similarity(target_synset)

::

    0.8571428571428571

In addition, we can also find the closest common ancestor via hypernyms::

    synset.lowest_common_hypernyms(target_synset)

::

    [Synset('kehakate.n.01')]


