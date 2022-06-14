import warnings

from psycopg2.sql import SQL

from estnltk import logger, Progressbar
from estnltk.converters import dict_to_layer
from estnltk.storage import postgres as pg


class PgSubCollectionLayer:
    """
    Wrapper class that provides read-only access to a subset of a collection.

    The subset is specified by a SQL select statement that is determined by
    - the detached layer
    - the selection criterion

    The main usecase for the class is iteration over its elements. 
    It is possible to iterate several times over the subcollection.

    Depending on the configuration attributes, the iterator returns:
    - layer object
    - layer object their index


    TODO: Complete the description

    ISSUES: How one specifies layer meta attributes? Do they come automatically
    retrieving layer meta attributes is not implemented
    """

    def __init__(self, collection: pg.PgCollection, detached_layer: str = None,
                 selection_criterion: pg.WhereClause = None, progressbar: str = None, return_index: bool = True,
                 skip_empty: bool = False):
        """
        """

        # TODO: Make sure that all objects used by the class are independent copies and cannot be
        #       changed form outside. This might invalidate invariants

        if not collection.exists():
            raise pg.PgCollectionException('collection {!r} does not exist'.format(collection.name))

        self.collection = collection

        if selection_criterion is None:
            self._selection_criterion = pg.WhereClause(collection=self.collection)
        elif isinstance(selection_criterion, pg.WhereClause):
            self._selection_criterion = selection_criterion
        else:
            raise TypeError('unexpected type of selection_criterion: {!r}'.format(type(selection_criterion)))

        self.detached_layer = detached_layer
        self.progressbar = progressbar
        self.return_index = return_index

        structure = collection._structure
        assert detached_layer in structure
        assert structure[detached_layer]['layer_type'] == 'detached'
        assert structure[detached_layer]['parent'] is None
        assert structure[detached_layer]['enveloping'] is None
        # skip_empty -- whether empty sparse layers are skipped from the output;
        # works only for sparse layers;
        if skip_empty and not collection.is_sparse( detached_layer ):
            warnings.warn( ('Setting skip_empty=True only affects sparse layers, '+\
                            'but the input detached layer {!r} is not sparse. '+\
                            '').format(detached_layer) )
        self.skip_empty = skip_empty

    @property
    def sql_query(self):
        """Returns a SQL select statement that defines the subcollection.
        
        BUGS: This function does not handle fragmented layers correctly.
        We need nested sql queries to combine fragments into single object per text_id
        This must be solved by defining a view during creation of fragmented layers
        or some dark magic query composition.
        """

        # TODO: Simplify query

        selected_columns = [SQL('{}."text_id"').format(pg.layer_table_identifier(self.collection.storage, self.collection.name, self.detached_layer)),
                            SQL('{}."data"').format(pg.layer_table_identifier(self.collection.storage, self.collection.name, self.detached_layer))]

        required_layers = sorted({self.detached_layer, *self._selection_criterion.required_layers})
        
        collection_identifier = pg.collection_table_identifier(self.collection.storage, self.collection.name)

        # Required layers are part of the main collection
        if not required_layers:
            # TODO: why this branch? this cannot happen if we only allow detached layers
            if self._selection_criterion:
                return SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                collection_identifier,
                                                                self._selection_criterion)
            
            return SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns), collection_identifier)
        else:
            # Detached layers
            # Build a FROM clause with joins to required detached layers
            from_clause = pg.FromClause(self.collection, [])
            for layer in required_layers:
                join_type = None
                if self.skip_empty:
                    # check whether we have a sparse layer
                    if self.collection.is_sparse( layer ):
                        # force using inner join
                        join_type = ['INNER JOIN']
                from_clause &= pg.FromClause(self.collection, [layer], join_type)
            # Build SELECT query
            if self._selection_criterion:
                return SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                                from_clause,
                                                                self._selection_criterion)
            else:
                return SQL("SELECT {} FROM {}").format(SQL(', ').join(selected_columns),
                                                       from_clause)

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

    def select(self, additional_constraint: pg.WhereClause = None):
        """
        Returns a new subcollection that satisfies additional constraints.

        TODO: Document its usages
        """

        if additional_constraint is None:
            return self

        return PgSubCollectionLayer(collection=self.collection,
                                    selection_criterion=self._selection_criterion & additional_constraint,
                                    detached_layer=self.detached_layer,
                                    progressbar=self.progressbar,
                                    return_index=self.return_index)

    def __iter__(self):
        """
        Yields all subcollection elements ordered by the text_id 

        Depending on self.return_index and self.meta_attributes yields either
        - layer
        - text_id, layer
        - layer, meta
        - text_id, layer, meta

        The value of these configuration attributes is fixed before starting the iteration.
        """

        # TODO: Correct code
        # Check that somebody else has not deleted the collection
        if not self.collection.exists():
            raise pg.PgCollectionException('collection {!r} has been unexpectedly deleted'.format(self.collection.name))

        with self.collection.storage.conn.cursor() as c:
            c.execute(self.sql_count_query)
            logger.debug(c.query.decode())
            total = next(c)[0]

        structure = self.collection.structure
        
        with self.collection.storage.conn.cursor('read', withhold=True) as c:
            c.execute(self.sql_query)
            logger.debug(c.query.decode())
            data_iterator = Progressbar(iterable=c, total=total, initial=0, progressbar_type=self.progressbar)

            # Cash configuration attributes to protect against unexpected changes during iteration
            return_index = self.return_index
            for row in data_iterator:
                text_id = row[0]
                data_iterator.set_description('text_id: {}'.format(text_id), refresh=False)

                if row[1] is not None:
                    layer = dict_to_layer( row[1] )
                else:
                    # In case of a sparse layer, None items can 
                    # be retrieved from LEFT OUTER JOIN
                    assert structure.version >= '3.0'
                    assert self.detached_layer is not None
                    assert structure[self.detached_layer]['sparse']
                    # Fetch layer template from the structure
                    layer_template = \
                        structure[self.detached_layer]['layer_template_dict']
                    layer = dict_to_layer(layer_template)

                if return_index:
                    yield text_id, layer
                else:
                    yield layer

    def __repr__(self):
        return ('{self.__class__.__name__}('
                'collection: {self.collection.name!r}, '
                'detached_layer={self.detached_layer!r}, '
                'progressbar={self.progressbar!r}, '
                'return_index={self.return_index}, '
                'skip_empty={self.skip_empty})').format(self=self)
