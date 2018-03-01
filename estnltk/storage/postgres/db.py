import os
import json
import pickle
import logging
import operator as op
from functools import reduce

import psycopg2
from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier

from estnltk.converters.dict_importer import dict_to_layer
from estnltk.converters.dict_exporter import layer_to_dict
from estnltk.converters import import_dict, export_json
from .query import Query

log = logging.getLogger(__name__)


class PgStorageException(Exception):
    pass


class PgCollection:
    """Convenience wrapper over PostgresStorage"""

    def __init__(self, name, storage):
        self.table_name = name
        self.storage = storage

    def create(self):
        return self.storage.create_table(self.table_name)

    def insert(self, text, key=None):
        return self.storage.insert(self.table_name, text, key)

    def exists(self):
        return self.storage.table_exists(self.table_name)

    def update(self, key, text):
        pass

    def select(self, query=None, order_by_key=False, layers=None):
        return self.storage.select(self.table_name, query, order_by_key, layers)

    def select_by_key(self, key, return_as_dict=False):
        return self.storage.select_by_key(self.table_name, key, return_as_dict)

    def find_fingerprint(self, layer, field, query_list, ambiguous=True, order_by_key=False):
        return self.storage.find_fingerprint(self.table_name, layer, field, query_list, ambiguous, order_by_key)

    def layer_name_to_table_name(self, layer_name):
        return self.storage.layer_name_to_table_name(self.table_name, layer_name)

    def create_layer(self, layer_name, callable, layers=None):
        layer_table = self.layer_name_to_table_name(layer_name)
        if self.storage.table_exists(layer_table):
            raise PgStorageException("Table '{}' for layer '{}' already exists.".format(layer_table, layer_name))
        conn = self.storage.conn
        with conn.cursor() as c:
            try:
                conn.autocommit = False
                # create layer table and index
                c.execute(SQL("CREATE TABLE {} (id serial PRIMARY KEY, data jsonb)").format(Identifier(layer_table)))
                c.execute(SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops)").format(
                    index=Identifier('idx_%s_data' % layer_table),
                    table=Identifier(layer_table)))
                # insert data
                for key, text in self.select(layers=layers):
                    layer = callable(text)
                    layer_dict = layer_to_dict(layer, text)
                    self.storage.insert_layer_row(layer_table, layer_dict, key)
            except:
                conn.rollback()
                raise
            finally:
                if conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    conn.commit()
                conn.autocommit = True

    def delete_layer(self, layer_name):
        layer_table = self.layer_name_to_table_name(layer_name)
        if not self.storage.table_exists(layer_table):
            raise PgStorageException()
        self.storage.drop_table(layer_table)

    def delete(self):
        conn = self.storage.conn
        conn.autocommit = False
        try:
            for layer_table in self.get_layer_tables():
                self.storage.drop_table(layer_table)
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
        return layer_name in self.get_layer_names()

    def get_layer_names(self):
        return [tbl[len(self.table_name) + 2:] for tbl in self.get_layer_tables()]

    def get_layer_tables(self):
        return [tbl for tbl in self.storage.get_all_table_names() if tbl.startswith("%s__" % self.table_name)]


