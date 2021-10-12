import collections
import json
import re
import time
from contextlib import contextmanager
from typing import Sequence, Dict

import pandas
import psycopg2
from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier, Literal, DEFAULT

from estnltk import logger
from estnltk_core import Layer
from estnltk.converters import dict_to_layer
from estnltk.converters import dict_to_text
from estnltk.converters import layer_to_dict
from estnltk_core.layer_operations import create_ngram_fingerprint_index
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import BufferedTableInsert
from estnltk.storage.postgres import CollectionDetachedLayerInserter
from estnltk.storage.postgres import CollectionTextObjectInserter
from estnltk.storage.postgres import count_rows
from estnltk.storage.postgres import drop_fragment_table
from estnltk.storage.postgres import drop_layer_table
from estnltk.storage.postgres import fragment_table_identifier
from estnltk.storage.postgres import fragment_table_name
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import structure_table_exists
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres.queries.missing_layer_query import MissingLayerQuery
from estnltk.storage.postgres.queries.slice_query import SliceQuery


class PgCollectionException(Exception):
    pass


RowMapperRecord = collections.namedtuple("RowMapperRecord", ["layer", "meta"])

class PgCollection:
    """Convenience wrapper over PostgresStorage

    """
    def __init__(self, name: str, storage, meta: dict = None, temporary: bool = False, version='0.0'):
        assert isinstance(name, str), name
        assert name.islower(), name
        assert name.isidentifier(), name
        if '__' in name:
            raise PgCollectionException('collection name must not contain double underscore: {!r}'.format(name))
        self.name = name
        self.storage = storage
        # TODO: read meta columns from collection table if exists, move this parameter to self.create
        self.meta = meta or {}
        self._temporary = temporary

        if version == '0.0':
            self._structure = pg.v00.CollectionStructure(self)
        elif version == '1.0':
            self._structure = pg.v10.CollectionStructure(self)
        elif version == '2.0':
            self._structure = pg.v20.CollectionStructure(self)
        else:
            raise ValueError("version must be '0.0', '1.0' or '2.0'")
        self.version = version

        self.column_names = ['id', 'data'] + list(self.meta)

        self._selected_layes = None
        self._is_empty = not self.exists() or len(self) == 0

    def create(self, description=None, meta: dict = None, temporary=None):
        """Creates the database tables for the collection

        """
        if description is None:
            description = 'created by {} on {}'.format(self.storage.user, time.asctime())

        self.structure.create_table()

        if meta:
            self.meta = meta
            self.column_names = ['id', 'data'] + list(meta)

        pg.create_collection_table(self.storage,
                                   collection_name=self.name,
                                   meta_columns=self.meta,
                                   description=description)

        logger.info('new empty collection {!r} created'.format(self.name))
        return self

    @property
    def structure(self):
        return self._structure

    @property
    def layers(self):
        if self._is_empty:
            return []
        return list(self._structure)

    @property
    def selected_layers(self):
        if self._selected_layes is None:
            if not self.exists():
                raise PgCollectionException('collection {!r} does not exist'.format(self.name))
            if self._is_empty is None:
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

           Returned layers are ordered ...
           The latter provides a correct order for loading and re-attaching detached layers

           TODO: Complete description
        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))
        
        layers_extended = []

        # TODO:
        # Rekursioonita on raske tagada õiget kihtide järjekorda
        # Vaja topoloogilist järjestust.
        #
        # Võimalikud lahendused on
        # 1. Otsida Algoritmide ja andmestruktuuride raamatust topoloogiline sort
        # 2. Lisada collection_structure tabelisse igale kihile autoinkrementiga järjekorranumber
        #    ja järjestada kihid vastavalt id numbrile
        # 3. Defineerida serialiseerimine nii, et pole vahet mis järjekorras kihid luuakse
        #    - Selleks peab saama EnvelopingSpani sisu defineerida avaldisega
        #    - Peab defineerima Layer.evaluate, mis kõik avaldised asendab hetkel tekkivate väärtustega
        #    See lahendus lubab vaevata ka depencency_layer deserialiseerimist
        #
        # Mina eelistaksin lahendust 2 ja tulevikus 3

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

    # TODO: make it work
    def extend(self, other: 'PgCollection'):
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
            with collection.insert() as collection_insert:
                collection_insert( Text( ... ), key=0, meta_data={'my_meta':'A'} )
                collection_insert( Text( ... ), key=1, meta_data={'my_meta':'B'} )
                ...
                
        Example usage 2. Insert annotated Text objects:
            # Create collection
            collection.create()
            # Insert into the collection
            with collection.insert() as collection_insert:
                collection_insert( Text( ... ).tag_layer('words') )
                collection_insert( Text( ... ).tag_layer('words') )
                ...
        
        Parameters:
        
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
        assert collection_table is structure_table, (collection_table, structure_table)
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
            fragment_table=fragment_table_identifier(self.storage, self.name, fragment_name))

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
               itersize: int= 10):
        """

        :param query:
        :param layers:
        :param collection_meta:
        :param progressbar:
        :param return_index:
        :return: PgSubCollection

        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))

        return pg.PgSubCollection(collection=self,
                                  selection_criterion=pg.WhereClause(collection=self, query=query),
                                  selected_layers=layers,
                                  meta_attributes=collection_meta,
                                  progressbar=progressbar,
                                  return_index=return_index,
                                  itersize=itersize
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
            required_layer_tables = [pg.layer_table_identifier(self.storage, self.name, layer)
                                     for layer in sorted(set(selected_detached_layers)) ]
            join_condition = SQL(" AND ").join(SQL('{}."id" = {}."text_id"').format(collection_identifier,
                                                                                    layer_table_identifier)
                                               for layer_table_identifier in required_layer_tables)
            required_tables = SQL(', ').join((collection_identifier, *required_layer_tables))
            query = SQL("SELECT {} FROM {} WHERE {} AND {}").format(SQL(', ').join(selected_columns),
                                                                    required_tables,
                                                                    join_condition,
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

        if isinstance(item, slice):  # TODO
            
            if item.step is not None:
                raise KeyError("Invalid index slice {!r}".format(item))

            return self.select(
                query=SliceQuery(item.start, item.stop), layers=self.selected_layers,
                collection_meta=None, return_index=False)

        raise KeyError(item)

    def __iter__(self):
        yield from self.select(layers=self.selected_layers, return_index=False)

    def count_values(self, layer, attr, **kwargs):
        """Count attribute values in the collection."""
        counter = collections.Counter()
        for i, t in self.select(layers=[layer], **kwargs):
            counter.update(t[layer].count_values(attr))
        return counter

    def create_fragment(self, fragment_name, data_iterator, row_mapper,
                        create_index=False, ngram_index=None):
        """Creates and fills a fragment table.

        Args:
            fragment_name: str
            data_iterator: iterator
                Produces tuples (text_id, text, parent_layer_id, *payload),
                where *payload is a variable number of values to be passed to the `row_mapper`
                See method `PgCollection.select_raw`
            row_mapper: callable
                It takes as input a full row produced by `data_iterator`
                and returns a list of Layer objects.
            create_index:
            ngram_index:

        """
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format(self.name))
        
        conn = self.storage.conn
        with conn.cursor() as c:
            try:
                conn.autocommit = False
                fragment_table = fragment_table_name(self.name, fragment_name)
                self._create_layer_table(cursor=c,
                                         layer_name=fragment_name,
                                         is_fragment=True,
                                         create_index=create_index,
                                         ngram_index=ngram_index)
                # insert data
                id_ = 0
                for row in data_iterator:
                    text_id, text = row[0], row[1]
                    for record in row_mapper(row):
                        fragment_dict = layer_to_dict(record['fragment'])
                        parent_layer_id = record['parent_id']
                        if ngram_index is not None:
                            ngram_values = [create_ngram_fingerprint_index(record.layer, attr, n)
                                            for attr, n in ngram_index.items()]
                        else:
                            ngram_values = None
                        layer_json = json.dumps(fragment_dict, ensure_ascii=False)
                        ngram_values = ngram_values or []
                        q = "INSERT INTO {}.{} VALUES (%s);" % ", ".join(['%s'] * (4 + len(ngram_values)))
                        q = SQL(q).format(Identifier(self.storage.schema), Identifier(fragment_table))
                        c.execute(q, (id_, parent_layer_id, text_id, layer_json, *ngram_values))
                        id_ += 1
            except:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()

    def continue_creating_layer(self, tagger, progressbar=None, query_length_limit=5000000):
        self.create_layer(tagger=tagger, progressbar=progressbar, query_length_limit=query_length_limit,
                          mode='append')

    def create_fragmented_layer(self, tagger, fragmenter: callable, meta: Sequence = None, progressbar: str = None,
                                      query_length_limit: int = 5000000):
        """
        Creates fragmented layer

        Args:
            tagger: Tagger
                tagger.make_layer method is called to create new layer
            fragmenter: callable
                fragmenter is called to brake layer into list of (sub)layers
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
                soft approximate query length limit in unicode characters, can be exceeded by the length of last buffer
                insert
        """

        layer_name = tagger.output_layer

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

        meta_columns = ()
        if meta is not None:
            meta_columns = tuple(meta)

        conn = self.storage.conn
        with conn.cursor() as c:
            try:
                conn.commit()
                conn.autocommit = True
                # create table and indices
                self._create_layer_table(cursor=c,
                                         layer_name=layer_name,
                                         meta=meta)

                structure_written = False
                with CollectionDetachedLayerInserter( self, layer_name, extra_columns=meta_columns, 
                                                      query_length_limit=query_length_limit ) as buffered_inserter:

                    for row in self.select(layers=tagger.input_layers, progressbar=progressbar):
                        text_id, text = row[0], row[1]

                        for fragment in fragmenter(tagger.make_layer(text, status={})):
                            layer = fragment.layer
                            extra_data = []
                            if meta_columns:
                                extra_data.extend( fragment.meta[k] for k in meta_columns )
                            buffered_inserter.insert(layer, text_id, key=DEFAULT, extra_data=extra_data)
                            
                            if not structure_written:
                                self._structure.insert(layer=layer, layer_type='fragmented', meta=meta)
                                structure_written = True
            except Exception:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()

        logger.info('fragmented layer created: {!r}'.format(layer_name))

    def create_layer(self, layer_name=None, data_iterator=None, row_mapper=None, tagger=None,
                     create_index=False, ngram_index=None, overwrite=False, meta=None, progressbar=None,
                     query_length_limit=5000000, mode=None):
        """
        Creates layer

        Args:
            layer_name:
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
        """
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer".format(
                self.name))

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
        data_iterator = data_iterator or self.select(layers=tagger.input_layers, progressbar=progressbar,
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
                                                      query_length_limit=query_length_limit ) as buffered_inserter:

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
                            self._structure.insert(layer=layer, layer_type='detached', meta=meta)
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
                        fragmented_layer: bool = False,
                        meta: Dict[str, str] = None,
                        create_index: bool = False,
                        ngram_index=None) -> None:
        """
        Adds detached or fragmented layer to the collection. You can use this 
        method to add an empty layer to the collection that will be filled with
        data later. Note, however, that the collection must already contain some
        documents before the layer can be added, and after adding the layer, 
        new documents can no longer be inserted.

        Layer must be specified by a template layer. The function fails only if 
        the layer is already present or the database schema is in an inconsistent 
        state. 
        One should set create_index only if one plans to search specific elements 
        from the layer. The ngram index speeds up search of element combinations. 
        This is useful when one uses phase grammars.
        
        Args:
            layer_template: Layer
                A template which is used as a basis on creating the new layer
            fragmented_layer: bool
                Whether a fragmented layer will be created (default: False)
            meta: dict of str -> str
                Specifies table column names and data types to create for storing additional
                meta information. E.g. meta={"sum": "int", "average": "float"}.
                See `pytype2dbtype` in `pg_operations` for supported types.
            create_index: bool
                Whether to create an index on json column (default: False)
            ngram_index: list
                A list of attributes for which to create an ngram index (default: None)
        """
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't add layer".format(self.name))

        if not isinstance( layer_template, Layer ):
            raise TypeError('(!) layer_template must be an instance of Layer')

        if self.layers is not None and layer_template.name in self.layers:
            raise PgCollectionException("The {!r} layer already exists.".format(layer_template.name))

        if self._is_empty:
            raise PgCollectionException("can't add layer {!r}, the collection is empty".format(layer_template.name))

        layer_table = layer_table_name(self.name, layer_template.name)
        if table_exists(self.storage, layer_table):
            raise PgCollectionException(
                "The table {!r} for the layer {!r} already exists.".format(layer_table, layer_template.name))

        layer_type = 'detached' if not fragmented_layer else 'fragmented'
        conn = self.storage.conn
        with conn.cursor() as cur:
            try:
                self._create_layer_table(
                    cursor=cur,
                    layer_name=layer_template.name,
                    is_fragment=fragmented_layer,
                    create_index=create_index,
                    ngram_index=ngram_index,
                    overwrite=False,
                    meta=meta)

                self._structure.insert(layer=layer_template, layer_type=layer_type, meta=meta)

            except Exception:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()

        logger.info('{} layer {!r} created from template'.format(layer_type, layer_template.name))

    def create_layer_block(self, tagger, block, meta=None, query_length_limit=5000000, mode=None):
        """Creates a layer block.
        
        Note: before the layer block can be created, the layer table must already exist.
        You can use the method add_layer() to create an empty layer (table).

        :param tagger: Tagger
            tagger to be applied on collection's texts
        :param block: Tuple[int, int]
            pair of integers `(module, remainder)`. Only texts with `id % module = remainder` are tagged.
        :param meta: dict of str -> str
            Specifies table column names and data types to create for storing additional
            meta information. E.g. meta={"sum": "int", "average": "float"}.
            See `pytype2dbtype` in `pg_operations` for supported types.
        :param query_length_limit: int
            soft approximate query length limit in unicode characters, can be exceeded by the length of last buffer
            insert
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

        with CollectionDetachedLayerInserter( self, layer_name, extra_columns=meta_columns, 
                                              query_length_limit=query_length_limit ) as buffered_inserter:

            layer_structure = None
            block_query = pg.BlockQuery(*block)
            if mode.lower() == 'append':
                block_query &= MissingLayerQuery( missing_layer = tagger.output_layer )
            for collection_text_id, text in self.select(query=block_query, layers=tagger.input_layers):
                layer = tagger.make_layer(text=text, status=None)

                if layer_structure is None:
                    if layer_name not in self._structure:
                        self._structure.load()
                    if layer_name not in self._structure:
                        try:
                            self._structure.insert(layer, layer_type='detached', meta=meta)
                        except psycopg2.IntegrityError:
                            pass
                        self._structure.load()
                    struct = self._structure[layer_name]
                    layer_structure = (layer_name, struct['attributes'], struct['ambiguous'], struct['parent'],
                                       struct['enveloping'])

                assert layer_structure == (layer.name, layer.attributes, layer.ambiguous, layer.parent, layer.enveloping)

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

    def delete_layer_fragment(self, layer_fragment_name):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format(self.name))
        lf_table = self.layer_fragment_name_to_table_name(layer_fragment_name)
        if layer_fragment_name not in self.get_layer_fragment_names():
            raise PgCollectionException("Collection does not have a layer fragment '%s'." % layer_fragment_name)
        if not self.storage.table_exists(lf_table):
            raise PgCollectionException("Layer fragment table '%s' does not exist." % lf_table)
        self.storage.drop_table(lf_table)

    def delete(self):
        """Removes collection and all related layers."""
        if not self.exists():
            return
        del self.storage[self.name]
        self._is_empty = True

    def has_layer(self, layer_name):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        return layer_name in self._structure

    def has_fragment(self, fragment_name):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        return fragment_name in self.get_fragment_names()

    def get_fragment_names(self):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        
        lf_names = []
        for tbl in self.get_fragment_tables():
            layer = re.sub("^%s__" % self.name, "", tbl)
            layer = re.sub("__fragment$", "", layer)
            lf_names.append(layer)
        return lf_names

    def get_fragment_tables(self):
        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist".format( self.name ))
        
        fragment_tables = []
        for tbl in pg.get_all_table_names(self.storage):
            if tbl.startswith("%s__" % self.name) and tbl.endswith("__fragment"):
                fragment_tables.append(tbl)
        return fragment_tables

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

        texts = self.select(layers=[layer], progressbar=progressbar, collection_meta=collection_meta)
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
                    'Use <b>create()</b> method to create a new collection with this name, or '+\
                    'check if the collection name is correct.'
                   ).format(self=self)
        
        if self._is_empty:
            structure_html = '<br/>unknown'
        else:
            structure_html = pandas.DataFrame.from_dict(self._structure.structure,
                                                        orient='index',
                                                        columns=['layer_type', 'attributes', 'ambiguous', 'parent',
                                                                 'enveloping', 'meta']
                                                        ).to_html()
        column_meta = self._collection_table_meta()
        meta_html = ''
        if column_meta is not None:
            column_meta.pop('id')
            column_meta.pop('data')
            if column_meta:
                meta_html = pandas.DataFrame.from_dict(column_meta,
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
