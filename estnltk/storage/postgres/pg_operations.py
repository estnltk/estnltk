from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.storage.postgres import structure_table_name
from estnltk.storage.postgres import collection_table_name
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import fragment_table_name

pytype2dbtype = {
    "int": "integer",
    "bigint": "bigint",
    "float": "double precision",
    "str": "text",
    'datetime': 'timestamp'
}


def create_schema(storage):
    storage.conn.commit()
    with storage.conn.cursor() as c:
        c.execute(SQL("CREATE SCHEMA {};").format(Identifier(storage.schema)))
    storage.conn.commit()


def delete_schema(storage):
    storage.conn.commit()
    with storage.conn.cursor() as c:
        c.execute(SQL("DROP SCHEMA {} CASCADE;").format(Identifier(storage.schema)))
    storage.conn.commit()


def table_identifier(storage, table_name):
    identifier = Identifier(table_name)
    if storage.temporary:
        return identifier
    return SQL('{}.{}').format(Identifier(storage.schema), identifier)


def table_exists(storage, table_name):
    if storage.temporary:
        raise NotImplementedError("don't know how to check existence of temporary table: {!r}".format(table_name))

    storage.conn.commit()
    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = {} AND tablename = {});"
                      ).format(Literal(storage.schema), Literal(table_name))
                  )
        return c.fetchone()[0]


def get_all_table_names(storage):
    if storage.closed():
        return None
    with storage.conn.cursor() as c:
        c.execute(SQL(
            "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'"),
            [storage.schema])
        table_names = [row[0] for row in c.fetchall()]
        return table_names


def get_all_tables(storage):
    if storage.closed():
        return None
    with storage.conn.cursor() as c:
        sql = SQL(
            "SELECT table_name, "
            "pg_size_pretty(pg_total_relation_size({schema}||'.'||table_name)), "
            "obj_description(({schema}||'.'||table_name)::regclass), "
            "S.n_live_tup "
            "FROM information_schema.tables "
            "LEFT JOIN pg_stat_user_tables S ON S.relname = table_name AND S.schemaname = table_schema "
            "WHERE table_schema={schema} AND table_type='BASE TABLE';").format(schema=Literal(storage.schema))
        logger.debug(sql.as_string(context=storage.conn))
        c.execute(sql)
        tables = {row[0]: {'total_size': row[1], 'comment': row[2], 'rows': row[3]} for row in c}
        return tables


def drop_table(storage, table_name: str, cascade: bool = False):
    if cascade:
        sql = SQL('DROP TABLE {} CASCADE;')
    else:
        sql = SQL('DROP TABLE {};')

    with storage.conn.cursor() as c:
        try:
            c.execute(sql.format(table_identifier(storage, table_name)))
        except Exception:
            raise
        finally:
            storage.conn.commit()
            logger.debug(c.query.decode())


def count_rows(storage, table=None, table_identifier=None):
    if table_identifier is not None:
        with storage.conn.cursor() as c:
            c.execute(SQL("SELECT count(*) FROM {}").format(table_identifier))
            return c.fetchone()[0]
    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT count(*) FROM {}.{}").format(Identifier(storage.schema), Identifier(table)))
        nrows = c.fetchone()[0]
        return nrows


def collection_table_identifier(storage, collection_name):
    table_name = collection_table_name(collection_name)
    return table_identifier(storage, table_name)


def structure_table_identifier(storage, collection_name):
    table_name = structure_table_name(collection_name)
    return table_identifier(storage, table_name)


def layer_table_identifier(storage, collection_name, layer_name):
    table_name = layer_table_name(collection_name, layer_name)
    return table_identifier(storage, table_name)


def fragment_table_identifier(storage, collection_name, fragment_name):
    table_name = fragment_table_name(collection_name, fragment_name)
    return table_identifier(storage, table_name)


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
    table = collection_table_identifier(storage, table_name)

    storage.conn.commit()
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


def fragment_table_exists(storage, collection_name, fragment_name):
    return table_exists(storage, fragment_table_name(collection_name, fragment_name))


def layer_table_exists(storage, collection_name, layer_name):
    return table_exists(storage, layer_table_name(collection_name, layer_name))


def collection_table_exists(storage, collection_name):
    table_name = collection_table_name(collection_name)
    return table_exists(storage, table_name)


def structure_table_exists(storage, collection_name):
    table_name = structure_table_name(collection_name)
    return table_exists(storage, table_name)


def drop_collection_table(storage, collection_name, cascade: bool = False):
    table_name = collection_table_name(collection_name)
    drop_table(storage, table_name, cascade=cascade)


def drop_structure_table(storage, collection_name):
    table_name = structure_table_name(collection_name)
    drop_table(storage, table_name)


def drop_layer_table(storage, collection_name, layer_name, cascade=False):
    table_name = layer_table_name(collection_name, layer_name)
    drop_table(storage, table_name, cascade=cascade)


def drop_fragment_table(storage, collection_name, fragment_name):
    table_name = fragment_table_name(collection_name, fragment_name)
    if not table_exists(storage, table_name):
        raise Exception("Fragment table '%s' does not exist." % table_name)
    drop_table(storage, table_name)
