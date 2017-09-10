import json

import psycopg2
from psycopg2.extensions import STATUS_BEGIN
from psycopg2.sql import SQL, Identifier

from estnltk.converters import import_dict, export_json
from .query import Query


class PostgresStorage:
    """`PostgresStorage` instance wraps a database connection and
    exposes interface to conveniently search/save json data.
    """

    def __init__(self, dbname, user, password, host='localhost', port=5432, **kwargs):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, **kwargs)
        self.conn.autocommit = True

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

    def select_by_key(self, table, key, return_as_dict=False):
        """Loads text object by `key`. If `return_as_dict` is True, returns a text object as dict"""
        with self.conn.cursor() as c:
            c.execute(SQL("SELECT * FROM {} WHERE id = %s").format(Identifier(table)), (key,))
            key, text_dict = c.fetchone()
            text = text_dict if return_as_dict is True else import_dict(text_dict)
            return text

    def select(self, table, query=None, order_by_key=False, return_as_dict=False):
        """
        :param table:
        :param return_as_dict:
        :param query:
        :param order_by_key:
        :return:
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
