from typing import Sequence
from psycopg2.sql import Composed, Identifier, SQL

from estnltk.storage import postgres as pg


class SelectedColumns(Composed):
    def __init__(self,
                 collection: pg.PgCollection,
                 layers: Sequence[str] = (),
                 collection_meta: Sequence[str] = (),
                 include_layer_ids: bool = True):

        self._layers = layers

        storage = collection.storage
        collection_name = collection.name

        collection_identifier = pg.collection_table_identifier(storage, collection_name)

        # List columns of main collection table.
        selected_columns = [SQL('{}.{}').format(collection_identifier, column_id) for
                            column_id in map(Identifier, ['id', 'data', *collection_meta])]

        # List columns of selected layers.
        for layer in layers:
            if include_layer_ids:
                selected_columns.append(SQL('{}."id"').format(pg.layer_table_identifier(storage, collection_name, layer)))
            selected_columns.append(SQL('{}."data"').format(pg.layer_table_identifier(storage, collection_name, layer)))

        super().__init__(selected_columns)

    @property
    def required_layers(self):
        return self._layers
