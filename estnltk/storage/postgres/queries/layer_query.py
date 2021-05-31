import json
from psycopg2.sql import SQL, Identifier
from typing import Set

from estnltk.storage.postgres import collection_table_identifier
from estnltk.storage.postgres import layer_table_identifier
from estnltk.storage.postgres.queries.query import Query


class LayerQuery(Query):
    """Constructs database query to search `layer` objects stored in jsonb format.
       Can be used to search both attached layers and detached layers.
       
       Example. Search lemmas "mis" OR "palju":
       
       q = LayerQuery('morph_analysis', lemma='mis') | \
           LayerQuery('morph_analysis', lemma='palju')
       collection.select( query=q )
       
    """
    __slots__ = ['layer_name', 'kwargs']

    def __init__(self, layer_name, **kwargs):
        if not kwargs:
            raise ValueError('At least one layer attribute is required.')
        self.layer_name = layer_name
        self.kwargs = kwargs

    @property
    def required_layers(self) -> Set[str]:
        return {self.layer_name}

    def eval(self, collection: 'PgCollection'):
        collection_name = collection.name
        storage = collection.storage
        # Check for the existence of the layer
        if not collection.has_layer( self.layer_name ):
            raise ValueError('Collection {!r} does not have the layer {!r}'.format(collection_name, self.layer_name))
        is_attached = (collection.structure[self.layer_name]['layer_type'] == 'attached')
        if is_attached:
            # attached layer
            table = collection_table_identifier(storage, collection_name)
            pat = SQL("""{table}."data"->'layers' @> '[{{"name": {layer}, "spans": [{{"annotations": [{condition}]}}]}}]'""")
            return pat.format(table=table, layer=Identifier(self.layer_name), condition=SQL(json.dumps(self.kwargs)))
        else:
            # detached layer
            table = layer_table_identifier(storage, collection_name, self.layer_name)
            pat = SQL("""{table}.data @> '{{"spans": [{{"annotations": [{condition}]}}]}}'""")
            return pat.format(table=table, condition=SQL(json.dumps(self.kwargs)))
