import collections
import json
import re
import time
from contextlib import contextmanager
from typing import Sequence, Dict
import warnings

import pandas
import psycopg2
from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier, Literal, DEFAULT

from estnltk import logger
from estnltk_core import Layer
from estnltk.converters import dict_to_layer
from estnltk.converters import dict_to_text
from estnltk.converters import layer_to_dict
from estnltk.converters import layer_to_json
from estnltk_core.layer_operations import create_ngram_fingerprint_index
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import BufferedTableInsert
from estnltk.storage.postgres import CollectionDetachedLayerInserter
from estnltk.storage.postgres import CollectionTextObjectInserter
from estnltk.storage.postgres import count_rows
from estnltk.storage.postgres import drop_fragment_table
from estnltk.storage.postgres import drop_layer_table
from estnltk.storage.postgres import fragment_table_name
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import structure_table_exists
from estnltk.storage.postgres import structure_table_identifier
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres.queries.missing_layer_query import MissingLayerQuery
from estnltk.storage.postgres.queries.slice_query import SliceQuery


class PgCollectionException(Exception):
    pass


RowMapperRecord = collections.namedtuple("RowMapperRecord", ["layer", "meta"])

class PgCollection:
    """
    Collection of Text objects and their metadata in the database.
    
    Allows to:
    * insert Text objects along with metadata and attached layers;
    * insert detached layers (incl. parallelization of layer creation via blocks);
    * query/iterate metadata of the collection;
    * query/iterate over Text objects and their layers;
    * export json layer content into a database table;
    
    Creating/accessing a collection
    ================================
    You can create a new collection via storage class, e.g.
    
        # Connect to the storage
        storage = PostgresStorage(...)
        
        # Create a new collection
        collection = storage.add_collection('my_collection')
    
    In order to retrieve an existing collection, use indexing
    operator of the storage:
    
        # Retrieve existing collection
        collection = storage['my_collection']
    
    ! Do not create PgCollection objects via constructor.
    
    Document insertion
    ====================
    Collection's insert() method provides a context manager, which 
    allows buffered insertion of Text objects into database.
    
    Example 1. Insert Text objects with metadata, but without annotation layers:
        # Create collection with metadata columns
        storage.add_collection( 'my_collection', 
                                meta=OrderedDict([('my_meta', 'str')]) )
        
        # Insert into the collection
        with collection.insert() as collection_insert:
            collection_insert( Text( ... ), key=0, meta_data={'my_meta':'A'} )
            collection_insert( Text( ... ), key=1, meta_data={'my_meta':'B'} )
            ...
    
    Example 2. Insert annotated Text objects:
        # Create collection
        storage.add_collection('my_collection')
        
        # Insert into the collection
        with collection.insert() as collection_insert:
            collection_insert( Text( ... ).tag_layer('words') )
            collection_insert( Text( ... ).tag_layer('words') )
            ...

    You can insert new Text objects into the collection as long as the
    collection does not have any detached layers. Once a detached layer
    is added to the collection, new Text objects can no longer be
    inserted.
    
    Attached layers
    =================
    If you insert Text objects with layers, these layers become "attached 
    layers", meaning that they are stored in the same table as Text objects, 
    and these layers will always be retrieved with Text objects.
    Note that attached layers are determined on the insertion of the first 
    Text: all the following inserted Text objects must have the same layers
    as the first Text.

    Detached layers
    ====================
    A detached layer is a layer that is stored in a separate table.
    If you iterate/query over documents of the collection, you can choose which
    detached layers you want to retrieve with the results.

    You can add detached layers to the collection after documents (with or without
    attached layers) have been inserted. Note that adding a detached layer freezes
    collection's size -- after that new documents cannot be added to the collection.
    You can create detached layers with a tagger:

            # Insert layers with a tagger
            collection.create_layer( tagger=tagger, mode='create' )

    Alternatively, you can use collection.add_layer(...) method to first add a new
    detached layer to the structure of the collection:

            # Add a template of the layer (an empty layer with correct attribute values)
            collection.add_layer( layer_template=tagger.get_layer_template() )

    After that, you can parallelize layer creation via launching separate tagging
    processes over different blocks of documents in the collection:

            # Insert layers with a tagger (first job)
            collection.create_layer_block( tagger=tagger, (2, 0) )

            # Insert layers with a tagger (second job)
            collection.create_layer_block( tagger=tagger, (2, 1) )

    Note that each parallel tagging process must be launched inside a different database
    connection.

    Single document access
    =======================
    If you want to retrieve a single document from the collection, you can get
    the document (Text object) via indexing operator:

            # set (detached) layers you want to retrieve
            collection.selected_layers = [ layer_1, layer_2 ]

            # retrieve the document via index
            collection[index]

    In order to retrieve metadata of a single document, use the collection.meta
    with indexing operator:

            # retrieve metadata of the document via index
            collection.meta[index]

    This returns dictionary with metadata values. You can also get a reduced
    dictionary that only has values of specific metadata columns, e.g.

            # retrieve only values of specific metadata columns
            collection.meta[index, [meta_column_1, meta_column_2]]


    Querying/Iterating
    ====================
    You can iterate over the collection via select() method, which yields a
    read-only sub collection of texts (a PgSubCollection object):

            # Iterate over the whole collection
            for text_id, text_obj in collection.select():
                # to something with text_id and text_obj
                ...

    Use parameter `query` in collection.select() to add more constraints to
    retrievable documents, e.g. query=SubstringQuery('laula') instructs to yield
    only documents with substring 'laula'.

    Use parameter `layers` in collection.select() to specify which (detached)
    layers will be retrieved with documents (alternatively, you can set layers via
    collection.selected_layers).

    Use parameter `collection_meta` in collection.select() to specify a list of
    metadata columns which values will be retrieved along with text_id, text_obj:

            data_iterator = collection.select(collection_meta=['meta_column_1'])
            for  text_id, text_obj, meta  in  data_iterator:
                # to something with text_id, text_obj and meta
                ...

    In order to iterate over metadata of documents (without Text objects), you
    can use the slice operator on collection.meta:

            # retrieve metadata of all documents
            collection.meta[0:]

            # retrieve metadata of documents starting from the index `start`
            collection.meta[start:]

    This returns a PgCollectionMetaSelection object, which can be iterated for
    metadata dictionaries.

    Removing layers
    ====================
    You can delete a detached layer in the following manner:

            collection.delete_layer( layer_name )

    Attached layers cannot be deleted.

    Removing collection
    ====================
    You can remove the whole collection via storage's delete_collection() method:

            storage.delete_collection(collection.name)

    More information
    ====================
    * https://github.com/estnltk/estnltk/blob/main/tutorials/storage/storing_text_objects_in_postgres.ipynb
    """

    def __init__(self, name: str, storage, temporary: bool = False, version='0.0'):
        """
        Initializes a new PgCollection object.

        **Important:** Do not create PgCollection objects via this constructor.
        Instead, create collections via storage class, e.g.

            # Connect to the storage
            storage = PostgresStorage(...)

            # Create a new collection
            collection = storage.add_collection('my_collection')

        In order to retrieve an existing collection, use indexing
        operator of the storage:

            # Retrieve existing collection
            collection = storage['my_collection']

        """
        assert isinstance(name, str), name
        assert name.islower(), name
        assert name.isidentifier(), name
        if '__' in name:
            raise PgCollectionException('collection name must not contain double underscore: {!r}'.format(name))
        self.name = name
        self.storage = storage
        self._temporary = temporary
        self._structure = None
        if version == '0.0':
            self._structure = pg.v00.CollectionStructure(self)
        elif version == '1.0':
            self._structure = pg.v10.CollectionStructure(self)
        elif version == '2.0':
            self._structure = pg.v20.CollectionStructure(self)
        elif version == '3.0':
            self._structure = pg.v30.CollectionStructure(self)
        else:
            raise ValueError("version must be '0.0', '1.0', '2.0' or '3.0'")
        self.version = version

        self._meta = None
        self._column_names = None
        self._selected_layes = None
        self._is_empty = not self.exists() or len(self) == 0

    def create(self, description=None, meta: dict = None, temporary=None):
        """Creates and adds new collection to the database. 
           * Creates tables of the collection (structure table and collection table);
           * Adds entry about the collection to StorageCollections's table
             (if the entry is missing);
          
          **Important:** this method is deprecated. Please use
          PostgresStorage.add_collection(...) to create a new collection.
        """
        error_msg = '(!) PgCollection.create() is deprecated. '+\
                    'Please use PostgresStorage.add_collection(...) '+\
                    'method to create a new collection in database.'
        raise Exception( error_msg )

    @property
    def structure(self):
        return self._structure

    @property
    def layers(self):
        if self._is_empty:
            return []
        return list(self._structure)

    @property
    def meta(self):
        if self._meta is None:
            self._meta = pg.PgCollectionMeta(self)
        return self._meta

    @property
    def column_names(self):
        if self._column_names is None:
            self._column_names = ['id', 'data'] + self.meta.columns
        return self._column_names

    @property
    def selected_layers(self):
        if self._selected_layes is None:
            if not self.exists():
                raise PgCollectionException('collection {!r} does not exist'.format(self.name))
            if self._is_empty:
                return []
            self._selected_layes = [layer for layer, properties in self._structure.structure.items()
                                    if properties['layer_type'] == 'attached']
        return self._selected_layes

    @selected_layers.setter
    def selected_layers(self, value):
        assert isinstance(value, list)
        assert all(isinstance(v, str) for v in value)
        assert set(value) <= set(self._structure)
        self._selected_layes = self.dependent_layers(value)

    def dependent_layers(self, selected_layers):
        """Returns all layers that depend on selected layers including selected layers.

           Returned layers are topologically ordered according to dependencies.
           The latter provides a correct order for loading and re-attaching detached layers.
        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))
        
        layers_extended = []

        def include_dep(layer):
            if layer is None:
                return
            for dep in (self._structure[layer]['parent'], self._structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in selected_layers:
            if layer not in self._structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                                               layer, self.name))
            include_dep(layer)

        return layers_extended

    def create_index(self):
        """Create index for the collection table.

        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))
        
        with self.storage.conn.cursor() as c:
            c.execute(
                SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops)").format(
                    index=Identifier('idx_%s_data' % self.name),
                    table=pg.collection_table_identifier(self.storage, self.name)))

    def drop_index(self):
        """Drop index of the collection table.
        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))
        
        with self.storage.conn.cursor() as c:
            c.execute(
                SQL("DROP INDEX {schema}.{index}").format(
                    schema=Identifier(self.storage.schema),
                    index=Identifier('idx_%s_data' % self.name)))

    
    def extend(self, other: 'PgCollection'):
        """
        Extends this collection with texts from the other collection. 
        Inserts texts of other collection along with metadata, attached and 
        detached layers into this collection.
        Assumes that two collections have the same metadata columns and 
        layer structure (same attached and detached layers).
        # TODO: this is an untested functionality
        # TODO: make it work ?
        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))
        if not other.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(other.name))
        
        if self.column_names != other.column_names:
            raise PgCollectionException("can't extend: different collection meta")
        if self._structure != other._structure:
            raise PgCollectionException("can't extend: structures are different")
        with self.storage.conn.cursor() as cursor:
            cursor.execute(SQL('INSERT INTO {} SELECT * FROM {}'
                               ).format(pg.collection_table_identifier(self.storage, self.name),
                                        pg.collection_table_identifier(other.storage, other.name)))
            for layer_name, struct in self._structure.structure.items():
                if struct['layer_type'] == 'detached':
                    cursor.execute(SQL('INSERT INTO {} SELECT * FROM {}').format(
                            layer_table_identifier(self.storage, self.name, layer_name),
                            layer_table_identifier(self.storage, other.name, layer_name)))

    def _collection_table_meta(self):
        if not self.exists():
            return None
        with self.storage.conn.cursor() as c:
            c.execute(SQL('SELECT column_name, data_type from information_schema.columns '
                          'WHERE table_schema={} and table_name={} '
                          'ORDER BY ordinal_position'
                          ).format(Literal(self.storage.schema), Literal(self.name)))
            return collections.OrderedDict(c.fetchall())


    @contextmanager
    def insert(self, buffer_size=10000, query_length_limit=5000000):
        """Context manager for buffered insertion of Text objects into the collection.
        Optionally, metadata and keys of insertable Text objects can be specified during
        the insertion.

        If inserted Text objects contain layers, then these layers become "attached
        layers", meaning that they are stored in the same table as Text objects,
        and these layers will always be retrieved with Text objects.
        After the first Text object has been inserted, the attached layers of the
        collection are frozen. Which means that other insertable Text objects must
        have exactly the same layers (and attached layers cannot be changed after
        the first insertion).

        Note that you can insert new Text objects into the collection as long as the
        collection does not have any detached layers. After a detached layer has been
        added to the collection, the size of the collection is frozen and new Texts
        cannot be inserted via this method.
        Be aware: there is no guarding mechanism that stops one from adding a detached
        layer while the insertion of Text objects is still in progress. It's up for
        users to avoid this situation, as this would mess up the integrity of the
        collection.

        Example usage 1. Insert Text objects with metadata, but w/o annotation layers::

            # Create collection w metadata
            storage.add_collection('my_collection', meta=OrderedDict([('my_meta', 'str')]))

            # Insert into the collection
            with collection.insert() as collection_insert:
                collection_insert( Text( ... ), key=0, meta_data={'my_meta':'A'} )
                collection_insert( Text( ... ), key=1, meta_data={'my_meta':'B'} )
                ...

        Example usage 2. Insert annotated Text objects::

            # Create collection
            storage.add_collection('my_collection')

            # Insert into the collection
            with collection.insert() as collection_insert:
                collection_insert( Text( ... ).tag_layer('words') )
                collection_insert( Text( ... ).tag_layer('words') )
                ...
        
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the size is met or exceeded, the insert buffer will be flushed.
            (Default: 10000)
        :param query_length_limit: int
            Soft approximate insert query length limit in unicode characters. 
            If the limit is met or exceeded, the insert buffer will be flushed.
            (Default: 5000000)

        """
        with CollectionTextObjectInserter(self, query_length_limit = query_length_limit,
                                                buffer_size = buffer_size ) as text_inserter:
            yield text_inserter


    def exists(self):
        """Returns True if collection tables exist"""
        collection_table = table_exists(self.storage, self.name)
        structure_table = structure_table_exists(self.storage, self.name)
        assert collection_table is structure_table, \
            ('Collection {!r} has inconsistent table structure: '+\
             'collection_table_exists: {}, '+\
             'collection_structure_table_exists: {}').format(self.name, collection_table, structure_table)
        return collection_table

    def select_fragment_raw(self, fragment_name, parent_layer_name, query=None, ngram_query=None):
        """Args:
            fragment_name:
            collection_name:
            parent_layer_name:
            query:
            ngram_query:

        Returns:
            Iterator of tuples.
            Each tuple has 6 elements:
                text_id
                text
                parent_id
                parent_layer
                fragment_id
                fragment_layer
        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))
        
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('Method collection.select_fragment_raw(...) is deprecated. ', 
                       DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        
        # 1. Build query
        q = SQL("""
            SELECT
              {text_table}.id, {text_table}.data, {parent_table}.id, {parent_table}.data,
              {fragment_table}.id, {fragment_table}.data
            FROM
              {text_table}, {parent_table}, {fragment_table}
            WHERE
              {fragment_table}.parent_id = {parent_table}.id AND {parent_table}.text_id = {text_table}.id
            """)
        q = q.format(
            text_table=pg.collection_table_identifier(self.storage, self.name),
            parent_table=layer_table_identifier(self.storage, self.name, parent_layer_name),
            fragment_table=layer_table_identifier(self.storage, self.name, fragment_name, layer_type='fragmented'))

        sql_parts = [q]

        if query is not None:
            # build constraint on fragment's data column
            sql_parts.append(SQL('AND'))
            sql_parts.append(query.eval())

        if ngram_query is not None:
            # build constraint on fragment's ngram index
            ngram_q = SQL(" AND ").join(SQL(self._build_column_ngram_query(q, col, fragment_name))
                                        for col, q in ngram_query)
            sql_parts.append(SQL('AND'))
            sql_parts.append(ngram_q)

        q = SQL(' ').join(sql_parts)

        # 2. Execute query
        logger.debug(q.as_string(self.storage.conn))
        with self.storage.conn.cursor() as c:
            c.execute(q)
            for row in c.fetchall():
                text_id, text_dict, parent_id, parent_dict, fragment_id, fragment_dict = row
                text = dict_to_text(text_dict)
                parent_layer = dict_to_layer(parent_dict, text)
                fragment_layer = dict_to_layer(fragment_dict, text)
                yield text_id, text, parent_id, parent_layer, fragment_id, fragment_layer

    def select(self,
               query=None,
               layers: Sequence[str] = None,
               collection_meta: Sequence[str] = None,
               progressbar: str = None,
               return_index: bool = True,
               itersize: int= 10,
               keep_all_texts: bool = True):
        """
        Creates a query / selection over text objects of the collection. 

        :param query:
            query objects specifying selection criteria. 
            this can be a composition of multiple query objects, joined by 
            "|" and "&" operators.
        :param layers:
            names of selected layers that will be attached to returned text objects. 
            dependencies are included automatically
        :param collection_meta:
            names of collection's meta attributes that will be yielded with every 
            text object.
        :param progressbar:
            progressbar for iteration. no progressbar by default.
            possible values: None, 'ascii', 'unicode' or 'notebook'
        :param return_index: bool
            whether collection id-s will be yielded with text objects.
            default: True
        :param itersize: int
            the number of simultaneously yielded elements
        :param keep_all_texts: bool
            whether collection's text objects are yielded even if they contain 
            empty layers in quieried sparse layers. 
            by default, this option is switched on, and as a result, collection's text 
            objects are retrieved even if their sparse layers are emtpy. 
            if switched off, then text objects that contain empty layers in any of the 
            quieried sparse layer tables will be excluded from the results. 
            this can speed up the query. 
            this parameter affects both selected layers and layers specified in query.  
        :return: PgSubCollection
            a read-only subset of this collection, which can be iterated and further 
            sub-selected
        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))

        return pg.PgSubCollection(collection=self,
                                  selection_criterion=pg.WhereClause(collection=self, query=query),
                                  selected_layers=layers,
                                  meta_attributes=collection_meta,
                                  progressbar=progressbar,
                                  return_index=return_index,
                                  itersize=itersize,
                                  keep_all_texts=keep_all_texts
                                  )

    def __len__(self):
        return count_rows(self.storage, self.name)


    def _select_by_key_query(self, key):
        """ Returns a SQL select statement that selects a single text by the given key from the collection. 
            Used in the __getitem__ method.
        """
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format(self.name))
        
        collection_identifier = pg.collection_table_identifier(self.storage, self.name)
        # Condition: select by the given key
        # Validate the key
        if key is None or not isinstance(key, int):
            raise ValueError('(!) Invalid key value: {!r}. Use integer'.format( key ))
        # Construct selection_criterion
        select_by_key_sql = SQL('{table}."id" = {key}').format(table=collection_identifier, key=Literal(key))
        # Construct query
        selected_detached_layers = [layer for layer in self.selected_layers if self.structure[layer]['layer_type'] == 'detached']
        selected_columns = pg.SelectedColumns(collection=self, layers=selected_detached_layers, 
                                              collection_meta=(), include_layer_ids=False)
        if selected_detached_layers:
            # Query includes detached_layers
            # Build a FROM clause with joins to required detached layers
            from_clause = pg.FromClause(self, [])
            for layer in selected_detached_layers:
                # Note: the join_type is determined automatically based on sparsity of the layer:
                # * LEFT JOIN for sparse layer tables
                # * INNER JOIN for non-sparse layer tables
                from_clause &= pg.FromClause( self, [layer] )
            query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                       from_clause,
                                                                       select_by_key_sql)
        else:
            # No detached_layers
            query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                             collection_identifier,
                                                             select_by_key_sql)
        return query

    def __getitem__(self, item):

        if isinstance(item, int):
            cursor = self.storage.conn.cursor()
            cursor.execute( self._select_by_key_query( item ) )
            result = cursor.fetchone()
            cursor.close()

            if result:
                return pg.PgSubCollection.assemble_text_object(
                    text_dict=result[1], layer_dicts=result[2:],
                    selected_layers=self.selected_layers, structure=self.structure)
            else:
                raise KeyError("Index {!r} is outside of the collection".format(item))

        if isinstance(item, slice):
            
            if item.step is not None:
                raise KeyError("Invalid index slice {!r}".format(item))

            return self.select(
                query=SliceQuery(item.start, item.stop), layers=self.selected_layers,
                collection_meta=None, return_index=False)

        raise KeyError(item)

    def __iter__(self):
        yield from self.select(layers=self.selected_layers, return_index=False)

    def count_values(self, layer, attr, **kwargs):
        """Count attribute values in the collection.
        Warning: could lead to memory failure on extremely large collections.
        """
        counter = collections.Counter()
        for i, t in self.select(layers=[layer], **kwargs):
            counter.update(t[layer].count_values(attr))
        return counter

    def continue_creating_layer(self, tagger, progressbar=None, query_length_limit=5000000):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('Method collection.continue_creating_layer(...) is deprecated. '+\
                      'Please use collection.create_layer(..., mode="append") instead. ', 
                       DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        self.create_layer(tagger=tagger, progressbar=progressbar, query_length_limit=query_length_limit,
                          mode='append')

    def create_fragmented_layer(self, tagger=None, fragmenter:callable=None, fragment_name:str=None, \
                                      data_iterator=None,  row_mapper=None,  create_index:bool=False, \
                                      ngram_index=None, meta: Sequence = None, progressbar: str = None, \
                                      query_length_limit: int = 5000000):
        """
        Creates fragmented layer table and fills with data.
        
        A fragmented layer is a layer that is composed of (sub)layers of 
        a parent layer, e.g. created by breaking one layer into multiple 
        sublayers.

        *Important:* You should use this method only after the insertion of 
        Text objects into the collection has been finished. Once you create 
        a fragmented layer, new Text objects cannot be inserted into the 
        collection.

        Args:
            tagger: Tagger
                tagger.make_layer method is called to create new layer. 
                Either tagger and fragmenter must be None or layer_name, 
                data_iterator and row_mapper must be None.
            fragmenter: callable
                if tagger is provided, then fragmenter is called to brake layer 
                into list of (sub)layers. (sub)layers should specify 'parent_layer_id' 
                in their meta;
            fragment_name: str
                If tagger and fragmenter are not provided, then this should be 
                the name of the creatable fragmented layer.
            data_iterator: iterator
                If tagger and fragmenter are not provided, then data_iterator should 
                be an iterable producing tuples (text_id, text, parent_layer_id, *payload), 
                where *payload is a variable number of values to be passed to the `row_mapper` 
                See method `PgCollection.select_raw`. 
                Otherwise (tagger is provided) data_iterator defaults to iterating 
                over the whole collection. 
            row_mapper: callable
                If tagger and fragmenter are not provided, this should be a function 
                that takes as input a full row produced by `data_iterator` and returns 
                a list of dictionaries with keys 'fragment' (Layer) and 'parent_id' 
                (int).
            meta: dict of str -> str
                Specifies table column names and data types for storing additional
                meta information. E.g. meta={"sum": "int", "average": "float"}.
                See `pytype2dbtype` in `pg_operations` for supported types.
            progressbar: str
                if 'notebook', display progressbar as a jupyter notebook widget
                if 'unicode', use unicode (smooth blocks) to fill the progressbar
                if 'ascii', use ASCII characters (1-9 #) to fill the progressbar
                else disable progressbar (default)
            query_length_limit: int
                soft approximate query length limit in unicode characters, can be exceeded 
                by the length of last buffer insert
            create_index:
                Whether to create an index on json column
            ngram_index:
                A list of attributes for which to create an ngram index.
                
        """
        # Check the configuration
        if not ((fragment_name is None and data_iterator is None and row_mapper is None) is not (tagger is None and fragmenter is None)):
            raise PgCollectionException( \
               ('Either tagger ({}) and fragmenter ({}) must be specified, or '+\
                'fragment_name ({}), data_iterator ({}) and row_mapper ({}) must be specified').format(tagger, fragmenter, \
                                                                            fragment_name, data_iterator, row_mapper ) )
        layer_name = fragment_name or tagger.output_layer
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer {!r}".format(
                                        self.name, layer_name))
        logger.info('collection: {!r}'.format(self.name))
        if self._is_empty:
            raise PgCollectionException("can't add fragmented layer {!r}, the collection is empty".format(layer_name))
        if self.has_layer(layer_name):
            exception = PgCollectionException("can't create layer {!r}, layer already exists".format(layer_name))
            logger.error(exception)
            raise exception
        if data_iterator is None:
            data_iterator = self.select(layers=tagger.input_layers, progressbar=progressbar)

        meta_columns = ()
        if meta is not None:
            meta_columns = tuple(meta)
        extra_columns = []
        if meta_columns:
            extra_columns.extend(meta_columns)
        if ngram_index is not None:
            ngram_index_keys = tuple(ngram_index.keys())
            extra_columns.extend(ngram_index_keys)
        columns = ["id", "parent_id", "text_id", "data"] + extra_columns

        conn = self.storage.conn
        with conn.cursor() as c:
            try:
                conn.commit()
                conn.autocommit = True
                # create table and indices
                self._create_layer_table(cursor=c,
                                         layer_name=layer_name,
                                         meta=meta,
                                         is_fragment=True,
                                         create_index=create_index,
                                         ngram_index=ngram_index)
                fragment_id = 0
                structure_written = False
                fragment_table_id = layer_table_identifier(self.storage, self.name, layer_name, layer_type='fragmented')
                with BufferedTableInsert(conn, fragment_table_id, columns=columns, query_length_limit=query_length_limit) \
                                                                                as buffered_inserter:
                    for row in data_iterator:
                        text_id, text = row[0], row[1]
                        if tagger is not None:
                            for fragment in fragmenter(tagger.make_layer(text, status={})):
                                layer = fragment.layer
                                # TODO: how should we get parent_layer_id value here ?
                                # previous version did not assign parent_layer_id at all. 
                                # currently, we are trying to get parent_layer_id from layer's 
                                # meta, and if it is missing from there, we fall back to 
                                # text_id;
                                parent_layer_id = \
                                    layer.meta.get('parent_layer_id', text_id)
                                extra_data = []
                                if meta_columns:
                                    extra_data.extend( fragment.meta[k] for k in meta_columns )
                                if ngram_index is not None:
                                    ngram_values = [create_ngram_fingerprint_index(layer, attr, n)
                                                                         for attr, n in ngram_index.items()]
                                    extra_data.extend( ngram_values )
                                assert isinstance(layer, Layer)
                                layer_json = layer_to_json(layer)
                                values = [fragment_id, parent_layer_id, text_id, layer_json] + extra_data
                                buffered_inserter.insert( values )
                                fragment_id += 1
                                if not structure_written:
                                    self._structure.insert(layer=layer, layer_type='fragmented', meta=meta, is_sparse=False)
                                    structure_written = True
                        else:
                            for record in row_mapper(row):
                                layer = record['fragment']
                                assert isinstance(layer, Layer)
                                # TODO: we need to ensure that the name of the output layer is fragment_name,
                                # and not a name of an existing layer (which would give us an error on writing 
                                # the structure). The old implementation did not write structure at all.
                                # Currently, we overwrite the layer name, but probably row_mapper should take 
                                # care of it
                                layer.name = fragment_name
                                layer_json = layer_to_json(layer)
                                parent_layer_id = record['parent_id']
                                extra_data = []
                                if meta_columns:
                                    extra_data.extend( layer.meta[k] for k in meta_columns )
                                if ngram_index is not None:
                                    ngram_values = [create_ngram_fingerprint_index(layer, attr, n)
                                                    for attr, n in ngram_index.items()]
                                    extra_data.extend( ngram_values )
                                values = [fragment_id, parent_layer_id, text_id, layer_json] + extra_data
                                buffered_inserter.insert( values )
                                fragment_id += 1
                                if not structure_written:
                                    self._structure.insert(layer=layer, layer_type='fragmented', meta=meta, is_sparse=False)
                                    structure_written = True

            except Exception:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()

        logger.info('fragmented layer created: {!r}'.format(layer_name))
        logger.debug('inserted {!r} layers into {!r}.'.format(fragment_id, layer_name))


    def create_layer(self, layer_name=None, data_iterator=None, row_mapper=None, tagger=None,
                     create_index=False, ngram_index=None, overwrite=False, meta=None, progressbar=None,
                     query_length_limit=5000000, mode=None, sparse=False):
        """
        Creates a new detached layer to this collection.

        **Important:** You should use this method only after the insertion of Text objects into
        the collection has been finished. Once you create a detached layer, new Text objects
        cannot be inserted into the collection.

        Args:

            layer_name: str
                Name of the layer added to the collection. If not provided, then
                `tagger` must be provided and the name of the layer will be
                `tagger.output_layer`.
            data_iterator: iterator
                Iterator over Text collection which generates tuples (`text_id`, `text`).
                See method `PgCollection.select`.
            row_mapper: function
                For each record produced by `data_iterator` return a list
                of `RowMapperRecord` objects.
            tagger: Tagger
                either tagger must be None or layer_name, data_iterator and row_mapper must be None
            create_index: bool
                Whether to create an index on json column
            ngram_index: list
                A list of attributes for which to create an ngram index
            overwrite: bool
                deprecated, use mode='overwrite' instead
                If True and layer table exists, table is overwritten.
                If False and layer table exists, error is raised.
            meta: dict of str -> str
                Specifies table column names and data types to create for storing additional
                meta information. E.g. meta={"sum": "int", "average": "float"}.
                See `pytype2dbtype` in `pg_operations` for supported types.
            progressbar: str
                if 'notebook', display progressbar as a jupyter notebook widget
                if 'unicode', use unicode (smooth blocks) to fill the progressbar
                if 'ascii', use ASCII characters (1-9 #) to fill the progressbar
                else disable progressbar (default)
            query_length_limit: int
                soft approximate query length limit in unicode characters, can be exceeded by the length of last buffer
                insert
            mode: str 
                Specifies how layer creation should handle existing layers. 
                Possible modes:
                * None / 'new' - creates a new layer. If the layer already exists in the collection, raises an exception.
                * 'append'     - appends to an existing layer; annotates only those documents that are missing the layer.
                                 raises an exception if the collection does not have the layer;
                * 'overwrite'  - deletes the old layer and creates a new layer in its place; 
                                 if the collection does not have the layer, then adds the new layer to the collection,
                                 and fills with data;
            sparse: bool
                Whether the layer table is created as a sparse tabel which means that empty layers are not stored in
                the table. The layer search and iteration process is faster on sparse tables.
                Note that collection version 3.0 is required for sparse tables.
        """
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer".format(self.name))

        if sparse and self.version < '3.0':
            raise PgCollectionException("Sparse tables are not supported in collection version {!r}.".format(self.version))

        assert (layer_name is None and data_iterator is None and row_mapper is None) is not (tagger is None),\
               'either tagger ({}) must be None or layer_name ({}), data_iterator ({}) and row_mapper ({}) must be None'.format(tagger, layer_name, data_iterator, row_mapper)

        # TODO: remove overwrite parameter
        assert overwrite is False or mode is None, (overwrite, mode)
        if overwrite:
            mode = 'overwrite'
        mode = mode or 'new'

        def default_row_mapper(row):
            text_id, text = row[0], row[1]
            status = {}
            layer = tagger.make_layer(text=text, status=status)
            return RowMapperRecord(layer=layer, meta=status)

        layer_name = layer_name or tagger.output_layer
        row_mapper = row_mapper or default_row_mapper

        missing_layer = layer_name if mode == 'append' else None
        if data_iterator is None:
            data_iterator = self.select(layers=tagger.input_layers, progressbar=progressbar,
                                        query=MissingLayerQuery(missing_layer=missing_layer) if missing_layer is not None else None)

        logger.info('collection: {!r}'.format(self.name))
        if self._is_empty:
            raise PgCollectionException("can't add detached layer {!r}, the collection is empty".format(layer_name))
        if self.has_layer(layer_name):
            if mode == 'overwrite':
                logger.info("overwriting output layer: {!r}".format(layer_name))
                self.delete_layer(layer_name=layer_name, cascade=True)
            elif mode == 'append':
                logger.info("appending existing layer: {!r}".format(layer_name))
            else:
                exception = PgCollectionException("can't create {!r} layer, the layer already exists".format(layer_name))
                logger.error(exception)
                raise exception
        else:
            if mode == 'append':
                exception = PgCollectionException("can't append layer {!r}, layer does not exist".format(layer_name))
                logger.error(exception)
                raise exception
            elif mode == 'new':
                logger.info('preparing to create a new layer: {!r}'.format(layer_name))
            elif mode == 'overwrite':
                logger.info('nothing to overwrite, preparing to create a new layer: {!r}'.format(layer_name))

        meta_columns = ()
        if meta is not None:
            meta_columns = tuple(meta)

        extra_columns = []
        if meta_columns:
            extra_columns.extend(meta_columns)
        if ngram_index is not None:
            ngram_index_keys = tuple(ngram_index.keys())
            extra_columns.extend(ngram_index_keys)

        conn = self.storage.conn
        conn.commit()
        conn.autocommit = True

        with conn.cursor() as c:
            try:
                # create table and indices
                if mode in {'new', 'overwrite'}:
                    self._create_layer_table(cursor=c,
                                             layer_name=layer_name,
                                             is_fragment=False,
                                             create_index=create_index,
                                             ngram_index=ngram_index,
                                             overwrite=overwrite,
                                             meta=meta)
                # insert data
                structure_written = (mode == 'append')
                logger.info('inserting data into the {!r} layer table'.format(layer_name))
                
                with CollectionDetachedLayerInserter( self, layer_name, extra_columns=extra_columns, 
                                                      query_length_limit=query_length_limit,
                                                      sparse=sparse ) as buffered_inserter:

                    for row in data_iterator:
                        collection_text_id, text = row[0], row[1]

                        record = row_mapper(row)
                        layer = record.layer

                        extra_values = []
                        if meta_columns:
                            extra_values.extend(record.meta[k] for k in meta_columns)

                        if ngram_index is not None:
                            extra_values.extend(create_ngram_fingerprint_index(layer=layer,
                                                                         attribute=attr,
                                                                         n=ngram_index[attr])
                                          for attr in ngram_index_keys)

                        buffered_inserter.insert(layer, collection_text_id, key=collection_text_id, extra_data=extra_values)

                        if not structure_written:
                            self._structure.insert(layer=layer, layer_type='detached', meta=meta, is_sparse=sparse)
                            structure_written = True
            except Exception:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()

        logger.info('layer created: {!r}'.format(layer_name))

    def add_layer(self, layer_template: Layer,
                        layer_type: str = 'detached',
                        fragmented_layer: bool = False,
                        meta: Dict[str, str] = None,
                        create_index: bool = False,
                        ngram_index=None,
                        sparse: bool = False) -> None:
        """
        Adds detached or fragmented layer to the collection. You can use this 
        method to add an empty layer to the collection that will be filled in
        with data later. Conditions:

        * the collection must already contain some documents before the layer can be added.
          After adding a layer, new documents can no longer be inserted into the collection;
        * this method should be called only once, even if the layer creation is spread among
          multiple processes/threads;

        Layer must be specified by a template layer. The function fails only if 
        the layer is already present or the database schema is in an inconsistent 
        state. 
        One should set create_index only if one plans to search specific elements 
        from the layer. The ngram index speeds up search of element combinations. 
        This is useful when one uses phase grammars.

        Args:
            layer_template: Layer
                A template which is used as a basis on creating the new layer
            layer_type: str
                Must be one of the following: {'detached', 'fragmented', 'multi'}.
                See also: PostgresStorage.TABLED_LAYER_TYPES
            fragmented_layer: bool
                Whether a fragmented layer will be created (default: False)
                Warning: this is a deprected argument and will be removed in 
                future version.
            meta: dict of str -> str
                Specifies table column names and data types to create for storing additional
                meta information. E.g. meta={"sum": "int", "average": "float"}.
                See `pytype2dbtype` in `pg_operations` for supported types.
            create_index: bool
                Whether to create an index on json column (default: False)
            ngram_index: list
                A list of attributes for which to create an ngram index (default: None)
                :param sparse:
            sparse: bool
                Whether the layer table is created as a sparse tabel which means
                that empty layers are not stored in the table.
                The layer search and iteration process is faster on sparse tables.
                Note that collection version 3.0 is required for sparse tables.
        """
        # Check existence of the collection
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't add layer".format(self.name))

        # Check input arguments
        if not isinstance( layer_template, Layer ):
            raise TypeError('(!) layer_template must be an instance of Layer')

        if sparse and self.version < '3.0':
            raise PgCollectionException("Sparse tables are not supported in collection version {!r}.".format(self.version))

        if layer_type not in pg.PostgresStorage.TABLED_LAYER_TYPES:
            raise PgCollectionException("Unexpected layer type {!r}. Supported layer types are: {!r}".format(layer_type, \
                                                                     pg.PostgresStorage.TABLED_LAYER_TYPES))

        if fragmented_layer:
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn('Flag collection.add_layer(...fragmented_layer=True) is deprecated. '+\
                          'Please use collection.add_layer(..., layer_type="fragmented") instead. '+\
                          'Currently, a detached layer is created.', 
                          DeprecationWarning)
            warnings.simplefilter("ignore", DeprecationWarning)

        # Check existence of the layer
        if self.layers is not None and layer_template.name in self.layers:
            raise PgCollectionException("The {!r} layer already exists.".format(layer_template.name))

        conn = self.storage.conn
        conn.commit()
        conn.autocommit = False
        with conn.cursor() as cur:
            try:
                structure_table_id = structure_table_identifier(self.storage, self.name)
                # EXCLUSIVE locking -- this mode allows only reads from the table 
                # can proceed in parallel with a transaction holding this lock mode.
                # Prohibit all other modification operations such as delete, insert, 
                # update, create index.
                # (https://www.postgresql.org/docs/9.4/explicit-locking.html)
                cur.execute(SQL('LOCK TABLE ONLY {} IN EXCLUSIVE MODE').format(structure_table_id))

                # We may have to wait for the lock and receive it later: validate that conditions are OK
                if self._is_empty:
                    raise PgCollectionException("the collection is empty".format(layer_template.name))

                if layer_table_exists(self.storage, self.name, layer_template.name, layer_type=layer_type):
                    raise PgCollectionException(
                        "The table for the {} layer {!r} already exists.".format(layer_type, layer_template.name))

                self._create_layer_table(
                    cursor=cur,
                    layer_name=layer_template.name,
                    is_fragment=(layer_type == 'fragmented'),
                    create_index=create_index,
                    ngram_index=ngram_index,
                    overwrite=False,
                    meta=meta)

                self._structure.insert(layer=layer_template, layer_type=layer_type, meta=meta, is_sparse=sparse)

            except Exception as layer_creation_error:
                conn.rollback()
                raise PgCollectionException("can't add layer {!r}".format(layer_template.name)) from layer_creation_error
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()

        logger.info('{} layer {!r} created from template'.format(layer_type, layer_template.name))

    def create_layer_block(self, tagger, block, data_iterator=None, meta=None, query_length_limit=5000000, mode=None):
        """Creates a layer block.
        
        Note: before the layer block can be created, the layer table must already exist.
        Use the method add_layer() to create an empty layer (table).

        **Important:** You should use this method only after the insertion of Text objects into
        the collection has been finished. Once you create a detached layer, new Text objects
        cannot be inserted into the collection.

        :param tagger: Tagger
            tagger to be applied on collection's texts.
            Note: tagger's input_layers will be selected automatically, 
            but the collection must have all the input layers. 
        :param block: Tuple[int, int]
            pair of integers `(module, remainder)`. Only texts with `id % module = remainder` are tagged.
        :param data_iterator: iterator
            Optional: iterator over Texts of this collection which generates tuples (`text_id`, `text`).
            If not provided, then applies the block query over all texts of this collection. 
            See method `PgCollection.select`.
        :param meta: dict of str -> str
            Specifies table column names and data types to create for storing additional
            meta information. E.g. meta={"sum": "int", "average": "float"}.
            See `pytype2dbtype` in `pg_operations` for supported types.
        :param query_length_limit: int
            soft approximate query length limit in unicode characters, can be exceeded by the length of 
            last buffer insert
        :param mode: str 
            Specifies how layer creation should handle existing layers inside the block. 
            Possible modes:
            * None / 'new' - attempts to tag all texts inside the block 
                             (creates a new block);
            * 'append'     - finds untagged texts inside the block and only tags untagged texts;
                             (continues a block which tagging has not been finished)
        """
        mode = 'new' if mode is None else mode
        layer_name = tagger.output_layer

        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer {!r}".format(
                self.name, layer_name))

        meta_columns = ()
        if meta is not None:
            meta_columns = tuple(meta)

        logger.info('inserting data into the {!r} layer table block {}'.format(layer_name, block))

        # Attempt to load the structure
        if layer_name not in self._structure:
            self._structure.load()
        if layer_name not in self._structure:
            # Note: at this point, the structure should already exist
            # ( created by add_layer(...) function )
            raise PgCollectionException(("Layer {!r} is missing from collection's structure. " + \
                                         "Use collection.add_layer(...) to update the structure " + \
                                         "before using this method.").format(layer_name))
        struct = self._structure[layer_name]
        if struct['layer_type'] != 'detached':
            raise PgCollectionException(("Wrong layer type: {!r}. This method can only be applied " + \
                                         "on 'detached' layers.").format(struct['layer_type']))
        layer_structure = (layer_name, struct['attributes'], struct['ambiguous'],
                           struct['parent'], struct['enveloping'])
        sparse = struct['sparse'] if 'sparse' in struct else False

        if data_iterator is not None:
            # Validate & extend input data_iterator
            if not isinstance(data_iterator, pg.PgSubCollection):
                raise TypeError( ('(!) Unexpected data_iterator type {!r}, '+
                                   'expected PgSubCollection.').format( type(data_iterator) ) )
            # Collection can only be self
            if data_iterator.collection != self:
                raise ValueError( "(!) wrong collection: data_iterator's collection should be "+\
                                  "this collection." )
            # Collect layers that should be added to selection
            add_selected_layers = []
            for required_layer in tagger.input_layers:
                if required_layer not in data_iterator.selected_layers:
                    if not self.has_layer( required_layer ):
                        raise PgCollectionException(("Tagger's input layer {!r} is missing from " +\
                                                     "this collection, cannot apply the tagger." +\
                                                     "").format(required_layer))
                    add_selected_layers.append( required_layer )
            # Extend data_iterator by new constraints and layers
            additional_constraint = pg.WhereClause(collection=self, query=pg.BlockQuery(*block))
            if mode.lower() == 'append':
                additional_constraint &= \
                    pg.WhereClause( collection=self, 
                                    query = MissingLayerQuery(missing_layer=tagger.output_layer))
            data_iterator = data_iterator.select( \
                additional_constraint=additional_constraint, 
                selected_layers=data_iterator.selected_layers + add_selected_layers )
        else:
            # Use default data_iterator
            block_query = pg.BlockQuery(*block)
            if mode.lower() == 'append':
                block_query &= MissingLayerQuery( missing_layer = tagger.output_layer )
            data_iterator = self.select(query=block_query, layers=tagger.input_layers)
        
        with CollectionDetachedLayerInserter( self, layer_name, extra_columns=meta_columns, 
                                              query_length_limit=query_length_limit,
                                              sparse=sparse) as buffered_inserter:

            for collection_text_id, text in data_iterator:
                layer = tagger.make_layer(text=text, status=None)
                # Check layer structure
                layer_structure_from_tagger = (layer.name, layer.attributes, layer.ambiguous,
                                               layer.parent, layer.enveloping)
                if layer_structure != layer_structure_from_tagger:
                    raise ValueError( ('(!) Mismatching layer structures: '+
                                       'structure in database: {!r} and '+
                                       'structure created by tagger: {!r}').format(layer_structure,
                                                                                   layer_structure_from_tagger) )

                extra_values = []
                if meta_columns:
                    extra_values.extend( [layer.meta[k] for k in meta_columns] )
                
                buffered_inserter.insert(layer, collection_text_id, key=collection_text_id, extra_data=extra_values)

        logger.info('block {} of {!r} layer created'.format(block, layer_name))

    def _create_layer_table(self, cursor, layer_name, is_fragment=False, create_index=True,
                            ngram_index=None, overwrite=False, meta=None):
        if is_fragment:
            layer_table = fragment_table_name(self.name, layer_name)
        else:
            layer_table = layer_table_name(self.name, layer_name)

        if overwrite:
            if is_fragment:
                raise NotImplementedError
            else:
                if layer_table_exists(self.storage, self.name, layer_name):
                    drop_layer_table(self.storage, self.name, layer_name)
        elif table_exists(self.storage, layer_table):
            raise PgCollectionException("The table {!r} of the {!r} layer already exists.".format(layer_table, layer_name))

        if self._temporary:
            temporary = SQL('TEMPORARY')
        else:
            temporary = SQL('')

        # create layer table and index
        q = ('CREATE {temporary} TABLE {layer_identifier} ('
             'id SERIAL PRIMARY KEY, '
             '%(parent_col)s'
             'text_id int NOT NULL, '
             'data jsonb'
             '%(meta_cols)s'
             '%(ngram_cols)s);')

        if is_fragment is True:
            parent_col = "parent_id int NOT NULL,"
        else:
            parent_col = ""

        if ngram_index is not None:
            ngram_cols = ", %s" % ",".join(["%s text[]" % Identifier(column).as_string(self.storage.conn)
                                            for column in ngram_index])
        else:
            ngram_cols = ""

        if meta is not None:
            cols = [Identifier(col).as_string(self.storage.conn) for col in meta.keys()]
            types = [pg.pytype2dbtype[py_type] for py_type in meta.values()]
            meta_cols = ", %s" % ",".join(["%s %s" % (c, d) for c, d in zip(cols, types)])
        else:
            meta_cols = ""

        q %= {"parent_col": parent_col, "ngram_cols": ngram_cols, "meta_cols": meta_cols}
        if is_fragment:
            layer_identifier = pg.table_identifier(self.storage, fragment_table_name(self.name, layer_name))
        else:
            layer_identifier = pg.table_identifier(self.storage, layer_table_name(self.name, layer_name))
        q = SQL(q).format(temporary=temporary, layer_identifier=layer_identifier)
        cursor.execute(q)
        logger.debug(cursor.query.decode())

        q = SQL("COMMENT ON TABLE {} IS {};").format(
                layer_identifier,
                Literal('created by {} on {}'.format(self.storage.user, time.asctime())))
        cursor.execute(q)
        logger.debug(cursor.query.decode())

        # create jsonb index
        if create_index is True:
            cursor.execute(SQL(
                "CREATE INDEX {index} ON {schema}.{table} USING gin ((data->'layers') jsonb_path_ops);").format(
                schema=Identifier(self.storage.schema),
                index=Identifier('idx_%s_data' % layer_table),
                table=Identifier(layer_table)))
            logger.debug(cursor.query.decode())

        # create ngram array index
        if ngram_index is not None:
            for column in ngram_index:
                cursor.execute(SQL(
                    "CREATE INDEX {index} ON {schema}.{table} USING gin ({column});").format(
                    schema=Identifier(self.storage.schema),
                    index=Identifier('idx_%s_%s' % (layer_table, column)),
                    table=Identifier(layer_table),
                    column=Identifier(column)))
                logger.debug(cursor.query.decode())

        cursor.execute(SQL(
            "CREATE INDEX {index} ON {layer_table} (text_id);").format(
            index=Identifier('idx_%s__text_id' % layer_table),
            layer_table=layer_identifier))
        logger.debug(cursor.query.decode())

    def delete_layer(self, layer_name, cascade=False):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't delete layer {!r}".format(
                self.name, layer_name))
    
        if layer_name not in self._structure:
            raise PgCollectionException("collection does not have a layer {!r}".format(layer_name))
        if self._structure[layer_name]['layer_type'] == 'attached':
            raise PgCollectionException("can't delete attached layer {!r}".format(layer_name))

        for ln, struct in self._structure.structure.items():
            if ln == layer_name:
                continue
            if layer_name == struct['enveloping'] or layer_name == struct['parent']:
                if cascade:
                    self.delete_layer(ln, cascade=True)
                else:
                    raise PgCollectionException("can't delete layer {!r}; "
                                                "there is a dependant layer {!r}".format(layer_name, ln))
        drop_layer_table(self.storage, self.name, layer_name)
        self._structure.delete_layer(layer_name)
        logger.info('layer deleted: {!r}'.format(layer_name))

    def delete_fragment(self, fragment_name):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format(self.name))
        if fragment_name not in self.get_fragment_names():
            raise PgCollectionException("Collection does not have a layer fragment '%s'." % fragment_name)
        drop_fragment_table(self.storage, self.name, fragment_name)

    def delete(self):
        """Removes collection and all related layers.
          **Important:** this method is deprecated. Please use
          PostgresStorage.delete_collection(...) to delete a collection.
        """
        error_msg = '(!) PgCollection.delete() is deprecated. '+\
                    'Please use PostgresStorage.delete_collection(...) '+\
                    'method to remove a collection from database.'
        raise Exception( error_msg )

    def has_layer(self, layer_name, layer_type=None):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        if layer_type is None:
            return layer_name in self._structure
        else:
            return layer_name in self.get_layer_names_by_type(layer_type=layer_type)

    def has_fragment(self, fragment_name):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('collection.has_fragment(...) is deprecated. '+\
                      'Use collection.has_layer(name, layer_type="fragmented") instead. ', 
                      DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        return fragment_name in self.get_fragment_names()

    def is_sparse(self, layer_name):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        if not self.has_layer(layer_name):
            raise ValueError('collection does not have layer {!r}'.format(layer_name))
        return self._structure[layer_name]['sparse'] if 'sparse' in self._structure[layer_name] else False

    def get_fragment_names(self):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('collection.get_fragment_tables(...) is deprecated. '+\
                      'Use collection.get_layer_names_by_type(layer_type="fragmented") instead. ', 
                      DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        
        lf_names = []
        for tbl in self.get_fragment_tables():
            layer = re.sub("^%s__" % self.name, "", tbl)
            layer = re.sub("__fragment$", "", layer)
            lf_names.append(layer)
        return lf_names

    def get_fragment_tables(self):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn('collection.get_fragment_tables(...) is deprecated. '+\
                      'Use collection.get_layer_names_by_type(layer_type="fragmented") with '+\
                      'fragment_table_name(...) instead. ', 
                      DeprecationWarning)
        warnings.simplefilter("ignore", DeprecationWarning)
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        
        fragment_tables = []
        for tbl in pg.get_all_table_names(self.storage):
            if tbl.startswith("%s__" % self.name) and tbl.endswith("__fragment"):
                fragment_tables.append(tbl)
        return fragment_tables

    def get_layer_names_by_type(self, layer_type:str='attached'):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        if layer_type not in pg.PostgresStorage.ALL_LAYER_TYPES:
            raise PgCollectionException("Unexpected layer type {!r}. Supported layer types are: {!r}".format(layer_type, \
                                                                     pg.PostgresStorage.ALL_LAYER_TYPES))
        layer_names = []
        for layer in self._structure.keys():
            cur_layer_type = self._structure[layer]['layer_type']
            if cur_layer_type == layer_type:
                layer_names.append( layer )
        return layer_names

    def get_layer_meta(self, layer_name):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        
        if layer_name not in self.layers:
            raise PgCollectionException("Collection does not have the layer {!r}".format(layer_name))

        with self.storage.conn.cursor() as c:
            columns = ['id', 'text_id'] + self._structure[layer_name]['meta']

            c.execute(SQL('SELECT {} FROM {};').format(
                SQL(', ').join(map(Identifier, columns)),
                layer_table_identifier(self.storage, self.name, layer_name)))
            data = c.fetchall()
            return pandas.DataFrame(data=data, columns=columns)

    def get_sparse_layer_template(self, layer_name, as_json=True):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))

        if not self.is_sparse(layer_name):
            raise ValueError('layer {!r} is not sparse'.format(layer_name))

        layer_template_dict = self._structure[layer_name]['layer_template_dict']
        layer_template = dict_to_layer(layer_template_dict) if layer_template_dict is not None else None
        if as_json:
            layer_template_json = layer_to_json(layer_template) if layer_template is not None else None
        return layer_template_json if as_json else layer_template

    def export_layer(self, layer, attributes, collection_meta=None, table_name=None, progressbar=None, mode='NEW'):
        """
        Exports annotations from the given layer to a separate table.
        
        At minimum, the exported layer table has the following columns:
        * id -- annotation id (unique in the whole collection);
        * text_id -- text's id in the collection;
        * span_nr -- span's index in the layer;
        * span_start -- span's start index in the text;
        * span_end   -- span's end index in the text;
        Optionally, if attributes is set, then there will be a separate 
        column for each layer attribute. And if collection_meta is set, 
        then there will be an additional column for each metadata field.
        
        Mode=='APPEND' can be used to append to an existing table. 
        However, it is responsibility of the user to ensure that the 
        existing export table has correct structure / columns, and 
        that the export will not produce any duplicate entries 
        (technically, you can create duplicates, because there is no 
         duplicate checking).

        The layer table will be created in the self.storage.schema.
        TODO: add a possibility to use a different schema 

        Parameters:
        
        :param layer: str
            Name of the layer to be exported. 
            Must be an existing layer of this collection.
        :param attributes: List[str]
            Attributes of the layer which will be exported.
            For each attribute, a separate table column will
            be created.
        :param collection_meta: List[str]
            Collection's metadata fields to be exported. 
            For each metadata field, a separate table column 
            will be created.
            Default: None
        :param table_name: str
            (Optional) Name for the export table. If not provided,
            then table name will be formatted as:
             '{}__{}__export'.format(collection_name, layer_name)
            Default: None
        :param progressbar: str
            (Optional) Whether the progressbar is used on iteration.
            Possible values: [None, 'ascii', 'notebook']
            Default: None
        :param  mode: str
            If mode=='NEW', then creates a new export table (and
            throws an expection if the table already exists). 
            If mode=='APPEND', then appends to an existing table 
            (and throws an expection if the table does not exist).
            Default: 'NEW'
        """
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't export layer {!r}".format(
                self.name, layer))
        
        if not isinstance(mode, str) or mode.upper() not in ['NEW', 'APPEND']:
            raise ValueError('(!) Mode {!r} not supported. Use {!r} or {!r}.'.format( mode, 'NEW', 'APPEND' ))
        mode = mode.upper()
        
        if collection_meta is None:
            collection_meta = []

        if table_name is None:
            table_name = '{}__{}__export'.format(self.name, layer)
        table_identifier = pg.table_identifier(storage=self.storage, table_name=table_name)

        logger.info('preparing to export {!r} layer with attributes {!r}'.format(layer, attributes))

        columns = [
            ('id', 'serial PRIMARY KEY'),
            ('text_id', 'int NOT NULL'),
            ('span_nr', 'int NOT NULL'),
            ('span_start', 'int NOT NULL'),
            ('span_end', 'int NOT NULL'),
        ]
        columns.extend((attr, 'text') for attr in attributes)
        columns.extend((attr, 'text') for attr in collection_meta)

        # Check for the existence of the table
        create_table = True
        if table_exists(self.storage, table_name):
            if mode == 'NEW':
                raise PgCollectionException( ('Exported layer table {!r} already exists. Please use '+
                                              'mode="APPEND" to append to the existing table.').format(table_name) )
            else:
                logger.info('appending to an existing export table')
                create_table = False
                # TODO: check that the old export table has the approriate columns
        else:
            if mode == 'APPEND':
                raise PgCollectionException( ('Exported layer table {!r} does not exist, cannot use '+
                                              'mode="APPEND". Please use mode="NEW" to create a new '+
                                              'table.').format(table_name) )

        if create_table:
            # Create new table
            columns_sql = SQL(",\n").join(SQL("{} {}").format(Identifier(n), SQL(t)) for n, t in columns)

            self.storage.conn.commit()
            with self.storage.conn.cursor() as c:
                logger.debug(c.query)
                c.execute(SQL("CREATE TABLE {} ({});").format(table_identifier,
                                                              columns_sql))
                logger.debug(c.query)
                c.execute(SQL("COMMENT ON TABLE {} IS {};").format(table_identifier,
                                                                   Literal('created by {} on {}'.format(self.storage.user,
                                                                                                        time.asctime()))))
                logger.debug(c.query)
                self.storage.conn.commit()

        texts = self.select(layers=[layer], progressbar=progressbar, collection_meta=collection_meta, keep_all_texts=False)
        i = 0
        initial_rows = 0
        if mode == 'APPEND':
            # Get the number of inserted rows so far
            initial_rows = count_rows(self.storage, table_identifier=table_identifier)
            # Shift id to the last inserted row
            i = initial_rows
        with BufferedTableInsert( self.storage.conn, table_identifier, columns=[c[0] for c in columns]) as buffered_inserter:
            for entry in texts:
                if len( collection_meta ) > 0:
                    text_id, text, meta = entry
                else: 
                    text_id, text = entry
                for span_nr, span in enumerate(text[layer]):
                    for annotation in span.annotations:
                        i += 1
                        values = [ i, text_id, span_nr, span.start, span.end ]
                        values.extend( [annotation[attr] for attr in attributes] )
                        values.extend( [meta[k] for k in collection_meta] )
                        buffered_inserter.insert( values )

        logger.info('{} annotations exported to "{}"."{}"'.format(i-initial_rows, self.storage.schema, table_name))

    def _repr_html_(self):
        if not self.exists():
            return ('<p style="color:red">{self.__class__.__name__} {self.name!r} does not exist!</p><br/> '+\
                    'Likely reason: the collection has been deleted from the database.'
                   ).format(self=self)
        
        if self.version < '3.0':
            structure_columns = ['layer_type', 'attributes', 'ambiguous', 'parent', 'enveloping', 'meta']
        else:
            structure_columns = ['layer_type', 'attributes', 'ambiguous', 'sparse', 'parent', 'enveloping', 'meta']
        if self._is_empty:
            structure_html = '<br/>unknown'
        else:
            structure_html = pandas.DataFrame.from_dict(self._structure.structure,
                                                        orient='index',
                                                        columns=structure_columns
                                                        ).to_html()
        meta_html = ''
        if self.meta is not None:
            if self.meta.columns:
                meta_html = pandas.DataFrame.from_dict(self.meta.column_types,
                                                       orient='index',
                                                       columns=['data type']
                                                       ).to_html()
            else:
                meta_html = 'This collection has no metadata.<br/>'
        return ('<b>{self.__class__.__name__}</b><br/>'
                '<b>name:</b> {self.name}<br/>'
                '<b>storage:</b> {self.storage}<br/>'
                '<b>count objects:</b> {count}<br/>'
                '<b>Metadata</b><br/>{meta_html}'
                '<b>Layers</b>{struct_html}'
                ).format(self=self, count=len(self), meta_html=meta_html, struct_html=structure_html)
