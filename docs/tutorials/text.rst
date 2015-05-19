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


Tokenization
============

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

You should also remember this, when you have defined custom tokenizers. In such cases you can force retokenization by
calling :py:meth:`~estnltk.text.Text.compute_words` and :py:meth:`~estnltk.text.Text.compute_sentences`.

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


POS tags table
--------------

=======     ===========================================================================  ====================
POS tag     Description                                                                  Example
=======     ===========================================================================  ====================
A           omadussõna - algvõrre (adjektiiv - positiiv), nii käänduvad kui käändumatud  kallis või eht
C           omadussõna - keskvõrre (adjektiiv - komparatiiv)                             laiem
D           määrsõna (adverb)                                                            kõrvuti
G           genitiivatribuut (käändumatu omadussõna)                                     balti
H           pärisnimi                                                                    Edgar
I           hüüdsõna (interjektsioon)                                                    tere
J           sidesõna (konjunktsioon)                                                     ja
K           kaassõna (pre/postpositsioon)                                                kaudu
N           põhiarvsõna (kardinaalnumeraal)                                              kaks
O           järgarvsõna (ordinaalnumeraal)                                               teine
P           asesõna (pronoomen)                                                          see
S           nimisõna (substantiiv)                                                       asi
U           omadussõna - ülivõrre (adjektiiv - superlatiiv)                              pikim
V           tegusõna (verb)                                                              lugema
X           verbi juurde kuuluv sõna, millel eraldi sõnaliigi tähistus puudub            plehku
Y           lühend                                                                       USA
Z           lausemärk                                                                    -, /, ...
=======     ===========================================================================  ====================

Noun forms table
----------------

======  ====================================================
Form    Description
======  ====================================================
ab      abessiiv (ilmaütlev)
abl     ablatiiv (alaltütlev)
ad      adessiiv (alalütlev)
adt     aditiiv	suunduv (lühike sisseütlev), nt. "majja"
all     allatiiv (alaleütlev)
el      elatiiv (seestütlev)
es      essiiv (olev)
g       genitiiv (omastav)
ill     illatiiv (sisseütlev)
in      inessiiv (seesütlev)
kom     komitatiiv (kaasaütlev)
n       nominatiiv (nimetav)
p       partitiiv (osastav)
pl      pluural (mitmus)
sg      ainsus (ainsus)
ter     terminatiiv (rajav)
tr      translatiiv (saav)
======  ====================================================


