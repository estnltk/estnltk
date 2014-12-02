.. estnltk documentation master file, created by
   sphinx-quickstart on Fri Nov 28 13:32:28 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

======================================================================
Estnltk --- Open source tools for Estonian natural language processing
======================================================================

Estnltk is a Python 2.7/Python 3.4 library for performing common language processing tasks in Estonian.
Although there are already many tools for processing Estonian, it is often not very trivial to interface them in applications or more complex research projects.
Extra work is required to write application specific interfaces each time a tool is used.

Another problem is that many of these tools are scattered around the web and are hard to find if you do not know where to look.
Although we have `keeleveeb.ee`_ and `EKT`_, `EKKTT`_ project pages, it can be hard for students and non-language people to dive in.
The aim of the project is to tie together a number of open source components so that they could be used easily:

.. _keeleveeb.ee: http://www.keeleveeb.ee/
.. _EKT: https://www.keeletehnoloogia.ee/et
.. _EKKTT: https://www.keeletehnoloogia.ee/et

* Word and sentence tokenization
* Morphological analysis and generation
* Lemmatization / stemming
* Clause detection
* Time expression detection
* Named entity recognition
* Estonian Wordnet integration.

The above list is actually only a modest fraction of different tools available, but is large enough to cover most basic uses cases.
Hopfully we are able to integrate more and more tools in future.


Installation
============

We do not recommend building the library from source in Windows as it can be very time-consuming.
Instead, we provide binary installers that can be downloaded from project `repository`_.

.. _repository:: https://github.com/tpetmanson/estnltk

Installers for 32 and 64 bit versions of Python2.7 and Python3.4:

* installer1
* installer2
* installer3
* installer4

However, in order to get it working, you need to install these dependencies:
TODO: try to put them all in a single installer

* pyvabamorf
* nltk
* whatever else

Next step is to download nltk data.

Building from source
--------------------

To build the `estnltk` module from source, we recommend using Visual Studio 2008 for Python2.7 and Visual Studio 2010 for Python3.4.
Note that for 64-bit versions you need to have also 64-bit toolchains, which are not included in Express versions of the Visual Studio.
Please read the Linux section of required dependencies.

Linux
-----

Although much development of the library is done in Linux, there are no pre-built binaries.
Fortunately, building software from source in Linux is somewhat easier than in Windows, so we provide the necessary steps.

First, you need to have installed following dependencies (typically installable from the package manager of your distro):

* Python development files
* GCC C++ compiler
* SWIG wrapper generator
* list here dependencies of dependencies etc.


