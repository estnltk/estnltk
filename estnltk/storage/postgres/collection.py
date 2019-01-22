import re
import json
import pandas
from contextlib import contextmanager
import collections

from tqdm import tqdm, tqdm_notebook

from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier, Literal, DEFAULT, Composed

from estnltk import logger
from estnltk.converters.dict_exporter import layer_to_dict
from estnltk.converters import text_to_json
from estnltk.layer_operations import create_ngram_fingerprint_index

from estnltk.storage.postgres import table_identifier
from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import create_collection_table
from estnltk.storage.postgres import drop_collection_table
from estnltk.storage.postgres import drop_structure_table
from estnltk.storage.postgres import drop_layer_table
from estnltk.storage.postgres import drop_fragment_table
from estnltk.storage.postgres import count_rows
from estnltk.storage.postgres import fragment_table_name
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import select_raw


class PgCollectionException(Exception):
    pass


RowMapperRecord = collections.namedtuple("RowMapperRecord", ["layer", "meta"])

pytype2dbtype = {
    "int": "integer",
    "bigint": "bigint",
    "float": "double precision",
    "str": "text"
}


def get_query_length(q):
    """:returns
    approximate number of characters in the psycopg2 SQL query
    """
    result = 0
    if isinstance(q, Composed):
        for r in q:
            result += get_query_length(r)
    elif isinstance(q, (SQL, Identifier)):
        result += len(q.string)
    else:
        result += len(str(q.wrapped))
    return result


