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
* Clause segmenter
* Temporal expression tagger
* Named entity recognition
* Verb chain detector
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


Post-installation steps
-----------------------

Downloading NLTK tokenizers for Estonian::

    python -m nltk.downloader punkt

Building default named entity tagger for Estonian (optional, installation should already come with a pre-trained model)::

    python -m estnltk.ner train_default_model

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
In lexical analysis, tokenization is the process of breaking a stream of text up into words, phrases, symbols, or other meaningful elements called tokens.
The list of tokens becomes input for further processing such as parsing or text mining.
Tokenization is useful both in linguistics (where it is a form of text segmentation), and in computer science, where it forms part of lexical analysis.


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
     'Keeletehnoloogid kasutavad arvutilingvistikas välja töötatud \nteooriaid, 
        et luua rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt 
        arvuti abil töödelda ja mõista. ', 
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and tokenized paragraphs::

    ['Keeletehnoloogia on arvutilingvistika praktiline pool.\nKeeletehnoloogid 
        kasutavad arvutilingvistikas välja töötatud \nteooriaid, et luua 
        rakendusi (nt arvutiprogramme), \nmis võimaldavad inimkeelt arvuti 
        abil töödelda ja mõista.',
     'Tänapäeval on keeletehnoloogia tuntumateks valdkondadeks \nmasintõlge, 
        arvutileksikoloogia, dialoogisüsteemid, \nkõneanalüüs ja kõnesüntees.\n']

and also the original full text can be accessed using ``text`` property of :class:`estnltk.corpus.Document`.
In case you get an error during tokenization, something like::

    LookupError: 
    **********************************************************************
      Resource u'tokenizers/punkt/estonian.pickle' not found.  Please
      use the NLTK Downloader to obtain the resource:  >>>
      nltk.download()

Then you have forgot post-installation step of downloading NLTK tokenizers. This can be done by invoking command::

    python -m nltk.downloader punkt

Token spans -- start and end positions
--------------------------------------

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

In linguistics, morphology is the identification, analysis, and description of the structure of a given language's morphemes and other linguistic units,
such as root words, lemmas, affixes/endings, parts of speech.

In morphology and lexicography, a lemma (plural lemmas or lemmata) is the canonical form, dictionary form, or citation form of a set of words (headword).
In grammar, a part of speech (also a word class, a lexical class, or a lexical category) is a linguistic category of words (or more precisely lexical items),
which is generally defined by the syntactic or morphological behaviour of the lexical item in question.
Common linguistic categories include noun and verb, among others.
Word forms define additional grammatical information such as cases, plurality etc.


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


The lemmas / stemmed words::
    
    ['keeletehnoloogia', 'olema', 'arvutilingvistika', 'praktiline', 'pool', 'keeletehnoloog', 
    'kasutama', 'arvutilingvistika', 'väli', 'töötatud', 'teooria', ',', 'et', 'looma', 
    'rakendus', '(', 'nt', 'arvutiprogramm', ')', ',', 'mis', 'võimaldama', 'inimkeel', 
    'arvuti', 'abi', 'töötlema', 'ja', 'mõistma', 'tänapäev', 'olema', 'keeletehnoloogia', 
    'tuntum', 'valdkond', 'masintõlge', ',', 'arvutileksikoloogia', ',', 'dialoogisüsteem', 
    ',', 'kõneanalüüs', 'ja', 'kõnesüntees']

The pos tags::

    ['S', 'V', 'S', 'A', 'S', 'S', 'A', 'S', 'S', 'A', 'S', 'Z', 'J', 'S', 'S', 'Z', 'Y', 
    'S', 'Z', 'Z', 'P', 'A', 'S', 'S', 'K', 'V', 'J', 'V', 'S', 'V', 'S', 'C', 'S', 'S', 
    'Z', 'S', 'Z', 'S', 'Z', 'S', 'J', 'S']

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

See `documentation`_ for possible parameters.

    .. _documentation: https://github.com/Filosoft/vabamorf/blob/master/doc/tagset.html

Clause segmenter
================
A simple sentence, also called an independent clause, typically contains a finite verb, and expresses a complete thought.
However, in many cases, natural language sentences are long and complex, consisting of two or more clauses joined together.
The clause structure can be made even more complex by embedded clauses, which are inserted into other clauses, and divide their parents into two halves.

Clause segmenter makes it possible to extract clauses from a complex sentence and treat them independently::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, ClauseSegmenter
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter()

    text = '''Mees, keda seal kohtasime, oli tuttav ja teretas meid.'''

    segmented = segmenter(analyzer(tokenizer(text)))

Clause segmenter requires that the input text has been tokenized (split into sentences and words) and morphologically analyzed (and also disambiguated, if possible).
The segmenter annotates clause boundaries between words, and start and end locations of embedded clauses. 
Based on the annotation, each word in the sentence is associated with a clause index. 
Following is an example on how to access both the initial clause annotations, and also clause indexes of the words::

    # Clause indices and annotations
    pprint(list(zip(segmented.words, segmented.clause_indices, segmented.clause_annotations)))

    [('Word(Mees)', 0, None),
     ('Word(,)', 1, 'embedded_clause_start'),
     ('Word(keda)', 1, None),
     ('Word(seal)', 1, None),
     ('Word(kohtasime)', 1, None),
     ('Word(,)', 1, 'embedded_clause_end'),
     ('Word(oli)', 0, None),
     ('Word(tuttav)', 0, None),
     ('Word(ja)', 0, 'clause_boundary'),
     ('Word(teretas)', 2, None),
     ('Word(meid.)', 2, None)]

There is also a  :class:`estnltk.corpus.Clause` type, that can be queried from the corpus::

    # The clauses themselves
    pprint(segmented.clauses)
    
    ['Clause(Mees oli tuttav ja [clause_index=0])',
     'Clause(, keda seal kohtasime , [clause_index=1])',
     'Clause(teretas meid. [clause_index=2])']

Here is also an example of how to group words by clauses::

    # Words grouped by clauses
    for clause in segmented.clauses:
        pprint(clause.words)
        
    ['Word(Mees)', 'Word(oli)', 'Word(tuttav)', 'Word(ja)']
    ['Word(,)', 'Word(keda)', 'Word(seal)', 'Word(kohtasime)', 'Word(,)']
    ['Word(teretas)', 'Word(meid.)']

Named entity recognition
========================

Named-entity recognition (NER) (also known as entity identification, entity chunking and entity extraction) is a subtask of information extraction that seeks to locate
and classify elements in text into pre-defined categories such as the names of persons, organizations, locations.
First thing is to build the named entity model as it is too large to include in the package itself. Do it by invoking command::

    python -m estnltk.ner train_default_model

This will build the default model tuned for named entity recognition in news articles.
In order to use named entity tagging, you also need to perform morphological analysis first.
A quick example, how to do it::

    from estnltk import Tokenizer, PyVabamorfAnalyzer, NerTagger
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    tagger = NerTagger()

    text = '''Eesti Vabariik on riik Põhja-Euroopas. 
    Eesti piirneb põhjas üle Soome lahe Soome Vabariigiga.

    Riigikogu on Eesti Vabariigi parlament. Riigikogule kuulub Eestis seadusandlik võim.

    2005. aastal sai peaministriks Andrus Ansip, kes püsis sellel kohal 2014. aastani.
    2006. aastal valiti presidendiks Toomas Hendrik Ilves.
    '''

    # tag the documents
    ner_tagged = tagger(analyzer(tokenizer(text)))

    # print the words and their explicit labels in BIO notation
    pprint(list(zip(ner_tagged.word_texts, ner_tagged.labels)))
    

As a result, we see the list of words with annotated labels::

    [('Eesti', 'B-LOC'),
     ('Vabariik', 'I-LOC'),
     ('on', 'O'),
     ('riik', 'O'),
     ('Põhja-Euroopas.', 'B-LOC'),
     ('Eesti', 'B-LOC'),
     ('piirneb', 'O'),
     ('põhjas', 'O'),
     ('üle', 'O'),
     ('Soome', 'B-LOC'),
     ('lahe', 'I-LOC'),
     ('Soome', 'B-LOC'),
     ('Vabariigiga.', 'O'),
     ('Riigikogu', 'B-ORG'),
     ('on', 'O'),
     ('Eesti', 'B-LOC'),
     ('Vabariigi', 'I-LOC'),
     ('parlament.', 'O'),
     ('Riigikogule', 'B-ORG'),
     ('kuulub', 'O'),
     ('Eestis', 'B-LOC'),
     ('seadusandlik', 'O'),
     ('võim.', 'O'),
     ('2005.', 'O'),
     ('aastal', 'O'),
     ('sai', 'O'),
     ('peaministriks', 'O'),
     ('Andrus', 'B-PER'),
     ('Ansip', 'I-PER'),
     (',', 'O'),
     ('kes', 'O'),
     ('püsis', 'O'),
     ('sellel', 'O'),
     ('kohal', 'O'),
     ('2014.', 'O'),
     ('aastani.', 'O'),
     ('2006.', 'O'),
     ('aastal', 'O'),
     ('valiti', 'O'),
     ('presidendiks', 'O'),
     ('Toomas', 'B-PER'),
     ('Hendrik', 'I-PER'),
     ('Ilves.', 'I-PER')]

Named entity tags are encoded using a widely accepted BIO annotation scheme, where each label is prefixed with B or I, or the entire label is given as O.
**B-** denotes the *beginning* and **I-** *inside* of an entity, while **O** means *omitted*.
This can be used to detect entities that consist of more than a single word as can be seen in above example.

It is also possible to query directly :class:`estnltk.corpus.NamedEntity` objects from tagged corpora.
This makes it easy to see all words that are grouped into a named entity::

    pprint (ner_tagged.named_entities)
    
    ['NamedEntity(eesti vabariik, LOC)',
     'NamedEntity(põhja-euroopa, LOC)',
     'NamedEntity(eesti, LOC)',
     'NamedEntity(soome lahe, LOC)',
     'NamedEntity(soome, LOC)',
     'NamedEntity(riigikogu, ORG)',
     'NamedEntity(eesti vabariik, LOC)',
     'NamedEntity(riigikogu, ORG)',
     'NamedEntity(eesti, LOC)',
     'NamedEntity(andrus ansip, PER)',
     'NamedEntity(toomas hendrik ilves, PER)']

See :class:`estnltk.corpus.NamedEntity` documentation for information on available properties.


Temporal expression (TIMEX) tagging
===================================

Temporal Expressions Tagger identifies temporal expressions (timexes) in text and normalizes these expressions (that is, finds calendaric dates and times corresponding to the expressions). The program outputs an annotation in a format similar to TimeML's TIMEX3 (see TODO for more details). 

According to TimeML, four types of temporal expressions are distinguished: 

* DATE expressions, e.g. *järgmisel kolmapäeval* (*on next Wednesday*)
* TIME expressions, e.g. *kell 18.00* (*at 18.00 o’clock*)
* DURATIONs, e.g. *viis päeva* (*five days*)
* SETs of times, e.g. *igal aastal* (*on every year*)

Temporal Expressions Tagger requires that the input text has been tokenized (split into sentences and words), and morphologically analyzed (and also disambiguated, if possible).

Example::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer
    from estnltk import TimexTagger
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    tagger = TimexTagger()

    text = ''''Potsataja ütles eile, et vaatavad nüüd Genaga viie aasta plaanid uuesti üle.'''
    tagged = tagger(analyzer(tokenizer(text)))

    pprint(tagged.timexes)

This prints found temporal expressions::

    [['Timex(eile, DATE, 2014-12-02, [timex_id=1])',
     'Timex(nüüd, DATE, PRESENT_REF, [timex_id=2])',
     'Timex(viie aasta, DURATION, P5Y, [timex_id=3])']

Note that the relative temporal expressions (such as *eile* (*yesterday*)) are normalized according to the date when the program was run (in the previous example: December 3, 2014). 
This behaviour can be changed by supplying `creation_date` argument to the tagger.
For example, let's tag the text given date June 10 1995::

    # retag with a new creation date
    import datetime

    tagged = tagger(tagged, creation_date=datetime.datetime(1995, 6, 10))
    pprint(tagged.timexes)
    
    ['Timex(eile, DATE, 1995-06-09, [timex_id=1])',
     'Timex(nüüd, DATE, PRESENT_REF, [timex_id=2])',
     'Timex(viie aasta, DURATION, P5Y, [timex_id=3])']

See :class:`estnltk.corpus.Timex` documentation for available attributes.


Verb chain detection
====================

In linguistics, a verb phrase or VP is a syntactic unit composed of at least one verb and its dependents—objects, complements and other modifiers—but not always including the subject.

Example::

    from estnltk import Tokenizer
    from estnltk import PyVabamorfAnalyzer
    from estnltk import ClauseSegmenter
    from estnltk import VerbChainDetector
    from pprint import pprint

    tokenizer = Tokenizer()
    analyzer = PyVabamorfAnalyzer()
    segmenter = ClauseSegmenter()
    detector = VerbChainDetector()

    text = ''''Samas on selge, et senine korraldus jätkuda ei saa.'''
    processed = detector(segmenter(analyzer(tokenizer(text))))

    # print timex objects
    pprint(processed.verb_chains)

This will print out the descriptions of found verb chains::

    ['VerbChain(on, ole, ole, POS)',
     'VerbChain(korraldus, verb, korraldu, POS)',
     'VerbChain(jätkuda ei saa., ei+verb+verb, ei_saa_jätku, NEG)']

Verb chain detection requires segmented clauses in input corpus, therefore we must use :class:`estnltk.clausesegmenter.ClauseSegmenter` class to analyze the data.
Property :class:`estnltk.corpus.Corpus.verb_chain` lists all found :class:`estnltk.corpus.VerbChain` objects.


Estonian Wordnet
================

TODO: Add KOM documentation here.

Understanding JSON notation and Estnltk corpora
===============================================

Here is a detailed description of the JSON structure and how it relates to Corpus objects in Estnltk.


Reading TEI corpora (koondkorpus, tasakaalustatud korpus)
---------------------------------------------------------

Example, how to read files of koondkorpus and tasakaalustatud korpus with Estnltk.


Using Python NLTK corpus readers with Estnltk
----------------------------------------------

Guidelines for using NLTK corpus readers with Estnltk.


Text classifier tool
====================

TODO: add text classifier tool documentation here.

Contents
=========

.. toctree::
   :maxdepth: 2

   estnltk.rst
   modules.rst
   estnltk.textclassifier.rst
   estnltk.estner.rst
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


