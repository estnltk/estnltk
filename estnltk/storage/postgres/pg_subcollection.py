from typing import Sequence
from tqdm import tqdm, tqdm_notebook

from estnltk.storage import postgres as pg


class PgSubCollection:
    def __init__(self, collection, layers=None, collection_meta=None, order_by_key=True, progressbar=None,
                 where_clause=None, selected_columns=None):
        self.collection = collection
        self.default_layers = layers
        self.collection_meta = collection_meta
        self.order_by_key = order_by_key
        self.progressbar = progressbar
        self._where_clause = where_clause
        self._selected_columns = selected_columns

    def select(self, query=None, layer_query=None, layer_ngram_query=None, keys=None, missing_layer: str = None):
        layers_extended = []

        def include_dep(layer):
            if layer is None:
                return
            for dep in (self.collection.structure[layer]['parent'], self.collection.structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in self.default_layers or []:
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
                               layers=self.default_layers,
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

        for layer in self.default_layers or []:
            if layer not in self.collection.structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                        layer, self.collection.name))
            include_dep(layer)

        attached_layer_names = [layer for layer in layers_extended if not self.collection.structure[layer]['detached']]
        detached_layer_names = [layer for layer in layers_extended if self.collection.structure[layer]['detached']]

        def data_iterator():
            for row in pg.select_raw(collection=self.collection,
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
