from typing import Sequence, List
from psycopg2.sql import SQL
from itertools import chain

from estnltk import logger, Progressbar
from estnltk import Text
from estnltk.converters import serialisation_modules
from estnltk.storage import postgres as pg
from estnltk.converters.layer_dict_converter import layer_converter_collection


class PgSubCollection:
    """
    Wrapper class that provides read-only access to a subset of a collection.

    The subset is specified by a SQL select statement that is determined by
    - the selection criterion
    - the set of selected layers
    - the set of meta attributes

    The main usecase for the class is iteration over its elements.
    It is possible to iterate several times over the subcollection.

    Depending on the configuration attributes, the iterator returns:
    - text objects with selected layers
    - text objects together with their index
    - text objects together with their index and meta fields

    The iteration speed depends on the network and collection parameters:
    - network bandwidth
    - application level ping time
    - average size of a collection element
    - the number of simultaneously fetched elements (itersize)

    The first three parameters determine the minimal time for complete iteration.
    The parameter itersize determines how fast the first iteration is completed:
    - Small itersize leads to small delays as only few elements must be fetched.
    - Small itersize increases overall running time as more queries are performed.
    - The overhead for each query is application-level ping time which is at least 20 msec.
    Exact trade-off is very configuration specific.


    TODO: Complete the description
    Not secure against deleting of the collection

    ISSUES: How one specifies layer meta attributes? Do they come automatically
    retrieving layer meta attributes is not implemented
    """

    def __init__(self, collection: pg.PgCollection, selection_criterion: pg.WhereClause = None,
                 selected_layers: Sequence[str] = None, meta_attributes: Sequence[str] = None,
                 progressbar: str = None, return_index: bool = True, itersize: int = 50):
        """
        :param collection: PgCollection
        :param selection_criterion: WhereClause
        :param selected_layers: Sequence[str]
            names of layers attached to the Text object, dependencies are included automatically
        :param meta_attributes: Sequence[str]
            names of collection meta attributes that yield in dict with text object
        :param progressbar: str, default None
            no progressbar by default
            'ascii', 'unicode' or 'notebook'
        :param return_index: bool
            yield collection id with text objects
        :param itersize: int
            the number of simultaneously fetched elements
        """

        #TODO: Make sure that all objects used by the class are independent copies and cannot be 
        #changed form the outside. This might invalidate invariants 

        self.collection = collection

        if selection_criterion is None:
            # TODO: This is fishy. Check and remove it
            self._selection_criterion = pg.WhereClause(collection=self.collection)
        elif isinstance(selection_criterion, pg.WhereClause):
            self._selection_criterion = selection_criterion
        else:
            raise TypeError('unexpected type of selection_criterion: {!r}'.format(type(selection_criterion)))

        #TODO: Why different default values? Unify
        self.selected_layers = selected_layers or []
        self.meta_attributes = meta_attributes or ()
        self.progressbar = progressbar
        self.return_index = return_index
        self.itersize = itersize

    def __len__(self):
        """
        Executes a SQL query to find the size of the subcollection. The result is not cached.
        """
        with self.collection.storage.conn.cursor() as cur:
            cur.execute(self.sql_count_query)
            logger.debug(cur.query.decode())
            return next(cur)[0]

    @property
    def selected_layers(self):
        return self._selected_layers

    @selected_layers.setter
    def selected_layers(self, layers: list):
        """
        Selects layers together with all layers needed to define them.
        """

        self._selected_layers = self.collection.dependent_layers(layers)
        self._attached_layers = [layer for layer in self._selected_layers
                                 if self.collection.structure[layer]['layer_type'] == 'attached']
        self._detached_layers = [layer for layer in self._selected_layers
                                 if self.collection.structure[layer]['layer_type'] == 'detached']

    @property
    def layers(self):
        return self.collection.get_layer_names()

    @property
    def detached_layers(self):
        return self._detached_layers

    @property
    def fragmented_layers(self):
        # TODO: Complete this
        raise NotImplementedError()

    @property
    def sql_query(self):
        """Returns a SQL select statement that defines the subcollection.
        
        BUGS: This function does not handle fragmented layers correctly.
        We need nested sql queries to combine fragments into single object per text_id
        This must be solved by defining a view during creation of fragmented layers
        or some dark magic query composition.

        """
        selected_columns = pg.SelectedColumns(collection=self.collection,
                                              layers=self._detached_layers,
                                              collection_meta=self.meta_attributes,
                                              include_layer_ids=False)

        required_layers = sorted(set(self._detached_layers + self._selection_criterion.required_layers))

        collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)

        # Required layers are part of the main collection
        if required_layers:
            # Build a join clauses to merge required detached layers by text_id
            required_layer_tables = [pg.layer_table_identifier(self.collection.storage, self.collection.name, layer)
                                     for layer in required_layers]
            join_condition = SQL(" AND ").join(SQL('{}."id" = {}."text_id"').format(collection_identifier,
                                                                                    layer_table_identifier)
                                               for layer_table_identifier in required_layer_tables)

            required_tables = SQL(', ').join((collection_identifier, *required_layer_tables))
            if self._selection_criterion:
                query = SQL("SELECT {} FROM {} WHERE {} AND {}").format(SQL(', ').join(selected_columns),
                                                                        required_tables,
                                                                        join_condition,
                                                                        self._selection_criterion)

            else:
                query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                 required_tables,
                                                                 join_condition)
        else:
            if self._selection_criterion:
                query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                 collection_identifier,
                                                                 self._selection_criterion)

            else:
                query = SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns), collection_identifier)

        return SQL('{} ORDER BY {}."id"').format(query, collection_identifier)

    @property
    def sql_query_text(self):
        return self.sql_query.as_string(self.collection.storage.conn)

    @property
    def sql_count_query(self):
        # TODO: Do not stress SQL analyzer write a flat query for it
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_query)

    @property
    def sql_count_query_text(self):
        return self.sql_count_query.as_string(self.collection.storage.conn)

    def select(self, additional_constraint: pg.WhereClause = None, selected_layers: Sequence[str] = None):
        """
        Returns a new subcollection that satisfies additional constraints.

        TODO: Document its usages
        """

        if selected_layers is None:
            selected_layers = self.selected_layers

        if additional_constraint is None:
            self.selected_layers = selected_layers
            return self

        return PgSubCollection(collection=self.collection,
                               selection_criterion=self._selection_criterion & additional_constraint,
                               selected_layers=selected_layers.copy(),
                               meta_attributes=self.meta_attributes,
                               progressbar=self.progressbar,
                               return_index=self.return_index
                               )

    __read_cursor_counter = 0


    def __iter__(self):
        """
        Yields all subcollection elements ordered by the text_id 

        Depending on self.return_index and self.meta_attributes yields either
        - text
        - text_id, text
        - text, meta
        - text_id, text, meta

        The value of these configuration attributes is fixed before starting the iteration.

        Tradeoff itersize ! Depends on size of the document and network ping
        """


        # Gain few milliseconds: Find the selection size only if it used in a progress bar.
        total = 0 if self.progressbar is None else len(self)

        # Server side cursor must have unique name per transaction
        # To make code thread-safe we use unique naming scheme inside storage (per connection)
        # TODO: Current naming scheme is not correct
        # Let the storage handle the naming

        self.__class__.__read_cursor_counter += 1
        cur_name = 'read_{}'.format(self.__class__.__read_cursor_counter)

        with self.collection.storage.conn.cursor(cur_name, withhold=True) as server_cursor:
            server_cursor.itersize = self.itersize
            server_cursor.execute(self.sql_query)
            logger.debug(server_cursor.query.decode())
            data_iterator = Progressbar(iterable=server_cursor, total=total, initial=0, progressbar_type=self.progressbar)

            if self.meta_attributes and self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)

                    text = self._dict_to_text(row[1], self._attached_layers)
                    for layer_dict in row[2 + len(self.meta_attributes):]:
                        layer = self._dict_to_layer(layer_dict, text)
                        text.add_layer(layer)

                    meta_values = row[2:2 + len(self.meta_attributes)]
                    meta = {attr: value for attr, value in zip(self.meta_attributes, meta_values)}

                    yield row[0], text, meta

            elif self.meta_attributes:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)

                    text = self._dict_to_text(row[1], self._attached_layers)
                    for layer_dict in row[2 + len(self.meta_attributes):]:
                        layer = self._dict_to_layer(layer_dict, text)
                        text.add_layer(layer)

                    meta_values = row[2:2 + len(self.meta_attributes)]
                    meta = {attr: value for attr, value in zip(self.meta_attributes, meta_values)}

                    yield text, meta

            elif self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)

                    text = self._dict_to_text(row[1], self._attached_layers)
                    for layer_dict in row[2:]:
                        layer = self._dict_to_layer(layer_dict, text)
                        text.add_layer(layer)

                    yield row[0], text

            else:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)

                    text = self._dict_to_text(row[1], self._attached_layers)
                    for layer_dict in row[2:]:
                        layer = self._dict_to_layer(layer_dict, text)
                        text.add_layer(layer)

                    yield text

    def head(self, n: int = 5) -> List[Text]:
        return [t for _, t in zip(range(n), self)]

    def tail(self, n: int = 5) -> List[Text]:
        # ineffective implementation:
        # return list(collections.deque(self, n))
        raise NotImplementedError()

    def select_all(self):
        self.selected_layers = self.layers
        return self

    def detached_layer(self, name):
        return pg.PgSubCollectionLayer(self.collection,
                                       detached_layer=name,
                                       selection_criterion=self._selection_criterion,
                                       progressbar=self.progressbar,
                                       return_index=self.return_index)

    def fragmented_layer(self, name):
        return pg.PgSubCollectionFragments(self.collection,
                                           fragmented_layer=name,
                                           selection_criterion=self._selection_criterion,
                                           progressbar=self.progressbar,
                                           return_index=self.return_index)

    def __repr__(self):
        return ('{self.__class__.__name__}('
                'collection: {self.collection.name!r}, '
                'selected_layers={self.selected_layers}, '
                'meta_attributes={self.meta_attributes}, '
                'progressbar={self.progressbar!r}, '
                'return_index={self.return_index})').format(self=self)

    @staticmethod
    def assemble_text_object(text_dict: str, layer_dicts: List[str], selected_layers: List[str],
                             structure: pg.CollectionStructureBase = None) -> Text:
        """
        Assembles Text object from json specification of texts and json specifications of detached layers.

        The list of layer names determines which layers are selected. The collection structure determines how these
        layers are reconstructed. Default reconstruction method is used when serialisation module is unspecified.

        All json specifications must be in recursive dict format.
        All serialisation modules must be registered in a serialisation map.
        Layer names must contain all dependencies or otherwise the reconstruction fails.
        """

        text = Text(text_dict['text'])
        text.meta = text_dict['meta']

        # Collections with structure versions < 2.0 are used same old serialisation module for all layers
        if structure is None or structure.version in {'0.0', '1.0'}:

            dict_to_layer = serialisation_modules.legacy_v0.dict_to_layer
            for layer_element in chain(text_dict['layers'], layer_dicts):
                if layer_element['name'] in selected_layers:
                    text.add_layer(dict_to_layer(layer_element, text))

            return text

        # Otherwise each layer can be serialised differently
        dict_to_layer = serialisation_modules.default.dict_to_layer
        for layer_element in chain(text_dict['layers'], layer_dicts):
            layer_name = layer_element['name']
            if layer_name in selected_layers:
                serialisation_module = structure[layer_name]['serialisation_module']

                # Use default serialisation if specification is missing
                if serialisation_module is None:
                    text.add_layer(dict_to_layer(layer_element, text))
                elif serialisation_module in layer_converter_collection:
                    text.add_layer(layer_converter_collection[serialisation_module].dict_to_layer(layer_element, text))
                else:
                    raise ValueError('serialisation module not registered in serialisation map: ' + layer_converter_collection)

        return text

    def _dict_to_layer(self, layer_dict: dict, text_object=None):
        # collections with structure versions <2.0 are used same old serialisation module for all layers
        if self.collection.structure.version in {'0.0', '1.0'}:
            return serialisation_modules.legacy_v0.dict_to_layer(layer_dict, text_object)

        serialisation_module = self.collection.structure[layer_dict['name']]['serialisation_module']
        # use default serialisation if specification is missing
        if serialisation_module is None:
            return serialisation_modules.default.dict_to_layer(layer_dict, text_object)

        if serialisation_module in layer_converter_collection:
            return layer_converter_collection[serialisation_module].dict_to_layer(layer_dict, text_object)

        raise ValueError('serialisation module not registered in serialisation map: ' + layer_converter_collection)

    def _dict_to_text(self, text_dict: dict, attached_layers) -> Text:
        text = Text(text_dict['text'])
        text.meta = text_dict['meta']
        for layer_dict in text_dict['layers']:
            if layer_dict['name'] in attached_layers:
                layer = self._dict_to_layer(layer_dict, text)
                text.add_layer(layer)
        return text
