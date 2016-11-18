Change Log
==========

All notable changes to this project will be documented in this file.

[1.4.1]
=======


Added
-----
* Improved NER performance using `__slots__` in estner data model;
* Added `sent_tokenizer_for_koond.py` : a sentence tokenizer for processing 'koondkorpus' text files ( as found in http://ats.cs.ut.ee/keeletehnoloogia/estnltk/koond.zip ), which provides several post-processing fixes to known sentence-splitting problems;
* Updated 'koondkorpus' processing scripts `teicorpus.py` and `convert_koondkorpus.py`: added the option to specify the encoding of the input files;
* Added `terminalprettyprinter.py` module, which provides a pretty-printer method that can be used for graphically formatting annotated texts in terminal;
* Added `gt_conversion.py` module that can be used for converting morphological analysis categories from Vabamorf's format to the Giellatekno's (gt) format;
* Added basic [support for syllable extraction](https://github.com/estnltk/estnltk/issues/57#issuecomment-219297186)
* Added EventTagger, KeywordTagger and RegexTagger and fixed basic Tagger API for creating new layers;
* Added adjective phrase tagger (marks fragments such as "väga hea" and "küllalt tore")

Changed
-------

* Updated Temporal expression tagger's and Clause segmenter's jar files to Java version 1.8;
* A major change: re-implementation of syntactic parsing interface:
	* pre-processing scripts of the the VISLCG3-based syntactic analyser were rewritten in Python to ensure platform-independent processing;
	* "estnltk.syntax.tagger.SyntaxTagger" was reimplemented in two modules ("SyntaxPreprocessing" and "VISLCG3Pipeline"), and the modules were made available as a common pipeline in "estnltk.syntax.parsers.VISLCG3Parser";
	* added a possibility to use custom rules in VISLCG3Parser, or to load rules from a custom location;
	* updated MaltParser's model so that surface-syntactic labels are now also generated during the parsing;
	* moved MaltParser-based syntactic analysis and VISLCG3-based syntactic analysis to a common interface; both parsers are now available in the module "estnltk.syntax.parsers";
	* changed how syntactic information is stored in Text: syntactic analyses are now attached in a separate layer (and different layers are created for MaltParser's analyses and VISLCG3's analyses);
	* added "estnltk.syntax.utils.Tree", which provides an interface for making queries over a syntactic tree, and allows to export syntactic analyses as nltk's DependencyGraphs and Trees;
	* added methods for importing syntactically analysed Texts from CG3 and CONLL format files;
* Improved NounPhraseChunker: made it compatible with the new interface of syntactic parsing;
* Converted tutorials to jupyter notebooks to make them runnable and testable;
* Tested and validated tutorials;

Fixed
-----

* Fix a bug in NER feature extraction module with python 3.4;
* Fix in MaltParser's interface: temporary files are now maintained in system specific temp files dir (to avoid permission errors);
* Updated Temporal expression tagger:
	* fixed a TIMEX normalization bug: verb tense information is now properly used;
	* improved TIMEX extraction: re-implemented phrase level joining to provide more accurate extraction of long phrases;
* Fixed [osx installs](https://github.com/estnltk/estnltk/issues/61);
* Updated Vabamorf to fix #55;
* Fixed too restrictive package dependencies;


[1.4.0] - 2016-04-25
====================

Added
-----

* Syntax and dependency parser;
* Support for parsing EstNLTK texts with Java-based Maltparser; Maltparser can be used for obtaining syntactic dependencies between words;
* Experimental NP chunker for Estonian; The chunker picks up NP chunks from the output of Maltparser;
* Disambiguator: added checking for input parameters;


Changed
-------

* VerbChainDetector: intervening punctuation is now ignored during the construction of regular verb chains. See `"test_verbchain_3"` in `"test_verbchains.py"` for a detailed example.
* Improved EstWordTokenizer: made it more aware of utf8 minus, dash and other hyphen-like symbols used instead of the regular hyphen symbol;

Fixed
-----

* Fix on https://github.com/estnltk/estnltk/issues/28 : unit-testing of Java components (with estnltk.run_tests) should now also work under Windows (tested on Windows 10 and with Python 3.4);
* Fix on https://github.com/estnltk/estnltk/issues/56 : improved word_tokenizer: now it should be more aware of mistakenly conjoined sentence endings and beginnings;
* Fix on https://github.com/estnltk/estnltk/issues/39 : verb chains are now annotated as multi-regions;
* Fix on https://github.com/estnltk/estnltk/issues/46 : added a hack solution which allows do to sentence tokenization based on the existing word tokenization;
*  Fixed a bug that caused some timex annotations to disappear after splitting the text into sentences;

