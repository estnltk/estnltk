.. _database_tutorial:

===========================================================
Handling large text collections with ElasticSearch database
===========================================================

.. content ..



Importing data
==============

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