class PostgresStorage:
    """`PostgresStorage` instance wraps a database connection and
    exposes interface to conveniently search/save json data.
    """

    def __init__(self, dbname=None, user=None, password=None, host='localhost', port=5432,
                 pgpass_file="~/.pgpass", **kwargs):
        """
        Connects to database either using connection parameters if specified, or ~/.pgpass file.
        ~/.pgpass file format: hostname:port:database:username:password
        """
        if dbname is None:
            log.debug("Database name not specified. Loading connection settings from '%s'" % pgpass_file)
            pgpass = os.path.expanduser(pgpass_file)
            if not os.path.exists(pgpass):
                raise PgStorageException("Configuration file '%s' not found." % pgpass)
            else:
                with open(pgpass, encoding="utf-8") as f:
                    host, port, dbname, user, password = f.readline().rstrip().split(":")
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, **kwargs)
        self.conn.autocommit = True
        self.schema = "public"

    def close(self):
        """Closes database connection"""
        self.conn.close()

    def create_table(self, table):
        """Creates a new table to store jsonb data:

            CREATE TABLE table(
                id serial PRIMARY KEY,
                data jsonb
            );

        and automatically adds a GIN index for the jsonb column:

            CREATE INDEX idx_table_data ON table USING gin ((data -> 'layers') jsonb_path_ops);
        """
        self.conn.autocommit = False
        with self.conn.cursor() as c:
            try:
                c.execute(SQL("CREATE TABLE {} (id serial PRIMARY KEY, data jsonb)").format(Identifier(table)))
                c.execute(SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops)").format(
                    index=Identifier('idx_%s_data' % table),
                    table=Identifier(table)))
            except:
                self.conn.rollback()
                raise
            finally:
                if self.conn.status == STATUS_BEGIN:
                    # no exception, transaction in progress
                    self.conn.commit()
                self.conn.autocommit = True

    def layer_name_to_table_name(self, collection_table, layer_name):
        return "%s__%s" % (collection_table, layer_name)

    def drop_table(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP TABLE {}").format(Identifier(table)))

    def drop_table_if_exists(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP TABLE IF EXISTS {}").format(Identifier(table)))

    def insert_layer_row(self, layer_table, layer_dict, key):
        layer_json = json.dumps(layer_dict, ensure_ascii=False)
        with self.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {} VALUES (%s, %s) RETURNING id;").format(Identifier(layer_table)),
                      (key, layer_json))
            row_key = c.fetchone()[0]
            return row_key

    def insert(self, table, text, key=None):
        """Saves a given `text` object into a given `table`. Returns a key of the inserted row."""
        text = export_json(text)
        with self.conn.cursor() as c:
            if key is not None:
                c.execute(SQL("INSERT INTO {} VALUES (%s, %s) RETURNING id;").format(Identifier(table)), (key, text))
            else:
                c.execute(SQL("INSERT INTO {} (data) VALUES (%s) RETURNING id;").format(Identifier(table)), (text,))
            row_key = c.fetchone()[0]
            return row_key

    def table_exists(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE  schemaname = %s AND tablename = %s);"),
                      [self.schema, table])
            return c.fetchone()[0]

    def count_rows(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT count(*) FROM {}").format(Identifier(table)))
            nrows = c.fetchone()[0]
            return nrows

    def select_by_key(self, table, key, return_as_dict=False):
        """Loads text object by `key`. If `return_as_dict` is True, returns a text object as dict"""
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT * FROM {} WHERE id = %s").format(Identifier(table)), (key,))
            res = c.fetchone()
            if res is None:
                raise PgStorageException("Key %s not not found." % key)
            key, text_dict = res
            text = text_dict if return_as_dict is True else import_dict(text_dict)
            return text

    def get_all_table_names(self):
        with self.conn.cursor() as c:
            c.execute(SQL(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"))
            table_names = [row[0] for row in c.fetchall()]
            return table_names

    def select(self, table, query=None, order_by_key=False, layers=None):
        """
        Query a table.

        Example:

            q = JsonbQuery('morph_analysis', lemma='laulma')
            for key, txt in storage.select(table, query=q):
                print(key, txt)

        :param query (JsonbQuery): query to execute
        :return: iterator of (key, text) pairs

        """
        with self.conn.cursor() as c:
            if layers is None:
                sql_parts = [SQL("SELECT * FROM {}").format(Identifier(table)).as_string(self.conn)]
            else:
                table_escaped = Identifier(table).as_string(self.conn)
                layers_escaped = [Identifier(self.layer_name_to_table_name(table, layer)).as_string(self.conn)
                                  for layer in layers]
                sql_parts = [
                    "SELECT {table}.id, {table}.data, {select} FROM {table}, {layer_tables} where {where}".format(
                        select=", ".join("%s.data" % layer for layer in layers_escaped),
                        table=table_escaped,
                        layer_tables=", ".join(layer for layer in layers_escaped),
                        where=" and ".join("%s.id = %s.id" % (table_escaped, layer) for layer in layers_escaped))]
            if query is not None:
                sql_parts.append("%s %s" % ("and" if "where" in sql_parts[0] else "where", query.eval()))
            if order_by_key is True:
                sql_parts.append("order by id")
            sql = ' '.join(sql_parts)  # bad, bad string concatenation, but we can't avoid it here, right?
            c.execute(sql)
            for row in c.fetchall():
                key = row[0]
                text_dict = row[1]
                text = import_dict(text_dict)
                if len(row) > 2:
                    for layer_name, layer_dict in zip(layers, row[2:]):
                        text[layer_name] = dict_to_layer(layer_dict, text)
                yield key, text

    def find_fingerprint(self, table, layer, field, query_list, ambiguous=True, order_by_key=False):
        """
        A wrapper over `select` method, which enables to conveniently build composite AND/OR queries
        involving a single layer and field.

        Example:

            res = storage.find_fingerprint('my_table', 'morph_analysis', 'lemma', [{'tuul', 'puhuma'}, {'kala'}])
            for key, text in res:
                pass

        :param query_list (list of sets): contains terms to build a boolean query.
                E.g., `[{a, b, c}, {d, e}]` -> `(a AND b AND c) OR (d AND e)`
        :return: iterator of (key, text) pairs
        """
        or_query_list = []
        for and_terms in query_list:
            if and_terms:
                and_query = reduce(op.__and__,
                                   (JsonbQuery(layer, ambiguous, **{field: term}) for term in and_terms))
                or_query_list.append(and_query)
        query = reduce(op.__or__, or_query_list) if or_query_list else None
        return self.select(table, query, order_by_key)

    def get_collection(self, table_name):
        return PgCollection(table_name, self)


class JsonbQuery(Query):
    def __init__(self, layer, ambiguous=True, **kwargs):
        if not kwargs:
            raise ValueError('At least one layer argument required.')
        self.layer = layer
        self.ambiguous = ambiguous
        self.kwargs = kwargs

    def eval(self):
        if self.ambiguous is True:
            pat = """data->'layers' @> '[{"name": "%s", "spans": [[%s]]}]'"""
        else:
            pat = """data->'layers' @> '[{"name": "%s", "spans": [%s]}]'"""
        return pat % (self.layer, json.dumps(self.kwargs))
