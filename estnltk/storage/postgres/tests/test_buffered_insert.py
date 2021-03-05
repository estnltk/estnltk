"""Test postgres storage buffered insert functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest
from collections import OrderedDict

from psycopg2.errors import DuplicateSchema
from psycopg2.sql import SQL, Identifier

from estnltk import Text
from estnltk import logger
from estnltk.taggers import TokensTagger
from estnltk.storage import postgres as pg

from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema
from estnltk.storage.postgres import BufferedTableInsert
from estnltk.storage.postgres import CollectionTextObjectInserter

logger.setLevel('DEBUG')


class TestBufferedTableInsert(unittest.TestCase):
    """ A small test for the basic functionality of BufferedTableInsert.
        ( we do not cover all the aspects of the class, because most of 
          the insertion functionality flows through it, and so it is 
          already heavily used in other tests ) """

    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise


    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def _create_test_table(self):
        table_identifier = pg.table_identifier(storage=self.storage, table_name="testing_buffered_table_insert")
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


    def test_simple_buffered_table_insert(self):
        # Create testing collection
        table_identifier, columns = self._create_test_table()
        
        # Perform insertions
        with BufferedTableInsert( self.storage.conn, table_identifier, columns=[c[0] for c in columns]) as buffered_inserter:
            buffered_inserter.insert( [0, 'Tere!', 'esimene lausung' ] )
            buffered_inserter.insert( [1, 'Mis kell on?', 'teine lausung' ] )
            buffered_inserter.insert( [2, 'Halloo!', 'kolmas kutsung' ] )

        # Closing buffered_inserter several times should be OK (even after the with statement)
        buffered_inserter.close()
        buffered_inserter.close()
        
        # Check inserted values
        result_rows = self._test_simple_query_on_table( table_identifier )
        expected_result_rows = [(0, 'Tere!', 'esimene lausung'),
                                (1, 'Mis kell on?', 'teine lausung'),
                                (2, 'Halloo!', 'kolmas kutsung')]
        self.assertListEqual(result_rows, expected_result_rows)


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestCollectionTextObjectInserter(unittest.TestCase):
    """Smoke testing for CollectionTextObjectInserter."""

    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise


    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def _create_test_collection(self):
        collection = self.storage[get_random_collection_name()]
        collection.create( meta=OrderedDict([('subcorpus', 'str'), ('type', 'str')]) )
        return collection


    def test_simple_collection_text_object_insert(self):
        # Create testing collection
        collection = self._create_test_collection()
        
        # Perform first insertions
        with CollectionTextObjectInserter( collection ) as col_inserter:
            col_inserter.insert( Text( 'esimene tekst' ), meta_data={} )
            col_inserter.insert( Text( 'teine tekst' ), meta_data={} )

        # Check collection length
        self.assertEqual(len(collection), 2)
        
        # Perform more insertions
        with CollectionTextObjectInserter( collection ) as col_inserter:
            col_inserter.insert( Text( 'kolmas tekst' ), meta_data={'subcorpus':'argikõned'} )
            col_inserter.insert( Text( 'neljas tekst' ), meta_data={'type':'artikkel'} )

        # Check collection length
        self.assertEqual(len(collection), 4)
        
        # Try an illegal insert: insert Text object that has wrong structure
        with CollectionTextObjectInserter( collection ) as col_inserter:
            with self.assertRaises( AssertionError ):
                col_inserter.insert( Text( 'viies tekst' ).tag_layer('words'), meta_data={} )

        # Add a detached layer
        collection.create_layer(tagger=TokensTagger())
        
        # Try an illegal insert: insert Text object after a detached layer has been added
        with self.assertRaises( Exception ):
            with CollectionTextObjectInserter( collection ) as col_inserter:
                col_inserter.insert( Text( 'kuues tekst' ), meta_data={} )

        # Check collection length
        self.assertEqual(len(collection), 4)

        # Clean up
        collection.delete()


if __name__ == '__main__':
    unittest.main()
