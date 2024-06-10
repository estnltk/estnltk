from psycopg2.sql import SQL, DEFAULT

from estnltk import logger
from estnltk.converters import text_to_json
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import is_empty
from estnltk.storage.postgres import BufferedTableInsert
from estnltk.storage.postgres.pg_operations import collection_table_identifier
from estnltk.text import Text


class CollectionTextObjectInserter(object):
    """Context manager for buffered insertion of Text objects into the collection.
       Optionally, metadata and keys of insertable Text objects can be specified 
       during the insertion. 
        
       Notes about layers. 
       1) Attached layers. After the first Text object has been inserted, its layers 
       will be taken as the attached layers of the collection. Which means that other 
       insertable Text objects must have exactly the same layers.
       (and attached layers cannot be changed after the first insertion)
       2) Detached layers. If this collection already has detached layer(s), new Text 
       objects cannot be inserted.
        
       Example usage 1. Insert Text objects with metadata, but wo annotation layers:
            # Create collection w metadata
            collection.create( meta=OrderedDict( [('my_meta', 'str')]) )
            # Insert into the collection
            with CollectionTextObjectInserter( collection ) as col_inserter:
                col_inserter.insert( Text( ... ), key=0, meta_data={'my_meta':'A'} )
                col_inserter.insert( Text( ... ), key=1, meta_data={'my_meta':'B'} )
                ...
                
       Example usage 2. Insert annotated Text objects:
            # Create collection
            collection.create()
            # Insert into the collection
            with CollectionTextObjectInserter( collection ) as col_inserter:
                col_inserter.insert( Text( ... ).tag_layer('words') )
                col_inserter.insert( Text( ... ).tag_layer('words') )
                ...
    """

    def __init__(self, collection, buffer_size=10000, query_length_limit=5000000):
        """Initializes context manager for Text object insertions.
        
        Parameters:
         
        :param collection: PgCollection
            Collection where Text objects will be inserted.
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the size is met or exceeded, the insert buffer will be flushed. 
            (Default: 10000)
        :param query_length_limit: int
            Soft approximate insert query length limit in unicode characters. 
            If the limit is met or exceeded, the insert buffer will be flushed.
            (Default: 5000000)
        """
        if collection is None or ( isinstance(collection, pg.PgCollection) and not collection.exists() ):
            raise pg.PgCollectionException("collection does not exist, can't create inserter")
        elif not isinstance(collection, pg.PgCollection):
            raise TypeError('collection must be an instance of PgCollection')
        self.collection = collection
        self.metadata_start_index = len( self.collection.structure.collection_base_columns )
        self._has_hidden_column = ('hidden' in self.collection.structure.collection_base_columns)
        self.table_identifier = collection_table_identifier( self.collection.storage, self.collection.name )
        self.buffer_size = buffer_size
        self.query_length_limit = query_length_limit
        self.buffered_inserter = None
        self.insert_counter = 0
        self.relation_layer_data_losses = 0


    def __enter__(self):
        """ Initializes the insertion buffer and does initial check-ups of the structure. """
        self.collection.storage.conn.commit()
        self.collection.storage.conn.autocommit = False
        # Make new buffered inserter
        self.buffered_inserter = BufferedTableInsert( self.collection.storage.conn, 
                                                      self.table_identifier,
                                                      columns = self.collection.column_names, 
                                                      query_length_limit = self.query_length_limit,
                                                      buffer_size = self.buffer_size )
        cursor = self.buffered_inserter.cursor
        assert cursor is not None
        # Validate the empty collection
        if self.collection._is_empty and is_empty(self.collection.storage, self.collection.name):
            # There should be no structure if the collection is empty
            # ( CollectionStructureBase should return None )
            if self.collection.structure:
                raise pg.PgCollectionException("collection already has structure {!r}, can't create another".format( self.collection.structure.structure ))
        # Check for existing detached/fragmented layers
        if self.collection.structure:
            if any(struct['layer_type'] in pg.PostgresStorage.TABLED_LAYER_TYPES for struct in self.collection.structure.structure.values()):
                raise pg.PgCollectionException("this collection has tabled layer(s), can't add new text objects")
        return self


    def __exit__(self, type, value, traceback):
        """ Closes the insertion buffer. """
        if self.buffered_inserter is not None:
            self.buffered_inserter.close()
            logger.info('inserted {} texts into the collection {!r}'.format(self.insert_counter, self.collection.name))
            if self.relation_layer_data_losses > 0:
                logger.warning( '(!) {} documents lost relation layers during the insertion'.format( \
                                    self.relation_layer_data_losses ) )

    def __call__(self, text, key=None, meta_data=None): 
        self.insert(text, key=key, meta_data=meta_data)


    def insert(self, text, key=None, meta_data=None):
        """Inserts given Text object into the collection.
           Optionally, metadata and key of insertable Text 
           object can be specified. 
        """
        assert isinstance(text, Text)
        assert self.buffered_inserter is not None
        # 1) Empty collection
        if self.collection._is_empty:
            self.collection._is_empty = False
            if len(self.collection) == 0:
                # Insert the first row
                if key is None:
                    key = 0
                row = [ key, text_to_json(text) ]
                if self._has_hidden_column:
                    row.append( False )
                
                for k in self.collection.column_names[self.metadata_start_index:]:
                    if meta_data is None:
                        raise ValueError(('(!) Metadata columns exist, but meta_data is None. '+\
                                          'Please use meta_data={} if you want to leave metadata columns empty.'))
                    if k in meta_data:
                        m = meta_data[k]
                    else:
                        m = DEFAULT
                    row.append(m)
                self.buffered_inserter.insert( row )
                self.insert_counter += 1
                # set attached span layers of the collection
                for layer in text.layers:
                    # TODO: meta = ???
                    self.collection.structure.insert(layer=text[layer], layer_type='attached', meta={}, is_sparse=False)
                if len(text.relation_layers) > 0:
                    if self.collection.version >= '4.0':
                        # set attached relation layers of the collection
                        for rel_layer in text.relation_layers:
                            # TODO: meta = ???
                            self.collection.structure.insert(layer=text[rel_layer], layer_type='attached', meta={}, is_sparse=False)
                    else:
                        # older collection versions: report data loss
                        logger.warning( ('possible data loss: skipped insertion of relation layers {!r}. collection version '+\
                                         '>= 4.0 is required for storing relation layers.').format( text.relation_layers ) )
                return
            self.collection.storage.conn.commit()
            self.collection.structure.load()
        # 2) Non-empty collection
        # Validate that insertable Text object has appropriate structure
        text_obj_all_layers = set(text.layers)
        if self.collection.version >= '4.0':
            text_obj_all_layers = text_obj_all_layers.union(set(text.relation_layers))
        if not text_obj_all_layers == set(self.collection.structure):
            raise AssertionError( \
                "collection's attached layers {!r} do not match text object's layers {!r}".format( set(self.collection.structure), \
                                                                                                   text_obj_all_layers ) )
        for layer_name in text.layers:
            layer = text[layer_name]
            layer_struct = self.collection.structure[layer_name]
            assert layer_struct['layer_type'] == 'attached'
            assert layer_struct['attributes'] == layer.attributes, '{} != {}'.format(
                    layer_struct['attributes'], layer.attributes)
            assert layer_struct.get('span_names', None) is None
            assert layer_struct['ambiguous'] == layer.ambiguous
            assert layer_struct['parent'] == layer.parent
            assert layer_struct['enveloping'] == layer.enveloping
            assert layer_struct['serialisation_module'] == layer.serialisation_module
        if len(text.relation_layers) > 0:
            if self.collection.version >= '4.0': # relation layers require collection version >= 4.0
                for rel_layer_name in text.relation_layers:
                    layer = text[rel_layer_name]
                    layer_struct = self.collection.structure[rel_layer_name]
                    assert layer_struct['layer_type'] == 'attached'
                    assert layer_struct['span_names'] == layer.span_names, '{} != {}'.format(
                            layer_struct['span_names'], layer.span_names)
                    assert layer_struct['attributes'] == layer.attributes, '{} != {}'.format(
                            layer_struct['attributes'], layer.attributes)
                    assert layer_struct['ambiguous'] == layer.ambiguous
                    assert layer_struct['parent'] is None
                    assert layer_struct['enveloping'] == layer.enveloping
                    assert layer_struct['serialisation_module'] == layer.serialisation_module
            else:
                # older collection versions: report data loss
                self.relation_layer_data_losses += 1
                if self.relation_layer_data_losses < 5:
                    logger.warning( ('possible data loss: skipped insertion of relation layers {!r}. collection version '+\
                                     '>= 4.0 is required for storing relation layers.').format( text.relation_layers ) )
        # Insert the next row
        if key is None:
            key = DEFAULT
        row = [key, text_to_json(text)]
        if self._has_hidden_column:
            row.append( False )
        for k in self.collection.column_names[self.metadata_start_index:]:
            if meta_data is None:
                raise ValueError(('(!) Metadata columns exist, but meta_data is None. '+\
                                  'Please use meta_data={} if you want to leave metadata columns empty.'))
            if k in meta_data:
                m = meta_data[k]
            else:
                m = DEFAULT
            row.append(m)
        self.buffered_inserter.insert( row )
        self.insert_counter += 1


