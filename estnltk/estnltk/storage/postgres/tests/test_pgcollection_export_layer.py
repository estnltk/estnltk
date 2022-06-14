"""Test PgCollection's export_layer functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest
from collections import OrderedDict

from psycopg2.sql import SQL, Identifier
from psycopg2.errors import DuplicateSchema

from estnltk import Text
from estnltk import Layer
from estnltk import logger

from estnltk.storage import postgres as pg
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres.collection import RowMapperRecord
from estnltk.storage.postgres import create_schema, delete_schema

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgCollectionExportLayer(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            # TODO: for some reason we get DuplicateSchema error. Unexpected?
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise


    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def _make_simple_query_on_table( self, table_identifier ):
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


    def test_export_layer(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), ('text_name', 'str')]))

        text_1 = Text('Esimene tekst.').tag_layer('words')
        text_2 = Text('Teine tekst').tag_layer('words')
        text_3 = Text('Kolmas tekst').tag_layer('words')

        with collection.insert() as collection_insert:
            collection_insert( text_1, meta_data={'text_id':1, 'text_name':'esimene yllitis'} )
            collection_insert( text_2, meta_data={'text_id':2, 'text_name':'teine yllitis'} )
            collection_insert( text_3, meta_data={'text_id':3, 'text_name':'kolmas yllitis'} )

        #
        # 1) Export layer without attributes nor metadata
        #
        collection.export_layer('words', [])
        table_name='{}__{}__export'.format(collection_name, 'words')
        assert pg.table_exists(self.storage, table_name)
        # Validate exported annotations
        table_identifier = pg.table_identifier(storage=self.storage, table_name=table_name)
        table_entries = self._make_simple_query_on_table( table_identifier )
        expected_entries = \
            [(1, 0, 0, 0, 7),
             (2, 0, 1, 8, 13),
             (3, 0, 2, 13, 14),
             (4, 1, 0, 0, 5),
             (5, 1, 1, 6, 11),
             (6, 2, 0, 0, 6),
             (7, 2, 1, 7, 12)]
        assert table_entries == expected_entries

        #
        # 2) Export layer with attributes, but no metadata
        #
        table_name='words_second_export'
        collection.export_layer('words', ('normalized_form',), table_name=table_name)
        assert pg.table_exists(self.storage, table_name)
        # Validate exported annotations
        table_identifier = pg.table_identifier(storage=self.storage, table_name=table_name)
        table_entries = self._make_simple_query_on_table( table_identifier )
        expected_entries = \
            [(1, 0, 0, 0, 7, None),
             (2, 0, 1, 8, 13, None),
             (3, 0, 2, 13, 14, None),
             (4, 1, 0, 0, 5, None),
             (5, 1, 1, 6, 11, None),
             (6, 2, 0, 0, 6, None),
             (7, 2, 1, 7, 12, None)]
        assert table_entries == expected_entries
        
        #
        # 3) Export layer with attributes and metadata
        #
        table_name='words_third_export'
        collection.export_layer('words', ('normalized_form',), collection_meta=('text_name',), table_name=table_name)
        assert pg.table_exists(self.storage, table_name)
        # Validate exported annotations
        table_identifier = pg.table_identifier(storage=self.storage, table_name=table_name)
        table_entries = self._make_simple_query_on_table( table_identifier )
        expected_entries = \
            [(1, 0, 0, 0, 7, None, 'esimene yllitis'),
             (2, 0, 1, 8, 13, None, 'esimene yllitis'),
             (3, 0, 2, 13, 14, None, 'esimene yllitis'),
             (4, 1, 0, 0, 5, None, 'teine yllitis'),
             (5, 1, 1, 6, 11, None, 'teine yllitis'),
             (6, 2, 0, 0, 6, None, 'kolmas yllitis'),
             (7, 2, 1, 7, 12, None, 'kolmas yllitis')]
        assert table_entries == expected_entries
        
        collection.delete()


    def test_export_layer_invalid_modes(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), ('text_name', 'str')]))
        
        text_1 = Text('Esimene tekst.').tag_layer('words')
        text_2 = Text('Teine tekst').tag_layer('words')
        with collection.insert() as collection_insert:
            collection_insert( text_1, meta_data={'text_id':1, 'text_name':'esimene yllitis'} )
            collection_insert( text_2, meta_data={'text_id':2, 'text_name':'teine yllitis'} )
        
        # 1) export_layer mode='APPEND' cannot be use with non-existing table
        with self.assertRaises(pg.PgCollectionException) as exception:
            collection.export_layer('words', [], mode='APPEND')
        
        collection.export_layer('words', [])
        
        # 2) export_layer mode='NEW' cannot be use with existing table
        with self.assertRaises(pg.PgCollectionException) as exception:
            collection.export_layer('words', [])
        
        collection.delete()


    def test_export_layer_appending(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), ('text_name', 'str')]))

        text_1 = Text('Esimene tekst.').tag_layer('words')
        text_2 = Text('Teine tekst').tag_layer('words')

        with collection.insert() as collection_insert:
            collection_insert( text_1, meta_data={'text_id':1, 'text_name':'esimene yllitis'} )
            collection_insert( text_2, meta_data={'text_id':2, 'text_name':'teine yllitis'} )
        
        # 1) Export first time
        collection.export_layer('words', ('normalized_form',), collection_meta=('text_name',))
        table_name='{}__{}__export'.format(collection_name, 'words')
        assert pg.table_exists(self.storage, table_name)
        
        # 2) Export second time with appending
        collection.export_layer('words', ('normalized_form',), collection_meta=('text_name',), mode='append')
        # Validate exported annotations
        table_identifier = pg.table_identifier(storage=self.storage, table_name=table_name)
        table_entries = self._make_simple_query_on_table( table_identifier )
        # Note: there will be duplicate entries, but currently it's expected behaviour
        expected_entries = \
            [(1, 0, 0, 0, 7, None, 'esimene yllitis'),
             (2, 0, 1, 8, 13, None, 'esimene yllitis'),
             (3, 0, 2, 13, 14, None, 'esimene yllitis'),
             (4, 1, 0, 0, 5, None, 'teine yllitis'),
             (5, 1, 1, 6, 11, None, 'teine yllitis'),
             (6, 0, 0, 0, 7, None, 'esimene yllitis'),
             (7, 0, 1, 8, 13, None, 'esimene yllitis'),
             (8, 0, 2, 13, 14, None, 'esimene yllitis'),
             (9, 1, 0, 0, 5, None, 'teine yllitis'),
             (10, 1, 1, 6, 11, None, 'teine yllitis')]
        assert table_entries == expected_entries
        
        collection.delete()


    def test_export_sparse_layer(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create(meta=OrderedDict([('text_id', 'int'), ('text_name', 'str')]))
        # Assert structure version 3.0+ (required for sparse layers)
        assert collection.version >= '3.0'

        text_1 = Text('Esimene tekst.')
        text_2 = Text('Teine tekst')
        text_3 = Text('Kolmas tekst')
        text_4 = Text('Viimane tekst')

        with collection.insert() as collection_insert:
            collection_insert( text_1, meta_data={'text_id':1, 'text_name':'esimene yllitis'} )
            collection_insert( text_2, meta_data={'text_id':2, 'text_name':'teine yllitis'} )
            collection_insert( text_3, meta_data={'text_id':3, 'text_name':'kolmas yllitis'} )
            collection_insert( text_4, meta_data={'text_id':4, 'text_name':'viimne yllitis'} )

        # Create a sparse layer
        def my_row_mapper(row):
            text_id, text = row[0], row[1]
            status = {}
            layer = Layer('my_sparse_layer', attributes=['attr1'])
            if text_id % 2 == 0:
                # Fill in only every second layer
                layer.add_annotation( (0, 4), attr1='{} snippet'.format(text_id) )
            return RowMapperRecord(layer=layer, meta=status)
        collection.create_layer( layer_name='my_sparse_layer', 
                                 data_iterator=collection.select(), 
                                 row_mapper=my_row_mapper, 
                                 sparse=True )

        # Export sparse table
        collection.export_layer('my_sparse_layer', ('attr1',), collection_meta=('text_name',))
        table_name='{}__{}__export'.format(collection_name, 'my_sparse_layer')
        assert pg.table_exists(self.storage, table_name)
        table_identifier = pg.table_identifier(storage=self.storage, table_name=table_name)
        table_entries = self._make_simple_query_on_table( table_identifier )
        expected_entries = \
            [(1, 0, 0, 0, 4, '0 snippet', 'esimene yllitis'),
             (2, 2, 0, 0, 4, '2 snippet', 'kolmas yllitis')]
        assert table_entries == expected_entries
        
        collection.delete()

if __name__ == '__main__':
    unittest.main()
