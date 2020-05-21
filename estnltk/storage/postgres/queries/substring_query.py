from psycopg2.sql import SQL, Literal

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query


class SubstringQuery(Query):
    """Constructs database query to search text objects that contain given substring in the raw text.

    """
    __slots__ = ['substring']

    def __init__(self, substring):
        self.substring = substring

    def eval(self, storage, collection_name):
        table = collection_table_identifier(storage, collection_name)

        pat = SQL("position({substring} in {table}.data->>'text')>0")

        return pat.format(table=table, substring=Literal(self.substring))