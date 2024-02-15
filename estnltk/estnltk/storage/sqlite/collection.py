import sqlite3
from contextlib import contextmanager


__version__ = '0.0'

class SqliteCollection:
    """
    Collection of Text objects and their metadata in an sqlite3 database.
    
    Allows to:
    * insert Text objects along with metadata and attached layers;
    * query/iterate over Text objects and their layers and metadata;


    Creating/accessing a collection
    ================================
    You can create or access collection via SqliteCollection class, e.g.
    
        # Access sqlite collection
        collection = SqliteCollection( 'my_collection', dir='.' )
        
    If collection (file) with that name already exists in the given dir, 
    then connects to an existing collection. Otherwise, creates a new 
    collection. 


    Document insertion
    ====================
    Collection's insert() method provides a context manager, which 
    allows buffered insertion of Text objects into database.
    
    Example. Insert Text objects with words layers:

        # Insert into the collection
        with collection.insert() as collection_insert:
            collection_insert( Text( ... ).tag_layer('words') )
            collection_insert( Text( ... ).tag_layer('words') )
            ...


    Attached layers
    =================
    If you insert Text objects with layers, these layers become "attached 
    layers", meaning that they are stored in the same table as Text objects, 
    and these layers will always be retrieved with Text objects.
    Note that attached layers are determined on the insertion of the first 
    Text object: all the following inserted Text objects must have the same 
    layers as the first Text.


    Single document access
    =======================
    If you want to retrieve a single document from the collection, you can get
    the document (Text object) via indexing operator:

        # retrieve the document via index
        collection[index]


    Querying/Iterating
    ====================
    You can get a slice of collection using the slice operator:

        # retrieve documents starting from the index `start`
        collection[start:]

    Alternatively, you can iterate over the collection via select() method, 
    which yields pairs (document_id, Text) by default::

        # Iterate over the whole collection
        for text_id, text_obj in collection.select():
            # to something with text_id and text_obj
            ...


    Closing connection
    ====================
    After you've done the work, close the connection:

        collection.close()

    """


    def __init__(self, name: str, dir: str='.'):
        """
        Opens an access to a sqlite-based collection. 
        
        If collection (file) with that name already exists in the given dir, 
        then connects to an existing collection. Otherwise, creates a new 
        collection. 
        
        Raises SqliteStorageException if a collection (file) already 
        exists and its version does not match with the __version__.
        
        Parameters
        -----------
        name: str
            Name of the collection. Must be a valid file name. 
            TODO: we could apply isidentifier restriction to the 
            name, see:
            https://docs.python.org/3/library/stdtypes.html#str.isidentifier
        dir: str
            Path to the directory of the collection. If the collection 
            is missing from the directory, a new collection is created; 
            otherwise, and existing collection is opened.
            Defaults to current working directory ('.').

        Returns
        --------
        SqliteCollection
            an instance of the created collection
        """
        pass


    @property
    def layers(self):
        """
        Returns names of the layers all Text objects in this collection have.
        """
        
        # TODO: simply query the first Text object and take its layers
        # TODO: or use a separate table that describes all the layers of 
        #       this collection, and query that layer ?
        pass


    @contextmanager
    def insert(self, buffer_size=10000):
        """
        Context manager for inserting of Text objects into the collection. 
        Ensures that all insertions will be properly commited to the database. 
        Example usage:
        
            with collection.insert() as collection_insert:
                collection_insert( Text( ... ) )
                collection_insert( Text( ... ) )
                ...
        
        If inserted Text objects contain layers, then these layers become "attached
        layers", meaning that they are stored in the same table as Text objects,
        and these layers will always be retrieved with Text objects.
        After the first Text object has been inserted, the attached layers of the
        collection are frozen. Which means that other insertable Text objects must
        have exactly the same layers (and attached layers cannot be changed after
        the first insertion).
        
        Parameters
        -----------
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the size is met or exceeded, the insert buffer will be flushed.
            (Default: 10000)
        """
        
        # TODO: if this collection is empty, then the structure must be initialized: 
        # a table for storing Text objects (and, optionally, metadata) must be created 
        
        # TODO: if this collection already has documents, then check that inserted 
        # Text objects have same layers as the collection. 
        # Raise a SqliteStorageException is one tries to insert documents with different 
        # layers.
        
        # TODO: How to define context managers, see:
        #   https://docs.python.org/3/library/contextlib.html
        #   https://github.com/estnltk/estnltk/tree/devel_1.7/estnltk/estnltk/storage/postgres/context_managers
        
        # TODO: Text object-s need to serialized / converted into json strings
        # https://github.com/estnltk/estnltk/blob/devel_1.7/tutorials/converters/json_exporter_importer.ipynb
        # All documents must obtain a unique index
        pass


    def select(self, progressbar: str = None, return_index: bool = True, start: int = None, end: int = None):
        """
        Iterates over text objects of the collection. 

        Raises SqliteStorageException if indexes start/end do not meet 
        limits of this collection.

        Parameters
        -----------
        :param progressbar:
            progressbar for iteration. no progressbar by default.
            possible values: None, 'ascii', 'unicode' or 'notebook'
        :param return_index: bool
            whether document id-s will be yielded with text objects.
            default: True
        :param start: int
            restriction: yield only documents starting from the given 
            document id (inclusive). if start==None, then no restriction
            is applied.
            default: None
        :param end: int
            restriction: yield only documents up to the given document id 
            (exclusive). if end==None, then no restriction is applied.
            default: None

        :yield: (int, Text) or Text
            yields documents of this collection
        """
        # TODO: Text object-s need to de-serialized from json to Text format
        # https://github.com/estnltk/estnltk/blob/devel_1.7/tutorials/converters/json_exporter_importer.ipynb
        pass

    def close(self):
        """Closes connection to the database."""
        pass

    def __len__(self):
        """
        Returns number of documents in this collection. 
        """
        pass

    def __getitem__(self, item):
        """
        In order to access specific documents (Text objects), you
        can either retrieve documents by index:

            # retrieve first document
            collection[0]
        
        Or you can use slice operator to retrieve a range of documents:

            # retrieve documents starting from the index `start`
            collection[start:]

        Raises KeyError if indexes do not meet limits of this collection.
        """
        if isinstance(item, int):
            # TODO: Retrieve a single document
            pass

        if isinstance(item, slice):
            # Retrieve slice of documents
            if item.step is not None:
                raise KeyError("Invalid index slice {!r}".format(item))

            return self.select(return_index=False, start=item.start, end=item.stop)

        raise KeyError(item)


    def __iter__(self):
        yield from self.select(return_index=False)


    def _repr_html_(self):
        # TODO: display HTML table with information about collection name, 
        # location (dir), number of text objects and layer structure (if 
        # text objects have been inserted)
        pass 