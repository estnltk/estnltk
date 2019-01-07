from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger


pytype2dbtype = {
    "int": "integer",
    "bigint": "bigint",
    "float": "double precision",
    "str": "text"
}


def create_schema(storage):
    with storage.conn.cursor() as c:
        c.execute(SQL("CREATE SCHEMA {};").format(Identifier(storage.schema)))


def delete_schema(storage):
    with storage.conn.cursor() as c:
        c.execute(SQL("DROP SCHEMA {} CASCADE;").format(Identifier(storage.schema)))


def create_table(storage, table, description=None, meta=None, temporary=False, table_identifier=None):
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

    temp = SQL('TEMPORARY') if temporary else SQL('')
    table_identifier = table_identifier or SQL('{}.{}').format(Identifier(storage.schema), Identifier(table))

    storage.conn.autocommit = False
    with storage.conn.cursor() as c:
        try:
            c.execute(SQL("CREATE {} TABLE {} ({});").format(
                temp, table_identifier, SQL(', ').join(columns)))
            logger.debug(c.query.decode())
            c.execute(
                SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops);").format(
                    index=Identifier('idx_%s_data' % table),
                    table=table_identifier))
            logger.debug(c.query.decode())
            if isinstance(description, str):
                c.execute(SQL("COMMENT ON TABLE {} IS {}").format(
                    table_identifier, Literal(description)))
                logger.debug(c.query.decode())
        except:
            storage.conn.rollback()
            raise
        finally:
            if storage.conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                storage.conn.commit()
            storage.conn.autocommit = True


def count_rows(storage, table=None, table_identifier=None):
    if table_identifier is not None:
        with storage.conn.cursor() as c:
            c.execute(SQL("SELECT count(*) FROM {}").format(table_identifier))
            return c.fetchone()[0]
    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT count(*) FROM {}.{}").format(Identifier(storage.schema), Identifier(table)))
        nrows = c.fetchone()[0]
        return nrows


def table_exists(storage, table, schema=None):
    if schema is None:
        schema = storage.schema
    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = %s AND tablename = %s);"),
                  [schema, table])
        return c.fetchone()[0]


def drop_table(storge, table):
    with storge.conn.cursor() as c:
        c.execute(SQL("DROP TABLE {}.{};").format(Identifier(storge.schema), Identifier(table)))
        logger.debug(c.query.decode())


def drop_table_if_exists(storage, table):
    with storage.conn.cursor() as c:
        c.execute(SQL("DROP TABLE IF EXISTS {}.{};").format(Identifier(storage.schema), Identifier(table)))

