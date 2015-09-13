.. _database_tutorial:

=====================================================
Handling large text collections with Elastic database
=====================================================

.. content ..

The activate Elastic (formerly Elasticsearch) carry out the guide from the Elastic team
at webpage `https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html`_.

.. _https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html: https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html/

When the installation is complete you can run Elastic (from Elastic folder) with the command::

    ./elasticsearch

Elastic has a visualization plugin that can be accessed through a browser of your choosing.
To do this you need to write  `http://localhost:9200/_plugin/head/`_ to the URL bar in your browser.

.. _http://localhost:9200/_plugin/head/: http://localhost:9200/_plugin/head/

For simple testing purposes one can increase the memory by using --ES_MAX_MEM switch.
Example of using the memory switch::

    ./elasticsearch --ES_MAX_MEM=4g

Bulk importing data
===================

Estnltk comes with an importer script that can be used to store a folder of JSON files to database::

    python3 -m estnltk.database.importer -h
    usage: importer.py [-h] index directory

    Import documents to elasticsearch database

    positional arguments:
      index       The name of the index
      directory   The directory containing JSON files that need to be imported

    optional arguments:
      -h, --help  show this help message and exit


For example, if you have folders ``corpora/eesti`` and ``corpora/koond`` containing the Estonian Wikipedia and
Eesti Koondkorpus, you can insert them using commands::

    python3 -m estnltk.database.importer koond corpora/koond
    python3 -m estnltk.database.importer eesti corpora/eesti


Insert Text object to database
==============================

Estnltk has a python function for inserting Text objects to Elastic database for further analysis.

It is important that you create a database before inserting. In the example there is a database created named 'test'.

After that the Text object is created with a sentence. Then the insert() function is being called.

Example for using the text insert::

    from ..database import Database
    from ...text import Text

    db = Database('test')

    text = Text('Mees, keda seal kohtasime, oli tuttav ja ta teretas meid.')

    db.insert(text)


Searching the database for keywords
===================================

To search from the Elastic database you need to specify the name of the database and the keywords that you need
to start the search for. The function to do the search with is query_documents().

The example search is from the 'test' database and the search word is 'aegna'::

    from ..database import Database

    db = Database('test')

    search = Database.query_documents(db, "aegna")

The search will return a json format query with the full text of the successful search result.