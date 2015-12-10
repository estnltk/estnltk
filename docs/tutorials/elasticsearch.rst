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

To access estnlkt elasticsearch wrappers::

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

