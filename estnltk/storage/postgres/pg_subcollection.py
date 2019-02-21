from typing import Sequence
from tqdm import tqdm, tqdm_notebook
from psycopg2.sql import SQL

from estnltk import logger
from estnltk.converters import dict_to_text, dict_to_layer
from estnltk.storage import postgres as pg


class PgSubCollection:
    def __init__(self, collection, layers=None, collection_meta=None, order_by_key=True, progressbar=None,
                 where_clause=None, selected_columns=None, query=None, layer_query=None, layer_ngram_query=None,
                 keys=None, missing_layer=None):
        self.collection = collection
        self.selected_layers = layers or []
        self.collection_meta = collection_meta
        self.order_by_key = order_by_key
        self.progressbar = progressbar
        self._where_clause = where_clause
        self.layer_query = layer_query
        self.layer_ngram_query = layer_ngram_query
        if where_clause is None:
            self._where_clause = pg.WhereClause(collection=self.collection,
                                                query=query,
                                                layer_query=layer_query,
                                                layer_ngram_query=layer_ngram_query,
                                                keys=keys,
                                                missing_layer=missing_layer)
        self.selected_layers = layers or []

        self._selected_columns = selected_columns

    @property
    def selected_layers(self):
        return self._selected_layers

    @selected_layers.setter
    def selected_layers(self, value: list):
        self._selected_layers = self.dependent_layers(value)
        self._detached_layers = [layer for layer in self._selected_layers if self.collection.structure[layer]['detached']]

    @property
    def sql_query(self):
        selected_columns = pg.SelectedColumns(collection=self.collection,
                                              layer_query=self.layer_query,
                                              layer_ngram_query=self.layer_ngram_query,
                                              layers=self._detached_layers,
                                              collection_meta=self.collection_meta)

        sql_parts = [selected_columns + self._where_clause]
        if self.order_by_key is True:
            sql_parts.append(SQL('ORDER BY "id"'))
        sql_parts.append(SQL(';'))
        sql = SQL(' ').join(sql_parts)
        return sql

    def dependent_layers(self, selected_layers):
        """Returns all layers that depend on selected layers including selected layers."""
        layers_extended = []

        # kirjuta ümber vastavalt fotole
        def include_dep(layer):
            if layer is None:
                return
            for dep in (self.collection.structure[layer]['parent'], self.collection.structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in selected_layers:
            if layer not in self.collection.structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                                               layer, self.collection.name))
            include_dep(layer)

        return layers_extended

    def select(self, query=None, layer_query=None, layer_ngram_query=None, keys=None, missing_layer: str = None):
        layers_extended = []

        def include_dep(layer):
            if layer is None:
                return
            for dep in (self.collection.structure[layer]['parent'], self.collection.structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in self.selected_layers or []:
            if layer not in self.collection.structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                                               layer, self.collection.name))
            include_dep(layer)

        detached_layer_names = [layer for layer in layers_extended if self.collection.structure[layer]['detached']]

        where_clause = pg.WhereClause(collection=self.collection,
                                      query=query,
                                      layer_query=layer_query,
                                      layer_ngram_query=layer_ngram_query,
                                      keys=keys,
                                      missing_layer=missing_layer)

        selected_columns = pg.SelectedColumns(collection=self.collection,
                                              layer_query=layer_query,
                                              layer_ngram_query=layer_ngram_query,
                                              layers=detached_layer_names,
                                              collection_meta=self.collection_meta)

        if self._where_clause is None and self._selected_columns is None:
            self._where_clause = where_clause
            self._selected_columns = selected_columns
            return self

        return PgSubCollection(collection=self.collection,
                               layers=self.selected_layers,
                               collection_meta=self.collection_meta,
                               order_by_key=self.order_by_key,
                               progressbar=self.progressbar,
                               where_clause=where_clause,
                               selected_columns=selected_columns)

    def __iter__(self):
        if not self.collection.exists():
            raise pg.PgCollectionException('collection does not exist')

        layers_extended = []

        def include_dep(layer):
            if layer is None:
                return
            for dep in (self.collection.structure[layer]['parent'], self.collection.structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in self.selected_layers or []:
            if layer not in self.collection.structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                        layer, self.collection.name))
            include_dep(layer)

        attached_layer_names = [layer for layer in layers_extended if not self.collection.structure[layer]['detached']]
        detached_layer_names = [layer for layer in layers_extended if self.collection.structure[layer]['detached']]

        def data_iterator():
            for row in self.select_raw(collection=self.collection,
                                       attached_layers=attached_layer_names,
                                       order_by_key=self.order_by_key,
                                       collection_meta=self.collection_meta,
                                       selected_columns=self._selected_columns,
                                       where_clause=self._where_clause):
                text_id, text, meta_list, detached_layers = row
                for layer_name in detached_layer_names:
                    text[layer_name] = detached_layers[layer_name]['layer']
                if self.collection_meta:
                    meta = {}
                    for meta_name, meta_value in zip(self.collection_meta, meta_list):
                        meta[meta_name] = meta_value
                    yield text_id, text, meta
                else:
                    yield text_id, text

        if self.progressbar not in {'ascii', 'unicode', 'notebook'}:
            yield from data_iterator()
            return

        total = pg.count_rows(self.collection.storage, self.collection.name)
        initial = 0
        if self.missing_layer is not None:
            initial = self.collection.storage.count_rows(
                    table_identifier=pg.layer_table_identifier(self.collection.storage,
                                                               self.collection.name, self.missing_layer))
        if self.progressbar == 'notebook':
            iter_data = tqdm_notebook(data_iterator(),
                                      total=total,
                                      initial=initial,
                                      unit='doc',
                                      smoothing=0)
        else:
            iter_data = tqdm(data_iterator(),
                             total=total,
                             initial=initial,
                             unit='doc',
                             ascii=(self.progressbar == 'ascii'),
                             smoothing=0)
        for data in iter_data:
            iter_data.set_description('collection_id: {}'.format(data[0]), refresh=False)
            yield data

    def all(self):
        layers = self.collection.get_layer_names()
        return self.select(layers=layers)

    def text(self):
        pass

    def layers(self, layers: Sequence[str]):
        return self.select(layers=layers)

    def raw_layer(self):
        pass

    def raw_fragment(self):
        pass

    def select_raw(self,
                   collection,
                   attached_layers=None,
                   order_by_key: bool = False,
                   collection_meta: list = None,
                   selected_columns=None,
                   where_clause=None):
        collection_meta = collection_meta or []

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
