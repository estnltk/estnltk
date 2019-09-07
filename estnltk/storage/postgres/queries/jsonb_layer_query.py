import json
from psycopg2.sql import SQL

from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres.queries.query import Query


class JsonbLayerQuery(Query):
    """Constructs database query to search `layer` objects stored in jsonb format.

    """
    __slots__ = ['layer_name', 'kwargs']

    def __init__(self, layer_name, ambiguous=True, **kwargs):
        if not kwargs:
            raise ValueError('At least one layer attribute is required.')
        self.layer_name = layer_name
        self.kwargs = kwargs

    def eval(self, storage, collection_name):
        table = layer_table_identifier(storage, collection_name, self.layer_name)
        pat = SQL("""{table}.data @> '{{"spans": [{{"annotations": [{condition}]}}]}}'""")

        return pat.format(table=table, condition=SQL(json.dumps(self.kwargs)))
