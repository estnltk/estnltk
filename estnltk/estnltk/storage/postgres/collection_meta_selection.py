from typing import Sequence, List
from psycopg2.sql import Composed, Identifier, Literal, SQL
from psycopg2.errors import UndefinedTable

from estnltk import logger, Progressbar
from estnltk.storage import postgres as pg
from estnltk.storage.postgres.collection import PgCollectionException
from estnltk.storage.postgres.queries.slice_query import SliceQuery

class PgCollectionMetaSelection:
    """Read-only iterable selection over PgCollection's metadata values.
    
       The subset of selected metadata values is determined by:
       - the selected indexes: list of indexes or slice of indexes;
       - the set of meta attributes (collection's meta columns);
    """
    
    def __init__(self, collection: pg.PgCollection, 
                       selected_indexes: Sequence[int] = None,
                       selected_slice: slice = None,
                       selected_attributes: Sequence[str] = None,
                       itersize: int = 50,
                       progressbar: str = None,
                       order_by_id: bool = True):
        """
        Initiates new PgCollectionMetaSelection object.
        
        :param collection: PgCollection
            collection which metadata will be selected.
        :param selected_indexes: Sequence[int]
            indexes defining the selection over collection.
            either selected_indexes or selected_slice must
            be set, but not both simultaneously.
        :param selected_slice: slice
            slice defining the selection over collection.
            either selected_indexes or selected_slice must
            be set, but not both simultaneously.
        :param selected_attributes: Sequence[str]
            names of collection's meta columns from which 
            values will be selected. If not set (default), 
            then selects values over all meta columns.
        :param itersize: int
            the number of simultaneously fetched elements.
            defaults to 50.
        :param progressbar: str, default None
            no progressbar by default
            'ascii', 'unicode' or 'notebook'
        :param order_by_id: bool
            whether results of the selection will be ordered
            by ids of the collection. default: True.
        """
        # Validate collection
        if collection is None or (isinstance(collection, pg.PgCollection) and not collection.exists()):
            raise PgCollectionException("collection does not exist, can't create subcollection")
        elif not isinstance(collection, pg.PgCollection):
            raise TypeError('collection must be an instance of PgCollection')
        self.collection = collection
        # Validate parameters
        self.selected_indexes = None
        self.selected_slice_start = None
        self.selected_slice_stop  = None
        self.selected_attributes  = None
        if selected_indexes is not None:
            # There must be either selected indexes or selected slice, but not both
            if selected_slice is not None:
                raise ValueError('cannot set selected_indexes and selected_slice simultaneously, '+
                                 'expecting only one of the two parameters')
            if not isinstance(selected_indexes, (list, tuple)):
                raise TypeError('selected_indexes must be an instance of list')
            for key in selected_indexes:
                if not isinstance(key, int):
                    raise TypeError('unexpected selected_indexes item {}, int was expected:'.format(key))
        self.selected_indexes = selected_indexes
        if selected_slice is not None:
            if isinstance(selected_slice, slice):
                if selected_slice.step is not None:
                    raise KeyError("Invalid index slice {!r}".format(selected_slice))
                self.selected_slice_start = selected_slice.start
                self.selected_slice_stop  = selected_slice.stop
            else:
                raise TypeError('selected_slice must be an instance of slice')
        if selected_attributes is not None:
            if not isinstance(selected_attributes, (list, tuple)):
                raise TypeError('selected_attributes must be an instance of list')
            for attr in selected_attributes:
                if not isinstance(attr, str):
                    raise TypeError('unexpected selected_attributes item {}, str was expected:'.format(attr))
            self.selected_attributes = selected_attributes
        else:
            # Select all attributes
            self.selected_attributes = collection.meta_columns
        self.itersize = 50
        self.progressbar = progressbar
        self.order_by_id = order_by_id

    def __len__(self):
        """
        Executes an SQL query to find the size of the metadata selection. The result is not cached.
        """
        with self.collection.storage.conn.cursor() as cur:
            cur.execute(self.sql_count_query)
            logger.debug(cur.query.decode())
            return next(cur)[0]

    @property
    def sql_query(self):
        """Returns a SQL select statement that defines the metadata selection over collection.
        """
        storage = self.collection.storage
        collection_name = self.collection.name
        collection_identifier = pg.collection_table_identifier(storage, collection_name)

        # Build selected columns (exclude data column)
        selected_columns = [SQL('{}.{}').format(collection_identifier, column_id) for
                            column_id in map(Identifier, ['id', *self.selected_attributes])]

        # Build selection criterion
        selection_criterion = SQL('FALSE') # return nothing if no indexes were selected
        if self.selected_indexes is not None:
            selection_criterion = \
                (pg.IndexQuery( self.selected_indexes )).eval( self.collection )
        elif self.selected_slice_start is not None or \
             self.selected_slice_stop is not None:
            selection_criterion = \
                (SliceQuery( self.selected_slice_start,
                             self.selected_slice_stop )).eval( self.collection )
        query = SQL("SELECT {} FROM {} WHERE {}").format(SQL(', ').join(selected_columns),
                                                         pg.FromClause(self.collection, []),
                                                         selection_criterion)
        
        if self.order_by_id:
            return SQL('{} ORDER BY {}."id"').format(query, collection_identifier)
        else:
            return query

    @property
    def sql_count_query(self):
        return SQL('SELECT count(*) FROM ({}) AS a').format(self.sql_query)

    @property
    def sql_query_text(self):
        return self.sql_query.as_string(self.collection.storage.conn)

    __read_cursor_counter = 0

    def __iter__(self):
        # Gain few milliseconds: Find the selection size only if it used in a progress bar.
        total = 0 if self.progressbar is None else len(self)
        
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
            for row in data_iterator:
                data_iterator.set_description('collection_id: {}'.format(row[0]), refresh=False)
                meta_stop = 1 + len(self.selected_attributes)
                meta = {attr: value for attr, value in zip(self.selected_attributes, row[1:meta_stop])}
                yield row[0], meta
