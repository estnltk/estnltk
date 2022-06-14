from typing import Sequence, List
from psycopg2.sql import SQL, Literal, Identifier
from psycopg2.errors import UndefinedTable
from itertools import chain
from random import uniform, randint

from estnltk import logger, Progressbar
from estnltk import Text
from estnltk_core.converters.serialisation_registry import SERIALISATION_REGISTRY
from estnltk_core.converters import default_serialisation
from estnltk.converters.serialisation_modules import legacy_v0 as legacy_serialisation
from estnltk.storage import postgres as pg
from estnltk.storage.postgres.collection import PgCollectionException



class PgSubCollection:
    """
    Wrapper class that provides read-only access to a subset of a collection.

    The subset is specified by a SQL select statement that is determined by
    - the selection criterion and skip_rows/limit_rows constraints
    - the set of selected layers
    - the set of meta attributes
    - the sparsity of layers (if texts with empty sparse layers are dropped)

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
                 progressbar: str = None, return_index: bool = True, itersize: int = 50,
                 skip_rows: int = None, limit_rows: int = None, keep_all_texts: bool = True ):
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
        :param skip_rows: int
            the number of rows to be skipped from the start of subcollection query (PostgreSQL's OFFSET clause).
            should be a positive integer or None (if the skipping constraint is not used).
        :param limit_rows: int
            the limit for the number of first rows to be fetched from the subcollection query (PostgreSQL's LIMIT clause).
            should be a positive integer or None (if the limiting constraint is not used).
        :param keep_all_texts: bool
            whether collection's text objects are returned even if they contain 
            empty layers in selected / required sparse layers. 
            by default, this option is switched on, and as a result, collection's text 
            objects are retrieved even if their sparse layers are emtpy. 
            (under the hood, this means using left outer join on all sparse layer tables). 
            if switched off, then text objects that contain empty layers in sparse layer 
            tables will be excluded from the results. this can speed up the query. 
            (under the hood, this means using inner join for all layer tables, including 
            sparse ones). 
            this parameter affects both selected layers and selection_criterion layers. 
        """

        #TODO: Make sure that all objects used by the class are independent copies and cannot be 
        #changed form the outside. This might invalidate invariants 

        if collection is None or (isinstance(collection, pg.PgCollection) and not collection.exists()):
            raise PgCollectionException("collection does not exist, can't create subcollection")
        elif not isinstance(collection, pg.PgCollection):
            raise TypeError('collection must be an instance of PgCollection')

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
        self.skip_rows  = skip_rows if isinstance(skip_rows,int) and skip_rows > 0 else None
        self.limit_rows = limit_rows if isinstance(limit_rows,int) and limit_rows >= 0 else None
        # for subcollection permutation
        self._permutation_seed     = None
        self._permutation_iterated = False
        # for sample documents query
        self._sampling_seed      = None  # seed given by the user
        self._sampling_seed_auto = None  # an automatically assigned seed (for repeatability with the progressbar)
        self._sampling_method = None
        self._sampling_percentage = None
        self._sample_construction = None
        # for sample from layer query
        self._sample_from_layer             = None
        self._sample_from_layer_seed        = None  # seed given by the user
        self._sample_from_layer_auto_seed   = None  # an automatically assigned seed (for repeatability with the progressbar)
        self._sample_from_layer_alpha       = None
        self._sample_from_layer_is_attached = None
        # use left outer join for all required sparse layers
        # if False, then inner join is used instead
        self._left_join_sparse_layers = keep_all_texts
        


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
        return self.collection.layers

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
            # Build a FROM clause with joins to required detached layers
            from_clause = pg.FromClause(self.collection, [])
            for layer in required_layers:
                join_type = None
                if not self._left_join_sparse_layers:
                    # check whether we have a sparse layer
                    if self.collection.is_sparse( layer ):
                        # force using inner join
                        join_type = ['INNER JOIN']
                from_clause &= pg.FromClause(self.collection, [layer], join_type)
            # Build SELECT query
            if self._selection_criterion:
                query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                        from_clause,
                                                                        self._selection_criterion)

            else:
                query = SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns),
                                                                 from_clause)
        else:
            if self._selection_criterion:
                query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                 collection_identifier,
                                                                 self._selection_criterion)

            else:
                query = SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns), collection_identifier)

        final_sql = SQL('{} ORDER BY {}."id"').format(query, collection_identifier)
        #  
        #  * LIMIT & OFFSET should come after WHERE conditions and ORDER BY expressions,
        #    therefore, we cannot make a pg.WhereClause for them;
        #  * "If both OFFSET and LIMIT appear, then OFFSET rows are skipped before 
        #     starting to count the LIMIT rows that are returned."
        #  Documentation:  https://www.postgresql.org/docs/13/queries-limit.html
        #
        if self.limit_rows is not None:
            final_sql = SQL("{} LIMIT {}").format( final_sql, Literal(self.limit_rows) )
        if self.skip_rows is not None:
            final_sql = SQL("{} OFFSET {}").format( final_sql, Literal(self.skip_rows) )
        return final_sql

    @property
    def sql_query_text(self):
        return self.sql_query.as_string(self.collection.storage.conn)

    @property
    def sql_count_query(self):
        # TODO: Do not stress SQL analyzer write a flat query for it.
        # Note: making a flat count(*) query out of self.sql_query is not trivial:
        # 1) construction of SELECTed columns, FROM clause and WHERE clause must be 
        #    refactored out from self.sql_query -- in a way that FROM/WHERE clauses 
        #    can be added to this query;
        # 2) ORDER BY needs to be switched off in self.sql_query 
        #    (because COUNT(*) and ORDER BY clause do not work together, 
        #     e.g. see https://stackoverflow.com/q/45096178 )
        # 3) The abstraction must be made in a way that it works also for 
        #    self.sql_sample_texts_count_query and self.sql_sample_from_layer_count_query
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_query)

    @property
    def sql_count_query_text(self):
        return self.sql_count_query.as_string(self.collection.storage.conn)

    @property
    def sql_sample_texts_query(self):
        """
        Returns a SQL select statement that defines a sample (of texts) over the subcollection.
        
        TODO: an idea for performance improvement:
              self.sql_query does joins over detached layers that are not part of where condition
              hence you need to define sql_index_query property for index selection
              while you are there you should optimise self.sql_count_query for the same reasons
        """
        collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)
        
        seed = None
        if self._sampling_seed is not None:
            # Use seed provided by the user
            seed = self._sampling_seed
        elif self._sampling_seed_auto is not None:
            # Use automatically generated seed (for repeatability with the progressbar)
            seed = self._sampling_seed_auto
        
        seed_sql = SQL(""" REPEATABLE({seed}) """).format(seed=Literal(seed)) if seed is not None else SQL("")
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
    def sql_sample_from_layer_query(self):
        """
        Returns a SQL select statement that samples elements from specific layer randomly.
        """
        alpha             = self._sample_from_layer_alpha
        layer             = self._sample_from_layer
        layer_is_attached = self._sample_from_layer_is_attached 

        # Note: we must setseed inside the sampling query (and before launching any 
        # queries with RANDOM()), otherwise, repeatability is not ensured.
        # See also: https://www.techonthenet.com/postgresql/functions/setseed.php
        seed_value = None
        seed_query = None
        if self._sample_from_layer_seed is not None:
            seed_value = self._sample_from_layer_seed
        elif self._sample_from_layer_auto_seed is not None:
            seed_value = self._sample_from_layer_auto_seed
        if seed_value is not None:
            seed_query = SQL("""SELECT setseed({seed_value})""").format( seed_value=Literal(seed_value) )

        # 1) Get layer's content and size
        if layer_is_attached:
            # attached layer
            collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)
            q0 = SQL("""SELECT {target_collection_table}."id", layer_json AS layer_data, layer_idx FROM {target_collection_table}, """+
                     """jsonb_array_elements( {target_collection_table}."data"->'layers' ) WITH ORDINALITY arr( layer_json, layer_idx ) """+
                     """WHERE layer_json::jsonb @> {layer_name}::jsonb""").format( target_collection_table=collection_identifier,
                     layer_name=Literal( '{{ "name":"{}" }}'.format(layer) ))
            q1 = SQL("""SELECT id, jsonb_array_length( layer_data->'spans' ) as layer_size, layer_data FROM ({q0}) AS q0""").format( q0=q0 )
            if seed_query is not None:
                q1 = SQL("""SELECT q1w.* FROM ({}) AS seed_setting, ({}) AS q1w""").format(seed_query, q1)
        else:
            # detached layer
            layer_identifier = pg.layer_table_identifier(self.collection.storage, self.collection.name, layer)
            q1 = SQL("""SELECT {target_layer_table}."text_id" AS id, """+
                     """jsonb_array_length( {target_layer_table}."data"->'spans' ) as layer_size, """+
                     """{target_layer_table}."data" as layer_data FROM {target_layer_table}""").format( target_layer_table=layer_identifier )
            if seed_query is not None:
                q1 = SQL("""SELECT q1w.* FROM ({}) AS seed_setting, ({}) AS q1w""").format(seed_query, q1)
        # 2) Make a random pick of texts
        q2 = SQL("""SELECT id, layer_size, 1-(1-{alpha})^layer_size as doc_threshold, RANDOM() as rnd1, layer_data FROM ({q1}) AS q1""").format(alpha=Literal(alpha), q1=q1)
        q3 = SQL("""SELECT id, layer_size, doc_threshold, rnd1, layer_data FROM ({q2}) AS q2 WHERE rnd1 <= doc_threshold""").format(q2=q2)
        # 3) Make a random pick of layer's spans
        q4 = SQL("""SELECT id, layer_size, doc_threshold, arr.layer_span_json AS layer_span, """+
                 """arr.layer_span_idx AS layer_span_index, """+
                 """{alpha}/(1-({alpha})^layer_size) AS span_threshold, """+
                 """RANDOM() as rnd2 FROM ({q3}) AS q3, """+
                 """jsonb_array_elements(layer_data->'spans') WITH ORDINALITY arr( layer_span_json, layer_span_idx )""").format(alpha=Literal(alpha), q3=q3)
        q5 = SQL("""SELECT id, layer_size, doc_threshold, layer_span, layer_span_index, span_threshold, rnd2 FROM ({q4}) AS q4 WHERE rnd2 <= span_threshold""").format(q4=q4)
        # 5) Build new json object: { 'spans': randomly_picked_spans }
        q6 = SQL("""SELECT id, jsonb_build_object( 'spans', array_agg( layer_span ORDER BY layer_span_index )) AS selected_spans FROM ({q5}) AS q5 GROUP BY id""").format(q5=q5)
        # 6) Assemble new layer json which only has the randomly selected spans;
        if layer_is_attached:
            # attached layer
            collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)
            q7 = SQL("""SELECT {target_collection_table}."id", {target_collection_table}."data" as text_data, layer_json::jsonb - 'spans' AS layer_wo_spans, layer_idx """+
                     """FROM {target_collection_table}, jsonb_array_elements( {target_collection_table}."data"->'layers' ) WITH ORDINALITY arr( layer_json, layer_idx ) """+
                     """WHERE layer_json::jsonb  @> {layer_name}::jsonb""").format( target_collection_table=collection_identifier,
                     layer_name=Literal( '{{ "name":"{}" }}'.format(layer) ) )
            q8 = SQL("""SELECT q6.id AS text_id, (q7.layer_wo_spans || q6.selected_spans) as layer_data_rnd_selection """+
                     """FROM ({q6}) q6 JOIN ({q7}) q7 ON (q6.id = q7.id)""").format(q6=q6, q7=q7)
        else:
            # detached layer
            layer_identifier = pg.layer_table_identifier(self.collection.storage, self.collection.name, layer)
            q7 = SQL("""SELECT {target_layer_table}."text_id" AS id, {target_layer_table}."data"::jsonb-'spans' AS layer_wo_spans FROM {target_layer_table}""").format(target_layer_table=layer_identifier)
            q8 = SQL("""SELECT q6.id AS text_id, (q7.layer_wo_spans || q6.selected_spans) as layer_data_rnd_selection FROM ({q6}) q6 JOIN ({q7}) q7 ON (q6.id = q7.id)""").format(q6=q6, q7=q7)

        # Now, a nice solution would be to seamlessly replace text objects or selected layers in 
        # the subcollection query with the ones that have randomly selected spans. 
        # But this requires hacking deeply into the subcollection query: providing unique names 
        # to all columns in the query, and reconstruction of query's columns with proper replacements
        # from the sampling query.
        #
        # Instead, we simply join sampling query with the subcollection query, and add the 
        # results of the sampling as the last column of the results row. So, the iterator 
        # function has to make proper replacements and assemble text object correspondingly.
        
        whole_sample_from_layer_sql = SQL("""SELECT subcollection.*, sample_selection.{sampling_result} """
                                          """FROM ({subcollection}) AS subcollection JOIN ({sample_query}) """+
                                          """AS sample_selection ON subcollection.id = sample_selection.text_id""").format(
            subcollection   = self.sql_query,
            sampling_result = Identifier("layer_data_rnd_selection"),
            sample_query    = q8
        )
        
        return whole_sample_from_layer_sql


    def _sql_selected_layer_size_query(self, layer):
        """
        Returns a SQL select statement that finds size (number of spans) of the given layer.
        The layer must be one of the selected_layers.
        """
        if layer is None or not layer in self.selected_layers:
            raise ValueError( ('(!) Invalid layer {!r}. '+
                               'Layer must be one of the layers selected by the subcollection query.').format(layer))
        layer_is_attached = ( self.collection.structure[layer]['layer_type'] == 'attached' )
        if layer_is_attached:
            # attached layer
            collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)
            q0 = SQL("""SELECT {target_collection_table}."id", layer_json AS layer_data, layer_idx FROM {target_collection_table}, """+
                     """jsonb_array_elements( {target_collection_table}."data"->'layers' ) WITH ORDINALITY arr( layer_json, layer_idx ) """+
                     """WHERE layer_json::jsonb @> {layer_name}::jsonb""").format( target_collection_table=collection_identifier,
                     layer_name=Literal( '{{ "name":"{}" }}'.format(layer) ))
            sql_layer_size_query = SQL("""SELECT id, jsonb_array_length( layer_data->'spans' ) as layer_size FROM ({q0}) AS q0""").format( q0=q0 )
        else:
            # detached layer
            layer_identifier = pg.layer_table_identifier(self.collection.storage, self.collection.name, layer)
            sql_layer_size_query = SQL("""SELECT {target_layer_table}."text_id" AS id, """+
                                       """jsonb_array_length( {target_layer_table}."data"->'spans' ) as layer_size, """+
                                       """{target_layer_table}."data" as layer_data FROM {target_layer_table}""").format( target_layer_table=layer_identifier )
        return SQL('SELECT SUM(a.layer_size) FROM ({}) AS a').format( sql_layer_size_query )


    @property
    def sql_sample_texts_count_query(self):
        # TODO: Do not stress SQL analyzer write a flat query for it
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_sample_texts_query)

    def _sample_texts_len(self):
        """
        Executes an SQL query to find the size of the sample subcollection. The result is not cached.
        """
        with self.collection.storage.conn.cursor() as cur:
            cur.execute(self.sql_sample_texts_count_query)
            logger.debug(cur.query.decode())
            return next(cur)[0]

    @property
    def sql_sample_from_layer_count_query(self):
        # TODO: Do not stress SQL analyzer write a flat query for it
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_sample_from_layer_query)

    @property
    def sql_permutate_query(self):
        # TODO: Do not stress SQL analyzer write a flat query for it
        if self._permutation_seed is not None:
            seed_query = SQL("""SELECT setseed({seed_value})""").format( seed_value=Literal(self._permutation_seed) )
            return SQL('SELECT subcollection.* FROM ({}) setting_seed, ({}) AS subcollection ORDER BY RANDOM()').format(seed_query, self.sql_query)
        else:
            return SQL('SELECT subcollection.* FROM ({}) AS subcollection ORDER BY RANDOM()').format(self.sql_query)

    def _sample_from_layer_len(self):
        """
        Executes an SQL query to find the size of the subcollection's sample from layer. The result is not cached.
        """
        with self.collection.storage.conn.cursor() as cur:
            cur.execute(self.sql_sample_from_layer_count_query)
            logger.debug(cur.query.decode())
            return next(cur)[0]

    def _selected_layer_size(self, layer):
        """
        Executes an SQL query to find the size of the given (selected) layer in spans.
        The layer must be one of the selected_layers.
        """
        if layer is None or not layer in self.selected_layers:
            raise ValueError( ('(!) Invalid layer {!r}. '+
                               'Layer must be one of the layers selected by the subcollection query.').format(layer))
        with self.collection.storage.conn.cursor() as cur:
            cur.execute(self._sql_selected_layer_size_query(layer))
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

        if additional_constraint is not None:
            # Adding more constraints to a head or tail query will 
            # likely mess it up, so this cannot be allowed;
            if self.limit_rows is not None:
                raise Exception('(!) Additional constraint(s) cannot be added to a head of the subcollection.')
            elif self.skip_rows is not None:
                raise Exception('(!) Additional constraint(s) cannot be added to a tail of the subcollection.')

        return PgSubCollection(collection=self.collection,
                               selection_criterion=self._selection_criterion & additional_constraint,
                               selected_layers=selected_layers.copy(),
                               meta_attributes=self.meta_attributes,
                               progressbar=self.progressbar,
                               return_index=self.return_index,
                               limit_rows=self.limit_rows,
                               skip_rows=self.skip_rows,
                               keep_all_texts=self._left_join_sparse_layers
                               )

    __read_cursor_counter = 0
    __read_sample_cursor_counter = 0
    __read_sample_from_layer_cursor_counter = 0
    __read_permutate_cursor_counter = 0
    
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
        if not isinstance(method, str) or method.upper() not in ['SYSTEM', 'BERNOULLI']:
            raise ValueError('(!) Sampling method {} not supported. Use {} or {}.'.format( method, 'SYSTEM', 'BERNOULLI' ))
        if not isinstance(amount_type, str) or amount_type.upper() not in ['PERCENTAGE', 'SIZE']:
            raise ValueError('(!) Sampling amount_type {} not supported. Use {} or {}.'.format( amount_type, 'PERCENTAGE', 'SIZE' ))
        method = method.upper()
        amount_type = amount_type.upper()
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
            elif selection_size < amount:
                raise ValueError('(!) Sample size {} exceeds subcollection size {}.'.format(amount, selection_size))
            # 2) Find the approximate percentage
            percentage = ( amount * 100.0 ) / selection_size
            assert not (percentage < 0 or percentage > 100)
        if seed is not None and not isinstance(seed, (int, float)):
            raise ValueError('(!) Invalid seed value {}. Used int or float.'.format( seed ))
        if not isinstance(construction, str) or construction.upper() not in ['JOIN', 'ANY']:
            raise ValueError('(!) Sampling construction {} not supported. Use {} or {}.'.format( construction, 'JOIN', 'ANY' ))
        # Check for reiteration
        if self._sampling_seed is None and seed is None:
            # If no seed was given, then do not allow a reiteration
            if self._sampling_method == method and \
               self._sampling_percentage == percentage:
               raise Exception('(!) You cannot reiterate sample unless you fix seed.')
        # Record arguments
        self._sampling_method = method
        self._sampling_percentage = percentage
        self._sampling_seed = seed
        # TODO: this is only for debugging purposes: to be removed later
        self._sample_construction = construction.upper()
        
        # TODO: the following code is basically a very close copy of the self.__iter__ method
        #       (with a small exception that concerns situations where construction == 'JOIN')
        #       It could be refactored into a separate function in future.
        
        if self.progressbar is not None:
            # If user wants a progressbar, we must fix a seed to ensure 
            # that the counting query and the real query give the same results
            self._sampling_seed_auto = randint(1, 2147483646)
            # NB! PostgreSQL's documentation does not give exact range for 
            # possible seed values, but we assume here that it accepts the
            # range of a positive INTEGER
        # Gain few milliseconds: Find the selection size only if it used in a progress bar.
        total = 0 if self.progressbar is None else self._sample_texts_len()

        # Server side cursor must have unique name per transaction
        # To make code thread-safe we use unique naming scheme inside storage (per connection)
        # TODO: Current naming scheme is not correct
        # Let the storage handle the naming

        self.__class__.__read_sample_cursor_counter += 1
        cur_name = 'sample_read_{}'.format(self.__class__.__read_sample_cursor_counter)

        with self.collection.storage.conn.cursor(cur_name, withhold=True) as server_cursor:
            server_cursor.itersize = self.itersize
            try:
                server_cursor.execute(self.sql_sample_texts_query)
            except UndefinedTable as undefined_table_error:
                raise PgCollectionException("collection {} does not exist anymore, can't iterate subcollection".format(self.collection.name))
            except:
                raise
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


    def sample_from_layer(self, layer, amount, amount_type:str='PERCENTAGE', seed=None):
        """
        Yields a sample over subcollection's documents and spans of the given layer.
        
        Amount of the sample can be either a percentage of spans
        (default), or an approximate number of spans -- in the 
        last case, an extra parameter amount_type='SIZE' must be 
        passed to the sample function. 
        Be aware that regardless of the amount_type, the number of 
        returned elements will not correspond exactly to the given 
        amount. If you need a sample with exact size, it is advisable 
        to sample a larger amount than needed, permute/shuffle the 
        sample (in order  to  ensure  that all elements have even
        chance ending up in the final sample), and then cut the 
        sample to the required size.
        
        Reiteration only works if the seed value has been fixed. 
        Otherwise,an Exception will be risen ('cannot reiterate 
        unless you fix seed').
        
        Parameters:
        
        :param layer: str
            Name of the layer to be sampled from.
            Must be one of the selected layers of the subcollection.
        :param amount: int or float
            Size of the sample. if amount_type=='PERCENTAGE' (default),
            then it is a percentage. Otherwise, it is an approximate 
            number of spans to be sampled.
        :param amount_type: str
            Amount type, one of the following: ['PERCENTAGE', 'SIZE']
        :param seed:  float
            Seed value to be fixed to ensure repeatability.
            Must be a value between -1.0 and 1.0;
        """
        alpha = None
        if not isinstance(amount_type, str) or amount_type.upper() not in ['PERCENTAGE', 'SIZE']:
            raise ValueError('(!) Sampling amount_type {!r} not supported. Use {} or {}.'.format( amount_type, 'PERCENTAGE', 'SIZE' ))
        amount_type = amount_type.upper()
        if amount_type == 'PERCENTAGE':
            percentage = amount
            if percentage < 0 or percentage > 100:
                raise ValueError('(!) Invalid percentage value {}.'.format( percentage ))
            alpha = percentage/100.0
        elif amount_type == 'SIZE':
            # 1) Find size of the layer in spans
            total_spans_in_layer = self._selected_layer_size( layer )
            if total_spans_in_layer < 1:
                raise Exception( ('(!) The layer is empty. Cannot make a sample.'))
            # 2) Recalculate alpha to meet the amount (roughly)
            if amount < total_spans_in_layer:
                alpha = amount / total_spans_in_layer
            else:
                alpha = 0.999999999
                if amount > total_spans_in_layer:
                    logger.warning("Sampling amount {} exceeds the size of the layer ({}). Yielding full subcollection.".format(amount, total_spans_in_layer))
        if not self.selected_layers:
            raise Exception( ('(!) This subcollection does not select any layers. '+
                               'Please select layers before making sample_from_layer query.'))
        if layer is None or not layer in self.selected_layers:
            raise ValueError( ('(!) Invalid layer {!r}. '+
                               'Layer must be one of the layers selected by the subcollection query.').format(layer))
        # Validate seed_value
        if seed is not None and not isinstance(seed, float):
            raise ValueError('(!) Invalid seed value {}. Use float from range -1.0 to 1.0.'.format( seed ))
        if isinstance(seed, float) and not (-1.0 <= seed and seed <= 1.0):
            raise ValueError('(!) Invalid seed value {}. Use float from range -1.0 to 1.0'.format( seed ))
        # Check for reiteration
        if self._sample_from_layer_seed is None and seed is None:
            # If no seed was given, then do not allow a reiteration
            if self._sample_from_layer == layer and \
               self._sample_from_layer_alpha == alpha:
               raise Exception('(!) You cannot reiterate sample unless you fix seed.')
        # Record arguments
        self._sample_from_layer             = layer
        self._sample_from_layer_seed        = seed
        self._sample_from_layer_alpha       = alpha
        self._sample_from_layer_is_attached = (self.collection.structure[layer]['layer_type'] == 'attached')
        if seed is None and self.progressbar is not None:
            # generate seed automatically (because we need matching results between the counting
            # query and the actual query)
            self._sample_from_layer_auto_seed = uniform(-1.0, 1.0)

        # TODO: the following code is derived from the self.__iter__ method, with some 
        #       modifications concerning replacing the layer with the one that has
        #       randomly sampled spans.
        #       In future, perhaps the common part of methods __iter__(), sample() and 
        #       sample_from_layer() could be abstracted away as a separate method.
        
        # Gain few milliseconds: Find the selection size only if it used in a progress bar.
        total = 0 if self.progressbar is None else self._sample_from_layer_len()
        
        self.__class__.__read_sample_from_layer_cursor_counter += 1
        cur_name = 'sample_from_layer_read_{}'.format(self.__class__.__read_sample_from_layer_cursor_counter)

        with self.collection.storage.conn.cursor(cur_name, withhold=True) as server_cursor:
            server_cursor.itersize = self.itersize
            try:
                server_cursor.execute(self.sql_sample_from_layer_query)
            except UndefinedTable as undefined_table_error:
                raise PgCollectionException("collection {} does not exist anymore, can't iterate subcollection".format(self.collection.name))
            except:
                raise
            logger.debug(server_cursor.query.decode())
            data_iterator = Progressbar(iterable=server_cursor, total=total, initial=0, progressbar_type=self.progressbar)
            structure = self.collection.structure

            if self.meta_attributes and self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    meta_stop = 2 + len(self.meta_attributes)
                    meta = {attr: value for attr, value in zip(self.meta_attributes, row[2:meta_stop])}
                    layer_dicts = row[meta_stop:-1]
                    text_obj_dict = row[1]
                    layer_with_rnd = row[-1]
                    assert isinstance( layer_with_rnd, dict )
                    if self._sample_from_layer_is_attached:
                        text_obj_dict['layers'] = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in text_obj_dict['layers']]
                    else:
                        layer_dicts = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in layer_dicts]
                    text = self.assemble_text_object(text_obj_dict, layer_dicts, self.selected_layers, structure)
                    yield row[0], text, meta

            elif self.meta_attributes:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    meta_stop = 2 + len(self.meta_attributes)
                    meta = {attr: value for attr, value in zip(self.meta_attributes, row[2:meta_stop])}
                    layer_dicts = row[meta_stop:-1]
                    text_obj_dict = row[1]
                    layer_with_rnd = row[-1]
                    assert isinstance( layer_with_rnd, dict )
                    if self._sample_from_layer_is_attached:
                        text_obj_dict['layers'] = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in text_obj_dict['layers']]
                    else:
                        layer_dicts = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in layer_dicts]
                    text = self.assemble_text_object(text_obj_dict, layer_dicts, self.selected_layers, structure)
                    yield text, meta

            elif self.return_index:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    layer_dicts = row[2:-1]
                    text_obj_dict = row[1]
                    layer_with_rnd = row[-1]
                    assert isinstance( layer_with_rnd, dict )
                    if self._sample_from_layer_is_attached:
                        text_obj_dict['layers'] = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in text_obj_dict['layers']]
                    else:
                        layer_dicts = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in layer_dicts]
                    yield row[0], self.assemble_text_object(text_obj_dict, layer_dicts, self.selected_layers, structure)

            else:
                for row in data_iterator:
                    data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                    layer_dicts = row[2:-1]
                    text_obj_dict = row[1]
                    layer_with_rnd = row[-1]
                    assert isinstance( layer_with_rnd, dict )
                    if self._sample_from_layer_is_attached:
                        text_obj_dict['layers'] = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in text_obj_dict['layers']]
                    else:
                        layer_dicts = [layer_with_rnd if layer['name']==layer_with_rnd['name'] else layer for layer in layer_dicts]
                    yield self.assemble_text_object(text_obj_dict, layer_dicts, self.selected_layers, structure)


    def permutate(self, seed=None):
        """
        Yields subcollection's documents in random order.
        
        Reiteration only works if the seed value has been fixed. 
        Otherwise,an Exception will be risen ('cannot reiterate 
        unless you fix seed').
        
        Parameters:
        
        :param seed:  float
            Seed value to be fixed to ensure repeatability.
            Must be a value between -1.0 and 1.0;
        """
        # Check that args have valid values
        if seed is not None and not isinstance(seed, float):
            raise ValueError('(!) Invalid seed value {}. Use float from range -1.0 to 1.0.'.format( seed ))
        # Validate seed_value
        if isinstance(seed, float) and not (-1.0 <= seed and seed <= 1.0):
            raise ValueError('(!) Invalid seed value {}. Use float from range -1.0 to 1.0'.format( seed ))
        # Check for reiteration
        if self._permutation_seed is None and seed is None:
            # If no seed was given, then do not allow a reiteration
            if self._permutation_iterated:
               raise Exception('(!) You cannot reiterate sample unless you fix seed.')
        # Record arguments
        self._permutation_seed = seed
        self._permutation_iterated = True
        
        # TODO: the following code is basically a very close copy of the self.__iter__ method
        #       It could be refactored into a separate function in future.
        
        # Gain few milliseconds: Find the selection size only if it used in a progress bar.
        total = 0 if self.progressbar is None else len(self)

        # Server side cursor must have unique name per transaction
        # To make code thread-safe we use unique naming scheme inside storage (per connection)
        # TODO: Current naming scheme is not correct
        # Let the storage handle the naming

        self.__class__.__read_permutate_cursor_counter += 1
        cur_name = 'permutate_read_{}'.format(self.__class__.__read_permutate_cursor_counter)

        with self.collection.storage.conn.cursor(cur_name, withhold=True) as server_cursor:
            server_cursor.itersize = self.itersize
            try:
                server_cursor.execute(self.sql_permutate_query)
            except UndefinedTable as undefined_table_error:
                raise PgCollectionException("collection {} does not exist anymore, can't iterate subcollection".format(self.collection.name))
            except:
                raise
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
            try:
                server_cursor.execute(self.sql_query)
            except UndefinedTable as undefined_table_error:
                raise PgCollectionException("collection {} does not exist anymore, can't iterate subcollection".format(self.collection.name))
            except:
                raise
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
        limit_rows = n
        if self.limit_rows is not None and self.limit_rows < n:
            raise ValueError(('(!) This subcollection already has a limit_rows={} constraint. '+\
                              'The new head value should be smaller.').format(self.limit_rows))
        return PgSubCollection(collection=self.collection,
               selection_criterion=self._selection_criterion,
               selected_layers=self.selected_layers,
               meta_attributes=self.meta_attributes,
               progressbar=self.progressbar,
               return_index=self.return_index,
               limit_rows=limit_rows,
               skip_rows=self.skip_rows,
               keep_all_texts=self._left_join_sparse_layers
        )

    def tail(self, n: int = 5) -> List[Text]:
        if self.limit_rows is not None:
            # NB! Adding tail after head gets messy, because "If both OFFSET and LIMIT appear, 
            #     then OFFSET rows are skipped before starting to count the LIMIT rows that 
            #     are returned." Therefore, we cannot allow that at the moment.
            raise NotImplementedError('(!) Applying tail on a head of the subcollection is currently not supported.')
        selection_size = len(self)
        skip_rows = (selection_size - n) if self.skip_rows is None else self.skip_rows + (selection_size - n)
        if skip_rows > 0:
            if self.skip_rows is not None and self.skip_rows > skip_rows:
                raise ValueError(('(!) This subcollection already has a skip_rows={} constraint. '+\
                                  'The new tail value should be smaller than {}.').format(self.skip_rows, selection_size))
            return PgSubCollection(collection=self.collection,
                   selection_criterion=self._selection_criterion,
                   selected_layers=self.selected_layers,
                   meta_attributes=self.meta_attributes,
                   progressbar=self.progressbar,
                   return_index=self.return_index,
                   limit_rows=self.limit_rows,
                   skip_rows=skip_rows,
                   keep_all_texts=self._left_join_sparse_layers
            )
        else:
            return self

    def create_layer(self, tagger, create_index=False, ngram_index=None, meta=None, 
                     progressbar=None, query_length_limit=5000000, mode=None):
        """
        Creates a sparse layer based on this subcollection.

        :param tagger: Tagger
            Tagger to be used for creating the layer. 
            Note: tagger's input_layers will be selected automatically, 
            but the collection must have all the input layers. 
        :param create_index: bool
            Whether to create an index on json column. 
        :param ngram_index: list
            A list of attributes for which to create an ngram index. 
        :param meta: dict of str -> str
            Specifies table column names and data types to create for storing 
            additional meta information. E.g. meta={"sum": "int", "average": "float"}. 
            See `pytype2dbtype` in `pg_operations` for supported types. 
        :param progressbar: str
            if 'notebook', display progressbar as a jupyter notebook widget
            if 'unicode', use unicode (smooth blocks) to fill the progressbar
            if 'ascii', use ASCII characters (1-9 #) to fill the progressbar
            else disable progressbar (default)
        :param query_length_limit: int
            soft approximate query length limit in unicode characters, can be exceeded 
            by the length of last buffer insert.
        :param mode: str 
            Specifies how layer creation should handle existing layers. 
            Possible modes:
            * None / 'new' - creates a new layer. If the layer already exists in the 
                             collection, raises an exception. Default option.
            * 'append'     - appends to an existing layer; annotates only those documents 
                             that are missing the layer.
                             raises an exception if the collection does not have the layer;
        """
        # Check collection's version
        if self.collection.version < '3.0':
            raise PgCollectionException( ("Creating sparse layer table is not supported in this "+\
                                          "collection version ({!r}).").format(self.collection.version) )
        # Check mode value
        if mode is not None:
            expected_mode_values = ['new', 'append']
            if mode.lower() not in expected_mode_values:
                raise ValueError('(!) Unexpected mode={!r}.'+\
                                 'Supported mode values are {!r}.'.format(mode, expected_mode_values))
            mode = mode.lower()
        # Check existing structure, if needed
        layer_name = tagger.output_layer
        if mode is not None and mode == 'append':
            # Check for the existing layer
            if not self.collection.has_layer( layer_name ):
                raise PgCollectionException(("Layer {!r} is missing from collection's structure, " + \
                                             "cannot use mode='append'. Use mode='new' instead." + \
                                             "").format(layer_name))
            if not self.collection.is_sparse( layer_name ):
                raise PgCollectionException(("Layer {!r} is not sparse. Only sparse layers can be tagged " + \
                                             "via this method. Use collection.create_layer(...) to tag " + \
                                             "a non-sparse layer.").format(layer_name))
        # Prepare data_iterator
        data_iterator=self
        add_selected_layers = []
        for required_layer in tagger.input_layers:
            if required_layer not in self.selected_layers:
                if not self.collection.has_layer( required_layer ):
                    raise PgCollectionException(("Tagger's input layer {!r} is missing from " +\
                                                 "this collection, cannot apply the tagger." +\
                                                 "").format(required_layer))
                add_selected_layers.append( required_layer )
        if add_selected_layers:
            # Extend data_iterator by new selected layers
            data_iterator = data_iterator.select( 
                selected_layers=data_iterator.selected_layers + add_selected_layers )
        
        # Use collection's create_layer method        
        def default_row_mapper(row):
            text_id, text = row[0], row[1]
            status = {}
            layer = tagger.make_layer(text=text, status=status)
            return pg.RowMapperRecord(layer=layer, meta=status)
        self.collection.create_layer(layer_name=tagger.output_layer, data_iterator=data_iterator, 
                                     row_mapper=default_row_mapper, meta=meta, progressbar=progressbar, 
                                     query_length_limit=query_length_limit, mode=mode, sparse=True)

    def create_layer_block(self, tagger, block, meta=None, query_length_limit=5000000, mode=None):
        """
        Creates a layer block based on this subcollection. 
        
        Note 1: before the layer block can be created, the layer table must already exist. 
        Use collection's method add_layer(..., sparse=True) to create an empty sparse layer 
        (table).
        
        Note 2: only sparse layers can be tagged with this method.

        :param tagger: Tagger
            tagger to be applied on collection's texts.
            Note: tagger's input_layers will be selected automatically, 
            but the collection must have all the input layers. 
        :param block: Tuple[int, int]
            pair of integers `(module, remainder)`. Only texts with `id % module = remainder` 
            are tagged.
        :param meta: dict of str -> str
            Specifies table column names and data types to create for storing additional
            meta information. E.g. meta={"sum": "int", "average": "float"}.
            See `pytype2dbtype` in `pg_operations` for supported types.
        :param query_length_limit: int
            soft approximate query length limit in unicode characters, can be exceeded by the 
            length of last buffer insert
        :param mode: str 
            Specifies how layer creation should handle existing layers inside the block. 
            Possible modes:
            * None / 'new' - attempts to tag all texts inside the block 
                             (creates a new block);
            * 'append'     - finds untagged texts inside the block and only tags untagged texts;
                             (continues a block which tagging has not been finished)
        """
        # Check for the existence and sparsity of the layer
        layer_name = tagger.output_layer
        if not self.collection.has_layer( layer_name ):
            raise PgCollectionException(("Layer {!r} is missing from collection's structure. " + \
                                         "Use collection.add_layer(..., sparse=True) to update " + \
                                         "the structure before using this method. Note that you "+\
                                         "can only tag a sparse layer with this method.").format(layer_name))
        if not self.collection.is_sparse( layer_name ):
            raise PgCollectionException(("Layer {!r} is not sparse. Only sparse layers can be created " + \
                                         "via this method. Use collection.create_layer_block(...) to " + \
                                         "create a non-sparse layer.").format(layer_name))
        data_iterator=self
        self.collection.create_layer_block( tagger=tagger, block=block, data_iterator=data_iterator,
                                            meta=meta, query_length_limit=query_length_limit,
                                            mode=mode )

    def select_all(self):
        self.selected_layers = self.layers
        return self

    def detached_layer(self, name):
        return pg.PgSubCollectionLayer(self.collection,
                                       detached_layer=name,
                                       selection_criterion=self._selection_criterion,
                                       progressbar=self.progressbar,
                                       return_index=self.return_index,
                                       skip_empty=not self._left_join_sparse_layers)

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

            dict_to_layer = legacy_serialisation.dict_to_layer
            for layer_element in chain(text_dict['layers'], layer_dicts):
                if layer_element['name'] in selected_layers:
                    text.add_layer(dict_to_layer(layer_element, text))

            return text

        # Otherwise each layer can be serialised differently
        dict_to_layer = default_serialisation.dict_to_layer
        # First, we need to reorder selected layers in 
        # the precise way they will be iterated
        text_layer_names = \
            [layer_dict['name'] for layer_dict in text_dict['layers']]
        reordered_selected_layers = []
        # 1) not all attached layers are selected: pick the selected ones
        for layer_name in text_layer_names:
            if layer_name in selected_layers:
                reordered_selected_layers.append( layer_name )
        # 2) remaining layer names belong to detached (selected) layers
        for layer_name in selected_layers:
            if layer_name not in text_layer_names:
                reordered_selected_layers.append( layer_name )
        assert len(reordered_selected_layers) == len(selected_layers)
        # While iterating results, keep track of the selected layers
        # (sparse layers can have None values which need to
        #  be replaced by layer templates)
        layer_index = 0
        cur_selected_layer = \
            reordered_selected_layers[layer_index] if layer_index < len(reordered_selected_layers) else None
        for layer_element in chain(text_dict['layers'], layer_dicts):
            if layer_element is None:
                # Handle sparse layers from LEFT JOIN query
                assert structure is not None
                assert structure.version >= '3.0'
                layer_name = cur_selected_layer
                assert layer_name is not None
                assert structure[layer_name]['sparse']
                # Fetch layer template from the structure
                layer_element = structure[layer_name]['layer_template_dict']

            layer_name = layer_element['name']
            if layer_name in reordered_selected_layers:
                serialisation_module = structure[layer_name]['serialisation_module']

                # Use default serialisation if specification is missing
                if serialisation_module is None:
                    text.add_layer(dict_to_layer(layer_element, text))
                elif serialisation_module in SERIALISATION_REGISTRY:
                    text.add_layer( SERIALISATION_REGISTRY[serialisation_module].dict_to_layer(layer_element, text) )
                else:
                    raise ValueError(('serialisation module {!r} not registered in serialisation map: '.format(serialisation_module))+SERIALISATION_REGISTRY.keys())
                layer_index += 1
                # Take the next selected layer
                cur_selected_layer = \
                    reordered_selected_layers[layer_index] if layer_index < len(reordered_selected_layers) else None
        return text

    def _dict_to_layer(self, layer_dict: dict, text_object=None):
        """Deprecated to be removed"""
        # collections with structure versions <2.0 are used same old serialisation module for all layers
        if self.collection.structure.version in {'0.0', '1.0'}:
            return legacy_serialisation.dict_to_layer(layer_dict, text_object)

        serialisation_module = self.collection.structure[layer_dict['name']]['serialisation_module']
        
        # use default serialisation if specification is missing
        if serialisation_module is None:
            return default_serialisation.dict_to_layer(layer_dict, text_object)

        if serialisation_module in SERIALISATION_REGISTRY:
            return SERIALISATION_REGISTRY[serialisation_module].dict_to_layer(layer_dict, text_object)

        raise ValueError(('serialisation module {!r} not registered in serialisation map: '.format(serialisation_module))+SERIALISATION_REGISTRY.keys())

    def _dict_to_text(self, text_dict: dict, attached_layers) -> Text:
        """Deprecated to be removed"""
        text = Text(text_dict['text'])
        text.meta = text_dict['meta']
        for layer_dict in text_dict['layers']:
            if layer_dict['name'] in attached_layers:
                layer = self._dict_to_layer(layer_dict, text)
                text.add_layer(layer)
        return text
