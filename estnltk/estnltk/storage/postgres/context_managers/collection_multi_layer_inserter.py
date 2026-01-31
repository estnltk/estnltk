import warnings
from collections import OrderedDict

from psycopg2.sql import DEFAULT

from estnltk import logger
from estnltk.converters import layer_to_json
from estnltk_core import Layer
from estnltk_core import RelationLayer
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import BufferedMultiTableInsert
from estnltk.storage.postgres.pg_operations import layer_table_identifier


class CollectionMultiLayerInserter(object):
    '''An extension of CollectionDetachedLayerInserter that holds an insertion buffer over multiple 
       layer tables at the same time. Allows to insert multiple (detached) layers of a Text object. 
       
       Builds upon: 
       https://github.com/estnltk/estnltk-workflows/blob/98109d50f6901a8c6baa422ee960faefee0274cf/enc_workflows/x_db_utils.py 
       https://github.com/estnltk/estnltk/blob/ab676f28df06cabee3b7e1f17c9eeaa1f635831d/estnltk/estnltk/storage/postgres/context_managers/collection_detached_layer_inserter.py 
    '''

    def __init__(self, collection, layers, sparse_layers: list=None, extra_columns: dict=None,
                       buffer_size=10000, query_length_limit=5000000, log_doc_completions:bool=False ):
        """Initializes context manager for multiple (detached) layer insertions.
        
        Parameters:
         
        :param collection: PgCollection
            Collection where layers will be inserted.
        :param layers: List[str]
            Names of the new layers that are inserted into the collection.
        :param sparse_layers: list
            List of layers which should be treated as sparse layers. This means 
            that only their non-empty instances are inserted in the layer table, 
            empty instances are skipped. 
        :param extra_columns: dict
            Mapping from layer names to extra columns to be inserted. Use this 
            if you want to insert additional data to some layer, e.g. fill in 
            metadata column values. 
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the size is met or exceeded, the insert buffer will be flushed. 
            (Default: 10000)
        :param query_length_limit: int
            Soft approximate insert query length limit in unicode characters. 
            If the limit is met or exceeded, the insert buffer will be flushed.
            (Default: 5000000)
        :param log_doc_completions: bool
            Whether completed insertions of documents will be explicitly logged.
            (Default: False)
        """
        self.collection = collection
        if self.collection.version < '4.0':
            raise pg.PgCollectionException( ("Cannot use this CollectionMultiLayerInserter with collection version {!r}. "+\
                                             "PgCollection version 4.0+ is required.").format(self.collection.version) )
        self.buffer_size = buffer_size
        self.query_length_limit = query_length_limit
        self.log_doc_completions = log_doc_completions
        existing_filled_layers = self.collection.layers or []
        # Validate target layers & collect corresponding collection layers
        assert isinstance(layers, list) and len(layers) > 0
        assert all([isinstance(l, str) for l in layers])
        unique_layers = []
        missing_layers = []
        for target_layer in layers:
            layer_exists = target_layer in existing_filled_layers
            if not layer_exists:
                missing_layers.append( target_layer )
            if target_layer not in unique_layers:
                # Take only unique layers, discard duplicates
                unique_layers.append( target_layer )
        if missing_layers:
            raise pg.PgCollectionException( f'(!) No tables have been created for layers {missing_layers!r}. '+\
                                             'Please use PgCollection.add_layer method to create layer tables.' )
        self.layers = unique_layers
        # Validate extra columns (must be a map from layers to list of their extra columns)
        assert extra_columns is None or isinstance(extra_columns, dict)
        if extra_columns is not None:
            for (layer, columns) in extra_columns.items():
                if layer not in self.layers:
                    raise Exception(f'(!) extra_columns layer {layer} not in layers list {self.layers}.')
                assert isinstance(columns, list)
                assert all([isinstance(c, str) for c in columns])
        self.extra_columns = extra_columns if extra_columns is not None else dict()
        # Validate sparse layers
        assert sparse_layers is None or isinstance(sparse_layers, list)
        if sparse_layers is not None:
            for layer in sparse_layers:
                if layer not in self.layers:
                    raise Exception(f'(!) sparse_layer {layer} not in layers list {self.layers}.')
        self.sparse_layers = set(sparse_layers) if sparse_layers is not None else set()
        # Make mapping from insertion phases to table names and columns
        self.insertion_phase_map = OrderedDict()
        insertable_tables = []
        # Layer tables
        for lid, layer_name in enumerate(self.layers):
            layer_table = layer_table_name(collection.name, layer_name)
            table_identifier = \
                layer_table_identifier(self.collection.storage, self.collection.name, layer_name)
            layer_table_columns = ["id", "text_id", "data"]
            if layer_name in self.extra_columns:
                layer_table_columns.extend( self.extra_columns.get(layer_name) )
            insertable_tables.append( [layer_table, table_identifier, layer_table_columns] )
            self.insertion_phase_map[f'_layer_{layer_name}'] = (layer_table, insertable_tables[-1][-1])
        self.insertable_tables = insertable_tables
        self.buffered_inserter = None
        self.text_insert_counter = 0
        self.layer_insert_counter = 0
        self.sparse_insert_counter = 0
        self.sparse_insert_extra_data_losses = 0


    def __enter__(self):
        """ Initializes the insertion buffer. Assumes collection structure & tables have already been created. """
        self.collection.storage.conn.commit()
        self.collection.storage.conn.autocommit = False
        assert self.insertable_tables is not None and len(self.insertable_tables) > 0
        # Make new buffered inserter
        self.buffered_inserter = BufferedMultiTableInsert( self.collection.storage, 
                                                           self.insertable_tables,
                                                           query_length_limit = self.query_length_limit,
                                                           buffer_size = self.buffer_size,
                                                           log_doc_completions = self.log_doc_completions)
        cursor = self.buffered_inserter.cursor
        assert cursor is not None
        return self


    def __exit__(self, type, value, traceback):
        """ Closes the insertion buffer. """
        if self.buffered_inserter is not None:
            self.buffered_inserter.close()
            if self.sparse_insert_counter > 0:
                logger.info( ('multi-inserted {} detached layers of {} texts into the collection {!r}, '+\
                              'skipped {} empty layers').format(self.layer_insert_counter, self.text_insert_counter,
                                                                self.collection.name, self.sparse_insert_counter) )
            else:
                logger.info( 'multi-inserted {} detached layers of {} texts into the collection {!r}'.format(self.layer_insert_counter,
                                                                                                             self.text_insert_counter,
                                                                                                             self.collection.name) )
            if self.sparse_insert_extra_data_losses > 0:
                logger.warning( '{} skipped detached {!r} layers had metadata that was lost'.format( \
                                    self.sparse_insert_extra_data_losses, 
                                    self.layer_name ) )


    def __call__(self, layer, text_id, key=None, extra_data=None): 
        self.insert(layer, text_id, key=key, extra_data=extra_data)


    def insert(self, layer, text_id, key=None, extra_data=None):
        """Inserts given Layer into the collection. 
           Value text_id must be provided to link the layer with 
           the Text object.
           Optionally, key of the insertable Layer and data for 
           extra columns can be provided. 
        """
        assert self.buffered_inserter is not None
        assert isinstance(layer, (Layer, RelationLayer))
        assert isinstance(text_id, int), '(!) id of the Text object associated with the layer must be an integer.'
        assert key is None or key is DEFAULT or isinstance(key, int)
        assert extra_data is None or isinstance(extra_data, list)
        # Validate insertion targets
        insertion_phase_key = f'_layer_{layer.name}'
        assert insertion_phase_key in self.insertion_phase_map.keys(), \
            f'(!) Layer {layer.name} not among insertable layers ({self.layers}).' 
        last_phase    = list( self.insertion_phase_map.keys() )[-1]
        table_name    = self.insertion_phase_map[insertion_phase_key][0]
        table_columns = self.insertion_phase_map[insertion_phase_key][1]
        extra_columns = table_columns[3:]
        if layer.name in self.sparse_layers and len(layer) == 0:
            # Sparse layer table: skip insertion of an empty layer
            self.sparse_insert_counter += 1
            # If extra metadata was provided, warn about the data loss
            if extra_data is not None and len(extra_data) > 0:
                # Display 5 warnings at maximum
                if self.sparse_insert_extra_data_losses < 5:
                    warnings.warn( ('Metadata items were lost during the sparse insertion '+\
                                    'of layer {!r}. Do not use sparse layer if you want to '+\
                                    'preserve metadata about an empty layer. Use non-sparse '+\
                                    'layer instead.').format(layer.name) )
                self.sparse_insert_extra_data_losses += 1
            # If this the last phase of the insertion, then 
            # mark this document as completed (in buffered_inserter)
            doc_completed = None
            if last_phase == insertion_phase_key:
                # Mark document insertion completed
                doc_completed = text_id
                self.buffered_inserter.completion_markers[table_name].append( doc_completed )
                self.text_insert_counter += 1
            return
        # Prepare data
        layer_json = layer_to_json( layer )
        if key is None:
            key = DEFAULT
        values = [key, text_id, layer_json]
        if extra_data:
            # Validate extra data
            if len(extra_data) > len(extra_columns):
                raise ValueError('(!) Unexpectedly extra_data contains more items than specified in extra_columns: {!r}.'.format( extra_columns ))
            elif len(extra_data) < len(extra_columns):
                raise ValueError('(!) Unexpectedly extra_data contains less items than specified in extra_columns: {!r}.'.format( extra_columns ))
            values.extend( extra_data )
        assert len(table_columns) == len(values)
        # If this the last phase of the insertion, then 
        # mark this document as completed
        doc_completed = None
        if last_phase == insertion_phase_key:
            # Mark document insertion completed
            doc_completed = text_id
            self.text_insert_counter += 1
        self.buffered_inserter.insert( table_name, values, doc_completed=doc_completed )
        self.layer_insert_counter += 1