class PgCollection:
    """Convenience wrapper over PostgresStorage"""

    def __init__(self, name, storage, meta=None, temporary=False):
        if '__' in name:
            raise PgCollectionException('collection name must not contain double underscore: {!r}'.format(name))
        self.name = name
        self.storage = storage
        # TODO: read meta columns from collection table if exists, move this parameter to self.create
        self.meta = meta or {}
        self._temporary = temporary
        self._structure = self._get_structure()
        self.column_names = ['id', 'data'] + list(self.meta)

        self._buffered_insert_query_length = 0

    def create(self, description=None, meta=None):
        """Creates the database tables for the collection"""
        temporary = SQL('TEMPORARY') if self._temporary else SQL('')
        with self.storage.conn.cursor() as c:
            c.execute(SQL('CREATE {temporary} TABLE {structure} ('
                          'layer_name text primary key, '
                          'detached bool not null, '
                          'attributes text[] not null, '
                          'ambiguous bool not null, '
                          'parent text, '
                          'enveloping text, '
                          '_base text, '
                          'meta text[]);').format(temporary=temporary,
                                                  structure=self._structure_identifier()))
            logger.info('new empty collection {!r} created'.format(self.name))
            logger.debug(c.query.decode())

        meta = meta or self.meta or {}

        return create_collection_table(self.storage,
                                       collection_name=self.name,
                                       meta_columns=meta,
                                       description=description)

    def create_index(self):
        """create index for the collection table"""
        with self.storage.conn.cursor() as c:
            c.execute(
                SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops)").format(
                    index=Identifier('idx_%s_data' % self.name),
                    table=collection_table_identifier(self.storage, self.name)))

    def drop_index(self):
        """drop index of the collection table"""
        with self.storage.conn.cursor() as c:
            c.execute(
                SQL("DROP INDEX {schema}.{index}").format(
                    schema=Identifier(self.storage.schema),
                    index=Identifier('idx_%s_data' % self.name)))

    # TODO: make it work
    def extend(self, other: 'PgCollection'):
        if self.column_names != other.column_names:
            raise PgCollectionException("can't extend: different collection meta")
        if self._structure != other._structure:
            raise PgCollectionException("can't extend: structures are different")
        with self.storage.conn.cursor() as cursor:
            cursor.execute(SQL('INSERT INTO {} SELECT * FROM {}'
                               ).format(collection_table_identifier(self.storage, self.name),
                                        collection_table_identifier(other.storage, other.name)))
            for layer_name, struct in self._structure.items():
                if struct['detached']:
                    cursor.execute(SQL('INSERT INTO {} SELECT * FROM {}').format(
                            layer_table_identifier(self.storage, self.name, layer_name),
                            layer_table_identifier(self.storage, other.name, layer_name)))

    def _get_structure(self):
        if not self.exists():
            return None
        structure = {}
        with self.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, detached, attributes, ambiguous, parent, enveloping, _base, meta "
                          "FROM {};").format(self._structure_identifier()))

            for row in c.fetchall():
                structure[row[0]] = {'detached': row[1],
                                     'attributes': tuple(row[2]),
                                     'ambiguous': row[3],
                                     'parent': row[4],
                                     'enveloping': row[5],
                                     '_base': row[6],
                                     'meta': row[7]}
        return structure

    def _collection_table_meta(self):
        if not self.exists():
            return None
        with self.storage.conn.cursor() as c:
            c.execute(SQL('SELECT column_name, data_type from information_schema.columns '
                          'WHERE table_schema={} and table_name={} '
                          'ORDER BY ordinal_position'
                          ).format(Literal(self.storage.schema), Literal(self.name)))
            return collections.OrderedDict(c.fetchall())

    def _insert_into_structure(self, layer, detached: bool, meta: dict=None):
        meta = list(meta or [])
        with self.storage.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {} (layer_name, detached, attributes, ambiguous, parent, enveloping, _base, meta) "
                          "VALUES ({}, {}, {}, {}, {}, {}, {}, {});").format(
                self._structure_identifier(),
                Literal(layer.name),
                Literal(detached),
                Literal(list(layer.attributes)),
                Literal(layer.ambiguous),
                Literal(layer.parent),
                Literal(layer.enveloping),
                Literal(layer._base),
                Literal(meta)
            )
            )
        self._structure = self._get_structure()

    def _delete_from_structure(self, layer_name):
        with self.storage.conn.cursor() as c:
            c.execute(SQL("DELETE FROM {} WHERE layer_name={};").format(
                self._structure_identifier(),
                Literal(layer_name)
            )
            )
            logger.debug(c.query.decode())
        self._structure = self._get_structure()

    def old_slow_insert(self, text, key=None, meta_data=None):
        with self.insert() as collection_insert:
            collection_insert(text=text, key=key, meta_data=meta_data)

    # TODO: merge this with buffered_layer_insert
    @contextmanager
    def insert(self, buffer_size=10000, query_length_limit=5000000):
        buffer = []
        self._buffered_insert_query_length = 0
        column_identifiers = SQL(', ').join(map(Identifier, self.column_names))
        table_identifier = collection_table_identifier(self.storage, self.name)

        with self.storage.conn.cursor() as cursor:

            def wrap_buffered_insert(text, key=None, meta_data=None):
                if self._structure is None:
                    for layer in text.layers:
                        self._insert_into_structure(text[layer], detached=False)
                elif any(struct['detached'] for struct in self._structure.values()):
                    # TODO: solve this case in a better way
                    raise PgCollectionException("this collection has detached layers, can't add new text objects")
                else:
                    assert set(text.layers) == set(self._structure), '{} != {}'.format(set(text.layers),
                                                                                       set(self._structure))
                    for layer_name, layer in text.layers.items():
                        layer_struct = self._structure[layer_name]
                        assert layer_struct['detached'] is False
                        assert layer_struct['attributes'] == layer.attributes, '{} != {}'.format(
                                layer_struct['attributes'],
                                layer.attributes)
                        assert layer_struct['ambiguous'] == layer.ambiguous
                        assert layer_struct['parent'] == layer.parent
                        assert layer_struct['enveloping'] == layer.enveloping
                        assert layer_struct['_base'] == layer._base
                text = text_to_json(text)
                if key is None:
                    key = DEFAULT
                else:
                    key = Literal(key)

                row = [key, Literal(text)]
                for k in self.column_names[2:]:
                    if k in meta_data:
                        m = Literal(meta_data[k])
                    else:
                        m = DEFAULT
                    row.append(m)

                q = SQL('({})').format(SQL(', ').join(row))
                self._buffered_insert_query_length += get_query_length(q)
                buffer.append(q)

                if len(buffer) >= buffer_size or self._buffered_insert_query_length >= query_length_limit:
                    self._flush_insert_buffer(cursor=cursor, table_identifier=table_identifier,
                                              column_identifiers=column_identifiers,
                                              buffer=buffer)
                    self._buffered_insert_query_length = 0

            try:
                yield wrap_buffered_insert
            finally:
                self._flush_insert_buffer(cursor=cursor,
                                          table_identifier=table_identifier,
                                          column_identifiers=column_identifiers,
                                          buffer=buffer)

    @contextmanager
    def buffered_layer_insert(self, table_identifier, columns, buffer_size=10000, query_length_limit=5000000):
        """General context manager for buffered insert"""
        buffer = []
        column_identifiers = SQL(', ').join(map(Identifier, columns))

        self._buffered_insert_query_length = get_query_length(column_identifiers)

        with self.storage.conn.cursor() as cursor:
            def buffered_insert(values):
                q = SQL('({})').format(SQL(', ').join(values))
                buffer.append(q)
                self._buffered_insert_query_length += get_query_length(q)

                if len(buffer) >= buffer_size or self._buffered_insert_query_length >= query_length_limit:
                    return self._flush_insert_buffer(cursor=cursor,
                                                           table_identifier=table_identifier,
                                                           column_identifiers=column_identifiers,
                                                           buffer=buffer)
            try:
                yield buffered_insert
            finally:
                self._flush_insert_buffer(cursor=cursor,
                                                table_identifier=table_identifier,
                                                column_identifiers=column_identifiers,
                                                buffer=buffer)
                self.storage.conn.autocommit = False

    def _flush_insert_buffer(self, cursor, table_identifier, column_identifiers, buffer):
        if len(buffer) == 0:
            return []

        cursor.execute(SQL('INSERT INTO {} ({}) VALUES {} RETURNING id;').format(
                       table_identifier,
                       column_identifiers,
                       SQL(', ').join(buffer)))
        row_key = cursor.fetchone()
        logger.debug('flush buffer: {} rows, {} bytes, {} estimated characters'.format(
                len(buffer), len(cursor.query), self._buffered_insert_query_length))
        buffer.clear()
        self._buffered_insert_query_length = get_query_length(column_identifiers)
        return row_key

    def exists(self):
        """Returns true if collection tables exists"""
        collection_table_exists = table_exists(self.storage, self.name)
        structure_table_exists = table_exists(self.storage, self._structure_table_name())
        assert collection_table_exists is structure_table_exists, (collection_table_exists, structure_table_exists)
        return collection_table_exists

    def select_fragment_raw(self, fragment_name, parent_layer_name, query=None, ngram_query=None):
        return self.storage.select_fragment_raw(
            fragment_name=fragment_name,
            collection_name=self.name,
            parent_layer_name=parent_layer_name,
            query=query,
            ngram_query=ngram_query)

    def select(self, query=None, layer_query=None, layer_ngram_query=None, layers=None, keys=None, order_by_key=False,
               collection_meta=None, progressbar=None, missing_layer: str = None):
        """See select_raw()"""
        if not self.exists():
            return
        layers_extended = []

        def include_dep(layer):
            if layer is None or not self._structure[layer]['detached']:
                return
            for dep in (self._structure[layer]['parent'], self._structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in layers or []:
            if layer not in self._structure:
                raise PgCollectionException('there is no {!r} layer in the collection {!r}'.format(
                        layer, self.name))
            include_dep(layer)

        def data_iterator():
            for row in select_raw(storage=self.storage,
                                  collection_name=self.name,
                                  query=query,
                                  layer_query=layer_query,
                                  layer_ngram_query=layer_ngram_query,
                                  layers=layers_extended,
                                  keys=keys,
                                  order_by_key=order_by_key,
                                  collection_meta=collection_meta,
                                  missing_layer=missing_layer):
                text_id, text, meta_list, detached_layers = row
                for layer_name in layers_extended:
                    text[layer_name] = detached_layers[layer_name]['layer']
                if collection_meta:
                    meta = {}
                    for meta_name, meta_value in zip(collection_meta, meta_list):
                        meta[meta_name] = meta_value
                    yield text_id, text, meta
                else:
                    yield text_id, text

        if progressbar not in {'ascii', 'unicode', 'notebook'}:
            yield from data_iterator()
            return

        total = count_rows(self.storage, self.name)
        initial = 0
        if missing_layer is not None:
            initial = self.storage.count_rows(
                    table_identifier=layer_table_identifier(self.storage, self.name, missing_layer))
        if progressbar == 'notebook':
            iter_data = tqdm_notebook(data_iterator(),
                                      total=total,
                                      initial=initial,
                                      unit='doc',
                                      smoothing=0)
        else:
            iter_data = tqdm(data_iterator(),
                             total=total,
                             initial=initial,
                             unit='doc',
                             ascii=(progressbar == 'ascii'),
                             smoothing=0)
        for data in iter_data:
            iter_data.set_description('collection_id: {}'.format(data[0]), refresh=False)
            yield data

    def select_by_key(self, key, return_as_dict=False):
        """See PostgresStorage.select_by_key()"""
        return self.storage.select_by_key(self.name, key, return_as_dict)

    def count_values(self, layer, attr, **kwargs):
        """Count attribute values in the collection."""
        counter = collections.Counter()
        for i, t in self.select(layers=[layer], **kwargs):
            counter.update(t[layer].count_values(attr))
        return counter

    def find_fingerprint(self, query=None, layer_query=None, layer_ngram_query=None, layers=None, order_by_key=False):
        """See PostgresStorage.find_fingerprint()"""
        return self.storage.find_fingerprint(self.name, query, layer_query, layer_ngram_query, layers,
                                             order_by_key)

    def _structure_table_name(self):
        return self.name + '__structure'

    def _structure_identifier(self):
        if self._temporary:
            return Identifier(self._structure_table_name())
        return SQL('{}.{}').format(Identifier(self.storage.schema), Identifier(self._structure_table_name()))

    def _fragment_identifier(self, fragment_name):
        if self._temporary:
            return Identifier('{}__{}__fragment'.format(self.name, fragment_name))
        return SQL('{}.{}').format(Identifier(self.storage.schema),
                                   Identifier('{}__{}__fragment'.format(self.name, fragment_name)))

    def create_fragment(self, fragment_name, data_iterator, row_mapper,
                        create_index=False, ngram_index=None):
        """
        Creates and fills a fragment table.

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
                        fragment_dict = layer_to_dict(record['fragment'], text)
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
                conn.autocommit = True

    def old_slow_create_layer(self, layer_name=None, data_iterator=None, row_mapper=None, tagger=None,
                              create_index=False, ngram_index=None, overwrite=False, meta=None, progressbar=None):
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
                If True and layer table exists, table is overwritten.
                If False and layer table exists, error is raised.
            meta: dict of str -> str
                Specifies table column names and data types to create for storing additional
                meta information. E.g. meta={"sum": "int", "average": "float"}.
                See `pytype2dbtype` for supported types.
            progressbar: str
                if 'notebook', display progressbar as a jupyter notebook widget
                if 'unicode', use unicode (smooth blocks) to fill the progressbar
                if 'ascii', use ASCII characters (1-9 #) to fill the progressbar
                else disable progressbar (default)
        """
        assert (layer_name is None and data_iterator is None and row_mapper is None) is not (tagger is None),\
               'either tagger must be None or layer_name, data_iterator and row_mapper must be None'

        def default_row_mapper(row):
            text_id, text = row[0], row[1]
            layer = tagger.make_layer(text=text)
            return [RowMapperRecord(layer=layer, meta=None)]

        layer_name = layer_name or tagger.output_layer
        row_mapper = row_mapper or default_row_mapper
        data_iterator = data_iterator or self.select(layers=tagger.input_layers, progressbar=progressbar)

        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer {!r}".format(
                self.name, layer_name))
        logger.info('collection: {!r}'.format(self.name))
        if self._structure is None:
            raise PgCollectionException("can't add detached layer {!r}, the collection is empty".format(layer_name))
        if self.has_layer(layer_name):
            if overwrite:
                logger.info("overwriting output layer: {!r}".format(layer_name))
                self.delete_layer(layer_name=layer_name, cascade=True)
            else:
                exception = PgCollectionException("can't create layer {!r}, layer already exists".format(layer_name))
                logger.error(exception)
                raise exception
        logger.info('preparing to create a new layer: {!r}'.format(layer_name))
        conn = self.storage.conn
        with conn.cursor() as c:
            try:
                conn.autocommit = False
                # create table and indices
                self._create_layer_table(cursor=c,
                                         layer_name=layer_name,
                                         is_fragment=False,
                                         create_index=create_index,
                                         ngram_index=ngram_index,
                                         overwrite=overwrite,
                                         meta=meta)

                # insert data
                id_ = 0

                meta_columns = ()
                if meta is not None:
                    meta_columns = tuple(meta)

                for row in data_iterator:
                    collection_id, text = row[0], row[1]
                    for record in row_mapper(row):
                        layer = record.layer
                        layer_dict = layer_to_dict(layer, text)
                        layer_json = json.dumps(layer_dict, ensure_ascii=False)

                        columns = ["id", "text_id", "data"]
                        values = [id_, collection_id, layer_json]

                        if meta_columns:
                            columns.extend(meta_columns)
                            values.extend(record.meta[k] for k in meta_columns)

                        if ngram_index is not None:
                            ngram_index_keys = tuple(ngram_index.keys())
                            columns.extend(ngram_index_keys)
                            values.extend(create_ngram_fingerprint_index(layer=layer,
                                                                         attribute=attr,
                                                                         n=ngram_index[attr])
                                          for attr in ngram_index_keys)

                        columns = SQL(', ').join(map(Identifier, columns))
                        q = SQL('INSERT INTO {} ({}) VALUES ({});'
                                ).format(layer_table_identifier(self.storage, self.name, layer_name),
                                         columns,
                                         SQL(', ').join(map(Literal, values)))
                        c.execute(q)
                        logger.debug('insert into layer {!r}, query size: {} bytes'.format(layer_name, len(c.query)))

                        id_ += 1
                self._insert_into_structure(layer, detached=True, meta=meta)
            except:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()
                conn.autocommit = True

        logger.info('layer created: {!r}'.format(layer_name))

    def continue_creating_layer(self, tagger, progressbar=None, query_length_limit=5000000):
        self.create_layer(tagger=tagger, progressbar=progressbar, query_length_limit=query_length_limit,
                          mode='append')

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
                See `pytype2dbtype` for supported types.
            progressbar: str
                if 'notebook', display progressbar as a jupyter notebook widget
                if 'unicode', use unicode (smooth blocks) to fill the progressbar
                if 'ascii', use ASCII characters (1-9 #) to fill the progressbar
                else disable progressbar (default)
            query_length_limit: int
                soft approximate query length limit in unicode characters, can be exceeded by the length of last buffer
                insert
        """
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
            return [RowMapperRecord(layer=layer, meta=status)]

        layer_name = layer_name or tagger.output_layer
        row_mapper = row_mapper or default_row_mapper

        missing_layer = layer_name if mode == 'append' else None
        data_iterator = data_iterator or self.select(layers=tagger.input_layers, progressbar=progressbar,
                                                     missing_layer=missing_layer)

        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer {!r}".format(
                self.name, layer_name))
        logger.info('collection: {!r}'.format(self.name))
        if self._structure is None:
            raise PgCollectionException("can't add detached layer {!r}, the collection is empty".format(layer_name))
        if self.has_layer(layer_name):
            if mode == 'overwrite':
                logger.info("overwriting output layer: {!r}".format(layer_name))
                self.delete_layer(layer_name=layer_name, cascade=True)
            elif mode == 'append':
                logger.info("appending existing layer: {!r}".format(layer_name))
            else:
                exception = PgCollectionException("can't create layer {!r}, layer already exists".format(layer_name))
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

        conn = self.storage.conn

        meta_columns = ()
        if meta is not None:
            meta_columns = tuple(meta)

        columns = ["id", "text_id", "data"]
        if meta_columns:
            columns.extend(meta_columns)

        if ngram_index is not None:
            ngram_index_keys = tuple(ngram_index.keys())
            columns.extend(ngram_index_keys)

        with conn.cursor() as c:
            try:
                conn.autocommit = True
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
                with self.buffered_layer_insert(table_identifier=layer_table_identifier(self.storage, self.name, layer_name),
                                                columns=columns,
                                                query_length_limit=query_length_limit) as buffered_insert:
                    for row in data_iterator:
                        collection_id, text = row[0], row[1]
                        for record in row_mapper(row):
                            layer = record.layer
                            layer_dict = layer_to_dict(layer, text)
                            layer_json = json.dumps(layer_dict, ensure_ascii=False)

                            values = [None, collection_id, layer_json]

                            if meta_columns:
                                values.extend(record.meta[k] for k in meta_columns)

                            if ngram_index is not None:
                                values.extend(create_ngram_fingerprint_index(layer=layer,
                                                                             attribute=attr,
                                                                             n=ngram_index[attr])
                                              for attr in ngram_index_keys)
                            values = list(map(Literal, values))
                            values[0] = DEFAULT
                            buffered_insert(values=values)
                            if not structure_written:
                                self._insert_into_structure(layer, detached=True, meta=meta)
                                structure_written = True
            except Exception:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()
                conn.autocommit = True

        logger.info('layer created: {!r}'.format(layer_name))

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
                #self.storage.drop_table_if_exists(layer_table)
        elif table_exists(self.storage, layer_table):
            raise PgCollectionException("Table {!r} for layer {!r} already exists.".format(layer_table, layer_name))

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
            types = [pytype2dbtype[py_type] for py_type in meta.values()]
            meta_cols = ", %s" % ",".join(["%s %s" % (c, d) for c, d in zip(cols, types)])
        else:
            meta_cols = ""

        q %= {"parent_col": parent_col, "ngram_cols": ngram_cols, "meta_cols": meta_cols}
        if is_fragment:
            layer_identifier = table_identifier(self.storage, fragment_table_name(self.name, layer_name))
        else:
            layer_identifier = table_identifier(self.storage, layer_table_name(self.name, layer_name))
        q = SQL(q).format(temporary=temporary, layer_identifier=layer_identifier)
        cursor.execute(q)
        logger.debug(cursor.query.decode())

        q = SQL("COMMENT ON TABLE {} IS {};").format(
            layer_identifier,
            Literal("%s %s layer" % (self.name, layer_name)))
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
        if layer_name not in self._structure:
            raise PgCollectionException("collection does not have a layer {!}".format(layer_name))
        if not self._structure[layer_name]['detached']:
            raise PgCollectionException("can't delete attached layer {!}".format(layer_name))

        for ln, struct in self._structure.items():
            if ln == layer_name:
                continue
            if layer_name == struct['enveloping'] or layer_name == struct['parent'] or layer_name == struct['_base']:
                if cascade:
                    self.delete_layer(ln, cascade=True)
                else:
                    raise PgCollectionException("can't delete layer {!r}; "
                                                "there is a dependant layer {!r}".format(layer_name, ln))
        drop_layer_table(self.storage, self.name, layer_name)
        self._delete_from_structure(layer_name)
        logger.info('layer deleted: {!r}'.format(layer_name))

    def delete_fragment(self, fragment_name):
        if fragment_name not in self.get_fragment_names():
            raise PgCollectionException("Collection does not have a layer fragment '%s'." % fragment_name)
        drop_fragment_table(self.storage, self.name, fragment_name)

    def delete_layer_fragment(self, layer_fragment_name):
        lf_table = self.layer_fragment_name_to_table_name(layer_fragment_name)
        if layer_fragment_name not in self.get_layer_fragment_names():
            raise PgCollectionException("Collection does not have a layer fragment '%s'." % layer_fragment_name)
        if not self.storage.table_exists(lf_table):
            raise PgCollectionException("Layer fragment table '%s' does not exist." % lf_table)
        self.storage.drop_table(lf_table)

    def delete(self):
        """Removes collection and all related layers."""
        conn = self.storage.conn
        conn.autocommit = False
        try:
            if self._structure is not None:
                for layer_name, struct in self._structure.items():
                    if struct['detached']:
                        drop_layer_table(self.storage, self.name, layer_name)
            drop_structure_table(self.storage, self.name)
            drop_collection_table(self.storage, self.name)
        except Exception:
            conn.rollback()
            raise
        finally:
            if conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                conn.commit()
            conn.autocommit = True
            logger.info('collection {!r} deleted'.format(self.name))

    def has_layer(self, layer_name):
        return layer_name in self._structure

    def has_fragment(self, fragment_name):
        return fragment_name in self.get_fragment_names()

    def get_fragment_names(self):
        lf_names = []
        for tbl in self.get_fragment_tables():
            layer = re.sub("^%s__" % self.name, "", tbl)
            layer = re.sub("__fragment$", "", layer)
            lf_names.append(layer)
        return lf_names

    def get_layer_names(self):
        if self._structure is None:
            return []
        return list(self._structure)

    def get_fragment_tables(self):
        fragment_tables = []
        for tbl in self.storage.get_all_table_names():
            if tbl.startswith("%s__" % self.name) and tbl.endswith("__fragment"):
                fragment_tables.append(tbl)
        return fragment_tables

    def get_layer_meta(self, layer_name):
        if layer_name not in self.get_layer_names():
            raise PgCollectionException("Collection does not have the layer {!r}".format(layer_name))

        with self.storage.conn.cursor() as c:
            columns = ['id', 'text_id'] + self._structure[layer_name]['meta']

            c.execute(SQL('SELECT {} FROM {};').format(
                SQL(', ').join(map(Identifier, columns)),
                layer_table_identifier(self.storage, self.name, layer_name)))
            data = c.fetchall()
            return pandas.DataFrame(data=data, columns=columns)

    def export_layer(self, layer, attributes, progressbar=None):
        export_table = '{}__{}__export'.format(self.name, layer)
        texts = self.select(layers=[layer], progressbar=progressbar)
        logger.info('preparing to export layer {!r} with attributes {!r}'.format(layer, attributes))

        columns = [
            ('id', 'serial PRIMARY KEY'),
            ('text_id', 'int NOT NULL'),
            ('span_nr', 'int NOT NULL')]
        columns.extend((attr, 'text') for attr in attributes)

        columns_sql = SQL(",\n").join(SQL("{} {}").format(Identifier(n), SQL(t)) for n, t in columns)

        i = 0
        with self.storage.conn.cursor() as c:
            c.execute(SQL("DROP TABLE IF EXISTS {}.{};").format(Identifier(self.storage.schema),
                                                                Identifier(export_table)))
            logger.debug(c.query)
            c.execute(SQL("CREATE TABLE {}.{} ({});").format(Identifier(self.storage.schema),
                                                             Identifier(export_table),
                                                             columns_sql))
            logger.debug(c.query)

            for text_id, text in texts:
                for span_nr, span in enumerate(text[layer]):
                    for annotation in span:
                        i += 1
                        values = [i, text_id, span_nr]
                        values.extend(str(getattr(annotation, attr)) for attr in attributes)
                        c.execute(SQL("INSERT INTO {}.{} "
                                      "VALUES ({});").format(Identifier(self.storage.schema),
                                                             Identifier(export_table),
                                                             SQL(', ').join(map(Literal, values))
                                                             ))
        logger.info('{} annotations exported to "{}"."{}"'.format(i, self.storage.schema, export_table))

    def __len__(self):
        return count_rows(self.storage, self.name)

    def _repr_html_(self):
        if self._structure is None:
            structure_html = '<br/>unknown'
        else:
            structure_html = pandas.DataFrame.from_dict(self._structure,
                                                        orient='index',
                                                        columns=['detached', 'attributes', 'ambiguous', 'parent',
                                                                 'enveloping', '_base', 'meta']
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
