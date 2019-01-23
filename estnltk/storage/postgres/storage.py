import os
import pandas
import operator as op
from functools import reduce

import psycopg2
from psycopg2.sql import SQL, Identifier, Literal, DEFAULT

from estnltk import logger
from estnltk.converters import dict_to_layer
from estnltk.converters import dict_to_text, text_to_json
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import JsonbLayerQuery
from estnltk.storage.postgres import JsonbTextQuery
from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres import fragment_table_identifier


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
            c.execute(SQL("SET ROLE {};").format(Identifier(role)))

        logger.info('schema: {!r}, temporary: {!r}, role: {!r}'.format(self.schema, self.temporary, role))

    def close(self):
        """Closes database connection"""
        self.conn.close()

    def closed(self):
        return self.conn.closed

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
                raise PgStorageException("Key %s not found." % key)
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

    def select_fragment_raw(self, fragment_name, collection_name, parent_layer_name, query=None, ngram_query=None):
        """

        Args:
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
            text_table=collection_table_identifier(self, collection_name),
            parent_table=layer_table_identifier(self, collection_name, parent_layer_name),
            fragment_table=fragment_table_identifier(self, collection_name, fragment_name))

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
        logger.debug(q.as_string(self.conn))
        with self.conn.cursor() as c:
            c.execute(q)
            for row in c.fetchall():
                text_id, text_dict, parent_id, parent_dict, fragment_id, fragment_dict = row
                text = dict_to_text(text_dict)
                parent_layer = dict_to_layer(parent_dict, text)
                fragment_layer = dict_to_layer(fragment_dict, text)
                yield text_id, text, parent_id, parent_layer, fragment_id, fragment_layer

    def build_layer_ngram_query(self, ngram_query, collection_name):
        sql_parts = []
        for layer_name in ngram_query:
            for column, q in ngram_query[layer_name].items():
                col_query = self._build_column_ngram_query(q, column, collection_name, layer_name)
                sql_parts.append(col_query)
        q = SQL(" AND ").join(sql_parts)
        return q

    def _build_column_ngram_query(self, query, column, collection_name, layer_name):
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

        table_identifier = layer_table_identifier(self, collection_name, layer_name)
        or_parts = []
        for and_term in or_terms:
            arr = ",".join("'%s'" % v for v in and_term)
            p = SQL("{table}.{column} @> ARRAY[%s]" % arr).format(
                table=table_identifier,
                column=Identifier(column))
            or_parts.append(p)
        column_ngram_query = SQL("({})").format(SQL(" OR ").join(or_parts))
        return column_ngram_query

    @staticmethod
    def find_fingerprint(collection, query=None, layer_query=None, layer_ngram_query=None, layers=None,
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

        return collection.select(query=jsonb_text_query, layer_query=jsonb_layer_query,
                                 layer_ngram_query=layer_ngram_query, layers=layers, order_by_key=order_by_key)

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
