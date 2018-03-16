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
        """Creates a database table for the collection"""
        return self.storage.create_table(self.table_name)

    def insert(self, text, key=None):
        """Inserts text object as a table row with a given key"""
        return self.storage.insert(self.table_name, text, key)

    def exists(self):
        """Returns true if table exists"""
        return self.storage.table_exists(self.table_name)

    def select(self, query=None, layer_query=None, order_by_key=False, layers=None):
        """See PostgresStorage.select()"""
        return self.storage.select(self.table_name, query, layer_query, order_by_key, layers)

    def select_by_key(self, key, return_as_dict=False):
        """See PostgresStorage.select_by_key()"""
        return self.storage.select_by_key(self.table_name, key, return_as_dict)

    def find_fingerprint(self, query=None, layer_query=None, order_by_key=False):
        """See PostgresStorage.find_fingerprint()"""
        return self.storage.find_fingerprint(self.table_name, query, layer_query, order_by_key)

    def layer_name_to_table_name(self, layer_name):
        return self.storage.layer_name_to_table_name(self.table_name, layer_name)

    def create_layer(self, layer_name, callable, layers=None, create_index=False):
        """
        Creates a new layer in a separate table and links it with the current collection.

        Args:
            layer_name:
            callable: callable
                A function to be applied to each `text` entry in a collection.
            layers: list of str
                The specified layers will be fetched and merged with the text object before passing it to `callable`.
            create_index: bool
                Whether to create a gin index for a jsonb column.

        Example:
            layer_name = "my_layer"
            tagger = VabamorfTaggerOld(layer_name=layer_name)
            collection.create_layer(layer_name, callable=lambda t: tagger.tag(t, return_layer=True))

        """
        layer_table = self.layer_name_to_table_name(layer_name)
        if self.storage.table_exists(layer_table):
            raise PgStorageException("Table '{}' for layer '{}' already exists.".format(layer_table, layer_name))
        conn = self.storage.conn
        with conn.cursor() as c:
            try:
                conn.autocommit = False
                # create layer table and index
                c.execute(SQL("CREATE TABLE {}.{} (id serial PRIMARY KEY, data jsonb)").format(
                    Identifier(self.storage.schema), Identifier(layer_table)))
                if create_index is True:
                    c.execute(SQL(
                        "CREATE INDEX {index} ON {schema}.{table} USING gin ((data->'layers') jsonb_path_ops)").format(
                        schema=Identifier(self.storage.schema),
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
        """Removes collection and all related layers."""
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
                 pgpass_file="~/.pgpass", schema="public", **kwargs):
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
        self.schema = schema

    def close(self):
        """Closes database connection"""
        self.conn.close()

    def create_schema(self):
        with self.conn.cursor() as c:
            c.execute(SQL("CREATE SCHEMA {};").format(Identifier(self.schema)))

    def delete_schema(self):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP SCHEMA {} CASCADE;").format(Identifier(self.schema)))

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
                c.execute(SQL("CREATE TABLE {}.{} (id serial PRIMARY KEY, data jsonb)").format(
                    Identifier(self.schema), Identifier(table)))
                c.execute(
                    SQL("CREATE INDEX {index} ON {schema}.{table} USING gin ((data->'layers') jsonb_path_ops)").format(
                        index=Identifier('idx_%s_data' % table),
                        schema=Identifier(self.schema),
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
        return "%s__%s" % (collection_table, layer_name)

    def drop_table(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP TABLE {}.{}").format(Identifier(self.schema), Identifier(table)))

    def drop_table_if_exists(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("DROP TABLE IF EXISTS {}.{}").format(Identifier(self.schema), Identifier(table)))

    def insert_layer_row(self, layer_table, layer_dict, key):
        layer_json = json.dumps(layer_dict, ensure_ascii=False)
        with self.conn.cursor() as c:
            c.execute(SQL("INSERT INTO {}.{} VALUES (%s, %s) RETURNING id;").format(Identifier(self.schema),
                                                                                    Identifier(layer_table)),
                      (key, layer_json))
            row_key = c.fetchone()[0]
            return row_key

    def insert(self, table, text, key=None):
        """
        Saves a given `text` object into a given `table`..
        Args:
            table: str
            text: text
            key: int

        Returns:
            int: row key (id)
        """
        text = export_json(text)
        with self.conn.cursor() as c:
            if key is not None:
                c.execute(SQL("INSERT INTO {}.{} VALUES (%s, %s) RETURNING id;").format(
                    Identifier(self.schema), Identifier(table)), (key, text))
            else:
                c.execute(SQL("INSERT INTO {}.{} (data) VALUES (%s) RETURNING id;").format(
                    Identifier(self.schema), Identifier(table)), (text,))
            row_key = c.fetchone()[0]
            return row_key

    def table_exists(self, table):
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE  schemaname = %s AND tablename = %s);"),
                      [self.schema, table])
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
            text = text_dict if return_as_dict is True else import_dict(text_dict)
            return text

    def get_all_table_names(self):
        with self.conn.cursor() as c:
            c.execute(SQL(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'"),
                [self.schema])
            table_names = [row[0] for row in c.fetchall()]
            return table_names

    def select(self, table, query=None, layer_query=None, order_by_key=False, layers=None):
        """
        Select from collection table with possible search constraints.

        Args:
            table: str
                collection table
            query: JsonbTextQuery
                collection table query
            layer_query: JsonbLayerQuery
                layer query
            order_by_key: bool
            layers: list of str
                Layers to fetch. Specified layers will be merged into returned text object and
                can be accessed as `text["layer_name"]`.

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
            if layers is None and layer_query is None:
                # select only text table
                q = SQL("SELECT * FROM {}.{}").format(Identifier(self.schema), Identifier(table)).as_string(self.conn)
                sql_parts.append(q)
            else:
                # need to join text and all layer tables
                if layers is not None:
                    layers_select = [SQL("{}.{}").format(Identifier(self.schema),
                                                         Identifier(
                                                             self.layer_name_to_table_name(table, layer))).as_string(
                        self.conn)
                                     for layer in layers]
                else:
                    layers_select = []
                if layer_query is not None:
                    layers_query = [SQL("{}.{}").format(Identifier(self.schema),
                                                        Identifier(
                                                            self.layer_name_to_table_name(table, layer))).as_string(
                        self.conn)
                                    for layer in layer_query.keys()]
                else:
                    layers_query = []
                layers_join = set(layers_select + layers_query)
                table_escaped = SQL("{}.{}").format(Identifier(self.schema), Identifier(table)).as_string(self.conn)
                q = "SELECT {table}.id, {table}.data {select} FROM {table}, {layer_tables} where {where}".format(
                    schema=Identifier(self.schema),
                    table=table_escaped,
                    select=", %s" % ", ".join("%s.data" % layer for layer in layers_select) if layers_select else "",
                    layer_tables=", ".join(layer for layer in layers_join),
                    where=" AND ".join("%s.id = %s.id" % (table_escaped, layer) for layer in layers_join))
                sql_parts.append(q)
                where = True
            if query is not None:
                # build constraint on the main text table
                sql_parts.append("%s %s" % ("and" if where else "where", query.eval()))
                where = True
            if layer_query is not None:
                # build constraint on related layer tables
                q = " AND ".join(query.eval() for layer, query in layer_query.items())
                sql_parts.append("%s %s" % ("and" if where else "where", q))
                where = True
            if order_by_key is True:
                sql_parts.append("order by id")
            sql = " ".join(sql_parts)  # bad, bad string concatenation, but we can't avoid it here, right?
            print(sql)
            # 2. Execute query
            c.execute(sql)
            for row in c.fetchall():
                key = row[0]
                text_dict = row[1]
                text = import_dict(text_dict)
                if len(row) > 2:
                    for layer_name, layer_dict in zip(layers, row[2:]):
                        text[layer_name] = dict_to_layer(layer_dict, text)
                yield key, text

    def find_fingerprint(self, table, query=None, layer_query=None, order_by_key=False):
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


        Example `query`:

            q = {
                 "layer": "morph_analysis",
                 "field": "lemma",
                 "ambiguous": True,
                 "query": ["mis", "palju"],  mis OR palju
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
        if query is None and layer_query is None:
            raise PgStorageException("Either 'query' or 'layer_query' should be specified.")

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

        return self.select(table, jsonb_text_query, jsonb_layer_query, order_by_key=order_by_key)

    def get_collection(self, table_name):
        """Returns a new instance of `PgCollection` without physically creating it."""
        return PgCollection(table_name, self)


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