Verb forms table
----------------
======== ============================================================= ===========================
Form     Description                                                   Example
======== ============================================================= ===========================
b        kindel kõneviis olevik 3. isik ainsus aktiiv jaatav kõne      loeb
d        kindel kõneviis olevik 2. isik ainsus aktiiv jaatav kõne      loed
da       infinitiiv jaatav kõne                                        lugeda
des      gerundium jaatav kõne                                         lugedes
ge       käskiv kõneviis olevik 2. isik mitmus aktiiv jaatav kõne      lugege
gem      käskiv kõneviis olevik 1. isik mitmus aktiiv jaatav kõne      lugegem
gu       käskiv kõneviis olevik 3. isik mitmus aktiiv jaatav kõne      (nad) lugegu
gu       käskiv kõneviis olevik 3. isik ainsus aktiiv jaatav kõne      (ta) lugegu
ks       tingiv kõneviis olevik 1. isik mitmus aktiiv jaatav kõne      (me) loeks
ks       tingiv kõneviis olevik 1. isik ainsus aktiiv jaatav kõne      (ma) loeks
ks       tingiv kõneviis olevik 2. isik mitmus aktiiv jaatav kõne      (te) loeks
ks       tingiv kõneviis olevik 2. isik ainsus aktiiv jaatav kõne      (sa) loeks
ks       tingiv kõneviis olevik 3. isik mitmus aktiiv jaatav kõne      (nad) loeks
ks       tingiv kõneviis olevik 3. isik ainsus aktiiv jaatav kõne      (ta) loeks
ksid     tingiv kõneviis olevik 2. isik ainsus aktiiv jaatav kõne      (sa) loeksid
ksid     tingiv kõneviis olevik 3. isik mitmus aktiiv jaatav kõne      (nad) loeksid
ksime    tingiv kõneviis olevik 1. isik mitmus aktiiv jaatav kõne      (me) loeksime
ksin     tingiv kõneviis olevik 1. isik ainsus aktiiv jaatav kõne      (ma) loeksin
ksite    tingiv kõneviis olevik 2. isik mitmus aktiiv jaatav kõne      (te) loeksite
ma       supiin aktiiv jaatav kõne sisseütlev                          lugema
maks     supiin aktiiv jaatav kõne saav                                lugemaks
mas      supiin aktiiv jaatav kõne seesütlev                           lugemas
mast     supiin aktiiv jaatav kõne seestütlev                          lugemast
mata     supiin aktiiv jaatav kõne ilmaütlev                           lugemata
me       kindel kõneviis olevik 1. isik mitmus aktiiv jaatav kõne      loeme
n        kindel kõneviis olevik 1. isik ainsus aktiiv jaatav kõne      loen
neg      eitav kõne                                                    ei
neg ge   käskiv kõneviis olevik 2. isik mitmus aktiiv eitav kõne       ärge
neg gem  käskiv kõneviis olevik 1. isik mitmus aktiiv eitav kõne       ärgem
neg gu   käskiv kõneviis olevik 3. isik mitmus aktiiv eitav kõne       (nad) ärgu
neg gu   käskiv kõneviis olevik 3. isik ainsus aktiiv eitav kõne       (ta) ärgu
neg gu   käskiv kõneviis olevik passiiv eitav kõne                     ärgu
neg ks   tingiv kõneviis olevik 1. isik mitmus aktiiv eitav kõne       (me) poleks
neg ks   tingiv kõneviis olevik 1. isik ainsus aktiiv eitav kõne       (ma) poleks
neg ks   tingiv kõneviis olevik 2. isik mitmus aktiiv eitav kõne       (te) poleks
neg ks   tingiv kõneviis olevik 2. isik ainsus aktiiv eitav kõne       (sa) poleks
neg ks   tingiv kõneviis olevik 3. isik mitmus aktiiv eitav kõne       (nad) poleks
neg ks   tingiv kõneviis olevik 3. isik ainsus aktiiv eitav kõne       (ta) poleks
neg me   käskiv kõneviis olevik 1. isik mitmus aktiiv eitav kõne       ärme
neg nud  kindel kõneviis lihtminevik 1. isik mitmus aktiiv eitav kõne  (me) polnud
neg nud  kindel kõneviis lihtminevik 1. isik ainsus aktiiv eitav kõne  (ma) polnud
neg nud  kindel kõneviis lihtminevik 2. isik mitmus aktiiv eitav kõne  (te) polnud
neg nud  kindel kõneviis lihtminevik 2. isik ainsus aktiiv eitav kõne  (sa) polnud
neg nud  kindel kõneviis lihtminevik 3. isik mitmus aktiiv eitav kõne  (nad) polnud
neg nud  kindel kõneviis lihtminevik 3. isik ainsus aktiiv eitav kõne  (ta) polnud
neg nuks tingiv kõneviis minevik 1. isik mitmus aktiiv eitav kõne      (me) polnuks
neg nuks tingiv kõneviis minevik 1. isik ainsus aktiiv eitav kõne      (ma) polnuks
neg nuks tingiv kõneviis minevik 2. isik mitmus aktiiv eitav kõne      (te) polnuks
neg nuks tingiv kõneviis minevik 2. isik ainsus aktiiv eitav kõne      (sa) polnuks
neg nuks tingiv kõneviis minevik 3. isik mitmus aktiiv eitav kõne      (nad) polnuks
neg nuks tingiv kõneviis minevik 3. isik ainsus aktiiv eitav kõne      (ta) polnuks
neg o    käskiv kõneviis olevik 2. isik ainsus aktiiv eitav kõne       ära
neg o    kindel kõneviis olevik 1. isik mitmus aktiiv eitav kõne       (me) pole
neg o    kindel kõneviis olevik 1. isik ainsus aktiiv eitav kõne       (ma) pole
neg o    kindel kõneviis olevik 2. isik mitmus aktiiv eitav kõne       (te) pole
neg o    kindel kõneviis olevik 2. isik ainsus aktiiv eitav kõne       (sa) pole
neg o    kindel kõneviis olevik 3. isik mitmus aktiiv eitav kõne       (nad) pole
neg o    kindel kõneviis olevik 3. isik ainsus aktiiv eitav kõne       (ta) pole
neg vat  kaudne kõneviis olevik 1. isik mitmus aktiiv eitav kõne       (me) polevat
neg vat  kaudne kõneviis olevik 1. isik ainsus aktiiv eitav kõne       (ma) polevat
neg tud  kesksõna minevik passiiv eitav kõne                           poldud
neg vat  kaudne kõneviis olevik 2. isik mitmus aktiiv eitav kõne       (te) polevat
neg vat  kaudne kõneviis olevik 2. isik ainsus aktiiv eitav kõne       (sa) polevat
neg vat  kaudne kõneviis olevik 3. isik mitmus aktiiv eitav kõne       (nad) polevat
neg vat  kaudne kõneviis olevik 3. isik ainsus aktiiv eitav kõne       (ta) polevat
nud      kesksõna minevik aktiiv jaatav kõne                           lugenud
nuks     tingiv kõneviis minevik 1. isik mitmus aktiiv jaatav kõne     (me) lugenuks
nuks     tingiv kõneviis minevik 1. isik ainsus aktiiv jaatav kõne     (ma) lugenuks
nuks     tingiv kõneviis minevik 2. isik mitmus aktiiv jaatav kõne     (te) lugenuks
nuks     tingiv kõneviis minevik 2. isik ainsus aktiiv jaatav kõne     (sa) lugenuks
nuks     tingiv kõneviis minevik 3. isik mitmus aktiiv jaatav kõne     (nad) lugenuks
nuks     tingiv kõneviis minevik 3. isik ainsus aktiiv jaatav kõne     (ta) lugenuks
nuksid   tingiv kõneviis minevik 2. isik ainsus aktiiv jaatav kõne     (sa) lugenuksid
nuksid   tingiv kõneviis minevik 3. isik mitmus aktiiv jaatav kõne     (nad) lugenuksid
nuksime  tingiv kõneviis minevik 1. isik mitmus aktiiv jaatav kõne     lugenuksime
nuksin   tingiv kõneviis minevik 1. isik ainsus aktiiv jaatav kõne     lugenuksin
nuksite  tingiv kõneviis minevik 2. isik mitmus aktiiv jaatav kõne     lugenuksite
nuvat    kaudne kõneviis minevik 1. isik mitmus aktiiv jaatav kõne     (me) lugenuvat
nuvat    kaudne kõneviis minevik 1. isik ainsus aktiiv jaatav kõne     (ma) lugenuvat
nuvat    kaudne kõneviis minevik 2. isik mitmus aktiiv jaatav kõne     (te) lugenuvat
nuvat    kaudne kõneviis minevik 2. isik ainsus aktiiv jaatav kõne     (sa) lugenuvat
nuvat    kaudne kõneviis minevik 3. isik mitmus aktiiv jaatav kõne     (nad) lugenuvat
nuvat    kaudne kõneviis minevik 3. isik ainsus aktiiv jaatav kõne     (ta) lugenuvat
o        käskiv kõneviis olevik 2. isik ainsus aktiiv jaatav kõne      loe
s        kindel kõneviis lihtminevik 3. isik ainsus aktiiv jaatav kõne luges
sid      kindel kõneviis lihtminevik 2. isik ainsus aktiiv jaatav kõne (sa) lugesid
sid      kindel kõneviis lihtminevik 3. isik mitmus aktiiv jaatav kõne (nad) lugesid
sime     kindel kõneviis lihtminevik 1. isik mitmus aktiiv jaatav kõne lugesime
sin      kindel kõneviis lihtminevik 1. isik ainsus aktiiv jaatav kõne lugesin
site     kindel kõneviis lihtminevik 2. isik mitmus aktiiv jaatav kõne lugesite
ta       kindel kõneviis olevik passiiv eitav kõne                     loeta
tagu     käskiv kõneviis olevik passiiv jaatav kõne                    loetagu
taks     tingiv kõneviis olevik passiiv jaatav kõne                    loetaks
takse    kindel kõneviis olevik passiiv jaatav kõne                    loetakse
tama     supiin passiiv jaatav kõne                                    loetama
tav      kesksõna olevik passiiv jaatav kõne                           loetav
tavat    kaudne kõneviis olevik passiiv jaatav kõne                    loetavat
te       kindel kõneviis olevik 2. isik mitmus aktiiv jaatav kõne      loete
ti       kindel kõneviis lihtminevik passiiv jaatav kõne               loeti
tud      kesksõna minevik passiiv jaatav kõne                          loetud
tuks     tingiv kõneviis minevik passiiv jaatav kõne                   loetuks
tuvat    kaudne kõneviis minevik passiiv jaatav kõne                   loetuvat
v        kesksõna olevik aktiiv jaatav kõne                            lugev
vad      kindel kõneviis olevik 3. isik mitmus aktiiv jaatav kõne      loevad
vat      kaudne kõneviis olevik 1. isik mitmus aktiiv jaatav kõne      (me) lugevat
vat      kaudne kõneviis olevik 1. isik ainsus aktiiv jaatav kõne      (ma) lugevat
vat      kaudne kõneviis olevik 2. isik mitmus aktiiv jaatav kõne      (te) lugevat
vat      kaudne kõneviis olevik 2. isik ainsus aktiiv jaatav kõne      (sa) lugevat
vat      kaudne kõneviis olevik 3. isik mitmus aktiiv jaatav kõne      (nad) lugevat
vat      kaudne kõneviis olevik 3. isik ainsus aktiiv jaatav kõne      (ta) lugevat
======== ============================================================= ===========================


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
     'form': 'pl ad', # word form, in this case plural and allative case
     'lemma': 'raudteejaam', # the dictionary form of the word
     'partofspeech': 'S', # POS tag, in this case substantive
     'root': 'raud_tee_jaam', # root form (same as lemma, but verbs do not have -ma suffix)
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


Phonetic markers
----------------

======= =======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
Marker  Description
======= =======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
<       silp on kolmandas vältes; asetseb vahetult silbi tuuma moodustava täishääliku ees
?       silp on rõhuline; asetseb vahetult silbi tuuma moodustava täishääliku ees (silbi rõhulisust märgitakse ainult sellisel juhul, kui rõhuline silp on midagi muud kui võiks ennustada, ja ennustamine käib järgmiselt: kui sõnas on kolmandas vältes silp, siis rõhk on sellel; muidu, kui sõnas on pika täishääliku või täishäälikuühendiga silp, siis rõhk on sellel; muidu on rõhk esimesel silbil)
]       eelmine häälik on palataliseeritud
~       n ja k ühendis hääldatakse n ja k selgelt eraldi, mitte ei sulandu kokku; kasutuses ainult sõnades soonkond ja tosinkond
======= =======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
