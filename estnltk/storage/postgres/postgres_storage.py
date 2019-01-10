import os
import json
import pandas
import operator as op
from functools import reduce
from itertools import chain

import psycopg2
from psycopg2.sql import SQL, Identifier, Literal, DEFAULT

from estnltk import logger
from estnltk.converters import dict_to_layer
from estnltk.converters import dict_to_text, text_to_json
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import JsonbLayerQuery
from estnltk.storage.postgres import JsonbTextQuery


class PgStorageException(Exception):
    pass


class PostgresStorage:
    """`PostgresStorage` instance wraps a database connection and
    exposes interface to conveniently search/save json data.
    """

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None,
                 pgpass_file=None, schema="public", role=None, temporary=False, **kwargs):
        """
        Connects to database either using connection parameters if specified, or ~/.pgpass file.

            ~/.pgpass file format: hostname:port:database:username:password

        """
        self.schema = schema
        self.temporary = temporary

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
                         'host: {!r}, port: {!r}, dbname: {!r}, user: {!r}.'.format(_host, _port, _dbname, _user))
            raise
        self.conn.autocommit = True

        with self.conn.cursor() as c:
            logger.info('role: {!r}'.format(role))
            c.execute(SQL("SET ROLE {};").format(Identifier(role)))

    def close(self):
        """Closes database connection"""
        self.conn.close()

    def closed(self):
        return self.conn.closed

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
        if self.closed():
            return None
        with self.conn.cursor() as c:
            c.execute(SQL(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'"),
                [self.schema])
            table_names = [row[0] for row in c.fetchall()]
            return table_names

    def get_all_tables(self):
        if self.closed():
            return None
        with self.conn.cursor() as c:
            c.execute(SQL(
                "SELECT table_name, "
                       "pg_size_pretty(pg_total_relation_size({schema}||'.'||table_name)), "
                       "obj_description(({schema}||'.'||table_name)::regclass) "
                "FROM information_schema.tables "
                "WHERE table_schema={schema} AND table_type='BASE TABLE';").format(schema=Literal(self.schema))
                )
            tables = {row[0]: {'total_size': row[1], 'comment':row[2]} for row in c}
            return tables

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

    def __str__(self):
        return '{self.__class__.__name__}({self.conn.dsn} schema={self.schema} temporary={self.temporary})'.format(
                self=self)

    def _repr_html_(self):
        tables = self.get_all_tables()

        structure = {}

        collection_tables = ''
        if tables is not None:
            for t, v in tables.items():
                t_split = t.split('__')
                if len(t_split) == 1 and t_split[0] + '__structure' in tables:
                    structure[(t_split[0], '')] = v
                elif len(t_split) == 3 and t_split[2] == 'layer' and t_split[0] in tables:
                    structure[(t_split[0], t_split[1])] = v

            if structure:
                df = pandas.DataFrame.from_dict(structure, orient='index', columns=['total_size', 'comment'])
                df.index.names = ('collection', 'layers')
                collection_tables = df.to_html()
            else:
                collection_tables = '<br/>This storage has no collections.'
        return ('<b>{self.__class__.__name__}</b><br/>\n{self.conn.dsn} schema={self.schema}<br/>'
                'temporary={self.temporary}\n'
                '{collections}').format(
                self=self, collections=collection_tables)
