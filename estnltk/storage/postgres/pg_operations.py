from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.converters import dict_to_text
from estnltk.converters import dict_to_layer
from estnltk.storage.postgres import structure_table_name
from estnltk.storage.postgres import collection_table_name
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import fragment_table_name
from estnltk.storage import postgres as pg


pytype2dbtype = {
    "int": "integer",
    "bigint": "bigint",
    "float": "double precision",
    "str": "text"
}


# PostgresStorage operations #


def create_schema(storage):
    with storage.conn.cursor() as c:
        c.execute(SQL("CREATE SCHEMA {};").format(Identifier(storage.schema)))


def delete_schema(storage):
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

    with storage.conn.cursor() as c:
        c.execute(SQL("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = {} AND tablename = {});"
                      ).format(Literal(storage.schema), Literal(table_name))
                  )
        return c.fetchone()[0]


def drop_table(storage, table_name):
    with storage.conn.cursor() as c:
        c.execute(SQL('DROP TABLE {};').format(table_identifier(storage, table_name)))
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


# PgCollection operations #


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


def drop_collection_table(storage, collection_name):
    table_name = collection_table_name(collection_name)
    drop_table(storage, table_name)


def drop_structure_table(storage, collection_name):
    table_name = structure_table_name(collection_name)
    drop_table(storage, table_name)


def drop_layer_table(storage, collection_name, layer_name):
    table_name = layer_table_name(collection_name, layer_name)
    drop_table(storage, table_name)


def drop_fragment_table(storage, collection_name, fragment_name):
    table_name = fragment_table_name(collection_name, fragment_name)
    if not table_exists(storage, table_name):
        raise Exception("Fragment table '%s' does not exist." % table_name)
    drop_table(storage, table_name)


def build_column_ngram_query(storage, collection_name, query, column, layer_name):
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

    table_identifier = layer_table_identifier(storage, collection_name, layer_name)
    or_parts = []
    for and_term in or_terms:
        arr = ",".join("'%s'" % v for v in and_term)
        p = SQL("{table}.{column} @> ARRAY[%s]" % arr).format(
            table=table_identifier,
            column=Identifier(column))
        or_parts.append(p)
    column_ngram_query = SQL("({})").format(SQL(" OR ").join(or_parts))
    return column_ngram_query


def build_layer_ngram_query(storage, collection_name, ngram_query):
    sql_parts = []
    for layer_name in ngram_query:
        for column, q in ngram_query[layer_name].items():
            col_query = build_column_ngram_query(storage, collection_name, q, column, layer_name)
            sql_parts.append(col_query)
    q = SQL(" AND ").join(sql_parts)
    return q


def build_sql_query(collection,
                    query=None,
                    layer_query: dict = None,
                    layer_ngram_query: dict = None,
                    layers: list = None,
                    keys: list = None,
                    order_by_key: bool = False,
                    collection_meta: list = None,
                    missing_layer: str = None):
    """
    Select from collection table with possible search constraints.
    Args:
        table: str
            collection table
        query: JsonbTextQuery
            collection table query
        layer_query: JsonbLayerQuery
            layer query
        layer_ngram_query: dict
        keys: list
            List of id-s.
        order_by_key: bool
        layers: list
            Layers to fetch. Specified layers will be merged into returned text object and
            become accessible via `text["layer_name"]`.
        collection_meta: list
            list of collection metadata column names
        missing_layer: str
            name of the layer
            select collection objects for which there is no entry in the table `missing_layer`
    Returns:
        iterator of (key, text) pairs
    Example:
        q = JsonbTextQuery('morph_analysis', lemma='laulma')
        for key, txt in storage.select(table, query=q):
            print(key, txt)
    """

    selected_columns = pg.SelectedColumns(collection=collection,
                                          layer_query=layer_query,
                                          layer_ngram_query=layer_ngram_query,
                                          layers=layers,
                                          collection_meta=collection_meta)

    where_clause = pg.WhereClause(collection=collection,
                                  query=query,
                                  layer_query=layer_query,
                                  layer_ngram_query=layer_ngram_query,
                                  keys=keys,
                                  missing_layer=missing_layer)

    sql_parts = [selected_columns + where_clause]

    if order_by_key is True:
        sql_parts.append(SQL('ORDER BY "id"'))

    sql_parts.append(SQL(';'))

    return SQL(' ').join(sql_parts)


def select_raw(collection,
               query=None,
               layer_query: dict = None,
               layer_ngram_query: dict = None,
               attached_layers=None,
               detached_layers=None,
               keys: list = None,
               order_by_key: bool = False,
               collection_meta: list = None,
               missing_layer: str = None,
               selected_columns=None,
               where_clause=None):
    """
    Select from collection table with possible search constraints.

    Args:
        table: str
            collection table
        query: JsonbTextQuery
            collection table query
        layer_query: JsonbLayerQuery
            layer query
        layer_ngram_query: dict
        keys: list
            List of id-s.
        order_by_key: bool
        layers: list
            Layers to fetch. Specified layers will be merged into returned text object and
            become accessible via `text["layer_name"]`.
        collection_meta: list
            list of collection metadata column names
        missing_layer: str
            name of the layer
            select collection objects for which there is no entry in the table `missing_layer`

    Returns:
        iterator of (key, text) pairs

    Example:

        q = JsonbTextQuery('morph_analysis', lemma='laulma')
        for key, txt in storage.select(table, query=q):
            print(key, txt)
    """

    collection_meta = collection_meta or []

    if selected_columns is None and where_clause is None:
        sql = build_sql_query(collection,
                              query=query,
                              layer_query=layer_query,
                              layer_ngram_query=layer_ngram_query,
                              layers=detached_layers,
                              keys=keys,
                              order_by_key=order_by_key,
                              collection_meta=collection_meta,
                              missing_layer=missing_layer)
    else:
        sql_parts = [selected_columns + where_clause]
        if order_by_key is True:
            sql_parts.append(SQL('ORDER BY "id"'))
        sql_parts.append(SQL(';'))
        sql = SQL(' ').join(sql_parts)

    with collection.storage.conn.cursor('read', withhold=True) as c:
        c.execute(sql)
        logger.debug(c.query.decode())
        for row in c:
            text_id = row[0]
            text_dict = row[1]
            text = dict_to_text(text_dict, attached_layers)
            meta = row[2:2+len(collection_meta)]
            detached_layers = {}
            if len(row) > 2 + len(collection_meta):
                for i in range(2 + len(collection_meta), len(row), 2):
                    layer_id = row[i]
                    layer_dict = row[i + 1]
                    layer = dict_to_layer(layer_dict, text, {k: v['layer'] for k, v in detached_layers.items()})
                    detached_layers[layer.name] = {'layer': layer, 'layer_id': layer_id}
            result = text_id, text, meta, detached_layers
            yield result
    c.close()
