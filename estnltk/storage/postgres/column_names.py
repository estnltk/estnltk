from psycopg2.sql import Composed, SQL, Identifier


class ColumnsSQL(Composed):
    """Stores comma separated Composable of SQL table qualified column names"""
    def __init__(self, table_identifier, main_columns, meta_columns):
        columns = main_columns + meta_columns
        columns = SQL(', ').join(SQL('{}.{}').format(table_identifier, Identifier(column)) for column in columns)
        super().__init__(columns)

    def __add__(self, other):
        return SQL(', ').join((self, other))


def collection_columns(collection_table_identifier, meta_columns):
    return ColumnsSQL(collection_table_identifier, ['id', 'data'], meta_columns)


def layer_columns(layer_table_identifier, meta_columns):
    return ColumnsSQL(layer_table_identifier, ['id', 'text_id', 'data'], meta_columns)
