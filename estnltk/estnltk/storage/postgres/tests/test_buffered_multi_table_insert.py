"""Test postgres storage buffered insertion into multiple tables simultaneously.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.
"""
import json
import random
import unittest
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema
from psycopg2.sql import SQL, Identifier

from estnltk import Text
from estnltk import get_logger_with_tqdm_handler
from estnltk.taggers import TokensTagger
from estnltk.storage import postgres as pg

from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import BufferedMultiTableInsert

logger = get_logger_with_tqdm_handler('DEBUG')


class TestBufferedMultiTableInsertInsert(unittest.TestCase):
    """ A small test for the basic functionality of BufferedTableInsert.
        ( we do not cover all the aspects of the class, because most of 
          the insertion functionality flows through it, and so it is 
          already heavily used in other tests ) """

    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)


    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def _create_test_table(self, name):
        table_identifier = pg.table_identifier(storage=self.storage, table_name=name)
        columns = [
            ('id', 'serial PRIMARY KEY'),
            ('text', 'text NOT NULL'),
            ('text_meta', 'text NOT NULL'),
        ]
        columns_sql = SQL(",\n").join(SQL("{} {}").format(Identifier(n), SQL(t)) for n, t in columns)
        self.storage.conn.commit()
        with self.storage.conn.cursor() as c:
            logger.debug(c.query)
            c.execute(SQL("CREATE TABLE {} ({});").format(table_identifier,
                                                          columns_sql))
            logger.debug(c.query)
            self.storage.conn.commit()
        return table_identifier, columns


    def _test_simple_query_on_table( self, table_identifier ):
        query = SQL('SELECT * FROM {}').format( table_identifier )
        rows = []
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( query )
            except:
                raise
            for row in cursor.fetchall():
                rows.append( row )
        return rows


    def test_simple_buffered_multi_table_insert(self):
        # Create testing collection
        table1_identifier, table1_columns = self._create_test_table('test_multitab_buff_1')
        table2_identifier, table2_columns = self._create_test_table('test_multitab_buff_2')
        table3_identifier, table3_columns = self._create_test_table('test_multitab_buff_3')
        table1_column_names = [column for (column, column_type) in table1_columns]
        table2_column_names = [column for (column, column_type) in table2_columns]
        table3_column_names = [column for (column, column_type) in table3_columns]
        
        # Perform insertions
        with BufferedMultiTableInsert( self.storage, 
                                       [('test_multitab_buff_1', table1_identifier, table1_column_names),
                                        ('test_multitab_buff_2', table2_identifier, table2_column_names),
                                        ('test_multitab_buff_3', table3_identifier, table3_column_names)]) as buffered_inserter:
            buffered_inserter.insert( 'test_multitab_buff_1', [0, 'Tere!', 'esimene lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_2', [0, 'Hei!', 'esimene lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_3', [0, 'Halloo!', 'esimene lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_1', [1, 'Mis kell on?', 'teine lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_2', [1, 'Paljonko kello on?', 'teine lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_3', [1, 'Wie spät ist es?', 'teine lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_1', [2, 'Kapsapuder?!', 'kolmas lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_2', [2, 'Mitään ei tapahtunut', 'kolmas lausung' ] )
            buffered_inserter.insert( 'test_multitab_buff_3', [2, 'Doch!', 'kolmas lausung' ] )

        # Closing buffered_inserter several times should be OK (even after the with statement)
        buffered_inserter.close()
        buffered_inserter.close()
        
        # Check inserted values
        result_rows1 = self._test_simple_query_on_table( table1_identifier )
        expected_result_rows1 = [(0, 'Tere!', 'esimene lausung'),
                                 (1, 'Mis kell on?', 'teine lausung'),
                                 (2, 'Kapsapuder?!', 'kolmas lausung')]
        self.assertListEqual(result_rows1, expected_result_rows1)
        result_rows2 = self._test_simple_query_on_table( table2_identifier )
        expected_result_rows2 = [(0, 'Hei!', 'esimene lausung'),
                                 (1, 'Paljonko kello on?', 'teine lausung'),
                                 (2, 'Mitään ei tapahtunut', 'kolmas lausung')]
        self.assertListEqual(result_rows2, expected_result_rows2)
        result_rows3 = self._test_simple_query_on_table( table3_identifier )
        expected_result_rows3 = [(0, 'Halloo!', 'esimene lausung'),
                                 (1, 'Wie spät ist es?', 'teine lausung'),
                                 (2, 'Doch!', 'kolmas lausung')]
        self.assertListEqual(result_rows3, expected_result_rows3)



def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))



if __name__ == '__main__':
    unittest.main()
