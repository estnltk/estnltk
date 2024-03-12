"""Test pgcollection's hide documents functionality.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import os
import random
import unittest

from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.errors import DuplicateObject

from estnltk_core import Layer
from estnltk import Text
from estnltk import logger
from estnltk.storage import postgres as pg
from estnltk.storage.postgres import LayerQuery
from estnltk.storage.postgres import PgCollection
from estnltk.storage.postgres import PgCollectionException
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import RowMapperRecord
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import layer_table_exists
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_name
from estnltk.storage.postgres import count_rows

from estnltk.taggers import ParagraphTokenizer

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))

# Attempt to get name of the pg admin user/role 
# (tests will be run only if that environment variable is defined)
PG_ADMIN_USER = os.environ.get('PG_ADMIN_USER', None)

class TestHiddenDocumentsBase(unittest.TestCase):

    def setUp(self):
        self.schema = "test_layer"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=self.schema, dbname='test_db', \
                                       create_schema_if_missing=True)
        # Name of the user role affected by the row level security. 
        # This role will be created from the scratch during the test
        self.user_role = 'normal_user'
        # Name of the admin user. Must be an existing role with 
        # approriate privileges
        self.admin_role = PG_ADMIN_USER

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    # ==============================================================================
    #    Creating, switching & revoking user roles
    # ==============================================================================

    def _create_role( self, schema, role_name='normal_user' ):
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( SQL('CREATE ROLE {}'.format(role_name) ) )
            except DuplicateObject as duplicateErr:
                # psycopg2.errors.DuplicateObject: role "normal_user" already exists
                pass
            except:
                raise
            try:
                # Grant reading rights inside the schema. Following the guide:
                #   https://aws.amazon.com/blogs/database/managing-postgresql-users-and-roles/
                # Grant rights to "look up" objects within the schema
                cursor.execute( \
                    SQL('GRANT USAGE ON SCHEMA {} TO {}').format(Identifier(schema), \
                                                                 Identifier(role_name)) \
                )
                # Grant SELECT access to existing tables and views in the schema
                cursor.execute( \
                    SQL('GRANT SELECT ON ALL TABLES IN SCHEMA {} TO {}').format(Identifier(schema), \
                                                                                Identifier(role_name)) \
                )
                # Grant SELECT access to future tables and views in the schema
                cursor.execute( \
                    SQL('ALTER DEFAULT PRIVILEGES IN SCHEMA {} GRANT SELECT ON TABLES TO {}').format(Identifier(schema), \
                                                                                                     Identifier(role_name)) \
                )
                # Grant SELECT access to existing sequences in the schema
                cursor.execute( \
                    SQL('GRANT SELECT ON ALL SEQUENCES IN SCHEMA {} TO {}').format(Identifier(schema), \
                                                                                   Identifier(role_name)) \
                )
                # Grant SELECT access to future sequences in the schema
                cursor.execute( \
                    SQL('ALTER DEFAULT PRIVILEGES IN SCHEMA {} GRANT SELECT ON SEQUENCES TO {}').format(Identifier(schema), \
                                                                                                        Identifier(role_name)) \
                )
            except:
                raise

    def _switch_to_role( self, role_name ):
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( SQL('SET ROLE {}'.format(role_name)) )
            except:
                raise

    def _drop_role( self, schema, role_name='normal_user' ):
        with self.storage.conn.cursor() as cursor:
            try:
                # Remove all privileges
                cursor.execute( \
                    SQL('REVOKE ALL ON SCHEMA {} FROM {}').format(Identifier(schema), 
                                                                  Identifier(role_name)) \
                )
                cursor.execute( SQL('DROP OWNED BY {}').format( Identifier(role_name) ) )
            except:
                raise
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( SQL('DROP ROLE {}').format( Identifier(role_name) ) )
            except:
                raise

    # ==============================================================================
    #    Changing row level policy & querying for row status
    # ==============================================================================

    def _add_hiding_policy( self, collection_name ):
        table_id = pg.collection_table_identifier(self.storage, collection_name)
        query = SQL('ALTER TABLE {} ENABLE ROW LEVEL SECURITY').format( table_id )
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( query )
            except:
                raise
        query = SQL('CREATE POLICY hide_deleted_rows ON {} FOR SELECT USING (hidden = False)').format( table_id )
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( query )
            except:
                raise

    def _query_hidden_status( self, collection_name ):
        table_id = pg.collection_table_identifier(self.storage, collection_name)
        query = SQL('SELECT id, hidden FROM {} ORDER BY id').format( table_id )
        rows = []
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( query )
                for row in cursor.fetchall():
                    rows.append( row )
            except:
                raise
        return rows

    def _hide_document( self, collection_name, text_id ):
        table_id = pg.collection_table_identifier(self.storage, collection_name)
        query = SQL('UPDATE {} SET hidden = True WHERE id = {}').format( table_id, Literal(text_id) )
        rows = []
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( query )
            except:
                raise

    def _remove_hiding_policy( self, collection_name ):
        table_id = pg.collection_table_identifier(self.storage, collection_name)
        query = SQL('DROP POLICY hide_deleted_rows ON {}').format( table_id )
        with self.storage.conn.cursor() as cursor:
            try:
                cursor.execute( query )
            except:
                raise

    # ==============================================================================

    @unittest.skipIf('hidden' not in pg.COLLECTION_BASE_COLUMNS(), 
                     "collection base columns do not have 'hidden' column required for this test")
    @unittest.skipIf(PG_ADMIN_USER is None, 
                     "role name of a Postgres admin user is required. "+\
                     "set environment variable PG_ADMIN_USER to enable this test." )
    def test_basic_hide_documents(self):
        self._switch_to_role( self.admin_role )
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        # Create role of normal_user (has SELECT privileges)
        self._create_role( self.schema, role_name=self.user_role )

        # Insert all documents
        with collection.insert() as collection_insert:
            text1 = Text('See on esimene lause').tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text('See on teine lause').tag_layer(["sentences"])
            collection_insert(text2)
            text3 = Text('Kolmas lause').tag_layer(["sentences"])
            collection_insert(text3)
            text4 = Text('Neljaski lause').tag_layer(["sentences"])
            collection_insert(text4)
            text5 = Text('Lõppu veel viies lause.').tag_layer(["sentences"])
            collection_insert(text5)
        # Insert detached layers
        para_tokenizer = ParagraphTokenizer()
        collection.create_layer( tagger=para_tokenizer )
        
        # Define a row-level security policy
        self._add_hiding_policy( collection_name )
        
        # Assert that everything is accessible at first
        self._switch_to_role( self.user_role )
        self.assertEqual( len(collection), 5)
        self.assertListEqual( self._query_hidden_status( collection_name ), \
                              [(0, False), (1, False), (2, False), (3, False), (4, False)] )

        # Hide documents:
        self._switch_to_role( self.admin_role )
        self._hide_document( collection_name, 2 )
        self._hide_document( collection_name, 3 )

        # A) Query collection table with the normal user
        self._switch_to_role( self.user_role )
        self.assertEqual( len(collection), 3)
        self.assertListEqual( self._query_hidden_status( collection_name ), \
                              [(0, False), (1, False), (4, False)] )

        with self.assertRaises(KeyError):
            # KeyError: 'Index 2 is outside of the collection'
            collection[2]
        with self.assertRaises(KeyError):
            # KeyError: 'Index 3 is outside of the collection'
            collection[3]

        # B) Query collection with detached layers
        items = []
        for doc_id, doc in collection.select(layers = ['paragraphs']):
            items.append( (doc_id, doc.layers) )
        self.assertListEqual( items, \
            [ (0, {'words', 'sentences', 'paragraphs'}), \
              (1, {'words', 'sentences', 'paragraphs'}), \
              (4, {'words', 'sentences', 'paragraphs'})  ] \
        )

        # Clean up
        self._switch_to_role( self.admin_role )
        # Remove normal_user role 
        self._drop_role( self.schema, role_name=self.user_role )
        # Remove security policy
        self._remove_hiding_policy( collection_name )

        # Remove collection
        self.storage.delete_collection(collection.name)



if __name__ == '__main__':
    unittest.main()
