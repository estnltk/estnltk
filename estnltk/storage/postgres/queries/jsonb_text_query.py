import json
from psycopg2.sql import SQL, Identifier
from typing import Set

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres.queries.query import Query


class JsonbTextQuery(Query):
    """Constructs database query to search `text` objects stored in jsonb format.
       Search conditions only apply on attached layers of `text` objects.
       
       Example. Search lemmas "mis" OR "palju":
       
       q = JsonbTextQuery('morph_analysis', lemma='mis') | \
           JsonbTextQuery('morph_analysis', lemma='palju')
       collection.select( query=q )
       
    """
    __slots__ = ['layer_name', 'kwargs']

    def __init__(self, layer_name, ambiguous=True, **kwargs):
        if not kwargs:
            raise ValueError('At least one layer attribute is required.')
        self.layer_name = layer_name
        self.kwargs = kwargs

    @property
    def required_layers(self) -> Set[str]:
        return set()

    def eval(self, storage, collection_name):
        table = collection_table_identifier(storage, collection_name)
        pat = SQL("""{table}."data"->'layers' @> '[{{"name": {layer}, "spans": [{{"annotations": [{condition}]}}]}}]'""")

        return pat.format(table=table, layer=Identifier(self.layer_name), condition=SQL(json.dumps(self.kwargs)))
