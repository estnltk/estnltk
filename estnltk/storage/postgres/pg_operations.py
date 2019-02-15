from itertools import chain
from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import STATUS_BEGIN

from estnltk import logger
from estnltk.converters import dict_to_text
from estnltk.converters import dict_to_layer
from estnltk.storage.postgres import structure_table_name
from estnltk.storage.postgres import collection_table_name
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import fragment_table_name


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
    storage.conn.commit()


def table_identifier(storage, table_name):
    identifier = Identifier(table_name)
    if storage.temporary:
        return identifier
    return SQL('{}.{}').format(Identifier(storage.schema), identifier)


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


def drop_fragment_table(storage, collection_name, fragment_name):
    table_name = fragment_table_name(collection_name, fragment_name)
    if not table_exists(storage, table_name):
        raise Exception("Fragment table '%s' does not exist." % table_name)
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


def build_column_ngram_query(storage, query, column, collection_name, layer_name):
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


def build_layer_ngram_query(storage, ngram_query, collection_name):
    sql_parts = []
    for layer_name in ngram_query:
        for column, q in ngram_query[layer_name].items():
            col_query = build_column_ngram_query(storage, q, column, collection_name, layer_name)
            sql_parts.append(col_query)
    q = SQL(" AND ").join(sql_parts)
    return q


def where_clause(storage,
                 collection_name,
                 query=None,
                 layer_query: dict = None,
                 layer_ngram_query: dict = None,
                 keys: list = None,
                 missing_layer: str = None):
    sql_parts = []

    if query is not None:
        # build constraint on the main text table
        sql_parts.append(query.eval(storage, collection_name))
    if layer_query:
        # build constraint on related layer tables
        q = SQL(" AND ").join(query.eval(storage, collection_name) for layer, query in layer_query.items())
        sql_parts.append(q)
    if keys is not None:
        # build constraint on id-s
        sql_parts.append(SQL('{table}."id" = ANY({keys})').format(
                             table=collection_table_identifier(storage, collection_name),
                             keys=Literal(list(keys))))
    if layer_ngram_query:
        # build constraint on related layer's ngram index
        sql_parts.append(build_layer_ngram_query(storage, layer_ngram_query, collection_name))
    if missing_layer:
        # select collection objects for which there is no entry in the layer table
        q = SQL('"id" NOT IN (SELECT "text_id" FROM {})'
                ).format(layer_table_identifier(storage, collection_name, missing_layer))
        sql_parts.append(q)

    if sql_parts:
        return SQL(" AND ").join(sql_parts)


def build_sql_query(storage,
                    collection_name,
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

    collection_identifier = collection_table_identifier(storage, collection_name)
    collection_meta = collection_meta or []
    collection_columns = [SQL('{}.{}').format(collection_identifier, column_id) for
                          column_id in map(Identifier, ['id', 'data', *collection_meta])]
    if not layers and layer_query is None and layer_ngram_query is None:
        # select only text table
        select = SQL("SELECT {} FROM {}").format(SQL(', ').join(collection_columns), collection_identifier)
        where_and = SQL('WHERE')
    else:
        # need to join text and all layer tables
        layers = layers or []
        layer_query = layer_query or {}
        layer_ngram_query = layer_ngram_query or {}

        layer_columns = []
        for layer in chain(layers):
            layer_columns.append(SQL('{}."id"').format(layer_table_identifier(storage, collection_name, layer)))
            layer_columns.append(SQL('{}."data"').format(layer_table_identifier(storage, collection_name, layer)))

        layers_join = []
        for layer in sorted(set(chain(layers, layer_query.keys(), layer_ngram_query.keys()))):
            layer = SQL("{}").format(layer_table_identifier(storage, collection_name, layer))
            layers_join.append(layer)

        select = SQL('SELECT {columns} FROM {tables} WHERE {condition}').format(
                     columns=SQL(', ').join(collection_columns + layer_columns),
                     tables=SQL(", ").join([collection_identifier, *layers_join]),
                     condition=SQL(" AND ").join(SQL('{}."id" = {}."text_id"').format(
                                                     collection_identifier, layer)
                                                 for layer in layers_join))
        where_and = SQL('AND')

    where = where_clause(storage=storage,
                         collection_name=collection_name,
                         query=query,
                         layer_query=layer_query,
                         layer_ngram_query=layer_ngram_query,
                         keys=keys,
                         missing_layer=missing_layer)
    if where:
        sql_parts = [select, where_and, where]
    else:
        sql_parts = [select]

    if order_by_key is True:
        sql_parts.append(SQL('ORDER BY "id"'))

    sql_parts.append(SQL(';'))

    return SQL(" ").join(sql_parts)


def select_raw(storage,
               collection_name,
               query=None,
               layer_query: dict = None,
               layer_ngram_query: dict = None,
               attached_layers=None,
               detached_layers=None,
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

    collection_meta = collection_meta or []

    sql = build_sql_query(storage,
                          collection_name,
                          query=query,
                          layer_query=layer_query,
                          layer_ngram_query=layer_ngram_query,
                          layers=detached_layers,
                          keys=keys,
                          order_by_key=order_by_key,
                          collection_meta=collection_meta,
                          missing_layer=missing_layer)

    with storage.conn.cursor('read', withhold=True) as c:
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
