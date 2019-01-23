import json
from psycopg2.sql import SQL, Identifier

from estnltk.storage.postgres import collection_table_identifier
from .query import Query


class JsonbTextQuery(Query):
    """
    Constructs database query to search `text` objects stored in jsonb format.
    """

    def __init__(self, layer, ambiguous=True, **kwargs):
        if not kwargs:
            raise ValueError('At least one layer attribute is required.')
        self.layer = layer
        self.ambiguous = ambiguous
        self.kwargs = kwargs

    def eval(self, storage, collection_name):
        table = collection_table_identifier(storage, collection_name)
        if self.ambiguous is True:
            pat = SQL("""{table}."data"->'layers' @> '[{{"name": {layer}, "spans": [[{condition}]]}}]'""")
        else:
            pat = SQL("""{table}."data"->'layers' @> '[{{"name": {layer}, "spans": [{condition}]}}]'""")

        return pat.format(table=table, layer=Identifier(self.layer), condition=SQL(json.dumps(self.kwargs)))
