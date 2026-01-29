# ===================================================================
#    Buffered insertion into multiple tables of the collection
# ===================================================================

from collections import OrderedDict

from psycopg2.sql import SQL, Identifier, Literal, Composed
from psycopg2.sql import DEFAULT as SQL_DEFAULT
from psycopg2.extensions import STATUS_BEGIN
from psycopg2 import Error as psycopg2_Error

from estnltk import logger

from estnltk.storage import postgres as pg
from estnltk.storage.postgres import BufferedTableInsert


class BufferedMultiTableInsert(object):
    '''A buffered inserter that maintains insertion buffers over multiple tables. 
       Allows to insert into multiple tables simultaneously. 
    
       Builds upon: 
       https://github.com/estnltk/estnltk-workflows/blob/98109d50f6901a8c6baa422ee960faefee0274cf/enc_workflows/x_db_utils.py
       https://github.com/estnltk/estnltk/blob/ab676f28df06cabee3b7e1f17c9eeaa1f635831d/estnltk/estnltk/storage/postgres/context_managers/buffered_table_insert.py 
    '''

    def __init__(self, storage, tables_columns, buffer_size=10000, query_length_limit=5000000, \
                       log_doc_completions=False):
        """Initializes context manager for buffered insertions.
        
        Parameters:
        
        :param storage: pg.PostgresStorage
            Postgres Storage into which insertions will be made.
        :param tables_columns:  List[Tuple[str, psycopg2.sql.SQL, List[str]]]
            List with table names, SQL identifiers and corresponding table column
            names into which insertions will be made. 
            Note: tables must already exist when the BufferedMultiTableInsert 
            object is created.
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the insertion buffer of any of the tables meets or exceeds this 
            size, then the insert buffer will be flushed. 
            (Default: 10000)
        :param query_length_limit: int
            Soft approximate insert query length limit in unicode characters. 
            If the limit is met or exceeded, the insert buffer will be flushed.
            (Default: 5000000)
        :param log_doc_completions: bool
            Whether completed insertions of documents will be explicitly logged.
            (Default: False)
        """
        self.conn = storage.conn
        self.storage = storage
        self.tables_columns = OrderedDict()
        for items in tables_columns:
            assert len(items) == 3, f'(!) Unexpected values {items!r} for tables_columns row. '+\
                                    'Expected: [table_name:str, SQL_table_identifier:Union[SQL,Composed], list_of_column_names:List[str]]'
            assert isinstance(items[0], str), \
                f'(!) Unexpected type {type(items[0])} for table_name: str'
            table_name = items[0]
            # Check for the existence of the table
            if not pg.table_exists( storage, table_name, omit_commit=True, omit_rollback=True ):
                raise ValueError(f'(!) Table {table_name!r} does not exist. ')
            assert isinstance(items[1], (SQL, Composed)), \
                f'(!) Unexpected type {type(items[1])} for SQL_table_identifier: Union[SQL,Composed].'
            table_sql_id = items[1]
            assert isinstance(items[2], list), \
                f'(!) Unexpected type {type(items[2])} for list_of_column_names: List[str]'
            column_identifiers = SQL(', ').join(map(Identifier, items[2]))
            self.tables_columns[table_name] = (table_sql_id, column_identifiers, items[2])
        self.buffer_size = buffer_size
        self.query_length_limit = query_length_limit
        self.log_doc_completions = log_doc_completions
        # Make new cursor for the insertion
        self.cursor = self.conn.cursor()
        # Initialize buffers -- each table has its own buffer
        self._buffered_insert_query_length = 0
        self.table_buffer = {}
        self.completion_markers = {}
        for table in self.tables_columns.keys():
            self.table_buffer[table] = []
            self.completion_markers[table] = []
            column_identifiers = self.tables_columns[table][1]
            self._buffered_insert_query_length += BufferedTableInsert.get_query_length(column_identifiers)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        '''Flushes the buffer and closes this insertion manager. 
           If you are initializing BufferedMultiTableInsert 
           outside the with statement, you should call this method 
           after all insertions have been done.'''
        # Final flushing of the buffer
        self._flush_insert_buffer()
        if self.cursor is not None:
            # Close the cursor
            self.cursor.close()

    def insert(self, table_name, values, doc_completed:int=None):
        """Inserts given values into the table via buffer. 
           Before the insertion, all values will be converted to 
           literals.
           Exceptionally, a value can also be psycopg2.sql.DEFAULT, 
           in which case it will not be converted.
           Optionally, if completion marker `doc_completed` is not 
           `None`, but points to a document id, then records that 
           the current insertion completes the data of the document 
           in all tables. This is used for book-keeping about which 
           of the documents have been completely inserted.
           Note: this method assumes that the table, where values
           will be inserted, has already been created.
        """
        assert self.cursor is not None
        assert self.conn.autocommit == False
        if table_name not in self.tables_columns.keys():
            raise KeyError(f'(!) Unexpected table {table_name!r}: no instructions '+\
                           'available on how to insert into that table.')
        column_names = self.tables_columns[table_name][2]
        assert len( values ) == len( column_names ), \
            f'(!) Number of insertable values: {len(values)} != number of table {table_name!r} columns: {len(column_names)}'
        # Convert values to literals
        converted = []
        for val in values:
            if val == SQL_DEFAULT:
                # Skip value that has already been converted
                converted.append( val )
            else:
                converted.append( Literal(val) )
        q_vals = SQL('({})').format(SQL(', ').join( converted ))
        # Find out how much the query length and the buffer size will increase
        added_query_length = BufferedTableInsert.get_query_length( q_vals )
        cur_buffer = self.table_buffer[table_name]
        # Completion marker: after this insertion, all should be completed for the given document
        if doc_completed is not None:
            self.completion_markers[table_name].append( doc_completed )
        # Do we need to flush the buffer before appending?
        if len(cur_buffer) + 1 >= self.buffer_size or \
           self._buffered_insert_query_length + added_query_length >= self.query_length_limit:
            self._flush_insert_buffer()
        # Add to the buffer
        self.table_buffer[table_name].append( q_vals )
        self._buffered_insert_query_length += added_query_length

    def has_unflushed_buffers(self):
        return any([ len(self.table_buffer[k]) > 0 for k in self.table_buffer.keys() ])

    def incomplete_documents(self):
        return [v for t in self.completion_markers.keys() for v in self.completion_markers[t]]

    def _flush_insert_buffer(self):
        """Flushes the insert buffer, i.e. attempts to execute and commit 
           insert queries of all the tables.
        """
        if not self.has_unflushed_buffers():
            return
        # Flush buffers of all tables
        rows_flushed = 0
        bytes_flushed = 0
        for table in self.tables_columns.keys():
            table_identifier = self.tables_columns[table][0]
            column_identifiers = self.tables_columns[table][1]
            buffer = self.table_buffer[table]
            if len( buffer ) > 0:
                try:
                    self.cursor.execute(SQL('INSERT INTO {} ({}) VALUES {};').format(
                                   table_identifier,
                                   column_identifiers,
                                   SQL(', ').join(buffer)))
                    rows_flushed += len(buffer)
                    bytes_flushed += len(self.cursor.query)
                    if len( self.completion_markers[table] ) > 0:
                        for doc_id in self.completion_markers[table]:
                            if self.log_doc_completions:
                                logger.info('completed insertion of document {}'.format(doc_id))
                        self.completion_markers[table].clear()
                except Exception as ex:
                    if issubclass(type(ex), psycopg2_Error):
                        # Log more information about psycopg2_Error
                        if ex.diag.message_primary is not None:
                            logger.error('{}: {}'.format( ex.__class__.__name__, \
                                                          ex.diag.message_primary ))
                        if ex.diag.message_detail is not None:
                            logger.error('DETAIL: {}'.format( ex.diag.message_detail ))
                        if ex.diag.message_hint is not None:
                            logger.error('HINT: {}'.format( ex.diag.message_hint ))
                        if ex.diag.context is not None:
                            logger.error('CONTEXT: {}'.format( ex.diag.context ))
                    logger.error(f'flush insert buffer failed at table {table}')
                    if rows_flushed > 0:
                        logger.error('number of rows inserted: {}'.format(rows_flushed))
                    logger.error('number of rows still in the buffer: {}'.format(len(buffer)))
                    incomplete_docs = self.incomplete_documents()
                    if incomplete_docs:
                        logger.error('partially inserted documents: {}'.format(incomplete_docs))
                    logger.error('estimated total insert query length: {}'.format(self._buffered_insert_query_length))
                    self.cursor.connection.rollback()
                    raise
                finally:
                    if self.cursor.connection.status == STATUS_BEGIN:
                        # no exception, transaction in progress
                        self.cursor.connection.commit()
        # Log progress
        logger.debug('flush buffer: {} rows, {} bytes, {} estimated characters'.format(
                     rows_flushed, bytes_flushed, self._buffered_insert_query_length))
        # Clear / reset buffer
        self._buffered_insert_query_length = 0
        for table in self.tables_columns.keys():
            self.table_buffer[table].clear()
            column_identifiers = self.tables_columns[table][1]
            self._buffered_insert_query_length += BufferedTableInsert.get_query_length(column_identifiers)

