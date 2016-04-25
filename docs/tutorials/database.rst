.. _database_tutorial:

Note! The interface described here should be considered deprecated. See the code and documentation for estnltk.database.elastic.

Estnltk Elastic wrapper
=======================

Estnlt has :py:class:`~estnltk.database.database.Database` class that represents a single index of Elastic.
The most important thing to know is the constructor signature::

    def __init__(self, index, doc_type='document', **kwargs):
        """
        Parameters
        ----------
        index: str
            The name of the Elastic index.
        doc_type:
            The document type to use (default: 'document')
        keyword_argument:
            All keyword arguments will be passed to Python Elasticsearch constructor.
        """

So, for instance, if you instead of default http://127.0.0.1:9200 want to connect to
http://myserver.com:12345, you need to use::

    from estnltk import Database

    hosts = [{
        'host': 'http://myserver.com',
        'port': 443
    }]
    db = Database('test', hosts=hosts)

Check the `Elastic Python docs`_ for more details.
If Elastic server runs in a certain machine you can access over SSH, you might also want to read about
`SSH tunneling`_ .
Another important property is the actual ElasticSearch instance that Estnltk wraps,
which can be retrieved via :py:meth:`~estnltk.database.database.Database.es` property.
Use this for **complete control over the connection**.

.. _`Elastic Python docs`: https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch
.. _`SSH tunneling`: http://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html


Inserting Text objects to database
==================================

Estnltk has a python function for inserting Text objects to Elastic database for further analysis.
It is important that you create a database before inserting.
In the example there is a database created named 'test'.
After that the Text object is created with a sentence.
Then the :py:meth:`~estnltk.database.database.Database.insert` method is being called.

Example for using the text insert::

    from ..database import Database
    from ...text import Text

    db = Database('test')

    text = Text('Mees, keda seal kohtasime, oli tuttav ja ta teretas meid.')

    db.insert(text)



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


Check out :ref:`wikipedia_tutorial`, :ref:`tei_tutorial` for more information
if you want to download some large and useful datasets to work with.

Searching the database for keywords
===================================

To search from the Elastic database you need to specify the name of the database and the keywords that you need
to start the search for. The function to do the search with is query_documents().

The example search is from the 'test' database and the search word is 'aegna'::

    from ..database import Database

    db = Database('test')

    search = Database.query_documents(db, "aegna")

The search will return a json format query with the full text of the successful search result.

