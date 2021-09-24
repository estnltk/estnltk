from psycopg2.sql import SQL, Identifier, Literal, Composed
from psycopg2.sql import DEFAULT as SQL_DEFAULT

from estnltk import logger

class BufferedTableInsert(object):
    """General context manager for buffered table insertions.
       Use this for large database insertions, e.g. for inserting
       texts and layers.
       
       Usage example:  
       
            # Connect to the storage
            storage = PostgresStorage( ... )
            
            # Create a simple table
            table_identifier = pg.table_identifier(storage=storage, 
                                                   table_name="testing_buffered_insert")
            columns = [ ('id', 'serial PRIMARY KEY'), ('text', 'text NOT NULL') ]
            columns_sql = SQL(",\n").join(SQL("{} {}").format(Identifier(n), SQL(t)) for n, t in columns)
            
            storage.conn.commit()
            with storage.conn.cursor() as c:
                c.execute(SQL("CREATE TABLE {} ({});").format(table_identifier,
                                                              columns_sql))
                storage.conn.commit()
            
            # Perform insertions
            with BufferedTableInsert( storage.conn, 
                                      table_identifier, 
                                      columns=[c[0] for c in columns] ) as buffered_inserter:
                buffered_inserter.insert( [0, 'Tere!'] )
                buffered_inserter.insert( [1, 'Mis kell on?'] )
       
    """

    def __init__(self, connection, table_identifier, columns, buffer_size=10000, query_length_limit=5000000):
        """Initializes context manager for buffered insertions.
        
        Parameters:
         
         :param connection:
            psycopg2's connection
        :param table_identifier:  psycopg2.sql.SQL
            Identifier of the table where values will be inserted.
            Note: the table may be non-existent when the BufferedTableInsert
            object is created, but it must exist before calling object's
            insert(...) method.
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
        self.table_identifier = table_identifier
        self.column_identifiers = SQL(', ').join(map(Identifier, columns))
        self.buffer_size = buffer_size
        self.query_length_limit = query_length_limit
        # Make new cursor for the insertion
        self.cursor = self.conn.cursor()
        # Initialize buffer
        self._buffered_insert_query_length = BufferedTableInsert.get_query_length(self.column_identifiers)
        self.buffer = []


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self.close()


    def close(self):
        '''Flushes the buffer and closes this insertion manager. 
           If you are initializing BufferedTableInsert outside 
           the with statement, you should call this method 
           after all insertions have been done.'''
        # Final flushing of the buffer
        self._flush_insert_buffer()
        if self.cursor is not None:
            # Close the cursor
            self.cursor.close()


    def insert(self, values):
        """Inserts given values into the table via buffer.
           Before the insertion, all values will be converted 
           to literals.
           Exceptionally, a value can also be psycopg2.sql.DEFAULT, 
           in which case it will not be converted.
           
           Note: this method assumes that the table, where values
           will be inserted, has already been created.
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
        # Find out how much the query length and the buffer size will increase
        added_query_length = BufferedTableInsert.get_query_length( q )
        # Do we need to flush the buffer before appending?
        if len(self.buffer) + 1 >= self.buffer_size or \
           self._buffered_insert_query_length + added_query_length >= self.query_length_limit:
            self._flush_insert_buffer()
        # Add to the buffer
        self.buffer.append( q )
        self._buffered_insert_query_length += added_query_length


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
        except Exception as ex:
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

