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

Tutorials
=========

.. toctree::
    :maxdepth: 2
    
    installation.rst
    
    tutorials/textdiagnostics.rst
    tutorials/tokenization.rst
    tutorials/morf_analysis.rst
    tutorials/clause_segmenter.rst
    tutorials/ner.rst
    tutorials/timex.rst
    tutorials/verbchain.rst
    tutorials/wordnet.rst
    tutorials/importing_tei.rst
    tutorials/json_format.rst
    tutorials/textclassifier_tutorial.rst


API reference
=============

.. toctree::
   :maxdepth: 2

   estnltk.rst
   estnltk.pyvabamorf.rst
   estnltk.mw_verbs.rst
   estnltk.wordnet.rst
   estnltk.textclassifier.rst
   estnltk.estner.rst
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


