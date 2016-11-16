Change Log
==========

All notable changes to this project will be documented in this file.

[1.4.1]
=======

Added
-----

* ...

Changed
-------

* ...

Fixed
-----

* ...

[1.4.0] - 2016-04-25
====================

Added
-----

* Syntax and dependency parser
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

