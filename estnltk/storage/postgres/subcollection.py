from typing import Sequence, List
from psycopg2.sql import SQL, Literal
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
        # for sampling query
        self._sampling_seed = None
        self._sampling_method = None
        self._sampling_percentage = None
        self._sample_construction = None

    def __len__(self):
        """
        Executes an SQL query to find the size of the subcollection. The result is not cached.
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

    @property
    def sql_sampler_query(self):
        """
        Returns a SQL select statement that defines a sample over the subcollection.
        
        TODO: an idea for performance improvement:
              self.sql_query does joins over detached layers that are not part of where condition
              hence you need to define sql_index_query property for index selection
              while you are there you should optimise self.sql_count_query for the same reasons
        """
        collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)
        
        seed_sql = SQL(""" REPEATABLE({seed}) """).format(seed=Literal(self._sampling_seed)) \
                       if self._sampling_seed is not None else SQL("")
        sample_sql = SQL("""SELECT {table}."id" FROM {table} TABLESAMPLE {sampling_method}({percentage}) {seed_sql}""").format( 
                         table=collection_identifier, 
                         sampling_method=SQL(self._sampling_method), 
                         percentage=Literal(self._sampling_percentage), 
                         seed_sql=seed_sql )
        if not self._sample_construction or self._sample_construction == 'JOIN':
            # 1) JOIN sample ON construction
            whole_sample_query_sql = SQL("""SELECT * FROM ({subcollection}) AS subcollection JOIN ({sample_query}) """+
                                         """AS sample_selection ON subcollection.id = sample_selection.id""").format(
                subcollection=self.sql_query,
                sample_query=sample_sql
            )
        elif self._sample_construction == 'ANY':
            # 2) WHERE id in ANY(sample) construction
            whole_sample_query_sql = SQL("""SELECT * FROM ({subcollection}) AS subcollection """+
                                         """WHERE subcollection.id = ANY({sample_query})""").format(
                subcollection=self.sql_query,
                sample_query=sample_sql
            )
        return whole_sample_query_sql

    @property
    def sql_sample_layer_query(self):
        """
        Returns a SQL select statement that selects layer elements randomly.
        
        TODO: This is a work in progress
        """
        
        # This version should work on a detached layer
        
        seed = 1
        alpha = 0.01
        layer = 'sentences'
        layer_table_identifier = pg.layer_table_identifier(self.collection.storage, self.collection.name, layer)

        q1 = SQL("""SELECT {{target_layer_table}}."text_id" AS id, """+
                 """jsonb_array_length( {{target_layer_table}}."data"->'spans' ) as layer_size, """+
                 """{{target_layer_table}}."data" as layer_data FROM {{target_layer_table}}""").format( target_layer_table=layer_table_identifier )
        q2 = SQL("""SELECT id, layer_size, 1-(1-{{alpha}})^layer_size as doc_threshold, RANDOM() as rnd1, layer_data FROM ({{q1}}) AS q1""").format(alpha=Literal(alpha), q1=q1)
        q3 = SQL("""SELECT id, layer_size, doc_threshold, rnd1, layer_data FROM ({{q2}}) AS q2 WHERE rnd1 <= doc_threshold""").format(q2=q2)
        q4 = SQL("""SELECT id, layer_size, doc_threshold, arr.layer_span_json AS layer_span, """+
                 """arr.layer_span_idx AS layer_span_index, """+
                 """{{alpha}}/(1-({{alpha}})^doc_threshold) AS span_threshold, """+
                 """RANDOM() as rnd2 FROM ({{q3}}) AS q3, """+
                 """jsonb_array_elements(layer_data->'spans') WITH ORDINALITY arr( layer_span_json, layer_span_idx )""").format(alpha=Literal(alpha), q3=q3)
        q5 = SQL("""SELECT id, layer_size, doc_threshold, layer_span, layer_span_index, span_threshold, rnd2 FROM ({{q4}}) AS q4 WHERE rnd2 <= span_threshold""").format(q4=q4)
        q6 = SQL("""SELECT id, jsonb_build_object( 'spans', array_agg( layer_span ORDER BY layer_span_index )) AS selected_spans FROM ({{q5}}) AS q5 GROUP BY id""").format(q5=q5)
        q7 = SQL("""SELECT {{target_layer_table}}."text_id" AS id, {{target_layer_table}}."data"::jsonb-'spans' AS layer_wo_spans FROM {{target_layer_table}}""").format(target_layer_table=layer_table_identifier)
        q8 = SQL("""SELECT q6.id AS text_id, (q7.layer_wo_spans || q6.selected_spans) as layer_data_rnd_selection FROM ({{q6}}) q6 JOIN ({{q7}}) q7 ON (q6.id = q7.id);""")

        seed_query = SQL("""SELECT setseed({{seed_value}});""").format( seed_value = Literal(seed) )
        
        # TODO: A version for an attached layer
        
        # TODO: join the query with the subcollection query
        
        return None

    @property
    def sql_sampler_count_query(self):
        # TODO: Do not stress SQL analyzer write a flat query for it
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_sampler_query)

    def _sample_len(self):
        """
        Executes an SQL query to find the size of the sample subcollection. The result is not cached.
        """
        with self.collection.storage.conn.cursor() as cur:
            cur.execute(self.sql_sampler_count_query)
            logger.debug(cur.query.decode())
            return next(cur)[0]

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
    __read_sample_cursor_counter = 0
    
    def sample(self, amount, amount_type:str='PERCENTAGE', seed=None, 
                     method:str='BERNOULLI', construction:str='JOIN'):
        """
        Yields a sample of subcollection elements ordered by the text_id.
        
        Amount of the sample can be either a percentage of elements
        (default), or an approximate number of elements -- in the 
        last case, an extra parameter amount_type='SIZE' must be 
        passed to the sample function. 
        Be aware that regardless of the amount_type, the number of 
        returned elements will not correspond exactly to the given 
        amount. If you need a sample with exact size, it is advisable 
        to sample a larger amount than needed, permute/shuffle the 
        sample (in order  to  ensure  that all elements have even
        chance ending up in the final sample), and then cut the 
        sample to the required size.
        
        Note: the sampling function relies on Postgre's TABLESAMPLE clause.
        For details, see:
        1) https://www.2ndquadrant.com/en/blog/tablesample-in-postgresql-9-5-2/
        2) https://www.postgresql.org/docs/13/sql-select.html > TABLESAMPLE

        Reiteration. If you iterate the function twice like this:

        sample = subcollection.sample( amount, seed=seed_value )
        for text in sample:
            print(text)
        for text in sample:
            print(text)

        then:
        - if the seed_value is a fixed integer, then the code runs OK;
        - otherwise (if seed_value is None) an Exception will be risen 
          ('cannot reiterate unless you fix seed')
        
        Parameters:
        
        :param amount: int or float
            Size of the sample. if amount_type=='PERCENTAGE' (default),
            then it is a percentage. Otherwise, it is an approximate 
            number of documents to be sampled.
        :param amount_type: str
            Amount type, one of the following: ['PERCENTAGE', 'SIZE']
        :param seed  int or float
            Seed value to be fixed to ensure repeatability.
        :param method: str
            Sampling method, one of the following: ['SYSTEM', 'BERNOULLI'].
            Note: this corresponds to Postgre's TABLESAMPLE's sampling methods.
        :param construction: str
            SQL-joining construction type, one of the following: ['JOIN', 'ANY'].
            Note: this parameter is here only for testing and debugging.
            Do not rely on this, as it will be removed later.

        TODO: Other less relevant question
        - do we use a separate PgSubcollectionSample class to pack the end result
          Fancy way to move sampling code out to different class.
          If we implement gazillion methods for sampling then this might be reasonable
          -- if we want to have uniform sampling over words/sentences instead of documents
        """
        # Check that args have valid values
        if method not in ['SYSTEM', 'BERNOULLI']:
            raise ValueError('(!) Sampling method {} not supported. Use {} or {}.'.format( method, 'SYSTEM', 'BERNOULLI' ))
        if amount_type not in ['PERCENTAGE', 'SIZE']:
            raise ValueError('(!) Sampling amount_type {} not supported. Use {} or {}.'.format( method, 'PERCENTAGE', 'SIZE' ))
        if amount_type == 'PERCENTAGE':
            percentage = amount
            if percentage < 0 or percentage > 100:
                raise ValueError('(!) Invalid percentage value {}.'.format( percentage ))
        elif amount_type == 'SIZE':
            if amount is None or not isinstance(amount, int):
                raise TypeError('(!) Invalid amount type {}. Used integer.'.format( amount ))
            # Recalculate amount as percentage
            # 1) Find the selection size
            selection_size = len(self)
            if selection_size == 0:
                raise ValueError('(!) Unable to sample a fixed amount from an empty subcollection.')
            # 2) Find the approximate percentage
            percentage = ( amount * 100.0 ) / selection_size
            assert not (percentage < 0 or percentage > 100)
        if seed is not None and not isinstance(seed, (int, float)):
            raise ValueError('(!) Invalid seed value {}. Used int or float.'.format( seed ))
        if construction and construction not in ['JOIN', 'ANY']:
            raise ValueError('(!) Sampling construction {} not supported. Use {} or {}.'.format( construction, 'JOIN', 'ANY' ))
        # Check for reiteration
        if not self._sampling_seed and not seed:
            # If no seed was given, then do not allow a reiteration
            if self._sampling_method == method and \
               self._sampling_percentage == percentage:
               raise Exception('(!) You cannot reiterate sample unless you fix seed.')
        # Record arguments
        self._sampling_method = method
        self._sampling_percentage = percentage
        self._sampling_seed = seed
        # TODO: this is only for debugging purposes: to be removed later
        self._sample_construction = construction
        
        # TODO: the following code is basically a very close copy of the self.__iter__ method
        #       (with a small exception that concerns situations where construction == 'JOIN')
        #       It could be refactored into a separate function in future.
        
        # Gain few milliseconds: Find the selection size only if it used in a progress bar.
        total = 0 if self.progressbar is None else self._sample_len()

        # Server side cursor must have unique name per transaction
        # To make code thread-safe we use unique naming scheme inside storage (per connection)
        # TODO: Current naming scheme is not correct
        # Let the storage handle the naming

        self.__class__.__read_sample_cursor_counter += 1
        cur_name = 'sample_read_{}'.format(self.__class__.__read_sample_cursor_counter)

        with self.collection.storage.conn.cursor(cur_name, withhold=True) as server_cursor:
            server_cursor.itersize = self.itersize
            server_cursor.execute(self.sql_sampler_query)
            logger.debug(server_cursor.query.decode())
            data_iterator = Progressbar(iterable=server_cursor, total=total, initial=0, progressbar_type=self.progressbar)
            structure = self.collection.structure

            if self.meta_attributes and self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    meta_stop = 2 + len(self.meta_attributes)
                    meta = {attr: value for attr, value in zip(self.meta_attributes, row[2:meta_stop])}
                    layer_dicts = row[meta_stop:] if construction != 'JOIN' else row[meta_stop:-1]
                    text = self.assemble_text_object(row[1], layer_dicts, self.selected_layers, structure)
                    yield row[0], text, meta

            elif self.meta_attributes:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    meta_stop = 2 + len(self.meta_attributes)
                    meta = {attr: value for attr, value in zip(self.meta_attributes, row[2:meta_stop])}
                    layer_dicts = row[meta_stop:] if construction != 'JOIN' else row[meta_stop:-1]
                    text = self.assemble_text_object(row[1], layer_dicts, self.selected_layers, structure)
                    yield text, meta

            elif self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    layer_dicts = row[2:] if construction != 'JOIN' else row[2:-1]
                    yield row[0], self.assemble_text_object(row[1], layer_dicts, self.selected_layers, structure)

            else:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    layer_dicts = row[2:] if construction != 'JOIN' else row[2:-1]
                    yield self.assemble_text_object(row[1], row[2:-1], self.selected_layers, structure)


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
            structure = self.collection.structure

            if self.meta_attributes and self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    meta_stop = 2 + len(self.meta_attributes)
                    meta = {attr: value for attr, value in zip(self.meta_attributes, row[2:meta_stop])}
                    text = self.assemble_text_object(row[1], row[meta_stop:], self.selected_layers, structure)
                    yield row[0], text, meta

            elif self.meta_attributes:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    meta_stop = 2 + len(self.meta_attributes)
                    meta = {attr: value for attr, value in zip(self.meta_attributes, row[2:meta_stop])}
                    text = self.assemble_text_object(row[1], row[meta_stop:], self.selected_layers, structure)
                    yield text, meta

            elif self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    yield row[0], self.assemble_text_object(row[1], row[2:], self.selected_layers, structure)

            else:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    yield self.assemble_text_object(row[1], row[2:], self.selected_layers, structure)

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
    def assemble_text_object(text_dict: dict, layer_dicts: List[dict], selected_layers: List[str],
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
        """Deprecated to be removed"""
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
        """Deprecated to be removed"""
        text = Text(text_dict['text'])
        text.meta = text_dict['meta']
        for layer_dict in text_dict['layers']:
            if layer_dict['name'] in attached_layers:
                layer = self._dict_to_layer(layer_dict, text)
                text.add_layer(layer)
        return text
