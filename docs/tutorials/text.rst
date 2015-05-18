===============
Getting started
===============

In this tutorial, we start with Estnltk basics and introduce you to the :py:class:`~estnltk.text.Text` class.
We will take the class apart to bits and pieces and put it back together to give a good overview, what it can do for you
and how can you work with it.

Working with Text
=================

One of the most important classes in Estnltk is :py:class:`~estnltk.text.Text`, which is essentally the main interface
for doing everything Estnltk is capable of. It is actually a subclass of standard ``dict`` class in Python and stores
all data relevant to the text there::

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


Tokenization
------------

One of the most basic tasks of any NLP pipeline is text and sentence tokenization.
The :py:class:`~estnltk.text.Text` class has properties :py:attr:`~estnltk.text.Text.word_texts` and
:py:attr:`~estnltk.text.Text.sentence_texts` properties that do this whenever you access them::

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

    {'text': 'Üle oja mäele, läbi oru jõele. Ämber läks ümber.',
     'words': [{'end': 3, 'start': 0},
               {'end': 7, 'start': 4},
               {'end': 13, 'start': 8},
               {'end': 14, 'start': 13},
               {'end': 19, 'start': 15},
               {'end': 23, 'start': 20},
               {'end': 29, 'start': 24},
               {'end': 30, 'start': 29},
               {'end': 36, 'start': 31},
               {'end': 41, 'start': 37},
               {'end': 47, 'start': 42},
               {'end': 48, 'start': 47}]}

As you can see, there is now a ``words`` element in the dictionary, which is a list of dictionaries denoting ``start``
and ``end`` positions of the respective words.
Basically, :py:attr:`~estnltk.text.Text.word_texts` property does basically the same as the following snippet::

    text = Text('Üle oja mäele, läbi oru jõele. Ämber läks ümber.')
    text.compute_words() # this method applies text tokenization
    print ([text['text'][word['start']:word['end']] for word in text['words']])

::

    ['Üle', 'oja', 'mäele', ',', 'läbi', 'oru', 'jõele', '.', 'Ämber', 'läks', 'ümber', '.']

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
     'words': [{'end': 4, 'start': 0},
               {'end': 16, 'start': 5},
               {'end': 23, 'start': 17},
               {'end': 30, 'start': 24},
               {'end': 37, 'start': 31},
               {'end': 40, 'start': 38},
               {'end': 47, 'start': 41},
               {'end': 60, 'start': 48},
               {'end': 67, 'start': 61},
               {'end': 81, 'start': 69},
               {'end': 87, 'start': 82}]}

Consequent calls to any property won't require retokenization as the stored start and end positions can be used
to construct new text fragments.

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
    [{'end': 7, 'start': 0}, {'end': 13, 'start': 8}, {'end': 14, 'start': 13}, {'end': 20, 'start': 15}, {'end': 26, 'start': 21}]
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


Note that if a dictionary alraedy has ``words`` and ``sentences`` elements (or any other element that we introduce later),
accessing these elements in a newly initialized :py:class:`~estnltk.text.Text` object does not require
recomputing them::

    text = Text({'sentences': [{'end': 14, 'start': 0}, {'end': 26, 'start': 15}],
                 'text': 'Esimene lause. Teine lause',
                 'words': [{'end': 7, 'start': 0},
                           {'end': 13, 'start': 8},
                           {'end': 14, 'start': 13},
                           {'end': 20, 'start': 15},
                           {'end': 26, 'start': 21}]})

    print (text.word_texts) # tokenization is already done, just extract words using the positions

