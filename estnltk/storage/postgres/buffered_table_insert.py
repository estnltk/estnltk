import psycopg2
from psycopg2.sql import SQL, Identifier, Literal, Composed
from psycopg2.sql import DEFAULT as SQL_DEFAULT

from estnltk import logger

class BufferedTableInsert(object):
    """General context manager for buffered table insertions.
       Use this for large database insertions, e.g. for inserting
       texts and layers.
       
       Usage example:  TODO
    """

    def __init__(self, connection, table_identifier, columns, buffer_size=10000, query_length_limit=5000000):
        """Initializes context manager for buffered insertions.
        
        Parameters:
         
         :param connection:
            psycopg2's connection
        :param table_identifier:  psycopg2.sql.SQL
            Identifier of the table where values will be inserted.
            Must be an existing table.
        :param columns: List[str]
            Names of the table columns where values will be inserted.
        :param buffer_size: int
            Maximum buffer size (in table rows) for the insert query. 
            If the size is met or exceeded, the insert buffer will be flushed. 
            (Default: 10000)
        :param query_length_limit: int
            Soft approximate insert query length limit in unicode characters. 
            If the limit is met or exceeded, the insert buffer will be flushed.
            (Default: 5000000)

        """
        self.conn   = connection
        self.cursor = None
        self.table_identifier = table_identifier
        self.column_identifiers = SQL(', ').join(map(Identifier, columns))
        self.buffer_size = buffer_size
        self.query_length_limit = query_length_limit
        self._buffered_insert_query_length = 0
        self.buffer = []


    def __enter__(self):
        # Make new cursor for the insertion
        self.cursor = self.conn.cursor()
        # Initialize buffer
        self._buffered_insert_query_length = BufferedTableInsert.get_query_length(self.column_identifiers)
        self.buffer = []
        return self


    def __exit__(self, type, value, traceback):
        # Finally: flush the buffer at the end
        self._flush_insert_buffer()


    def insert(self, values):
        """Inserts given values into the table via buffer.
           Before the insertion, all values will be converted 
           to literals.
           Exceptionally, a value can also be psycopg2.sql.DEFAULT, 
           in which case it will not be converted.
        """
        assert self.cursor is not None
        # Convert values to literals
        converted = []
        for val in values:
            if val == SQL_DEFAULT:
                # Skip value that has already been converted
                converted.append( val )
            else:
                converted.append( Literal(val) )
        q = SQL('({})').format(SQL(', ').join( converted ))
        # Add to the buffer
        self.buffer.append( q )
        self._buffered_insert_query_length += BufferedTableInsert.get_query_length( q )
        # Do we need to flush the buffer?
        if len(self.buffer) >= self.buffer_size or self._buffered_insert_query_length >= self.query_length_limit:
            self._flush_insert_buffer()


    def _flush_insert_buffer(self):
        """Flushes the insert buffer, i.e. attempts to execute and commit the 
           insert query.
        """
        if len(self.buffer) == 0:
            return
        try:
            self.cursor.execute(SQL('INSERT INTO {} ({}) VALUES {};').format(
                           self.table_identifier,
                           self.column_identifiers,
                           SQL(', ').join(self.buffer)))
            self.cursor.connection.commit()
        except Exception:
            logger.error('flush insert buffer failed')
            logger.error('number of rows in the buffer: {}'.format(len(self.buffer)))
            logger.error('estimated insert query length: {}'.format(self._buffered_insert_query_length))
            raise
        logger.debug('flush buffer: {} rows, {} bytes, {} estimated characters'.format(
                     len(self.buffer), len(self.cursor.query), self._buffered_insert_query_length))
        self.buffer.clear()
        self._buffered_insert_query_length = BufferedTableInsert.get_query_length(self.column_identifiers)


    @staticmethod 
    def get_query_length( q ):
        """:returns
           approximate number of characters in the psycopg2 SQL query
        """
        result = 0
        if isinstance(q, Composed):
            for r in q:
                result += BufferedTableInsert.get_query_length(r)
        elif isinstance(q, (SQL, Identifier)):
            result += len(q.string)
        else:
            result += len(str(q.wrapped))
        return result

