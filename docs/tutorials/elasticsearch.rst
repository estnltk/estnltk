.. _database_tutorial:

=====================================================
Handling large text collections with Elastic database
=====================================================

Estnltk has database module that simplifies working with large corpora.
Check out :ref:`wikipedia_tutorial`, :ref:`tei_tutorial` for more information
about getting started with larger text document collections.

Estnltk database integrates with `Elastic`_, which is a distributed RESTful schema-free
JSON database, based on `Apache Lucene`_.
See this `guide`_ for installation.

.. _Elastic: https://www.elastic.co/downloads/elasticsearch
.. _Apache Lucene: https://lucene.apache.org/
.. _guide: https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html

When the installation is complete you can run Elastic (from Elastic folder) with the command::

    ./bin/elasticsearch

.. hint::
If you have trouble running Elastic, please refer to `Elastic guide`_.
  Do your research before asking us. Estnltk has only a very thin wrapper around the `Elastic Python API`_ .

.. _Elastic guide: https://www.elastic.co/guide/index.html
.. _Elastic Python API: https://elasticsearch-py.readthedocs.org/en/master/


Estnltk Elastic wrapper
=======================

To access estnltk elasticsearch wrappers::

    from estnlkt.database.elastic import *

To create an index::

    index = create_index('demo_index')

Or to connect to an existing index::

    index = connect('demo_index')

To specify non-default arguments to elasticsearch connection, you can either pass the parameters to either method or create and Index instance manually, passing the Elastic python API client object as the first parameter.

These methods return an index object that has two important methods: save and sentences::

    t = Text('See on demolause. Sellele järgneb veel üks.')
    index.save(t)

    for sentence in index.sentences():
        print(t.lemmas) #note that the sentences generator returns estnltk Text objects by default.


To see the mapping and data structure in the elasticsearch index, refer to the mappings.py file.

Iterating over corpora
======================

To iterate over the entire corpus use the Index.sentences generator. In the general case it is enough to do::

    index = connect('demo_index')
    for sentence in index.sentences():
        print(index)


Iterating over query results
============================

To iterate over query results, pass the elasticsearch query to the sentences generator as the "query" parameter. The query should be a dictionary as expected by elasticsearch python API. It will be transformed into json before being transmitted.

To simplify writing some queries, see the query_helper module. It defines the Word class that maps well to estnltk morphological analysis results.
The general workflow is:

1. Define words to match with the Word class.
2. Combine them with boolean operators "&" and "|"
3. Wrap them in a Grammar object
4. Get the query via the Grammar.query() method.
5. Annotate the results with the Grammar.annotate() method that creates a layer that marks the matching words.

For example::

    grammar = Grammar(Word(lemma='karu') & Word(lemma='jahimees') & Word(partofspeech='V'))
    for sentence in index.sentences(query=grammar.query()):
        grammar.annotate(sentence, 'result')

The results can be visualised with the PrettyPrinter class or worked on using any other standard tools that work on estnltk layers.
