from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import STATUS_BEGIN, TRANSACTION_STATUS_INERROR

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
    assert storage.conn.autocommit == False
    with storage.conn.cursor() as c:
        try:
            c.execute(SQL("CREATE SCHEMA {};").format(Identifier(storage.schema)))
        except:
            storage.conn.rollback()
            raise
        finally:
            if storage.conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                storage.conn.commit()

def schema_exists(storage, omit_commit: bool=False):
    return_value = False
    with storage.conn.cursor() as c:
        c.execute(SQL('SELECT EXISTS (SELECT 1 from information_schema.schemata '
                      'WHERE schema_name={}) ').format(Literal(storage.schema)))
        return_value = c.fetchone()[0]
    if not omit_commit:
        # make a commit to avoid 'idle in transaction' status
        storage.conn.commit()
    return return_value

def delete_schema(storage):
    assert storage.conn.autocommit == False
    with storage.conn.cursor() as c:
        try:
            c.execute(SQL("DROP SCHEMA {} CASCADE;").format(Identifier(storage.schema)))
        except:
            storage.conn.rollback()
            raise
        finally:
            if storage.conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                storage.conn.commit()

def table_identifier(storage, table_name):
    identifier = Identifier(table_name)
    if storage.temporary:
        return identifier
    return SQL('{}.{}').format(Identifier(storage.schema), identifier)


def table_exists(storage, table_name, omit_commit: bool=False, omit_rollback: bool=False):
    if storage.temporary:
        raise NotImplementedError("don't know how to check existence of temporary table: {!r}".format(table_name))
    if not omit_rollback:
        if storage.conn.info.transaction_status == TRANSACTION_STATUS_INERROR:
            # rollback an aborted transaction, so that a new one can be started. 
            # this removes "psycopg2.errors.InFailedSqlTransaction: current transaction 
            # is aborted, commands ignored until end of transaction block"
            storage.conn.rollback()
    return_value = False
    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = {} AND tablename = {});"
                      ).format(Literal(storage.schema), Literal(table_name))
                  )
        return_value = c.fetchone()[0]
    if not omit_commit:
        # make a commit to avoid 'idle in transaction' status
        storage.conn.commit()
    return return_value


def get_all_table_names(storage, omit_commit: bool=False):
    if storage.closed():
        return None
    table_names = []
    with storage.conn.cursor() as c:
        c.execute(SQL(
            "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'"),
            [storage.schema])
        table_names = [row[0] for row in c.fetchall()]
    if not omit_commit:
        # make a commit to avoid 'idle in transaction' status
        storage.conn.commit()
    return table_names


def get_all_tables(storage, omit_commit: bool=False):
    if storage.closed():
        return None
    tables = []
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
    if not omit_commit:
        # make a commit to avoid 'idle in transaction' status
        storage.conn.commit()
    return tables


def drop_table(storage, table_name: str, cascade: bool = False):
    assert storage.conn.autocommit == False
    if cascade:
        sql = SQL('DROP TABLE {} CASCADE;')
    else:
        sql = SQL('DROP TABLE {};')
    with storage.conn.cursor() as c:
        try:
            c.execute(sql.format(table_identifier(storage, table_name)))
        except Exception:
            storage.conn.rollback()
            raise
        finally:
            if storage.conn.status == STATUS_BEGIN:
                # no exception, transaction in progress
                storage.conn.commit()
                logger.debug(c.query.decode())


def is_empty(storage, table=None, table_identifier=None):
    # An optimized function to quickly find out if a collection / table is empty
    # (should work relatively fast even on large tables)
    with storage.conn:
        if table_identifier is not None:
            with storage.conn.cursor() as c:
                c.execute(SQL("SELECT NOT EXISTS (SELECT 1 FROM {} LIMIT 1)").format(table_identifier))
                return c.fetchone()[0]
        with storage.conn.cursor() as c:
            c.execute(SQL("SELECT NOT EXISTS (SELECT 1 FROM {}.{} LIMIT 1)").format(Identifier(storage.schema), Identifier(table)))
            return c.fetchone()[0]


