"""Test that a syntax_v0 layer can be stored in / loaded from PgCollection.

Requires ~/.pgpass file with database connection settings to `test_db` database.
Schema/table creation and read/write rights are required.

"""
import random
import os.path
import unittest
from collections import OrderedDict

from psycopg2.sql import SQL, Identifier
from psycopg2.errors import DuplicateSchema

from estnltk_core.layer_operations import split_by_sentences

from estnltk import Text
from estnltk import logger
from estnltk.common import abs_path
from estnltk.converters import dict_to_layer
from estnltk.converters import dict_to_text, text_to_dict
from estnltk.converters.conll.conll_importer import conll_to_text

from estnltk.storage import postgres as pg
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import delete_schema

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))

test_example_syntax_file = \
    abs_path('storage/postgres/tests/test_example_syntax.conll')

class TestPgCollectionStoreSyntaxV0Layer(unittest.TestCase):

    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db', \
                                       create_schema_if_missing=True)


    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()


    def test_store_and_load_syntax_v0_layer(self):
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)
        
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
        self.storage.delete_collection(collection.name)


    @unittest.skipIf(not os.path.exists(test_example_syntax_file),
                     reason="missing input file {!r}".format(test_example_syntax_file))
    def test_store_and_load_syntax_v0_tutorial_example(self):
        # syntax saving and loading test based on former tutorial:
        #  https://github.com/estnltk/estnltk/blob/93727e60dff115707c9b1a88b17e6b92e8c808a4/tutorials/storage/storing_text_objects_with_syntax_layer_in_postgres.ipynb
        collection_name = get_random_collection_name()
        collection = self.storage.add_collection(collection_name)

        # Load syntax from conll file and validate data
        conll_text = conll_to_text(file=test_example_syntax_file, syntax_layer='malt_1')
        assert conll_text.layers == {'malt_1', 'words', 'sentences'}
        assert len(conll_text['sentences']) == 7
        assert len(conll_text['malt_1']) == 88
        assert len(conll_text['words']) == 88
        assert conll_text['malt_1'].serialisation_module == 'syntax_v0'
        conll_texts = split_by_sentences(conll_text, layers_to_keep=['words', 'malt_1'])
        for text in conll_texts:
            assert text.layers == {'malt_1', 'words'}
            assert text['malt_1'].serialisation_module == 'syntax_v0'

        # Perform insertion
        with collection.insert() as collection_insert:
            for text in conll_texts:
                collection_insert(text)
        
        # Validate that db content matches content from conll
        assert len(collection) == 7
        assert set(collection.layers) == {'malt_1', 'words'}
        collection.selected_layers = ['malt_1', 'words']
        for tid, conll_text in enumerate(conll_texts):
            text_from_collection = collection[tid]
            assert text_from_collection.text == conll_text.text
            assert text_from_collection['malt_1'].serialisation_module == 'syntax_v0'
            assert text_to_dict(text_from_collection) == text_to_dict(conll_text)

        self.storage.delete_collection(collection.name)

if __name__ == '__main__':
    unittest.main()
