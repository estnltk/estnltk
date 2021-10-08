"""Test that a syntax_v0 layer can be stored in / loaded from PgCollection.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import unittest
from collections import OrderedDict

from psycopg2.sql import SQL, Identifier
from psycopg2.errors import DuplicateSchema

from estnltk import Text
from estnltk import logger
from estnltk.converters import dict_to_layer

from estnltk.storage import postgres as pg
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import create_schema, delete_schema

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestPgCollectionStoreSyntaxV0Layer(unittest.TestCase):

    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')
        try:
            create_schema(self.storage)
        except DuplicateSchema as ds_error:
            # If some of the previous database tests failed and did not clean 
            # up the schema after the test, then we get a DuplicateSchema error.
            # We can 'restart' by deleting the old schema and creating a new one
            delete_schema(self.storage)
            create_schema(self.storage)
        except:
            raise


    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def test_store_and_load_syntax_v0_layer(self):
        collection_name = get_random_collection_name()
        collection = self.storage[collection_name]
        collection.create()
        
        text_1 = Text('Ühel kenal päeval')
        syntax_layer = dict_to_layer( \
                {'ambiguous': False,
                 'attributes': ('id',
                                'lemma',
                                'upostag',
                                'xpostag',
                                'feats',
                                'head',
                                'deprel',
                                'deps',
                                'misc',
                                'parent_span',
                                'children'),
                 'enveloping': None,
                 'meta': {},
                 'name': 'stanza_syntax',
                 'parent': None,
                 'serialisation_module': 'syntax_v0',
                 'spans': [{'annotations': [{'deprel': 'det',
                                             'deps': '_',
                                             'feats': {'ad': 'ad', 'sg': 'sg'},
                                             'head': 3,
                                             'id': 1,
                                             'lemma': 'üks',
                                             'misc': '_',
                                             'upostag': 'P',
                                             'xpostag': 'P'}],
                            'base_span': (0, 4)},
                           {'annotations': [{'deprel': 'amod',
                                             'deps': '_',
                                             'feats': {'ad': 'ad', 'pos': 'pos', 'sg': 'sg'},
                                             'head': 3,
                                             'id': 2,
                                             'lemma': 'kena',
                                             'misc': '_',
                                             'upostag': 'A',
                                             'xpostag': 'A'}],
                            'base_span': (5, 10)},
                           {'annotations': [{'deprel': 'root',
                                             'deps': '_',
                                             'feats': {'ad': 'ad', 'com': 'com', 'sg': 'sg'},
                                             'head': 0,
                                             'id': 3,
                                             'lemma': 'päev',
                                             'misc': '_',
                                             'upostag': 'S',
                                             'xpostag': 'S'}],
                            'base_span': (11, 17)}]} )
        text_1.add_layer( syntax_layer )
        
        with collection.insert() as collection_insert:
            collection_insert( text_1 )

        # 1) Validate that Text with syntax layer was successfully inserted
        assert len(collection) == 1

        # 2) Validate that Text with syntax layer can be successfully loaded
        loaded_text = collection[0]
        assert loaded_text.text == text_1.text
        assert loaded_text.layers == { 'stanza_syntax' }
        
        # Validate parent_span/children attributes
        assert list( loaded_text['stanza_syntax'].parent_span ) == [ loaded_text['stanza_syntax'][2], \
                                                                     loaded_text['stanza_syntax'][2], \
                                                                     None ]
        assert list( loaded_text['stanza_syntax'].children ) == [ (), \
                                                                  (), \
                                                                  ( loaded_text['stanza_syntax'][0], \
                                                                    loaded_text['stanza_syntax'][1] ) ]
        collection.delete()


if __name__ == '__main__':
    unittest.main()