def count_rows(storage, table=None, table_identifier=None):
    # Convenient way of using connections and cursors as context managers:
    # https://www.psycopg.org/docs/usage.html#with-statement
    with storage.conn:
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


def layer_table_identifier(storage, collection_name, layer_name, layer_type='detached'):
    if layer_type=='detached':
        return table_identifier(storage, layer_table_name(collection_name, layer_name))
    elif layer_type=='fragmented':
        return table_identifier(storage, fragment_table_name(collection_name, layer_name))
    else:
        error_msg = \
          "(!) layer_table_identifier not implemented for layer type: {!r}".format(layer_type)
        raise NotImplementedError( error_msg )


def create_collection_table(storage, collection_name, meta_columns=None, description=None):
    """Creates a new table to store jsonb data:

        CREATE TABLE table(
            id serial PRIMARY KEY,
            data jsonb
        );

    and automatically adds a GIN index for the jsonb column:

        CREATE INDEX idx_table_data ON table USING gin ((data -> 'layers') jsonb_path_ops);
        
    The types for meta columns can be int, bigint, float, str and datetime. For more information consult the source code. 
    """
    assert storage.conn.autocommit == False

    columns = [SQL('id BIGSERIAL PRIMARY KEY'),
               SQL('data jsonb')]
    if meta_columns is not None:
        for col_name, col_type in meta_columns.items():
            columns.append(SQL('{} {}').format(Identifier(col_name), SQL(pytype2dbtype[col_type])))

    temp = SQL('TEMPORARY') if storage.temporary else SQL('')
    table_name = collection_table_name(collection_name)
    table = collection_table_identifier(storage, table_name)

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


def layer_table_exists(storage, collection_name, layer_name, layer_type='detached', omit_commit: bool=False, omit_rollback: bool=False):
    if layer_type=='detached':
        return table_exists(storage, layer_table_name(collection_name, layer_name), omit_commit=omit_commit, omit_rollback=omit_rollback)
    elif layer_type=='fragmented':
        return table_exists(storage, fragment_table_name(collection_name, layer_name), omit_commit=omit_commit, omit_rollback=omit_rollback)
    else:
        error_msg = \
          "(!) Checking table's existence not implemented for layer type: {!r}".format(layer_type)
        raise NotImplementedError( error_msg )


def collection_table_exists(storage, collection_name, omit_commit: bool=False, omit_rollback: bool=False):
    table_name = collection_table_name(collection_name)
    return table_exists(storage, table_name, omit_commit=omit_commit, omit_rollback=omit_rollback)


def structure_table_exists(storage, collection_name, omit_commit: bool=False, omit_rollback: bool=False):
    table_name = structure_table_name(collection_name)
    return table_exists(storage, table_name, omit_commit=omit_commit, omit_rollback=omit_rollback)


def drop_collection_table(storage, collection_name, cascade: bool = False):
    table_name = collection_table_name(collection_name)
    drop_table(storage, table_name, cascade=cascade)


def drop_structure_table(storage, collection_name):
    table_name = structure_table_name(collection_name)
    drop_table(storage, table_name)


def drop_layer_table(storage, collection_name, layer_name, cascade=False, layer_type='detached'):
    if layer_type=='detached':
        table_name = layer_table_name(collection_name, layer_name)
        drop_table(storage, table_name, cascade=cascade)
    elif layer_type=='fragmented':
        table_name = fragment_table_name(collection_name, layer_name)
        drop_table(storage, table_name, cascade=cascade)
    else:
        error_msg = \
          "(!) Removing layer table not implemented for layer type: {!r}".format(layer_type)
        raise NotImplementedError( error_msg )


def drop_all_storage_tables(storage):
    # Delete the whole storage, including dependent tables
    for collection in storage.collections[:]:
        storage.delete_collection(collection, cascade=True)
    drop_table(storage, '__collections')