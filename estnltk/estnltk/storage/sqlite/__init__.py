"""
This package provides tools to conveniently store and search `estnltk` Text objects in a sqlite3 database.
( https://docs.python.org/3/library/sqlite3.html )

Currently, we assume that SqliteCollection (one document collection) corresponds to a single db file. 

An open question: since sqlite is optimized for handling multiple tables in a single file (but see also:
https://stackoverflow.com/a/50281741 ), we could, in principle, also store multiple (small?) collections 
in a single file (we could define SqliteStorage for handling multi-collection storage). Would it give a 
better reading/writing performance than processing from multiple files at once, e.g. if one tries to do 
something with both collections?

Example usage:

    # Connect to database: create a new collection or access to an existing one
    collection = SqliteCollection( 'my_collection', dir='.' )

    # Insert into the collection
    # Note: all texts must have same layers
    with collection.insert() as collection_insert:
        collection_insert( Text( ... ) )
        collection_insert( Text( ... ) )
        ...

    # Single document access (via index)
    collection[index]
    
    # Iterate over the whole collection
    for text_id, text_obj in collection.select():
        # to something with text_id and text_obj
        ...
    
    # Close connection to the collection
    collection.close()

    # 
"""
from .collection import SqliteCollection