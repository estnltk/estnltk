from typing import Sequence
from tqdm import tqdm, tqdm_notebook

from estnltk.storage import postgres as pg


class PgSubCollection:
    def __init__(self, collection, query=None, layer_query=None, layer_ngram_query=None, layers=None, keys=None,
                 order_by_key=True, collection_meta: bool = None, progressbar=None, missing_layer: str = None):
        self.collection = collection
        self.query = query
        self.layer_query = layer_query
        self.layer_ngram_query = layer_ngram_query
        self.default_layers = layers
        self.keys = keys
        self.order_by_key = order_by_key
        self.collection_meta = collection_meta
        self.progressbar = progressbar
        self.missing_layer = missing_layer

    def __iter__(self):
        yield from self.select(layers=self.default_layers)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.select(layers=[item])
        if isinstance(item, tuple):
            if not all(isinstance(i, str) for i in item):
                raise KeyError(item)
            return self.select(layers=item)
        if item == slice(None, None, None):
            all_layers = self.collection.get_layer_names()
            return self.select(layers=all_layers)
        if item == []:
            return self.select(layers=item)

        raise KeyError(item)

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

    def select(self, layers):
        if not self.collection.exists():
            raise pg.PgCollectionException('collection does not exist')
        layers_extended = []

        def include_dep(layer):
            if layer is None or not self.collection.structure[layer]['detached']:
                return
            for dep in (self.collection.structure[layer]['parent'], self.collection.structure[layer]['enveloping']):
                include_dep(dep)
            if layer not in layers_extended:
                layers_extended.append(layer)

        for layer in layers or []:
            if layer not in self.collection.structure:
                raise pg.PgCollectionException('there is no layer {!r} in the collection {!r}'.format(
                        layer, self.collection.name))
            include_dep(layer)

        def data_iterator():
            for row in pg.select_raw(storage=self.collection.storage,
                                     collection_name=self.collection.name,
                                     query=self.query,
                                     layer_query=self.layer_query,
                                     layer_ngram_query=self.layer_ngram_query,
                                     layers=layers_extended,
                                     keys=self.keys,
                                     order_by_key=self.order_by_key,
                                     collection_meta=self.collection_meta,
                                     missing_layer=self.missing_layer):
                text_id, text, meta_list, detached_layers = row
                for layer_name in layers_extended:
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


def find_examples(collection, layer, attributes, output_layers=None, return_text=False, return_count=False, **kwargs):
    """Find examples for attribute value tuples in the collection.

    collection: PgCollection
        instance of the EstNLTK PostgreSQL collection
    layer: str
        layer name
    attributes: Sequence[str]
        attribute names which values are extracted for the examples
    output_layers: Sequence[str]
        names of the layers that are attached to the Text object if return_text is True
    return_count: bool
        return number of occurrences in the collection for each example
    :returns
        Tuple(example, key, span_pos, text, count) where
        example is a tuple of attribute values that correspond to attributes parameter
        key is the collection id of the Text object
        span_pos is the index of the span in the Text object
        text is the Text object returned if return_text is True
        count is the number occurrences of the example in the collection returned if return_count is True
    """
    if not return_text:
        output_layers = None
    if output_layers is None:
        output_layers = [layer]
    elif layer not in output_layers:
        output_layers.append(layer)

    if return_count:
        raise NotImplementedError('return_count=True not yet implemented')
    else:
        examples = set()
        for key, text in collection.select(layers=output_layers, **kwargs):
            for span_pos, span in enumerate(text[layer]):
                for annotation in span.annotations:
                    example = tuple(getattr(annotation, attr) for attr in attributes)
                    if example not in examples:
                        examples.add(example)
                        if return_text:
                            yield example, key, span_pos, text
                        else:
                            yield example, key, span_pos


def filter_fragmets(collection, fragmented_layer: str, ngram_query, filter):
    """

    :param fragments:
    :param ngram_query:
    :param filter:
        filter ja ngram_query on alternatiivsed ?
    :return:
    fragments
    """
    pass