There are no pre-built binaries for Linux. For building, you need to have installed Python development files (headers and libraries), GCC C++ compiler and also SWIG wrapper generator ( http://swig.org/ ). Depending on your distribution, you might be able to simply install them from software repositories of your distribution.

After all dependencies are installed, the easiest way to build the pyvabamorf package is using the pip tool:

sudo pip install pyvabamorf
Another way is to clone the repository and execute the setup.py script inside:

sudo python setup.py install
Then run the tests and see if they all pass (NB! Do not run them from same directory you have cloned the source distribution):



========
Tutorial
========

As they say, it is best to learn by example.
In this section, we cover all basic use cases of the library.
We recommend that the user would read the tutorial and try out the examples themselves to become comfortable with the library.
The source code for the examples can also be found in `estnltk/examples` directory of the package.


Paragraph, sentence and word tokenization
=========================================

The first step in most text processing tasks is to tokenize the input into smaller pieces, typically paragraphs, sentences and words.
Estnltk provides the :class:`estnltk.tokenize.Tokenizer` class that does this.
In the next example, we define some text, then import and initialize a :class:`estnltk.tokenize.Tokenizer` instance and use to create a :class:`estnltk.corpus.Document` instance::

    # Let's define a sample document
    text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
    Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
    teooriaid, et luua rakendusi (nt arvutiprogramme), 
    mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

    Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
    masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
    kõneanalüüs ja kõnesüntees.
    '''

    # tokenize it using default tokenizer
    from estnltk import Tokenizer
    tokenizer = Tokenizer()
    document = tokenizer.tokenize(text)

    # tokenized results
    print (document.word_texts)
    print (document.sentence_texts)
    print (document.paragraph_texts)
    print (document.text)

    
This will print out the tokenized words::

    ['Keeletehnoloogia', 'on', 'arvutilingvistika', 'praktiline', 'pool.', 'Keeletehnoloogid', 
    'kasutavad', 'arvutilingvistikas', 'välja', 'töötatud', 'teooriaid', ',', 'et', 'luua', 
    'rakendusi', '(', 'nt', 'arvutiprogramme', ')', ',', 'mis', 'võimaldavad', 'inimkeelt', 
    'arvuti', 'abil', 'töödelda', 'ja', 'mõista.', 'Tänapäeval', 'on', 'keeletehnoloogia', 
    'tuntumateks', 'valdkondadeks', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteemid', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees.']
    
and tokenized sentences::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.', 
    'Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud \nteooriaid, et luua rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt arvuti abil töödelda ja mõista. ', 
    'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and tokenized paragraphs::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.\nKeeletehnoloogid kasutavad arvutilingvistikas välja töötatud \nteooriaid, et luua rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt arvuti abil töödelda ja mõista.',
    'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and also the original full text can be accessed using ``text`` property of :class:`estnltk.corpus.Document`::

Token spans -- start and end positions
======================================

In addition to tokenization, it is often necessary to know where the tokens reside in the original document.
For example, you might want to inspect the context of a particular word.
For this purpose, estnltk provide ``word_spans``, ``sentence_spans`` and ``paragraph_spans`` methods.
Following the previous example, we can group together words and their start and end positions 
in the document using the following::

    zip(document.word_texts, document.word_spans)
    
This will create a list of tuples, where the first element is the tokenized word and the second element is a tuple
containing the start and end positions::

    [('Keeletehnoloogia', (0, 16)),
     ('on', (17, 19)),
     ('arvutilingvistika', (20, 37)),
     ('praktiline', (38, 48)),
     ('pool.', (49, 54)),
     ...
     ('kõneanalüüs', (340, 351)),
     ('ja', (352, 354)),
     ('kõnesüntees.', (355, 367))]

For other possible options, please check :class:`estnltk.corpus.Corpus`, :class:`estnltk.corpus.Document`, :class:`estnltk.corpus.Paragraph`, :class:`estnltk.corpus.Sentence` and :class:`estnltk.corpus.Word` classes.


Morphological analysis
======================

Estnltk contains :class:`estnltk.morf.analyze` function for performing morphological analysis::

    from estnltk import analyze
    from pprint import pprint

    pprint(analyze('Tüünete öötööde allmaaraudteejaam'))

The result will be JSON-style data::

    [{'analysis': [{'clitic': '',
                    'ending': 'te',
                    'form': 'pl g',
                    'lemma': 'tüüne',
                    'partofspeech': 'A',
                    'root': 'tüüne',
                    'root_tokens': ['tüüne']}],
      'text': 'Tüünete'},
     {'analysis': [{'clitic': '',
                    'ending': 'de',
                    'form': 'pl g',
                    'lemma': 'öötöö',
                    'partofspeech': 'S',
                    'root': 'öö_töö',
                    'root_tokens': ['öö', 'töö']}],
      'text': 'öötööde'},
     {'analysis': [{'clitic': '',
                    'ending': '0',
                    'form': 'sg n',
                    'lemma': 'allmaaraudteejaam',
                    'partofspeech': 'S',
                    'root': 'all_maa_raud_tee_jaam',
                    'root_tokens': ['all', 'maa', 'raud', 'tee', 'jaam']}],
      'text': 'allmaaraudteejaam'}]

Note that the underlying `vabamorf`_ library does not yet include disambiguation, so all possible analysis will be returned.
The tags are documented in vabamorf tagset `documentation`_.

    .. _vabamorf: https://github.com/Filosoft/vabamorf/
    .. _documentation: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html


The morphological analysis can also be applied on pretokenized data, so it will be possible to more easily list all lemmas, pos tags etc.
To do that, one needs to use :class:`estnltk.morf.PyVabamorfAnalyzer` class::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()

    text = '''Keeletehnoloogia on arvutilingvistika praktiline pool.
    Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud 
    teooriaid, et luua rakendusi (nt arvutiprogramme), 
    mis võimaldavad inimkeelt arvuti abil töödelda ja mõista. 

    Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks 
    masintõlge, arvutileksikoloogia, dialoogisüsteemid, 
    kõneanalüüs ja kõnesüntees.
    '''

    # first tokenize and then morphologically analyze
    morf_analyzed = analyzer(tokenizer(text))

    # print some results
    print (morf_analyzed.lemmas)
    print (morf_analyzed.postags)
    
    # print more information together
    pprint (list(zip(morf_analyzed.word_texts,
                     morf_analyzed.lemmas,
                     morf_analyzed.forms,
                     morf_analyzed.postags)))


The lemmas::
    
    ['keeletehnoloogia', 'olema', 'arvutilingvistika', 'praktiline', 'pool', 'keeletehnoloog', 'kasutama', 'arvutilingvistika', 'väli', 'töötatud', 'teooria', ',', 'et', 'looma', 'rakendus', '(', 'nt', 'arvutiprogramm', ')', ',', 'mis', 'võimaldama', 'inimkeel', 'arvuti', 'abi', 'töötlema', 'ja', 'mõistma', 'tänapäev', 'olema', 'keeletehnoloogia', 'tuntum', 'valdkond', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteem', ',', 'kõneanalüüs', 'ja', 'kõnesüntees']

The pos tags::

    ['S', 'V', 'S', 'A', 'S', 'S', 'A', 'S', 'S', 'A', 'S', 'Z', 'J', 'S', 'S', 'Z', 'Y', 'S', 'Z', 'Z', 'P', 'A', 'S', 'S', 'K', 'V', 'J', 'V', 'S', 'V', 'S', 'C', 'S', 'S', 'Z', 'S', 'Z', 'S', 'Z', 'S', 'J', 'S']

More information put together::

    [('Keeletehnoloogia', 'keeletehnoloogia', 'sg g', 'S'),
     ('on', 'olema', 'b', 'V'),
     ('arvutilingvistika', 'arvutilingvistika', 'sg g', 'S'),
     ('praktiline', 'praktiline', 'sg n', 'A'),
     ('pool.', 'pool', 'sg n', 'S'),
     ('Keeletehnoloogid', 'keeletehnoloog', 'pl n', 'S'),
     ('kasutavad', 'kasutama', 'pl n', 'A'),
     ('arvutilingvistikas', 'arvutilingvistika', 'sg in', 'S'),
     ('välja', 'väli', '', 'S'),
     ('töötatud', 'töötatud', 'pl n', 'A'),
     ('teooriaid', 'teooria', 'pl p', 'S'),
     (',', ',', '', 'Z'),
     ('et', 'et', '', 'J'),
     ('luua', 'looma', 'da', 'S'),
     ('rakendusi', 'rakendus', 'pl p', 'S'),
     ('(', '(', '', 'Z'),
     ('nt', 'nt', '?', 'Y'),
     ('arvutiprogramme', 'arvutiprogramm', 'pl p', 'S'),
     (')', ')', '', 'Z'),
     (',', ',', '', 'Z'),
     ('mis', 'mis', 'pl n', 'P'),
     ('võimaldavad', 'võimaldama', 'pl n', 'A'),
     ('inimkeelt', 'inimkeel', 'sg p', 'S'),
     ('arvuti', 'arvuti', 'sg g', 'S'),
     ('abil', 'abi', '', 'K'),
     ('töödelda', 'töötlema', 'da', 'V'),
     ('ja', 'ja', '', 'J'),
     ('mõista.', 'mõistma', 'da', 'V'),
     ('Tänapäeval', 'tänapäev', 'sg ad', 'S'),
     ('on', 'olema', 'b', 'V'),
     ('keeletehnoloogia', 'keeletehnoloogia', 'sg g', 'S'),
     ('tuntumateks', 'tuntum', 'pl tr', 'C'),
     ('valdkondadeks', 'valdkond', 'pl tr', 'S'),
     ('masintõlge', 'masintõlge', 'sg n', 'S'),
     (',', ',', '', 'Z'),
     ('arvutileksikoloogia', 'arvutileksikoloogia', 'sg g', 'S'),
     (',', ',', '', 'Z'),
     ('dialoogisüsteemid', 'dialoogisüsteem', 'pl n', 'S'),
     (',', ',', '', 'Z'),
     ('kõneanalüüs', 'kõneanalüüs', 'sg n', 'S'),
     ('ja', 'ja', '', 'J'),
     ('kõnesüntees.', 'kõnesüntees', 'sg n', 'S')]


Morphological synthesis
=======================

Estnltk can also do morphological synthesis using :class:`estnltk.morf.synthesize` function::

    from estnltk import synthesize

    print(synthesize('pood', form='pl p', partofspeech='S'))
    print(synthesize('palk', form='sg kom'))

That will print::

    ['poode', 'poodisid']
    ['palgaga', 'palgiga']

Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: estnltk

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

