import os
import json
import logging
import operator as op
from functools import reduce

import psycopg2
from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier

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

    def select(self, query=None, remote_layers=None, order_by_key=False, return_as_dict=False):
        return self.storage.select(self.table_name, query, order_by_key, return_as_dict)

    def select_by_key(self, key, return_as_dict=False):
        return self.storage.select_by_key(self.table_name, key, return_as_dict)

    def find_fingerprint(self, layer, field, query_list, ambiguous=True, order_by_key=False, return_as_dict=False):
        return self.storage.find_fingerprint(self.table_name, layer, field, query_list, ambiguous, order_by_key,
                                             return_as_dict)

    # def add_layer(self, layer_name, callable, query=None, remote_layers=None, inplace=True):
    #     for in self.select(query, remote_layers):

    def delete(self):
        self.storage.drop_table(self.table_name)

    def delete_attached_layer(self, layer_name):
        pass


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
                host, port, dbname, user, passwd = open(pgpass, encoding="utf-8").readline().rstrip().split(":")
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

    def drop_table(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP TABLE {}").format(Identifier(table)))

    def insert(self, table, text, key=None):
        """Saves a given `text` object into a given `table`. Returns a key of the inserted row."""
        with self.conn.cursor() as c:
            if key is not None:
                c.execute(SQL("INSERT INTO {} VALUES (%s, %s) RETURNING id;").format(Identifier(table)),
                          (key, export_json(text)))
            else:
                c.execute(SQL("INSERT INTO {} (data) VALUES (%s) RETURNING id;").format(Identifier(table)),
                          (export_json(text),))
            row_key = c.fetchone()[0]
        return row_key

    def table_exists(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE  schemaname = %s AND tablename = %s);"),
                      [self.schema, table])
            return c.fetchone()[0]

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

    def select(self, table, query=None, order_by_key=False, return_as_dict=False):
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
            sql_parts = [SQL("SELECT * FROM {}").format(Identifier(table)).as_string(self.conn)]
            if query is not None:
                sql_parts.append("where %s" % query.eval())
            if order_by_key is True:
                sql_parts.append("order by id")
            sql = ' '.join(sql_parts)  # bad, bad string concatenation, but we can't avoid it here, right?
            c.execute(sql)
            for (key, text_dict) in c.fetchall():
                text = text_dict if return_as_dict is True else import_dict(text_dict)
                yield key, text

    def find_fingerprint(self, table, layer, field, query_list, ambiguous=True, order_by_key=False,
                         return_as_dict=False):
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
        return self.select(table, query, order_by_key, return_as_dict)

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
