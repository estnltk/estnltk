Change Log
==========

All notable changes to this project will be documented in this file.


[1.6.2-beta] - 2018-04-16
=========================
Changed
-------
 * Moved command line scripts for processing etTenTen and koondkorpus from `estnltk/corpus_processing` to `corpus_processing`;
 * The command line scripts for processing etTenTen and koondkorpus were remade in a way that they both use the JSON format of the version 1.6 for storing intermediate results;
 * Restructured tutorials: `basic_nlp_toolchain.ipynb` was split into 7 separate tutorials and moved to `tutorials/nlp_pipeline`. Morphology and syntax-related tutorials were also move to `tutorials/nlp_pipeline`;


Added
-----
* Functionality to store and query text objects in the Postgres database.
* Tagger `AddressGrammarTagger` to extract address information from text.
* Tutorial demonstrating how to extract addresses from text using `AddressGrammarTagger` and store results in the Postgres database (tutorials/postgres/storing_text_objects_in_postgres.ipynb).
* Module `parse_koondkorpus.py`, which can be used for loading texts from XML TEI files of the Estonian Reference Corpus as EstNLTK Text objects. The module was ported from the version 1.4.1.1 and improved upon. Improvements: default encoding is now 'utf-8', and there is a working option to preserve the original sentence and paragraph tokenization from the XML files;
* Tutorial about loading XML TEI files with EstNLTK;
* Added more helpful scripts for processing large corpora (a script for random selection and clean-up of files);
* Added AdjectivePhraseTagger (ported from version 1.4.1.1);


[1.6.1-beta] - 2018-03-27
=========================
Changed
-------
* Redesigned Tagger base class. The deprecated TaggerOld is also in use so far.
* Moved morphology-related modules from `estnltk/taggers/` to `estnltk/taggers/morph/`;
* Moved functions that convert between Vabamorf dicts and EstNLTK's Spans to `estnltk/taggers/morph/morf_common.py`;
* Updated _make\_resolver_: default parameters for morphological analysis are now taken from `morf_common.py`;
* Updated SentenceTokenizer: _base\_sentence\_tokenizer_ is now customizable (e.g. [LineTokenizer](http://www.nltk.org/api/nltk.tokenize.html#nltk.tokenize.simple.LineTokenizer) can be used to split into sentences by newlines);


Added
-----
* Finite grammar module and GrammarParsingTagger.
* New taggers GapTagger, EnvelopingGapTagger, PhraseTagger, SpanTagger and vocabulary reading methods for PhraseTagger and SpanTagger.
* Added command line scripts that can be used for processing etTenTen and Koondkorpus;
* Added JavaProcess (ported from version 1.4.1.1);
* Added ClauseSegmenter (ported from version 1.4.1.1). Layer 'clauses' can now be added to the Text object. _Note_: this adds Java dependency to the EstNLTK: Java SE Runtime Environment (version >= 1.8) must be installed into the system and available from the PATH environment variable;
* Added UserDictTagger, which can be used to provide dictionary-based post-corrections to morphological analyses;

Fixed
-----
* Bugfix in PostMorphAnalysisTagger: postcorrections are no longer applied to empty spans;
* Bugfix in VabamorfTagger: _layer\_name_ can now be changed without running into errors;
* Fix in GTMorphConverter: added the missing disambiguation step. Clause annotations are now used to resolve the ambiguities related to conversion of _sid_, _ksid_, _nuksid_ forms;
* SyntaxIgnoreTagger: improved detection of parenthesized acronyms;
* CompoundTokenTagger: improved detection of numbers with percentages;


[1.6.0-beta] - 2017-12-23
=========================
EstNLTK has gone through a major redesign of the interface.
Changes include re-designing the interface of a basic data structure (the Text class), re-designing interfaces of analysis tools, up to the level of morphological analysis, and improving quality of basic text operations (such as sentence and word segmentation).

Changed
-------
* EstNLTK no longer supports Python 2.7. 
Recommended Python's version is 3.5;
* Text class has been redesigned. 
Text annotations are now decomposed into Span-s, SpanList-s and Layer-s;
* A common class for text annotators -- Tagger class -- has been introduced;
* Word segmentation has been redesigned. 
It is now a three-step process, which includes basic tokenization (layer 'tokens'), creation of compound tokens (layer 'compound\_tokens'), and creation of words (layer 'words') based on 'tokens' and 'compound\_tokens'.
Token compounding rules that are aware of text units containing punctuation (such as abbreviations, emoticons, web addresses) have been implemented;
* The segmentation order has been changed: word segmentation now comes before the sentence segmentation, and the paragraph segmentation comes after the sentence segmentation; 
* Sentence segmentation has been redesigned. 
Sentence segmenter is now aware of the compound tokens (fixing compound tokens can improve sentence segmentation results), and special post-correction steps are applied to improve quality of sentence segmentation;
* Morphological analysis interface has been redesigned.
Morphological analyses are no longer attached to the layer 'words' (although they can be easily accessed through the words, if needed), but are contained in a separate layer named 'morph_analysis'.
* Morphological analysis process can now more easily decomposed into analysis and disambiguation (using special taggers VabamorfAnalyzer and VabamorfDisambiguator).
Also, a tagger responsible for post-corrections of morphological analysis (PostMorphAnalysisTagger) has been introduced, and post-corrections for improving quality of part of speech, and quality of analysis of numbers and pronouns have been implemented;
* Rules for converting morphological analysis categories from Vabamorf's format to GT (giellatekno) format have been ported from the previous version of EstNLTK.
Note, however, that the porting is not complete: full functionality requires 'clauses' annotation (which is currently not available);
* ...
* Other components of EstNLTK (such as the temporal expression tagger, and the named entity recognizer) are yet to be ported to the new version in the future;

Added
-----
* SyntaxIgnoreTagger, which can be used for detecting parts of text that should be ignored by the syntactic analyser.
Note: it is yet to be integrated with the pre-processing module of syntactic analysis;



[1.4.0] - 2016-04-25
====================

Added
-----

* Support for parsing EstNLTK texts with Java-based Maltparser; Maltparser can be used for obtaining syntactic dependencies between words
* Experimental NP chunker for Estonian; The chunker picks up NP chunks from the output of Maltparser
* Disambiguator: added checking for input parameters;

Changed
-------

* VerbChainDetector: intervening punctuation is now ignored during the construction of regular verb chains. See "test_verbchain_3" in "test_verbchains.py" for a detailed example.
* Improved EstWordTokenizer: made it more aware of utf8 minus, dash and other hyphen-like symbols used instead of the regular hyphen symbol;

Fixed
-----

* Fix on https://github.com/estnltk/estnltk/issues/28 : unit-testing of Java components (with estnltk.run_tests) should now also work under Windows (tested on Windows 10 and with Python 3.4);
* Fix on https://github.com/estnltk/estnltk/issues/56 : improved word_tokenizer: now it should be more aware of mistakenly conjoined sentence endings and beginnings;
* Fix on https://github.com/estnltk/estnltk/issues/39 : verb chains are now annotated as multi-regions;
* Fix on https://github.com/estnltk/estnltk/issues/46 : added a hack solution which allows do to sentence tokenization based on the existing word tokenization;
*  Fixed a bug that caused some timex annotations to disappear after splitting the text into sentences;

