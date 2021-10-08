from psycopg2.sql import DEFAULT

from estnltk import logger
from estnltk.converters import layer_to_json
from estnltk_core import Layer
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import BufferedTableInsert
from estnltk.storage.postgres.pg_operations import layer_table_identifier


class CollectionDetachedLayerInserter(object):
    """Context manager for buffered insertion of detached layers into the collection.
    """

    def __init__(self, collection, layer_name, extra_columns=[], 
                 buffer_size=10000, query_length_limit=5000000):
        """Initializes context manager for detached layer insertions.
        
        Parameters:
         
        :param collection: PgCollection
            Collection where detached layers will be inserted.
        :param layer_name: str
            Name of the detached layer.
        :param extra_columns: List[str]
            Names of table's additional columns covered by the insert.
            By default, no extra columns will be used.
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the size is met or exceeded, the insert buffer will be flushed. 
            (Default: 10000)
        :param query_length_limit: int
            Soft approximate insert query length limit in unicode characters. 
            If the limit is met or exceeded, the insert buffer will be flushed.
            (Default: 5000000)
        """
        if collection is None or (isinstance(collection, pg.PgCollection) and not collection.exists()):
            raise pg.PgCollectionException("collection does not exist, can't create inserter")
        elif not isinstance(collection, pg.PgCollection):
            raise TypeError('collection must be an instance of PgCollection')
        self.collection = collection
        self.columns = ["id", "text_id", "data"]
        if extra_columns:
            self.extra_columns = extra_columns
            self.columns.extend( extra_columns )
        self.layer_table_identifier = layer_table_identifier(self.collection.storage, self.collection.name, layer_name)
        self.layer_name = layer_name
        self.buffer_size = buffer_size
        self.query_length_limit = query_length_limit
        self.buffered_inserter = None
        self.insert_counter = 0


    def __enter__(self):
        """ Initializes the insertion buffer. """
        # Make new buffered inserter
        self.buffered_inserter = BufferedTableInsert( self.collection.storage.conn, 
                                                      self.layer_table_identifier,
                                                      columns = self.columns, 
                                                      query_length_limit = self.query_length_limit,
                                                      buffer_size = self.buffer_size )
        assert self.buffered_inserter.cursor is not None
        return self


    def __exit__(self, type, value, traceback):
        """ Closes the insertion buffer. """
        if self.buffered_inserter is not None:
            self.buffered_inserter.close()
            logger.info('inserted {} detached {!r} layers into the collection {!r}'.format(self.insert_counter, self.layer_name, self.collection.name))


    def insert(self, layer, text_id, key=None, extra_data=None):
        """Inserts given Layer into the collection. 
           Value text_id must be provided to link the layer with 
           the Text object.
           Optionally, key of the insertable Layer and data for 
           extra columns can be provided. 
        """
        assert self.buffered_inserter is not None
        assert isinstance(layer, Layer)
        assert isinstance(text_id, int), '(!) id of the Text object associated with the layer must be an integer.'
        assert key is None or key is DEFAULT or isinstance(key, int)
        assert extra_data is None or isinstance(extra_data, list)
        # Prepare data
        layer_json = layer_to_json( layer )
        if key is None:
            key = DEFAULT
        values = [key, text_id, layer_json]
        if extra_data:
            # Validate extra data
            if len(extra_data) > len(self.extra_columns):
                raise ValueError('(!) Unexpectedly extra_data contains more items than specified in extra_columns: {!r}.'.format( self.extra_columns ))
            elif len(extra_data) < len(self.extra_columns):
                raise ValueError('(!) Unexpectedly extra_data contains less items than specified in extra_columns: {!r}.'.format( self.extra_columns ))
            values.extend( extra_data )
        # Make the insertion
        self.buffered_inserter.insert(values=values)
        self.insert_counter += 1


