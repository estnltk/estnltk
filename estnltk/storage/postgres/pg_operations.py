from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from .sql_strings import structure_table_name, collection_table_name, layer_table_name


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


def table_identifier(storage, table_name):
    identifier = Identifier(table_name)
    if storage.temporary:
        return identifier
    return SQL('{}.{}').format(Identifier(storage.schema), identifier)


def create_structure_table(storage, collection_name):
    table = table_identifier(storage, structure_table_name(collection_name))
    temporary = SQL('TEMPORARY') if storage.temporary else SQL('')
    with storage.conn.cursor() as c:
        c.execute(SQL('CREATE {temporary} TABLE {table} ('
                      'layer_name text primary key, '
                      'detached bool not null, '
                      'attributes text[] not null, '
                      'ambiguous bool not null, '
                      'parent text, '
                      'enveloping text, '
                      '_base text, '
                      'meta text[]);').format(temporary=temporary,
                                              table=table))
        logger.debug(c.query.decode())


def create_collection_table(storage, collection_name, meta_columns=None, description=None):
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
    if meta_columns is not None:
        for col_name, col_type in meta_columns.items():
            columns.append(SQL('{} {}').format(Identifier(col_name), SQL(pytype2dbtype[col_type])))

    temp = SQL('TEMPORARY') if storage.temporary else SQL('')
    table_name = collection_table_name(collection_name)
    table = table_identifier(storage, table_name)

    storage.conn.autocommit = False
    with storage.conn.cursor() as c:
        try:
            c.execute(SQL("CREATE {} TABLE {} ({});").format(
                temp, table, SQL(', ').join(columns)))
            logger.debug(c.query.decode())
            c.execute(
                SQL("CREATE INDEX {index} ON {table} USING gin ((data->'layers') jsonb_path_ops);").format(
                    index=Identifier('idx_%s_data' % table_name),
                    table=table))
            logger.debug(c.query.decode())
            if isinstance(description, str):
                c.execute(SQL("COMMENT ON TABLE {} IS {}").format(
                    table, Literal(description)))
                logger.debug(c.query.decode())
        except:
            storage.conn.rollback()
            raise
        finally:
            if storage.conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                storage.conn.commit()
            storage.conn.autocommit = True


def table_exists(storage, table_name):
    if storage.temporary:
        raise NotImplementedError("don't know how to check existence of temporary table: {!r}".format(table_name))

    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = {} AND tablename = {});"
                      ).format(Literal(storage.schema), Literal(table_name))
                  )
        return c.fetchone()[0]


def collection_table_exists(storage, collection_name):
    table_name = collection_table_name(collection_name)
    return table_exists(storage, table_name)


def structure_table_exists(storage, collection_name):
    table_name = structure_table_name(collection_name)
    return table_exists(storage, table_name)


def drop_table(storage, table_name):
    with storage.conn.cursor() as c:
        c.execute(SQL('DROP TABLE {};').format(table_identifier(storage, table_name)))
        logger.debug(c.query.decode())


def drop_collection_table(storage, collection_name):
    table_name = collection_table_name(collection_name)
    drop_table(storage, table_name)


def drop_structure_table(storage, collection_name):
    table_name = structure_table_name(collection_name)
    drop_table(storage, table_name)


def drop_layer_table(storage, collection_name, layer_name):
    table_name = layer_table_name(collection_name, layer_name)
    drop_table(storage, table_name)


def count_rows(storage, table=None, table_identifier=None):
    if table_identifier is not None:
        with storage.conn.cursor() as c:
            c.execute(SQL("SELECT count(*) FROM {}").format(table_identifier))
            return c.fetchone()[0]
    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT count(*) FROM {}.{}").format(Identifier(storage.schema), Identifier(table)))
        nrows = c.fetchone()[0]
        return nrows
