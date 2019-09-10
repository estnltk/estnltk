import collections
import json
import operator as op
import pandas
import re
from typing import Sequence
from functools import reduce
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier, Literal, DEFAULT, Composed
import time

from estnltk import logger
from estnltk.converters import layer_to_dict
from estnltk.converters import layer_to_json
from estnltk.converters import dict_to_text
from estnltk.converters import dict_to_layer
from estnltk.converters import text_to_json
from estnltk.layer_operations import create_ngram_fingerprint_index

from estnltk.storage.postgres import structure_table_identifier
from estnltk.storage.postgres import fragment_table_identifier
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import structure_table_exists
from estnltk.storage.postgres import drop_layer_table
from estnltk.storage.postgres import drop_fragment_table
from estnltk.storage.postgres import count_rows
from estnltk.storage.postgres import fragment_table_name
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import JsonbLayerQuery
from estnltk.storage.postgres import JsonbTextQuery
from estnltk.storage import postgres as pg


class PgCollectionException(Exception):
    pass


RowMapperRecord = collections.namedtuple("RowMapperRecord", ["layer", "meta"])


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

        self._buffered_insert_query_length = 0
        self._selected_layes = None
        self._is_empty = not self.exists() or len(self) == 0

    def create(self, description=None, meta: dict = None, temporary=None):
        """Creates the database tables for the collection

        """
        if description is None:
            description = 'created by {} on {}'.format(self.storage.user, time.asctime())

        self.structure.create_table()

        pg.create_collection_table(self.storage,
                                   collection_name=self.name,
                                   meta_columns=meta or self.meta or {},
                                   description=description)

        logger.info('new empty collection {!r} created'.format(self.name))
        return self

    @property
    def structure(self):
        return self._structure

    @property
    def layers(self):
        if self._is_empty:
            return
        return list(self._structure)

    @property
    def selected_layers(self):
        if self._selected_layes is None:
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
        with self.storage.conn.cursor() as c:
            c.execute(
                SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops)").format(
                    index=Identifier('idx_%s_data' % self.name),
                    table=pg.collection_table_identifier(self.storage, self.name)))

    def drop_index(self):
        """Drop index of the collection table.

        """
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

    def _delete_from_structure(self, layer_name):
        with self.storage.conn.cursor() as c:
            c.execute(SQL("DELETE FROM {} WHERE layer_name={};").format(
                structure_table_identifier(self.storage, self.name),
                Literal(layer_name)
            )
            )
            self.storage.conn.commit()
            logger.debug(c.query.decode())

    def _insert_first(self, text, key, meta_data, cursor, table_identifier, column_identifiers):
        if key is None:
            key = 0

        row = [Literal(key), Literal(text_to_json(text))]
        for k in self.column_names[2:]:
            if k in meta_data:
                m = Literal(meta_data[k])
            else:
                m = DEFAULT
            row.append(m)

        query = SQL('({})').format(SQL(', ').join(row))

        self._flush_insert_buffer(cursor=cursor, table_identifier=table_identifier,
                                  column_identifiers=column_identifiers, buffer=[query])

        assert not self._structure, self._structure.structure
        for layer in text.layers:
            # TODO: meta = ???
            self._structure.insert(layer=text[layer], layer_type='attached', meta={})

    # TODO: merge this with buffered_layer_insert
    @contextmanager
    def insert(self, buffer_size=10000, query_length_limit=5000000):
        buffer = []
        self._buffered_insert_query_length = 0
        self._insert_counter = 0
        column_identifiers = SQL(', ').join(map(Identifier, self.column_names))
        table_identifier = pg.collection_table_identifier(self.storage, self.name)

        self.storage.conn.commit()
        self.storage.conn.autocommit = False
        with self.storage.conn.cursor() as cursor:

            def wrap_buffered_insert(text, key=None, meta_data=None):
                if self._is_empty:
                    self._is_empty = False
                    cursor.execute(SQL('LOCK TABLE {}').format(table_identifier))
                    if len(self) == 0:
                        self._insert_first(text=text, key=key, meta_data=meta_data, cursor=cursor,
                                           table_identifier=table_identifier, column_identifiers=column_identifiers)
                        return
                    self.storage.conn.commit()
                    self._structure.load()

                if any(struct['layer_type'] == 'detached' for struct in self._structure.structure.values()):
                    # TODO: solve this case in a better way
                    raise PgCollectionException("this collection has detached layers, can't add new text objects")
                else:
                    assert set(text.layers) == set(self._structure), '{} != {}'.format(set(text.layers),
                                                                                       set(self._structure))
                    for layer_name, layer in text.layers.items():
                        layer_struct = self._structure[layer_name]
                        assert layer_struct['layer_type'] == 'attached'
                        assert layer_struct['attributes'] == layer.attributes, '{} != {}'.format(
                                layer_struct['attributes'], layer.attributes)
                        assert layer_struct['ambiguous'] == layer.ambiguous
                        assert layer_struct['parent'] == layer.parent
                        assert layer_struct['enveloping'] == layer.enveloping
                        assert layer_struct['serialisation_module'] == layer.dict_converter_module
                if key is None:
                    key = DEFAULT
                else:
                    key = Literal(key)

                row = [key, Literal(text_to_json(text))]
                for k in self.column_names[2:]:
                    if k in meta_data:
                        m = Literal(meta_data[k])
                    else:
                        m = DEFAULT
                    row.append(m)

                q = SQL('({})').format(SQL(', ').join(row))
                self._buffered_insert_query_length += get_query_length(q)
                self._insert_counter += 1
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
                logger.info('inserted {self._insert_counter} texts into the collection {self.name!r}'.format(self=self))

    @contextmanager
    def buffered_layer_insert(self, table_identifier, columns, buffer_size=10000, query_length_limit=5000000):
        """General context manager for buffered insert

        """
        buffer = []
        column_identifiers = SQL(', ').join(map(Identifier, columns))

        self._buffered_insert_query_length = get_query_length(column_identifiers)

        with self.storage.conn.cursor() as cursor:
            def buffered_insert(values):
                q = SQL('({})').format(SQL(', ').join(values))
                buffer.append(q)
                self._buffered_insert_query_length += get_query_length(q)

                if len(buffer) >= buffer_size or self._buffered_insert_query_length >= query_length_limit:
                    self._flush_insert_buffer(cursor=cursor,
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

    def _flush_insert_buffer(self, cursor, table_identifier, column_identifiers, buffer):
        if len(buffer) == 0:
            return []

        try:
            cursor.execute(SQL('INSERT INTO {} ({}) VALUES {};').format(
                           table_identifier,
                           column_identifiers,
                           SQL(', ').join(buffer)))
            cursor.connection.commit()
        except Exception:
            logger.error('flush insert buffer failed')
            logger.error('number of rows in the buffer: {}'.format(len(buffer)))
            logger.error('estimated insert query length: {}'.format(self._buffered_insert_query_length))
            raise
        logger.debug('flush buffer: {} rows, {} bytes, {} estimated characters'.format(
                     len(buffer), len(cursor.query), self._buffered_insert_query_length))
        buffer.clear()
        self._buffered_insert_query_length = get_query_length(column_identifiers)

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

    def select(self, query=None, layer_query=None, layer_ngram_query=None, layers: Sequence[str] = None,
               keys: Sequence[int] = None, collection_meta: Sequence[str] = None, progressbar: str = None,
               missing_layer: str = None, return_index: bool = True):
        """

        :param query:
        :param layer_query:
        :param layer_ngram_query:
        :param layers:
        :param keys:
        :param collection_meta:
        :param progressbar:
        :param missing_layer:
        :param return_index:
        :return: PgSubCollection

        """
        if not self.exists():
            raise PgCollectionException('collection {!r} does not exist'.format(self.name))

        where_clause = pg.WhereClause(collection=self,
                                      query=query,
                                      layer_query=layer_query,
                                      layer_ngram_query=layer_ngram_query,
                                      keys=keys,
                                      missing_layer=missing_layer)

        return pg.PgSubCollection(collection=self,
                                  selection_criterion=where_clause,
                                  selected_layers=layers,
                                  meta_attributes=collection_meta,
                                  progressbar=progressbar,
                                  return_index=return_index
                                  )

    def __len__(self):
        return count_rows(self.storage, self.name)

    def __getitem__(self, item):
        if isinstance(item, int):
            result = list(self.select(layers=self.selected_layers, keys=[item]))
            if result:
                return result[0][1]
            raise KeyError(item)
        if isinstance(item, slice):  # TODO
            if item.step not in {1, None}:
                raise NotImplementedError('slicing step not supported: {}'.format(item.step))
            raise NotImplementedError('slicing not implemented')

        raise KeyError(item)

    def __iter__(self):
        yield from self.select(layers=self.selected_layers, return_index=False)

    def _select_by_key(self, key, return_as_dict=False):
        """Loads text object by `key`. If `return_as_dict` is True, returns a text object as dict"""
        self.storage.conn.commit()
        self.storage.conn.autocommit = True
        with self.storage.conn.cursor() as c:
            c.execute(SQL("SELECT * FROM {}.{} WHERE id = %s;").format(Identifier(self.storage.schema),
                                                                       Identifier(self.name)),
                      (key,))
            res = c.fetchone()
            if res is None:
                raise PgCollectionException("Key not found: {!r}".format(key))
            key, text_dict = res
            text = text_dict if return_as_dict is True else dict_to_text(text_dict)
            return text

    def count_values(self, layer, attr, **kwargs):
        """Count attribute values in the collection."""
        counter = collections.Counter()
        for i, t in self.select(layers=[layer], **kwargs):
            counter.update(t[layer].count_values(attr))
        return counter

    def find_fingerprint(self, query=None, layer_query=None, layer_ngram_query=None, layers=None, order_by_key=False):
        """A wrapper over `select` method, which enables to conveniently build composite AND/OR queries.

        Args:
            table: str
                collection table name
            query: dict
                Query applied to collection table
            layer_query: dict
                Query applied to layer table
            order_by_key: bool
                Sort results by key in ascending order
        Returns:
            iterator of tuples (key, text)

        Example `layer_ngramm_query`:

            Search ("üks,kaks" AND "kolm,neli") OR "viis,kuus":

            q = {
                "some_layer": {
                     "field": "some_field",
                     "query": [[("üks", "kaks"), ("kolm", "neli")], [("viis", "kuus")]],
                },
                ...

        Example `query`:

            q = {
                 "layer": "morph_analysis",
                 "field": "lemma",
                 "ambiguous": True,
                 "query": ["mis", "palju"],  # mis OR palju
                 }

        Example `layer_query`:

            q = {
                layer1: {
                    "field": "lemma",
                    "query": ["ööbik"],
                    "ambiguous": True
                },
                layer2: {
                    "field": "lemma",
                    "query": ["ööbik"],
                    "ambiguous": True
                }}

        """
        if query is None and layer_query is None and layer_ngram_query is None:
            raise PgCollectionException("One of 'query', 'layer_query' or 'layer_ngramm_query' should be specified.")

        def build_text_query(q):
            or_query_list = []
            for and_terms in q["query"]:
                if not isinstance(and_terms, (list, tuple, set)):
                    and_terms = [and_terms]
                if and_terms:
                    and_query = reduce(op.__and__, (JsonbTextQuery(q["layer"], q["ambiguous"], **{q["field"]: term})
                                                    for term in and_terms))
                    or_query_list.append(and_query)
            if len(or_query_list) > 0:
                jsonb_query = reduce(op.__or__, or_query_list)
            else:
                jsonb_query = None
            return jsonb_query

        def build_layer_query(layer_name, q):
            or_query_list = []
            for and_terms in q["query"]:
                if not isinstance(and_terms, (list, tuple, set)):
                    and_terms = [and_terms]
                if and_terms:
                    and_query = reduce(op.__and__,
                                       (JsonbLayerQuery(layer_name, q["ambiguous"], **{q["field"]: term})
                                        for term in and_terms))
                    or_query_list.append(and_query)
            if len(or_query_list) > 0:
                jsonb_query = reduce(op.__or__, or_query_list)
            else:
                jsonb_query = None
            return jsonb_query

        jsonb_text_query = build_text_query(query) if query is not None else None
        jsonb_layer_query = {layer: build_layer_query(layer, q) for layer, q in
                             layer_query.items()} if layer_query is not None else None

        return self.select(query=jsonb_text_query, layer_query=jsonb_layer_query,
                           layer_ngram_query=layer_ngram_query, layers=layers)

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

        columns = ["id", "text_id", "data"]
        if meta_columns:
            columns.extend(meta_columns)

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
                with self.buffered_layer_insert(table_identifier=layer_table_identifier(self.storage, self.name, layer_name),
                                                columns=columns,
                                                query_length_limit=query_length_limit) as buffered_insert:
                    for row in self.select(layers=tagger.input_layers, progressbar=progressbar):
                        text_id, text = row[0], row[1]

                        for fragment in fragmenter(tagger.make_layer(text, status={})):
                            layer = fragment.layer
                            layer_json = layer_to_json(fragment)

                            values = [None, text_id, layer_json]

                            if meta_columns:
                                values.extend(fragment.meta[k] for k in meta_columns)

                            values = list(map(Literal, values))
                            values[0] = DEFAULT
                            buffered_insert(values=values)
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
            return RowMapperRecord(layer=layer, meta=status)

        layer_name = layer_name or tagger.output_layer
        row_mapper = row_mapper or default_row_mapper

        missing_layer = layer_name if mode == 'append' else None
        data_iterator = data_iterator or self.select(layers=tagger.input_layers, progressbar=progressbar,
                                                     missing_layer=missing_layer)

        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer {!r}".format(
                self.name, layer_name))
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

        columns = ["id", "text_id", "data"]
        if meta_columns:
            columns.extend(meta_columns)

        if ngram_index is not None:
            ngram_index_keys = tuple(ngram_index.keys())
            columns.extend(ngram_index_keys)

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
                with self.buffered_layer_insert(table_identifier=layer_table_identifier(self.storage, self.name, layer_name),
                                                columns=columns,
                                                query_length_limit=query_length_limit) as buffered_insert:
                    for row in data_iterator:
                        collection_id, text = row[0], row[1]

                        record = row_mapper(row)
                        layer = record.layer
                        layer_dict = layer_to_dict(layer)
                        layer_json = json.dumps(layer_dict, ensure_ascii=False)

                        values = [collection_id, collection_id, layer_json]

                        if meta_columns:
                            values.extend(record.meta[k] for k in meta_columns)

                        if ngram_index is not None:
                            values.extend(create_ngram_fingerprint_index(layer=layer,
                                                                         attribute=attr,
                                                                         n=ngram_index[attr])
                                          for attr in ngram_index_keys)
                        values = list(map(Literal, values))
                        buffered_insert(values=values)
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

    def create_layer_block(self, tagger, block, meta=None, query_length_limit=5000000):
        """Creates a layer block

        :param tagger: Tagger

        :param block: Tuple[int, int]
            pair of integers `(module, remainder)`. Only texts with `id % module = remainder` are tagged.
        :param meta: dict of str -> str
            Specifies table column names and data types to create for storing additional
            meta information. E.g. meta={"sum": "int", "average": "float"}.
            See `pytype2dbtype` in `pg_operations` for supported types.
        :param query_length_limit: int
            soft approximate query length limit in unicode characters, can be exceeded by the length of last buffer
            insert

        """
        layer_name = tagger.output_layer

        if not self.exists():
            raise PgCollectionException("collection {!r} does not exist, can't create layer {!r}".format(
                self.name, layer_name))

        meta_columns = ()
        if meta is not None:
            meta_columns = tuple(meta)

        columns = ["id", "text_id", "data"]
        columns.extend(meta_columns)

        logger.info('inserting data into the {!r} layer table block {}'.format(layer_name, block))

        with self.buffered_layer_insert(table_identifier=layer_table_identifier(self.storage, self.name, layer_name),
                                        columns=columns,
                                        query_length_limit=query_length_limit) as buffered_insert:
            layer_structure = None
            for collection_id, text in self.select(query=pg.BlockQuery(*block), layers=tagger.input_layers):
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

                layer_dict = layer_to_dict(layer, text)
                layer_json = json.dumps(layer_dict, ensure_ascii=False)

                values = [Literal(collection_id), Literal(collection_id), Literal(layer_json)]
                values.extend(Literal(layer.meta[k]) for k in meta_columns)

                buffered_insert(values=values)

        logger.info('block {} of {!r} layer created'.format(block, layer_name))

    def create_layer_table(self, layer_name, meta=None):
        layer_table = pg.layer_table_name(self.name, layer_name)

        if pg.table_exists(self.storage, layer_table):
            raise PgCollectionException("The table {!r} of the {!r} layer already exists.".format(layer_table, layer_name))

        layer_identifier = pg.table_identifier(self.storage, pg.layer_table_name(self.name, layer_name))

        columns = [('id', 'SERIAL PRIMARY KEY'), ('text_id', 'int NOT NULL'), ('data', 'jsonb')]
        if meta is not None:
            columns.extend([(name, pg.pytype2dbtype[py_type]) for name, py_type in meta.items()])

        columns = SQL(', ').join(SQL('{} {}').format(Identifier(name), SQL(db_type)) for name, db_type in columns)
        q = SQL('CREATE TABLE {layer_identifier} ({columns})').format(layer_identifier=layer_identifier,
                                                                      columns=columns)

        with self.storage.conn.cursor() as cursor:
            cursor.execute(q)
            logger.debug(cursor.query.decode())

            q = SQL("COMMENT ON TABLE {} IS {};").format(
                    layer_identifier,
                    Literal('created by {} on {}'.format(self.storage.user, time.asctime())))
            cursor.execute(q)
            logger.debug(cursor.query.decode())

        self.storage.conn.commit()

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
        if not self.exists():
            return
        del self.storage[self.name]
        self._is_empty = True

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

    # TODO: remove
    def get_layer_names(self):
        return self.layers

    def get_fragment_tables(self):
        fragment_tables = []
        for tbl in pg.get_all_table_names(self.storage):
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

    def export_layer(self, layer, attributes, collection_meta=None, table_name=None, progressbar=None):
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

        with self.buffered_layer_insert(table_identifier=table_identifier,
                                        columns=[c[0] for c in columns]) as insert:
            i = 0
            for text_id, text, meta in texts:
                for span_nr, span in enumerate(text[layer]):
                    for annotation in span:
                        i += 1
                        values = [Literal(i), Literal(text_id), Literal(span_nr), Literal(span.start), Literal(span.end)]
                        values.extend(Literal(getattr(annotation, attr)) for attr in attributes)
                        values.extend(Literal(meta[k]) for k in collection_meta)
                        insert(values)

        logger.info('{} annotations exported to "{}"."{}"'.format(i, self.storage.schema, table_name))

    def _repr_html_(self):
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
