import os
import re
import json
import pandas
import operator as op
from collections import namedtuple
from functools import reduce
from itertools import chain
from tqdm import tqdm, tqdm_notebook

import psycopg2
from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier, Literal, DEFAULT

from estnltk import logger
from estnltk.converters.dict_importer import dict_to_layer
from estnltk.converters.dict_exporter import layer_to_dict
from estnltk.converters import dict_to_text, text_to_json
from estnltk.layer_operations import create_ngram_fingerprint_index
from .query import Query


class PgStorageException(Exception):
    pass


class PgCollectionException(Exception):
    pass


RowMapperRecord = namedtuple("RowMapperRecord", ["layer", "meta"])

pytype2dbtype = {
    "int": "integer",
    "bigint": "bigint",
    "float": "double precision",
    "str": "text"
}


class PgCollection:
    """Convenience wrapper over PostgresStorage"""

    def __init__(self, name, storage, meta=None):
        self.table_name = name
        self.storage = storage
        self.meta = meta or {}
        self._structure = None
        if self.exists():
            self._structure = self.get_structure()

    def create(self, description=None):
        """Creates a database table for the collection"""
        with self.storage.conn.cursor() as c:
            c.execute(SQL("""CREATE TABLE {}.{}  (
                               layer_name text primary key,
                               detached bool not null,
                               attributes text[] not null,
                               ambiguous bool not null,
                               parent text,
                               enveloping text,
                               _base text);""").format(
                Identifier(self.storage.schema),
                Identifier(self.table_name+'_structure')))
            logger.info('create table {}.{}'.format(self.storage.schema, self.table_name+'_structure'))

        return self.storage.create_table(self.table_name, description, self.meta)

    def get_structure(self):
        structure = {}
        with self.storage.conn.cursor() as c:
            c.execute(SQL("SELECT layer_name, detached, attributes, ambiguous, parent, enveloping, _base FROM {}.{};"
                          ).format(Identifier(self.storage.schema),
                                   Identifier(self.table_name+'_structure')))

            for row in c.fetchall():
                structure[row[0]] = {'detached': row[1],
                                     'attributes': tuple(row[2]),
                                     'ambiguous': row[3],
                                     'parent': row[4],
                                     'enveloping': row[5],
                                     '_base': row[6]}
        return structure

    def _insert_into_structure(self, layer, detached: bool):
        with self.storage.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {}.{} (layer_name, detached, attributes, ambiguous, parent, enveloping, _base) "
                          "VALUES ({}, {}, {}, {}, {}, {}, {});").format(
                Identifier(self.storage.schema),
                Identifier(self.table_name+'_structure'),
                Literal(layer.name),
                Literal(detached),
                Literal(list(layer.attributes)),
                Literal(layer.ambiguous),
                Literal(layer.parent),
                Literal(layer.enveloping),
                Literal(layer._base)
            )
            )
        self._structure = self.get_structure()

    def _delete_from_structure(self, layer_name):
        with self.storage.conn.cursor() as c:
            c.execute(SQL("DELETE FROM {}.{} WHERE layer_name={};").format(
                Identifier(self.storage.schema),
                Identifier(self.table_name+'_structure'),
                Literal(layer_name)
            )
            )
            logger.debug(c.query.decode())
        self._structure = self.get_structure()

    def insert(self, text, key=None, meta_data=None):
        """Saves a given `Text` object into the collection.

        Args:
            text: Text
            key: int
            meta_data: dict

        Returns:
            int: row key (id)
        """

        if self._structure is None:
            for layer in text.layers:
                self._insert_into_structure(text[layer], detached=False)
        elif any(struct['detached'] for struct in self._structure.values()):
            # TODO: solve this case in a better way
            raise PgCollectionException("This collection has detached layers. Can't add new text objects.")
        else:
            assert set(text.layers) == set(self._structure), '{} != {}'.format(set(text.layers), set(self._structure))
            for layer_name, layer in text.layers.items():
                layer_struct = self._structure[layer_name]
                assert layer_struct['detached'] is False
                assert layer_struct['attributes'] == layer.attributes, '{} != {}'.format(layer_struct['attributes'],
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

        column_names = [Identifier('id'), Identifier('data')]
        expressions = [key, Literal(text)]
        if meta_data:
            for k in self.meta:
                column_names.append(Identifier(k))
                if k in meta_data:
                    expressions.append(Literal(meta_data[k]))
                else:
                    expressions.append(DEFAULT)

        with self.storage.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {}.{} ({}) VALUES ({}) RETURNING id;").format(
                Identifier(self.storage.schema),
                Identifier(self.table_name),
                SQL(', ').join(column_names),
                SQL(', ').join(expressions)))
            row_key = c.fetchone()[0]
            return row_key

    def exists(self):
        """Returns true if table exists"""
        return self.storage.table_exists(self.table_name)

    def select_fragment_raw(self, fragment_name, parent_layer_name, query=None, ngram_query=None):
        return self.storage.select_fragment_raw(
            fragment_table=self.fragment_name_to_table_name(fragment_name),
            text_table=self.table_name,
            parent_layer_table=self.layer_name_to_table_name(parent_layer_name),
            query=query,
            ngram_query=ngram_query)

    def select(self, query=None, layer_query=None, layer_ngram_query=None, layers=None, keys=None, order_by_key=False):
        """See PostgresStorage.select()"""
        layers_extended = []

        def include_dep(layer):
            if layer is None or not self._structure[layer]['detached']:
                return
            for dep in (self._structure[layer]['parent'], self._structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in layers or []:
            include_dep(layer)

        return self.storage.select(self.table_name, query, layer_query, layer_ngram_query, layers_extended, keys=keys,
                                   order_by_key=order_by_key)

    def select_raw(self, query=None, layer_query=None, layer_ngram_query=None, layers=None, keys=None,
                   order_by_key=False):
        """See PostgresStorage.select_raw()"""
        return self.storage.select_raw(self.table_name, query, layer_query, layer_ngram_query, layers, keys,
                                       order_by_key)

    def select_by_key(self, key, return_as_dict=False):
        """See PostgresStorage.select_by_key()"""
        return self.storage.select_by_key(self.table_name, key, return_as_dict)

    def find_fingerprint(self, query=None, layer_query=None, layer_ngram_query=None, layers=None, order_by_key=False):
        """See PostgresStorage.find_fingerprint()"""
        return self.storage.find_fingerprint(self.table_name, query, layer_query, layer_ngram_query, layers,
                                             order_by_key)

    def layer_name_to_table_name(self, layer_name):
        return self.storage.layer_name_to_table_name(self.table_name, layer_name)

    def fragment_name_to_table_name(self, fragment_name):
        return self.storage.fragment_name_to_table_name(self.table_name, fragment_name)

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
                # create fragment table and indices
                self.create_fragment_table(c, fragment_name,
                                           create_index=create_index,
                                           ngram_index=ngram_index)
                # insert data
                fragment_table = self.fragment_name_to_table_name(fragment_name)
                id_ = 0
                for row in data_iterator:
                    text_id, text, parent_layer_id = row[0], row[1], row[2]
                    for record in row_mapper(row):
                        fragment_dict = layer_to_dict(record.layer, text)
                        if ngram_index is not None:
                            ngram_values = [create_ngram_fingerprint_index(record.layer, attr, size)
                                            for attr, size in ngram_index.items()]
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

    def create_layer(self, layer_name, data_iterator, row_mapper,
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
                if 'unicode', display progressbar as a unicode string
                else disable progressbar (default)
        """
        logger.info('creating a new layer: {!r}'.format(layer_name))
        if self._structure is None:
            raise PgCollectionException("can't add detached layer {!r}, the collection is empty".format(layer_name))
        if self.has_layer(layer_name):
            if overwrite:
                logger.info("overwriting output layer: {!r}".format(layer_name))
                self.delete_layer(layer_name=layer_name)
            else:
                exception = PgCollectionException("can't create layer {!r}, layer already exists".format(layer_name))
                logger.error(exception)
                raise exception
        logger.info('creating layer: {!r}'.format(layer_name))
        conn = self.storage.conn
        with conn.cursor() as c:
            try:
                conn.autocommit = False
                # create table and indices
                self.create_layer_table(cursor=c,
                                        layer_name=layer_name,
                                        create_index=create_index,
                                        ngram_index=ngram_index,
                                        overwrite=overwrite,
                                        meta=meta)
                # insert data
                layer_table = self.layer_name_to_table_name(layer_name)
                id_ = 0

                meta_columns = ()
                if meta is not None:
                    meta_columns = tuple(meta)

                total = self.storage.count_rows(self.table_name)
                if progressbar == 'notebook':
                    iter_data = tqdm_notebook(data_iterator,
                                              total=total,
                                              unit='doc')
                else:
                    iter_data = tqdm(data_iterator,
                                     total=total,
                                     unit='doc',
                                     disable=(progressbar != 'unicode'))

                for row in iter_data:
                    collection_id, text = row[0], row[1]
                    iter_data.set_description('collection_id: {}'.format(collection_id), refresh=False)
                    for record in row_mapper(row):
                        layer = record.layer
                        layer_dict = layer_to_dict(layer, text)
                        layer_json = json.dumps(layer_dict, ensure_ascii=False)

                        columns = ["id", "text_id", "data"]
                        values = ["%s"] * 3

                        meta_values = []
                        if meta_columns:
                            columns.extend(meta_columns)
                            values.extend(["%s"] * len(meta_columns))
                            meta_values = [record.meta[k] for k in meta_columns]

                        if ngram_index is not None:
                            columns.extend(ngram_index.keys())
                            values.extend(["%s"] * len(ngram_index.keys()))
                            ngram_values = [create_ngram_fingerprint_index(layer, attr, size)
                                            for attr, size in ngram_index.items()]
                        else:
                            ngram_values = []

                        columns = ", ".join([SQL("{}").format(Identifier(c)).as_string(conn)
                                             for c in columns])
                        values = ", ".join(values)
                        q = "INSERT INTO {}.{} (%s) VALUES (%s);" % (columns, values)
                        q = SQL(q).format(Identifier(self.storage.schema), Identifier(layer_table))
                        data = (id_, collection_id, layer_json, *meta_values, *ngram_values)
                        c.execute(q, data)

                        id_ += 1
                self._insert_into_structure(layer, detached=True)
            except:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()
                conn.autocommit = True

        logger.info('layer created: {!r}'.format(layer_name))

    def create_layer_table(self, cursor, layer_name, create_index=True, ngram_index=None, overwrite=False, meta=None):
        is_fragment = False
        table_name = self.layer_name_to_table_name(layer_name)
        return self._create_layer_table(cursor, table_name, layer_name, is_fragment, create_index, ngram_index,
                                        overwrite=overwrite, meta=meta)

    def create_fragment_table(self, cursor, fragment_name, create_index=True, ngram_index=None):
        is_fragment = True
        table_name = self.fragment_name_to_table_name(fragment_name)
        return self._create_layer_table(cursor, table_name, fragment_name, is_fragment, create_index, ngram_index)

    def _create_layer_table(self, cursor, layer_table, layer_name, is_fragment=False, create_index=True,
                            ngram_index=None, overwrite=False, meta=None):
        if overwrite:
            self.storage.drop_table_if_exists(layer_table)
        elif self.storage.table_exists(layer_table):
            raise PgStorageException("Table {!r} for layer {!r} already exists.".format(layer_table, layer_name))

        else:
            ngram_cols_sql = ""
        # create layer table and index
        q = ('CREATE TABLE {}.{} ('
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
        q = SQL(q).format(Identifier(self.storage.schema), Identifier(layer_table))
        cursor.execute(q)
        logger.debug(cursor.query.decode())

        q = SQL("COMMENT ON TABLE {}.{} IS {};").format(
            Identifier(self.storage.schema), Identifier(layer_table),
            Literal("%s %s layer" % (self.table_name, layer_name)))
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
            "CREATE INDEX {index} ON {schema}.{table} (text_id);").format(
            index=Identifier('idx_%s__text_id' % layer_table),
            schema=Identifier(self.storage.schema),
            table=Identifier(layer_table)))
        logger.debug(cursor.query.decode())

    def delete_layer(self, layer_name):
        layer_table = self.layer_name_to_table_name(layer_name)
        if layer_name not in self.get_layer_names():
            raise PgCollectionException("Collection does not have a layer '%s'." % layer_name)
        if not self.storage.table_exists(layer_table):
            raise PgStorageException("Layer table '%s' does not exist." % layer_table)
        for ln, struct in self._structure.items():
            if ln == layer_name:
                continue
            if layer_name == struct['enveloping'] or layer_name == struct['parent'] or layer_name == struct['_base']:
                raise PgCollectionException("Can't delete layer {!r}. "
                                            "There is a dependant layer {!r}.".format(layer_name, ln))
        self.storage.drop_table(layer_table)
        self._delete_from_structure(layer_name)
        logger.info('layer deleted: {!r}'.format(layer_name))

    def delete_fragment(self, fragment_name):
        fragment_table = self.fragment_name_to_table_name(fragment_name)
        if fragment_name not in self.get_fragment_names():
            raise PgStorageException("Collection does not have a layer fragment '%s'." % fragment_name)
        if not self.storage.table_exists(fragment_table):
            raise PgStorageException("Layer fragment table '%s' does not exist." % fragment_table)
        self.storage.drop_table(fragment_table)

    def delete_layer_fragment(self, layer_fragment_name):
        lf_table = self.layer_fragment_name_to_table_name(layer_fragment_name)
        if layer_fragment_name not in self.get_layer_fragment_names():
            raise PgStorageException("Collection does not have a layer fragment '%s'." % layer_fragment_name)
        if not self.storage.table_exists(lf_table):
            raise PgStorageException("Layer fragment table '%s' does not exist." % lf_table)
        self.storage.drop_table(lf_table)

    def delete(self):
        """Removes collection and all related layers."""
        conn = self.storage.conn
        conn.autocommit = False
        try:
            for layer_table in self.get_layer_tables():
                self.storage.drop_table(layer_table)
            self.storage.drop_table(self.table_name+'_structure')
            self.storage.drop_table(self.table_name)
        except:
            conn.rollback()
            raise
        finally:
            if conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                conn.commit()
            conn.autocommit = True

    def has_layer(self, layer_name):
        return layer_name in self._structure

    def has_fragment(self, fragment_name):
        return fragment_name in self.get_fragment_names()

    def get_fragment_names(self):
        lf_names = []
        for tbl in self.get_fragment_tables():
            layer = re.sub("^%s__" % self.table_name, "", tbl)
            layer = re.sub("__fragment$", "", layer)
            lf_names.append(layer)
        return lf_names

    def get_layer_names(self):
        layer_names = []
        for tbl in self.get_layer_tables():
            layer = re.sub("^%s__" % self.table_name, "", tbl)
            layer = re.sub("__layer$", "", layer)
            layer_names.append(layer)
        return layer_names

    def get_fragment_tables(self):
        fragment_tables = []
        for tbl in self.storage.get_all_table_names():
            if tbl.startswith("%s__" % self.table_name) and tbl.endswith("__fragment"):
                fragment_tables.append(tbl)
        return fragment_tables

    def get_layer_tables(self):
        layer_tables = []
        for tbl in self.storage.get_all_table_names():
            if tbl.startswith("%s__" % self.table_name) and tbl.endswith("__layer"):
                layer_tables.append(tbl)
        return layer_tables

    def get_layer_meta(self, layer_name):
        layer_table = self.layer_name_to_table_name(layer_name)
        if layer_name not in self.get_layer_names():
            raise PgStorageException("Collection does not have a layer '{}'.".format(layer_name))
        if not self.storage.table_exists(layer_table):
            raise PgStorageException("Layer table '{}' does not exist.".format(layer_table))

        with self.storage.conn.cursor() as c:
            c.execute(SQL("SELECT column_name FROM information_schema.columns "
                          "WHERE table_schema=%s AND table_name=%s;"),
                      (self.storage.schema, layer_table))
            res = c.fetchall()
            columns = [r[0] for r in res if r[0] != 'data']

            c.execute(SQL('SELECT {} FROM {}.{};').format(
                SQL(', ').join(map(Identifier, columns)),
                Identifier(self.storage.schema),
                Identifier(layer_table)))
            data = c.fetchall()
            return pandas.DataFrame(data=data, columns=columns)

    def export_layer(self, layer, attributes, input_layers):
        export_table = '{}__{}__export'.format(self.table_name, layer)
        texts = self.select(layers=input_layers)

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
            c.execute(SQL("CREATE TABLE {}.{} ({});").format(Identifier(self.storage.schema),
                                                             Identifier(export_table),
                                                             columns_sql))

            for text_id, text in texts:
                for span_nr, span in enumerate(text[layer]):
                    for annotation in span:
                        i += 1
                        values = [i, text_id, span_nr]
                        values.extend(getattr(annotation, attr) for attr in  attributes)
                        c.execute(SQL("INSERT INTO {}.{}\n"
                                      "VALUES ({});").format(Identifier(self.storage.schema),
                                                            Identifier(export_table),
                                                            SQL(', ').join(map(Literal, values))
                                                            ))
        print('{} annotations exported to {}.{}'.format(i, self.storage.schema, export_table))


class PostgresStorage:
    """`PostgresStorage` instance wraps a database connection and
    exposes interface to conveniently search/save json data.
    """

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None,
                 pgpass_file=None, schema="public", role=None, **kwargs):
        """
        Connects to database either using connection parameters if specified, or ~/.pgpass file.

            ~/.pgpass file format: hostname:port:database:username:password

        """
        self.schema = schema
        _host, _port, _dbname, _user, _password = host, port, dbname, user, password
        if _host is None or _port is None or _dbname is None or _user is None or _password is None:
            if pgpass_file is None:
                raise PgStorageException("If 'host', 'port', 'dbname', 'user' or 'password' is None, "
                                         "then 'pgpass_file' must not be None.")
            pgpass = os.path.expanduser(pgpass_file)
            if not os.path.isfile(pgpass):
                raise PgStorageException('pgpass file {!r} not found.'.format(pgpass))
            with open(pgpass, encoding="utf-8") as f:
                for line in f:
                    line_split = line.rstrip().split(':')
                    if line.startswith('#') or len(line_split) != 5:
                        continue
                    f_host, f_port, f_dbname, f_user, f_password = line_split

                    _host = f_host
                    if host is None:
                        if f_host == '*':
                            continue
                    elif f_host in {'*', host}:
                        _host = host
                    else:
                        continue

                    _port = f_port
                    if port is None:
                        if f_port == '*':
                            continue
                    elif f_port in {'*', port}:
                        _port = port
                    else:
                        continue

                    _dbname = f_dbname
                    if dbname is None:
                        if f_dbname == '*':
                            continue
                    elif f_dbname in {'*', dbname}:
                        _dbname = dbname
                    else:
                        continue

                    _user = f_user
                    if user is None:
                        if f_user == '*':
                            continue
                    elif f_user in {'*', user}:
                        _user = user
                    else:
                        continue

                    _password = password or f_password
                    break

            if _password is None:
                raise PgStorageException(('no password found for '
                                          'host: {}, port: {}, dbname: {}, user: {}'
                                          ).format(host, port, dbname, user))
        if role is None:
            role = _user
        logger.info('connecting to host: {!r}, port: {!r}, dbname: {!r}, user: {!r}'.format(_host, _port, _dbname, _user))

        try:
            self.conn = psycopg2.connect(dbname=_dbname, user=_user, password=_password, host=_host, port=_port,
                                         **kwargs)
        except Exception:
            logger.error('Failed to connect '
                         'host: {}, port: {}, database: {}, user: {}.'.format(_host, _port, _dbname, _user))
            raise
        self.conn.autocommit = True

        with self.conn.cursor() as c:
            logger.info('role: {!r}'.format(role))
            c.execute(SQL("SET ROLE {};").format(Identifier(role)))

    def close(self):
        """Closes database connection"""
        self.conn.close()

    def create_schema(self):
        with self.conn.cursor() as c:
            c.execute(SQL("CREATE SCHEMA {};").format(Identifier(self.schema)))

    def delete_schema(self):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP SCHEMA {} CASCADE;").format(Identifier(self.schema)))

    def create_table(self, table, description=None, meta=None):
        """Creates a new table to store jsonb data:

            CREATE TABLE table(
                id serial PRIMARY KEY,
                data jsonb
            );

        and automatically adds a GIN index for the jsonb column:

            CREATE INDEX idx_table_data ON table USING gin ((data -> 'layers') jsonb_path_ops);
        """
        columns = [SQL('id BIGSERIAL PRIMARY KEY'),
                   SQL('data jsonb')]
        if meta is not None:
            for col_name, col_type in meta.items():
                columns.append(SQL('{} {}').format(Identifier(col_name), SQL(pytype2dbtype[col_type])))

        self.conn.autocommit = False
        with self.conn.cursor() as c:
            try:
                c.execute(SQL("CREATE TABLE {}.{} ({})").format(
                    Identifier(self.schema), Identifier(table), SQL(', ').join(columns)))
                c.execute(
                    SQL("CREATE INDEX {index} ON {schema}.{table} USING gin ((data->'layers') jsonb_path_ops)").format(
                        index=Identifier('idx_%s_data' % table),
                        schema=Identifier(self.schema),
                        table=Identifier(table)))
                if isinstance(description, str):
                    c.execute(SQL("COMMENT ON TABLE {}.{} IS {}").format(
                        Identifier(self.schema), Identifier(table), Literal(description)))
            except:
                self.conn.rollback()
                raise
            finally:
                if self.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    self.conn.commit()
                self.conn.autocommit = True

    @staticmethod
    def fragment_name_to_table_name(collection_table, fragment_name):
        """
        Constructs table name for a fragment.

        Args:
            collection_table: str
                parent collection table
            fragment_name: str
                fragment name
        Returns:
            str: fragment table name

        """
        return "%s__%s__fragment" % (collection_table, fragment_name)

    @staticmethod
    def layer_name_to_table_name(collection_table, layer_name):
        """
        Constructs layer table name.

        Args:
            collection_table: str
                parent collection table
            layer_name: str
                layer name
        Returns:
            str: layer table name

        """
        return "%s__%s__layer" % (collection_table, layer_name)

    def drop_table(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP TABLE {}.{};").format(Identifier(self.schema), Identifier(table)))
            logger.debug(c.query.decode())

    def drop_table_if_exists(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP TABLE IF EXISTS {}.{};").format(Identifier(self.schema), Identifier(table)))

    def insert_layer_row(self, layer_table, layer_dict, row_id, text_id, ngram_values=None):
        layer_json = json.dumps(layer_dict, ensure_ascii=False)
        ngram_values = ngram_values or []
        with self.conn.cursor() as c:
            sql = "INSERT INTO {}.{} VALUES (%s) RETURNING id;" % ", ".join(['%s'] * (3 + len(ngram_values)))
            c.execute(SQL(sql).format(Identifier(self.schema), Identifier(layer_table)),
                      (row_id, text_id, layer_json, *ngram_values))
            row_key = c.fetchone()[0]
            return row_key

    def insert(self, table, text, key=None, meta=None):
        """
        Saves a given `text` object into a given `table`..
        Args:
            table: str
            text: text
            key: int

        Returns:
            int: row key (id)
        """
        text = text_to_json(text)
        if key is None:
            key = DEFAULT
        else:
            key = Literal(key)
        with self.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {}.{} VALUES ({}, %s) RETURNING id").format(
                Identifier(self.schema), Identifier(table), key), (text,))
            row_key = c.fetchone()[0]
            return row_key

    def table_exists(self, table, schema=None):
        if schema is None:
            schema = self.schema
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE  schemaname = %s AND tablename = %s);"),
                      [schema, table])
            return c.fetchone()[0]

    def count_rows(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT count(*) FROM {}.{}").format(Identifier(self.schema), Identifier(table)))
            nrows = c.fetchone()[0]
            return nrows

    def select_by_key(self, table, key, return_as_dict=False):
        """Loads text object by `key`. If `return_as_dict` is True, returns a text object as dict"""
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT * FROM {}.{} WHERE id = %s").format(Identifier(self.schema), Identifier(table)),
                      (key,))
            res = c.fetchone()
            if res is None:
                raise PgStorageException("Key %s not not found." % key)
            key, text_dict = res
            text = text_dict if return_as_dict is True else dict_to_text(text_dict)
            return text

    def get_all_table_names(self):
        with self.conn.cursor() as c:
            c.execute(SQL(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'"),
                [self.schema])
            table_names = [row[0] for row in c.fetchall()]
            return table_names

    def select_fragment_raw(self, fragment_table, text_table, parent_layer_table, query=None, ngram_query=None):
        """

        Args:
            fragment_table:
            text_table:
            parent_layer_table:
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
        q = """
            SELECT
              {text_table}.id, {text_table}.data, {parent_table}.id, {parent_table}.data,
              {fragment_table}.id, {fragment_table}.data
            FROM
              {text_table}, {parent_table}, {fragment_table}
            WHERE
              {fragment_table}.parent_id = {parent_table}.id AND {parent_table}.text_id = {text_table}.id
            """

        format_table = lambda tbl: SQL("{}.{}").format(Identifier(self.schema), Identifier(tbl)).as_string(
            self.conn)

        q = q.format(
            text_table=format_table(text_table),
            parent_table=format_table(parent_layer_table),
            fragment_table=format_table(fragment_table))

        if query is not None:
            # build constraint on fragment's data column
            q = "%s AND %s" % (q, query.eval())

        if ngram_query is not None:
            # build constraint on fragment's ngram index
            ngram_q = " AND ".join([self._build_column_ngram_query(q, col, fragment_table)
                                    for col, q in ngram_query])
            q = "%s AND %s" % (q, ngram_q)

        # 2. Execute query
        with self.conn.cursor() as c:
            c.execute(q)
            for row in c.fetchall():
                text_id, text_dict, parent_id, parent_dict, fragment_id, fragment_dict = row
                text = dict_to_text(text_dict)
                parent_layer = dict_to_layer(parent_dict, text)
                fragment_layer = dict_to_layer(fragment_dict, text)
                yield text_id, text, parent_id, parent_layer, fragment_id, fragment_layer

    def select_raw(self,
                   table: str,
                   query: str = None,
                   layer_query: 'JsonbLayerQuery' = None,
                   layer_ngram_query: dict = None,
                   layers: list = None,
                   keys: list = None,
                   order_by_key: bool = False):
        """
        Select from collection table with possible search constraints.

        Args:
            table: str
                collection table
            query: JsonbTextQuery
                collection table query
            layer_query: JsonbLayerQuery
                layer query
            keys: list
                List of id-s.
            order_by_key: bool
            layers: list
                Layers to fetch. Specified layers will be merged into returned text object and
                become accessible via `text["layer_name"]`.

        Returns:
            iterator of (key, text) pairs

        Example:

            q = JsonbTextQuery('morph_analysis', lemma='laulma')
            for key, txt in storage.select(table, query=q):
                print(key, txt)


        """
        with self.conn.cursor() as c:
            # 1. Build query

            where = False
            sql_parts = []
            table_escaped = SQL("{}.{}").format(Identifier(self.schema), Identifier(table)).as_string(self.conn)
            if not layers and layer_query is None and layer_ngram_query is None:
                # select only text table
                q = SQL("SELECT id, data FROM {}.{}").format(Identifier(self.schema), Identifier(table)).as_string(self.conn)
                sql_parts.append(q)
            else:
                # need to join text and all layer tables
                layers = layers or []
                layer_query = layer_query or {}
                layer_ngram_query = layer_ngram_query or {}

                layers_select = []
                for layer in chain(layers):
                    layer = self.layer_name_to_table_name(table, layer)
                    layer = SQL("{}.{}").format(Identifier(self.schema), Identifier(layer)).as_string(self.conn)
                    layers_select.append(layer)

                layers_join = set()
                for layer in chain(layers, layer_query.keys(), layer_ngram_query.keys()):
                    layer = self.layer_name_to_table_name(table, layer)
                    layer = SQL("{}.{}").format(Identifier(self.schema), Identifier(layer)).as_string(self.conn)
                    layers_join.add(layer)

                q = "SELECT {table}.id, {table}.data {select} FROM {table}, {layers_join} where {where}".format(
                    schema=Identifier(self.schema),
                    table=table_escaped,
                    select=", %s" % ", ".join(
                        "{0}.id, {0}.data".format(layer) for layer in layers_select) if layers_select else "",
                    layers_join=", ".join(layer for layer in layers_join),
                    where=" AND ".join("%s.id = %s.text_id" % (table_escaped, layer) for layer in layers_join))
                sql_parts.append(q)
                where = True
            if query is not None:
                # build constraint on the main text table
                sql_parts.append("%s %s" % ("and" if where else "where", query.eval()))
                where = True
            if layer_query:
                # build constraint on related layer tables
                q = " AND ".join(query.eval() for layer, query in layer_query.items())
                sql_parts.append("%s %s" % ("and" if where else "where", q))
                where = True
            if keys is None:
                keys = []
            else:
                keys = list(map(int, keys))
                # build constraint on id-s
                sql_parts.append("AND" if where else "WHERE")
                sql_parts.append("{table}.id = ANY(%(keys)s)".format(table=table_escaped))
                where = True
            if layer_ngram_query:
                # build constraint on related layer's ngram index
                q = self.build_layer_ngram_query(layer_ngram_query, table)
                if where is True:
                    q = "AND %s" % q
                sql_parts.append(q)
                where = True
            if order_by_key is True:
                sql_parts.append("order by id")

            sql = " ".join(sql_parts)  # bad, bad string concatenation, but we can't avoid it here, right?

            # 2. Execute query
            c.execute(sql, {'keys': keys})
            for row in c.fetchall():
                text_id = row[0]
                text_dict = row[1]
                text = dict_to_text(text_dict)
                layers = []
                if len(row) > 2:
                    detached_layers = {}
                    for i in range(2, len(row), 2):
                        layer_id = row[i]
                        layer_dict = row[i + 1]
                        layer = dict_to_layer(layer_dict, text, detached_layers)
                        detached_layers[layer.name] = layer
                        layers.append(layer_id)
                        layers.append(layer)
                result = text_id, text, *layers
                yield result

    def select(self, table, query=None, layer_query=None, layer_ngram_query=None, layers=None, keys=None,
               order_by_key=False):
        for row in self.select_raw(table, query, layer_query, layer_ngram_query, layers, keys=keys,
                                   order_by_key=order_by_key):
            text_id = row[0]
            text = row[1]
            if len(row) > 2:
                for i, layer_name in zip(range(3, len(row), 2), layers):
                    layer = row[i]
                    text[layer_name] = layer
            yield text_id, text

    def build_layer_ngram_query(self, ngram_query, collection_table):
        sql_parts = []
        for layer in ngram_query:
            for column, q in ngram_query[layer].items():
                layer_table = self.layer_name_to_table_name(collection_table, layer)
                col_query = self._build_column_ngram_query(q, column, layer_table)
                sql_parts.append(col_query)
        q = " AND ".join(sql_parts)
        return q

    def _build_column_ngram_query(self, query, column, table_name):
        if not isinstance(query, list):
            query = list(query)
        if isinstance(query[0], list):
            # case: [[(a),(b)], [(c)]] -> a AND b OR c
            or_terms = [["-".join(e) for e in and_term] for and_term in query]
        elif isinstance(query[0], tuple):
            # case: [(a), (b)] -> a OR b
            or_terms = [["-".join(e)] for e in query]
        elif isinstance(query[0], str):
            # case: [a, b] -> "a-b"
            or_terms = [["-".join(query)]]
        else:
            raise ValueError("Invalid ngram query format: {}".format(query))

        or_parts = []
        for and_term in or_terms:
            arr = ",".join("'%s'" % v for v in and_term)
            p = SQL("{schema}.{table}.{column} @> ARRAY[%s]" % arr).format(
                schema=Identifier(self.schema),
                table=Identifier(table_name),
                column=Identifier(column)).as_string(self.conn)
            or_parts.append(p)
        column_ngram_query = "(%s)" % " OR ".join(or_parts)
        return column_ngram_query

    def find_fingerprint(self, table, query=None, layer_query=None, layer_ngram_query=None, layers=None,
                         order_by_key=False):
        """
        A wrapper over `select` method, which enables to conveniently build composite AND/OR queries.

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
            raise PgStorageException("One of 'query', 'layer_query' or 'layer_ngramm_query' should be specified.")

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

        def build_layer_query(layer, q):
            or_query_list = []
            layer_table = self.layer_name_to_table_name(table, layer)
            for and_terms in q["query"]:
                if not isinstance(and_terms, (list, tuple, set)):
                    and_terms = [and_terms]
                if and_terms:
                    and_query = reduce(op.__and__,
                                       (JsonbLayerQuery(layer_table, q["ambiguous"], **{q["field"]: term})
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

        return self.select(table, jsonb_text_query, jsonb_layer_query, layer_ngram_query, layers,
                           order_by_key=order_by_key)

    def get_collection(self, table_name, meta_fields=None):
        """Returns a new instance of `PgCollection` without physically creating it."""
        return PgCollection(name=table_name, storage=self, meta=meta_fields)


class JsonbTextQuery(Query):
    """
    Constructs database query to search `text` objects stored in jsonb format.
    """

    def __init__(self, layer, ambiguous=True, **kwargs):
        if not kwargs:
            raise ValueError('At least one layer attribute is required.')
        self.layer = layer
        self.ambiguous = ambiguous
        self.kwargs = kwargs

    def eval(self):
        if self.ambiguous is True:
            pat = """data->'layers' @> '[{"name": "%s", "spans": [[%s]]}]'"""
        else:
            pat = """data->'layers' @> '[{"name": "%s", "spans": [%s]}]'"""
        return pat % (self.layer, json.dumps(self.kwargs))


class JsonbLayerQuery(Query):
    """
    Constructs database query to search `layer` objects stored in jsonb format.
    """

    def __init__(self, layer_table, ambiguous=True, **kwargs):
        if not kwargs:
            raise ValueError('At least one layer attribute is required.')
        self.layer_table = layer_table
        self.ambiguous = ambiguous
        self.kwargs = kwargs

    def eval(self):
        if self.ambiguous is True:
            pat = """%s.data @> '{"spans": [[%s]]}'"""
        else:
            pat = """%s.data @> '{"spans": [%s]}'"""
        return pat % (self.layer_table, json.dumps(self.kwargs))
