"""Tests PostgresStorage's view-based schema functionality: detection of view-based 
schemas and reading from collections of a view-based schema. 

Test setup creates a regular (table-based) schema, fills it with data via EstNLTK's 
interface, and then builds a second, view-based schema on top of the first one via 
raw SQL (creation of view-based schemas is currently out of the scope of EstNLTK's 
interface).

Requires ~/.pgpass file with database connection settings to `test_db` database. 
Schema/table/view creation and read/write rights are required. 
"""
import unittest
from collections import OrderedDict

from psycopg2.sql import SQL, Identifier

from estnltk import Text
from estnltk import get_logger_with_tqdm_handler

from estnltk.storage import postgres as pg
from estnltk.storage.postgres import PostgresStorage
from estnltk.storage.postgres import LayerQuery
from estnltk.storage.postgres import SubstringQuery
from estnltk.storage.postgres import delete_schema
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres.storage import PgStorageException
from estnltk.storage.postgres.storage import PgReadOnlyStorageException
from estnltk.storage.postgres.pg_operations import get_relation_kinds
from estnltk.storage.postgres.pg_operations import TABLE_RELKINDS
from estnltk.storage.postgres.pg_operations import VIEW_RELKINDS
from estnltk.storage.postgres.collection_meta import PgCollectionMeta
from estnltk.storage.postgres.collection_meta_selection import PgCollectionMetaSelection
from estnltk.taggers import VabamorfTagger

logger = get_logger_with_tqdm_handler('DEBUG')


BASE_SCHEMA  = 'test_view_based_base'    # regular (table-based) schema
VIEW_SCHEMA  = 'test_view_based_views'   # view-based schema built on top of BASE_SCHEMA
EMPTY_SCHEMA = 'test_view_based_empty'   # regular schema without any collections
EMPTY_VIEW_SCHEMA = 'test_view_based_empty_views'  # view-based schema on top of EMPTY_SCHEMA

# Collection with metadata, attached layers and a detached layer
MAIN_COLLECTION = 'docs_with_layers'
# Collection without metadata and layers
PLAIN_COLLECTION = 'docs_plain'

DETACHED_LAYER = 'morph_detached'

MAIN_COLLECTION_TEXTS = [
    'Ööbik laulab. Öökull ei laula.',
    'Mis kell on? Kell on kolm.',
    'See on kolmas tekst.',
    'Väljas sajab vihma. Toas on soe.',
    'Viimane tekst lõpetab kollektsiooni.',
]

PLAIN_COLLECTION_TEXTS = [
    'Esimene lihtne tekst.',
    'Teine lihtne tekst.',
]


def connect_storage(schema, create_schema_if_missing=False):
    return PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db',
                           create_schema_if_missing=create_schema_if_missing)


def drop_schema_if_exists(storage, schema):
    """Drops the given schema (if it exists) along with all of its relations.
       Uses the connection of the given storage, which must be a regular
       (not view-based) storage, because sessions of view-based storages are
       read-only."""
    assert not storage.view_based
    storage.conn.commit()
    with storage.conn.cursor() as c:
        c.execute(SQL('DROP SCHEMA IF EXISTS {} CASCADE;').format(Identifier(schema)))
    storage.conn.commit()


def create_view_based_schema(base_storage, view_schema, collections_as_view=True,
                             copy_as_tables=()):
    """Creates a new schema that exposes all tables of the base_storage's schema
       as views (`CREATE VIEW ... AS SELECT * FROM ...`).

       :param base_storage: PostgresStorage
           regular (table-based) storage which tables will be exposed. the
           connection of this storage is used for creating the new schema.
       :param view_schema: str
           name of the new schema.
       :param collections_as_view: bool
           whether '__collections' is created as a view (default) or as a table
           which has the same content as '__collections' of the base_storage.
       :param copy_as_tables: Sequence[str]
           names of tables that will be created as tables (copies) instead of
           views. use this to create inconsistent schemas that mix views and
           tables.
    """
    assert not base_storage.view_based
    base_schema = base_storage.schema
    table_names = sorted(pg.get_all_table_names(base_storage))
    assert '__collections' in table_names
    with base_storage.conn.cursor() as c:
        c.execute(SQL('CREATE SCHEMA {};').format(Identifier(view_schema)))
        for table_name in table_names:
            as_view = True
            if table_name == '__collections':
                as_view = collections_as_view
            elif table_name in copy_as_tables:
                as_view = False
            relation_type = SQL('VIEW') if as_view else SQL('TABLE')
            c.execute(SQL('CREATE {relation_type} {view_schema}.{name} AS '
                          'SELECT * FROM {base_schema}.{name};').format(
                              relation_type=relation_type,
                              view_schema=Identifier(view_schema),
                              base_schema=Identifier(base_schema),
                              name=Identifier(table_name)))
            logger.debug(c.query.decode())
    base_storage.conn.commit()


class ViewBasedSchemaTestBase(unittest.TestCase):
    """Common setup: creates a regular schema that contains 2 collections:
       *) MAIN_COLLECTION -- has metadata columns, attached layers (segmentation
          layers) and a detached layer (DETACHED_LAYER);
       *) PLAIN_COLLECTION -- no metadata, no layers;
       View-based schemas are built on top of it inside tests.
    """

    def setUp(self):
        self._opened_storages = []
        # Create base storage / connection
        self.base_storage = connect_storage(BASE_SCHEMA, create_schema_if_missing=True)
        # Clean up leftovers of previous (interrupted) test runs
        for schema in [VIEW_SCHEMA, EMPTY_VIEW_SCHEMA, EMPTY_SCHEMA]:
            drop_schema_if_exists(self.base_storage, schema)
        self._fill_base_schema()

    def tearDown(self):
        # Important: connections reading the views must be closed before the
        # schemas can be dropped (otherwise, their open transactions can hold
        # locks on views/tables and DROP SCHEMA remains waiting behind them)
        for storage in self._opened_storages:
            if not storage.closed():
                storage.close()
        for schema in [VIEW_SCHEMA, EMPTY_VIEW_SCHEMA, EMPTY_SCHEMA]:
            drop_schema_if_exists(self.base_storage, schema)
        delete_schema(self.base_storage)
        self.base_storage.close()

    def _fill_base_schema(self):
        # 1) Collection with metadata, attached layers and a detached layer
        collection = self.base_storage.add_collection(
            MAIN_COLLECTION, meta=OrderedDict([('text_nr', 'int'), ('text_name', 'str')]))
        with collection.insert() as collection_insert:
            for i, text_str in enumerate(MAIN_COLLECTION_TEXTS):
                text = Text(text_str).tag_layer(['sentences'])
                collection_insert(text, key=i, meta_data={'text_nr': i + 1,
                                                          'text_name': '{}. tekst'.format(i + 1)})
        tagger = VabamorfTagger(disambiguate=False, output_layer=DETACHED_LAYER)
        collection.create_layer(tagger=tagger)
        assert collection.has_layer('words', 'attached')
        assert collection.has_layer('sentences', 'attached')
        assert collection.has_layer(DETACHED_LAYER, 'detached')
        # 2) Collection without metadata and layers
        plain_collection = self.base_storage.add_collection(PLAIN_COLLECTION)
        with plain_collection.insert() as collection_insert:
            for i, text_str in enumerate(PLAIN_COLLECTION_TEXTS):
                collection_insert(Text(text_str), key=i)
        self.base_storage.conn.commit()

    def _connect(self, schema, create_schema_if_missing=False):
        """Connects to the given schema; the connection will be closed in tearDown."""
        storage = connect_storage(schema, create_schema_if_missing=create_schema_if_missing)
        self._opened_storages.append(storage)
        return storage

    def _assert_texts_equal(self, text, expected_text):
        self.assertIsInstance(text, Text)
        self.assertEqual(text.text, expected_text.text)
        self.assertEqual(text.meta, expected_text.meta)
        self.assertSetEqual(set(text.layers), set(expected_text.layers))
        for layer in expected_text.layers:
            self.assertEqual(text[layer], expected_text[layer],
                             'layer {!r} of text {!r} differs'.format(layer, text.text))


class TestViewBasedSchemaDetection(ViewBasedSchemaTestBase):

    def test_regular_schema_is_not_view_based(self):
        # The schema that has only tables is a regular schema
        self.assertFalse(self.base_storage.view_based)
        self.assertFalse(self.base_storage.conn.readonly)
        self.assertListEqual(self.base_storage.collections,
                             sorted([MAIN_COLLECTION, PLAIN_COLLECTION]))
        # Reconnecting to the schema or refreshing it does not change the status
        storage = self._connect(BASE_SCHEMA)
        self.assertFalse(storage.view_based)
        storage.refresh()
        self.assertFalse(storage.view_based)
        # Relations of the regular schema are tables
        relation_names = ['__collections', MAIN_COLLECTION, PLAIN_COLLECTION,
                          pg.structure_table_name(MAIN_COLLECTION),
                          pg.layer_table_name(MAIN_COLLECTION, DETACHED_LAYER)]
        kinds = get_relation_kinds(storage, relation_names)
        for name in relation_names:
            self.assertIn(kinds[name], TABLE_RELKINDS)
            self.assertTrue(table_exists(storage, name))
            self.assertFalse(table_exists(storage, name, relkinds=VIEW_RELKINDS))

    def test_view_based_schema_with_collections_as_view(self):
        # Case 1: all relations of the schema (including '__collections') are views
        create_view_based_schema(self.base_storage, VIEW_SCHEMA, collections_as_view=True)
        storage = self._connect(VIEW_SCHEMA)
        self.assertTrue(storage.view_based)
        # Session of a view-based storage is read-only
        self.assertTrue(storage.conn.readonly)
        self.assertListEqual(storage.collections, sorted([MAIN_COLLECTION, PLAIN_COLLECTION]))
        # All relations are views
        relation_names = ['__collections', MAIN_COLLECTION, PLAIN_COLLECTION,
                          pg.structure_table_name(MAIN_COLLECTION),
                          pg.structure_table_name(PLAIN_COLLECTION),
                          pg.layer_table_name(MAIN_COLLECTION, DETACHED_LAYER)]
        kinds = get_relation_kinds(storage, relation_names)
        self.assertSetEqual(set(kinds.keys()), set(relation_names))
        for name in relation_names:
            self.assertIn(kinds[name], VIEW_RELKINDS)
            # in a view-based storage, table_exists(...) looks for views by default:
            self.assertTrue(table_exists(storage, name))
            # however, if we look for table relkinds, there is no such table:
            self.assertFalse(table_exists(storage, name, relkinds=TABLE_RELKINDS))
        self.assertFalse(table_exists(storage, 'nonexistent_relation'))
        # Collections exist and have their structure
        for collection_name in [MAIN_COLLECTION, PLAIN_COLLECTION]:
            self.assertTrue(storage[collection_name].exists())
        self.assertTrue(pg.layer_table_exists(storage, MAIN_COLLECTION, DETACHED_LAYER))
        # Status remains the same after refresh
        storage.refresh()
        self.assertTrue(storage.view_based)
        self.assertTrue(storage.conn.readonly)
        # The base schema remains a regular schema
        self.base_storage.refresh()
        self.assertFalse(self.base_storage.view_based)

    def test_view_based_schema_with_collections_as_table(self):
        # Case 2: '__collections' is a table, but all the collections are views
        create_view_based_schema(self.base_storage, VIEW_SCHEMA, collections_as_view=False)
        storage = self._connect(VIEW_SCHEMA)
        kinds = get_relation_kinds(storage, ['__collections', MAIN_COLLECTION, PLAIN_COLLECTION])
        self.assertIn(kinds['__collections'], TABLE_RELKINDS)
        self.assertIn(kinds[MAIN_COLLECTION], VIEW_RELKINDS)
        self.assertIn(kinds[PLAIN_COLLECTION], VIEW_RELKINDS)
        self.assertTrue(storage.view_based)
        self.assertTrue(storage.conn.readonly)
        self.assertListEqual(storage.collections, sorted([MAIN_COLLECTION, PLAIN_COLLECTION]))
        for collection_name in [MAIN_COLLECTION, PLAIN_COLLECTION]:
            self.assertTrue(storage[collection_name].exists())
        storage.refresh()
        self.assertTrue(storage.view_based)

    def test_mixed_schema_raises_exception(self):
        # If collections listed in '__collections' are a mix of views and
        # tables, then connecting to the schema raises an exception.
        # This holds regardless of the type of '__collections'
        for collections_as_view in [True, False]:
            with self.subTest(collections_as_view=collections_as_view):
                drop_schema_if_exists(self.base_storage, VIEW_SCHEMA)
                # MAIN_COLLECTION is a view, PLAIN_COLLECTION is a table
                create_view_based_schema(self.base_storage, VIEW_SCHEMA,
                                         collections_as_view=collections_as_view,
                                         copy_as_tables=[PLAIN_COLLECTION])
                with self.assertRaises(PgStorageException) as raised:
                    self._connect(VIEW_SCHEMA)
                error_message = str(raised.exception)
                self.assertIn('mixes view-based collections', error_message)
                self.assertIn(MAIN_COLLECTION, error_message)
                self.assertIn(PLAIN_COLLECTION, error_message)

    def test_empty_regular_schema_is_not_view_based(self):
        # A new schema (created via EstNLTK) has an empty '__collections' table.
        # A schema without collections is considered as a regular schema
        storage = self._connect(EMPTY_SCHEMA, create_schema_if_missing=True)
        kinds = get_relation_kinds(storage, ['__collections'])
        self.assertIn(kinds['__collections'], TABLE_RELKINDS)
        self.assertListEqual(storage.collections, [])
        self.assertFalse(storage.view_based)
        self.assertFalse(storage.conn.readonly)
        # The status does not change after refresh and reconnecting
        storage.refresh()
        self.assertFalse(storage.view_based)
        storage_2 = self._connect(EMPTY_SCHEMA)
        self.assertListEqual(storage_2.collections, [])
        self.assertFalse(storage_2.view_based)

    def test_empty_schema_with_collections_view_is_view_based(self):
        # A schema without collections is considered as view-based if its
        # '__collections' is a view
        empty_storage = self._connect(EMPTY_SCHEMA, create_schema_if_missing=True)
        self.assertFalse(empty_storage.view_based)
        create_view_based_schema(empty_storage, EMPTY_VIEW_SCHEMA, collections_as_view=True)
        storage = self._connect(EMPTY_VIEW_SCHEMA)
        kinds = get_relation_kinds(storage, ['__collections'])
        self.assertIn(kinds['__collections'], VIEW_RELKINDS)
        self.assertListEqual(storage.collections, [])
        self.assertTrue(storage.view_based)
        self.assertTrue(storage.conn.readonly)
        storage.refresh()
        self.assertTrue(storage.view_based)

    def test_empty_view_based_schema_detects_new_collections_on_refresh(self):
        # Start with an empty view-based schema
        empty_storage = self._connect(EMPTY_SCHEMA, create_schema_if_missing=True)
        create_view_based_schema(empty_storage, EMPTY_VIEW_SCHEMA, collections_as_view=True)
        storage = self._connect(EMPTY_VIEW_SCHEMA)
        self.assertListEqual(storage.collections, [])
        self.assertTrue(storage.view_based)
        storage.conn.commit()
        # Add a collection to the underlying regular schema and expose it via views
        collection = empty_storage.add_collection('new_docs')
        with collection.insert() as collection_insert:
            collection_insert(Text('Uus tekst.'), key=0)
        with empty_storage.conn.cursor() as c:
            for name in ['new_docs', pg.structure_table_name('new_docs')]:
                c.execute(SQL('CREATE VIEW {view_schema}.{name} AS SELECT * FROM {base_schema}.{name};').format(
                    view_schema=Identifier(EMPTY_VIEW_SCHEMA), base_schema=Identifier(EMPTY_SCHEMA),
                    name=Identifier(name)))
        empty_storage.conn.commit()
        # After refresh, the new collection appears in the view-based schema
        storage.refresh()
        self.assertListEqual(storage.collections, ['new_docs'])
        self.assertTrue(storage.view_based)
        self.assertTrue(storage['new_docs'].exists())
        self.assertEqual(storage['new_docs'][0].text, 'Uus tekst.')
        # The underlying schema remains a regular schema
        empty_storage.refresh()
        self.assertFalse(empty_storage.view_based)


class TestViewBasedSchemaReading(ViewBasedSchemaTestBase):
    """Tests reading from collections of a view-based schema. Results are compared
       against the results obtained from the underlying regular schema."""

    def setUp(self):
        super().setUp()
        create_view_based_schema(self.base_storage, VIEW_SCHEMA, collections_as_view=True)
        self.view_storage = self._connect(VIEW_SCHEMA)
        assert self.view_storage.view_based
        self.base_collection = self.base_storage[MAIN_COLLECTION]
        self.view_collection = self.view_storage[MAIN_COLLECTION]

    def test_collection_properties(self):
        base_collection, view_collection = self.base_collection, self.view_collection
        self.assertTrue(view_collection.exists())
        self.assertEqual(view_collection.version, base_collection.version)
        self.assertEqual(len(view_collection), len(MAIN_COLLECTION_TEXTS))
        # Layer structure
        self.assertListEqual(view_collection.layers, base_collection.layers)
        self.assertDictEqual(view_collection.structure.structure,
                             base_collection.structure.structure)
        self.assertTrue(view_collection.has_layer('words', 'attached'))
        self.assertTrue(view_collection.has_layer('sentences', 'attached'))
        self.assertTrue(view_collection.has_layer(DETACHED_LAYER, 'detached'))
        self.assertFalse(view_collection.has_layer('nonexistent_layer'))
        self.assertListEqual(view_collection.get_layer_names_by_type('detached'), [DETACHED_LAYER])
        self.assertFalse(view_collection.is_sparse(DETACHED_LAYER))
        self.assertFalse(view_collection.has_ngram_index(DETACHED_LAYER))
        # By default, attached layers are selected
        self.assertListEqual(view_collection.selected_layers, base_collection.selected_layers)
        self.assertNotIn(DETACHED_LAYER, view_collection.selected_layers)
        # Collection without layers and metadata
        plain_collection = self.view_storage[PLAIN_COLLECTION]
        self.assertTrue(plain_collection.exists())
        self.assertEqual(len(plain_collection), len(PLAIN_COLLECTION_TEXTS))
        self.assertListEqual(plain_collection.layers, [])
        # Refreshing collection's structure works on views
        view_collection.refresh()
        self.assertListEqual(view_collection.layers, base_collection.layers)

    def test_collection_getitem(self):
        base_collection, view_collection = self.base_collection, self.view_collection
        tagger = VabamorfTagger(disambiguate=False, output_layer=DETACHED_LAYER)
        # 1) collection[i] with attached layers only
        for i, text_str in enumerate(MAIN_COLLECTION_TEXTS):
            text = view_collection[i]
            expected_text = Text(text_str).tag_layer(['sentences'])
            self._assert_texts_equal(text, expected_text)
            self.assertNotIn(DETACHED_LAYER, text.layers)
            self._assert_texts_equal(text, base_collection[i])
        # 2) collection[i] with attached layers and the detached layer
        view_collection.selected_layers = \
            view_collection.selected_layers + [DETACHED_LAYER]
        base_collection.selected_layers = \
            base_collection.selected_layers + [DETACHED_LAYER]
        self.assertEqual(len(base_collection.layers), len(base_collection.selected_layers))
        self.assertEqual(len(view_collection.layers), len(view_collection.selected_layers))
        self.assertIn(DETACHED_LAYER, view_collection.selected_layers)
        self.assertIn('words', view_collection.selected_layers)
        for i, text_str in enumerate(MAIN_COLLECTION_TEXTS):
            text = view_collection[i]
            expected_text = Text(text_str).tag_layer(['sentences'])
            tagger.tag(expected_text)
            self.assertIn(DETACHED_LAYER, text.layers)
            self._assert_texts_equal(text, expected_text)
            self._assert_texts_equal(text, base_collection[i])
        # 3) Index outside of the collection
        with self.assertRaises(KeyError):
            view_collection[len(MAIN_COLLECTION_TEXTS)]
        # 4) Invalid index
        with self.assertRaises(KeyError):
            view_collection['0xxHr']
        # 5) collection[i] on a collection without layers
        plain_collection = self.view_storage[PLAIN_COLLECTION]
        for i, text_str in enumerate(PLAIN_COLLECTION_TEXTS):
            text = plain_collection[i]
            self.assertEqual(text.text, text_str)
            self.assertEqual(len(text.layers), 0)

    def test_collection_getitem_slice(self):
        view_collection = self.view_collection
        # collection[start:end] yields texts (without indexes)
        texts = list(view_collection[1:3])
        self.assertListEqual([text.text for text in texts], MAIN_COLLECTION_TEXTS[1:3])
        texts = list(view_collection[3:])
        self.assertListEqual([text.text for text in texts], MAIN_COLLECTION_TEXTS[3:])
        texts = list(view_collection[:2])
        self.assertListEqual([text.text for text in texts], MAIN_COLLECTION_TEXTS[:2])

    def test_collection_iteration(self):
        # Iterating over the collection yields texts with selected (attached) layers
        texts = list(self.view_collection)
        self.assertEqual(len(texts), len(MAIN_COLLECTION_TEXTS))
        for text, text_str in zip(texts, MAIN_COLLECTION_TEXTS):
            self._assert_texts_equal(text, Text(text_str).tag_layer(['sentences']))

    def test_basic_select(self):
        base_collection, view_collection = self.base_collection, self.view_collection
        # By default, all attached layers have been selected
        self.assertEqual(len(view_collection.layers)-1, len(view_collection.selected_layers))
        # 1) Select all texts: yields (text_id, text) with attached layers
        subcollection = view_collection.select(layers=view_collection.selected_layers)
        self.assertIsInstance(subcollection, pg.PgSubCollection)
        self.assertEqual(len(subcollection), len(MAIN_COLLECTION_TEXTS))
        results = list(subcollection)
        self.assertListEqual([text_id for text_id, text in results],
                             list(range(len(MAIN_COLLECTION_TEXTS))))
        for (text_id, text), text_str in zip(results, MAIN_COLLECTION_TEXTS):
            self._assert_texts_equal(text, Text(text_str).tag_layer(['sentences']))
            self.assertNotIn(DETACHED_LAYER, text.layers)
        # the subcollection can be iterated several times
        self.assertListEqual([text.text for text_id, text in subcollection], MAIN_COLLECTION_TEXTS)

        # 2) Select without index
        results = list(view_collection.select(return_index=False))
        self.assertListEqual([text.text for text in results], MAIN_COLLECTION_TEXTS)

        # 3) Select all texts with the detached layer (joins the layer view)
        results = list(view_collection.select( \
            layers=view_collection.selected_layers + [DETACHED_LAYER]) )
        base_results = list(base_collection.select( \
            layers=base_collection.selected_layers + [DETACHED_LAYER]))
        self.assertEqual(len(results), len(MAIN_COLLECTION_TEXTS))
        self.assertEqual(len(results), len(base_results))
        for (text_id, text), (base_text_id, base_text) in zip(results, base_results):
            self.assertEqual(text_id, base_text_id)
            self.assertIn(DETACHED_LAYER, text.layers)
            self.assertSetEqual(set(base_text.layers), set(text.layers))
            self._assert_texts_equal(text, base_text)

        # 4) Select with collection metadata: yields (text_id, text, meta)
        results = list(view_collection.select(collection_meta=['text_nr', 'text_name']))
        self.assertEqual(len(results), len(MAIN_COLLECTION_TEXTS))
        for text_id, text, meta in results:
            self.assertEqual(text.text, MAIN_COLLECTION_TEXTS[text_id])
            self.assertDictEqual(meta, {'text_nr': text_id + 1,
                                        'text_name': '{}. tekst'.format(text_id + 1)})

        # 5) Select on a collection without layers
        plain_collection = self.view_storage[PLAIN_COLLECTION]
        results = list(plain_collection.select())
        self.assertListEqual([text_id for text_id, text in results],
                             list(range(len(PLAIN_COLLECTION_TEXTS))))
        self.assertListEqual([text.text for text_id, text in results], PLAIN_COLLECTION_TEXTS)

    def test_select_with_query(self):
        base_collection, view_collection = self.base_collection, self.view_collection
        # 1) Query over the collection view
        query = SubstringQuery('tekst')
        results = list(view_collection.select(query=query))
        self.assertListEqual([text_id for text_id, text in results], [2, 4])
        self.assertListEqual([text.text for text_id, text in results],
                             [MAIN_COLLECTION_TEXTS[2], MAIN_COLLECTION_TEXTS[4]])
        # 2) Query over the detached layer view (the query joins layer view with
        #    the collection view)
        query = LayerQuery(DETACHED_LAYER, lemma='kell')
        results = list(view_collection.select(query=query, layers=[DETACHED_LAYER]))
        base_results = list(base_collection.select(query=query, layers=[DETACHED_LAYER]))
        self.assertListEqual([text_id for text_id, text in results], [1])
        self.assertListEqual([text_id for text_id, text in results],
                             [text_id for text_id, text in base_results])
        for (text_id, text), (base_text_id, base_text) in zip(results, base_results):
            self.assertIn(DETACHED_LAYER, text.layers)
            self._assert_texts_equal(text, base_text)
        # 3) Query that matches nothing
        results = list(view_collection.select(query=SubstringQuery('seda sõna siin ei ole')))
        self.assertListEqual(results, [])

    def test_select_head(self):
        base_collection, view_collection = self.base_collection, self.view_collection
        subcollection = view_collection.select(layers=view_collection.selected_layers)
        head = list(subcollection.head(0))
        self.assertListEqual(head, [])
        head = list(subcollection.head(2))
        self.assertEqual(len(head), 2)
        self.assertListEqual([text_id for text_id, text in head], [0, 1])
        self.assertListEqual([text.text for text_id, text in head], MAIN_COLLECTION_TEXTS[:2])
        for text_id, text in head:
            self._assert_texts_equal(text, base_collection[text_id])
        # head larger than the collection
        head = list(subcollection.head(20))
        self.assertEqual(len(head), len(MAIN_COLLECTION_TEXTS))
        # head with the detached layer
        head = list(view_collection.select(layers=[DETACHED_LAYER]).head(3))
        base_head = list(base_collection.select(layers=[DETACHED_LAYER]).head(3))
        self.assertListEqual([text_id for text_id, text in head], [0, 1, 2])
        for (text_id, text), (base_text_id, base_text) in zip(head, base_head):
            self.assertIn(DETACHED_LAYER, text.layers)
            self._assert_texts_equal(text, base_text)
        # head of a query
        head = list(view_collection.select(query=SubstringQuery('tekst')).head(1))
        self.assertListEqual([text_id for text_id, text in head], [2])

    def test_select_tail(self):
        base_collection, view_collection = self.base_collection, self.view_collection
        last_id = len(MAIN_COLLECTION_TEXTS) - 1
        subcollection = view_collection.select(layers=view_collection.selected_layers)
        tail = list(subcollection.tail(0))
        self.assertListEqual(tail, [])
        tail = list(subcollection.tail(2))
        self.assertEqual(len(tail), 2)
        self.assertListEqual([text_id for text_id, text in tail], [last_id - 1, last_id])
        self.assertListEqual([text.text for text_id, text in tail], MAIN_COLLECTION_TEXTS[-2:])
        for text_id, text in tail:
            self._assert_texts_equal(text, base_collection[text_id])
        # tail larger than the collection
        tail = list(subcollection.tail(20))
        self.assertEqual(len(tail), len(MAIN_COLLECTION_TEXTS))
        # tail with the detached layer
        tail = list(view_collection.select(layers=[DETACHED_LAYER]).tail(3))
        base_tail = list(base_collection.select(layers=[DETACHED_LAYER]).tail(3))
        self.assertListEqual([text_id for text_id, text in tail],
                             [last_id - 2, last_id - 1, last_id])
        for (text_id, text), (base_text_id, base_text) in zip(tail, base_tail):
            self.assertIn(DETACHED_LAYER, text.layers)
            self._assert_texts_equal(text, base_text)
        # tail of a query
        tail = list(view_collection.select(query=SubstringQuery('tekst')).tail(1))
        self.assertListEqual([text_id for text_id, text in tail], [4])

    def test_collection_meta(self):
        base_collection, view_collection = self.base_collection, self.view_collection
        meta = view_collection.meta
        self.assertIsInstance(meta, PgCollectionMeta)
        # Metadata columns and their types can be retrieved from a view
        self.assertListEqual(meta.columns, ['text_nr', 'text_name'])
        self.assertEqual(meta.column_types, OrderedDict([('text_nr', 'integer'), ('text_name', 'text')]))
        self.assertEqual(meta.column_types, base_collection.meta.column_types)
        self.assertListEqual(view_collection.column_names, base_collection.column_names)

        # 1) meta[index]: all metadata of a single document
        for i in range(len(MAIN_COLLECTION_TEXTS)):
            self.assertDictEqual(meta[i], {'text_nr': i + 1, 'text_name': '{}. tekst'.format(i + 1)})
            self.assertDictEqual(meta[i], base_collection.meta[i])

        # 2) meta[start:end]: all metadata of a slice of documents
        selection = meta[1:4]
        self.assertIsInstance(selection, PgCollectionMetaSelection)
        self.assertEqual(len(selection), 3)
        self.assertListEqual(list(selection),
                             [{'text_nr': i + 1, 'text_name': '{}. tekst'.format(i + 1)} for i in [1, 2, 3]])
        self.assertListEqual(list(meta[3:]),
                             [{'text_nr': i + 1, 'text_name': '{}. tekst'.format(i + 1)} for i in [3, 4]])
        self.assertListEqual(list(meta[0:]), list(base_collection.meta[0:]))

        # 3) meta[indexes]: all metadata of selected documents
        self.assertListEqual(list(meta[[0, 2, 4]]),
                             [{'text_nr': i + 1, 'text_name': '{}. tekst'.format(i + 1)} for i in [0, 2, 4]])

        # 4) meta[index, attributes]: selected metadata of a single document
        self.assertDictEqual(meta[2, 'text_name'], {'text_name': '3. tekst'})
        self.assertDictEqual(meta[2, ['text_nr']], {'text_nr': 3})

        # 5) meta[start:end, attributes] and meta[indexes, attributes]
        self.assertListEqual(list(meta[0:2, ['text_nr']]), [{'text_nr': 1}, {'text_nr': 2}])
        self.assertListEqual(list(meta[[1, 3], 'text_name']),
                             [{'text_name': '2. tekst'}, {'text_name': '4. tekst'}])

        # 6) Invalid metadata column
        with self.assertRaises(KeyError):
            meta[0, 'nonexistent_column']

        # 7) Collection without metadata columns
        plain_meta = self.view_storage[PLAIN_COLLECTION].meta
        self.assertListEqual(plain_meta.columns, [])
        self.assertEqual(plain_meta.column_types, OrderedDict([]))
        with self.assertRaises(pg.PgCollectionException):
            plain_meta[0]

class TestViewBasedSchemaWritingGuards(ViewBasedSchemaTestBase):
    """Tests that writing into collections of a view-based schema is not possible: 
       guards exist that block the writing with PgReadOnlyStorageException."""

    def setUp(self):
        super().setUp()
        create_view_based_schema(self.base_storage, VIEW_SCHEMA, collections_as_view=True)
        self.view_storage = self._connect(VIEW_SCHEMA)
        assert self.view_storage.view_based

    def test_view_based_storage_guards(self):
        self.assertTrue(self.view_storage.view_based)
        # Cannot add new collection
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            self.view_storage.add_collection('new_main_collection')
        error_message = str(raised.exception)
        self.assertIn('is view-based and therefore read-only.', error_message)
        # Cannot add delete existing collection
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            self.view_storage.delete_collection(MAIN_COLLECTION)

    def test_view_based_collection_guards(self):
        self.assertTrue(self.view_storage.view_based)
        assert MAIN_COLLECTION in self.view_storage.collections
        view_collection = self.view_storage[MAIN_COLLECTION]
        # Cannot add (more) texts
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            with view_collection.insert() as collection_insert:
                for text_str in MAIN_COLLECTION_TEXTS:
                    text = Text(text_str).tag_layer(['sentences'])
                    collection_insert(text)
        # Cannot create more layers
        new_tagger = VabamorfTagger(output_layer='new_morph_layer')
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            view_collection.add_layer(new_tagger.get_layer_template())
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            view_collection.create_layer(new_tagger)
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            view_collection.create_layer_block(new_tagger, (2, 0))
        # Cannot delete existing layers
        assert view_collection.has_layer('sentences', 'attached')
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            view_collection.delete_layer('sentences')
        assert view_collection.has_layer(DETACHED_LAYER, 'detached')
        with self.assertRaises(PgReadOnlyStorageException) as raised:
            view_collection.delete_layer(DETACHED_LAYER)


class TestViewBasedSchemaSamplingTexts(unittest.TestCase):
    """Tests sampling texts from a collection of a view-based schema. 
       Note: sampling from a view-based schema does not give the same 
       results as sampling from the underlying table-based schema because 
       different sampling implementations are used. 
    """

    def setUp(self):
        self._opened_storages = []
        # Create base storage / connection
        self.base_storage = connect_storage(BASE_SCHEMA, create_schema_if_missing=True)
        # Clean up leftovers of previous (interrupted) test runs
        drop_schema_if_exists(self.base_storage, VIEW_SCHEMA)

    def tearDown(self):
        # Important: connections reading the views must be closed before the
        # schemas can be dropped (otherwise, their open transactions can hold
        # locks on views/tables and DROP SCHEMA remains waiting behind them)
        for storage in self._opened_storages:
            if not storage.closed():
                storage.close()
        drop_schema_if_exists(self.base_storage, VIEW_SCHEMA)
        delete_schema(self.base_storage)
        self.base_storage.close()

    def _connect(self, schema, create_schema_if_missing=False):
        """Connects to the given schema; the connection will be closed in tearDown."""
        storage = connect_storage(schema, create_schema_if_missing=create_schema_if_missing)
        self._opened_storages.append(storage)
        return storage

    def _create_test_collection_of_docs(self, collection_name, size=100):
        assert size in [100, 200], '(!) Unexpected test collection size: {}'.format(size)
        # Create a test collection
        collection = self.base_storage.add_collection( collection_name, 
                          meta=OrderedDict([('text_id', 'int'), ('text_name', 'str')]) )
        # Populate collection with test sentences
        logger.debug('Creating a collection of {} texts:'.format(size))
        subj_words = ['kiisumiisu', 'vanahärra', 'vanama', 'neidis', 'sugulane']
        verb_words = ['loeb', 'keerab', 'kasvatab', 'kangutab', 'organiseerib']
        obj_words = ['raamatut', 'ruutmeetreid', 'kanu', 'kohvrit']
        with collection.insert() as collection_insert:
            counter = 0
            for subj in subj_words:
                for verb in verb_words:
                    for obj in obj_words:
                        if size == 100:
                            text_str = (' '.join([subj, verb, obj])).capitalize()+'.'
                            text = Text( text_str ).tag_layer('sentences')
                            text.meta['text_id'] = counter+1
                            text.meta['text_name'] = 'text_{}'.format(counter+1)
                            collection_insert(text, meta_data={'text_id':text.meta['text_id'],\
                                                               'text_name':text.meta['text_name'] })
                            counter += 1
                        elif size == 200:
                            for adj in ['hea', 'tore']:
                                text_str = (' '.join([adj, subj, verb, obj])).capitalize()+'.'
                                text = Text( text_str ).tag_layer('sentences')
                                text.meta['text_id'] = counter+1
                                text.meta['text_name'] = 'text_{}'.format(counter+1)
                                collection_insert(text, meta_data={'text_id':text.meta['text_id'],\
                                                                   'text_name':text.meta['text_name'] })
                                counter += 1
        return collection

    def test_pgsubcollection_sample_query_based_on_simple_select(self):
        # Create testing collection (in a table-base schema)
        TARGET_COLLECTION = 'docs_texts'
        base_collection = self._create_test_collection_of_docs(TARGET_COLLECTION, size=100)
        # Create a view-based schema based on the table-base schema
        create_view_based_schema(self.base_storage, VIEW_SCHEMA)
        view_storage = self._connect(VIEW_SCHEMA)
        self.assertTrue(view_storage.view_based)
        self.assertTrue(TARGET_COLLECTION in view_storage.collections)
        view_collection = view_storage[TARGET_COLLECTION]
        #
        # Construction types: JOIN, ANY
        #
        for constr in ['JOIN', 'ANY']:
            # Default select with sample size approx. 5%
            res = list( view_collection.select().sample(5, seed=55, method='BERNOULLI', construction=constr) )
            self.assertEqual(len(res), 5)
            self.assertEqual(len(res[0]), 2)
            self.assertListEqual([t[1].meta['text_id'] for t in res], [14, 24, 41, 53, 97])
            # Note: sampling with the same seed in a table-base schema gives 'text_id'-s: [20, 38, 77, 98]
            
            # Default select without indexes and with sample size approx. 5%
            res = list( view_collection.select(return_index=False).sample(5, seed=55, method='BERNOULLI', construction=constr) )
            self.assertEqual(len(res), 5)
            self.assertTrue( type(res[0]) is Text )
            self.assertListEqual([t.meta['text_id'] for t in res], [14, 24, 41, 53, 97])

            # Default select with collection_meta and sample size approx. 5% 
            res = list( view_collection.select(collection_meta=['text_id']).sample(5, seed=55, method='BERNOULLI', construction=constr) )
            self.assertEqual(len(res), 5)
            self.assertEqual(len(res[0]), 3)
            self.assertListEqual([t[2] for t in res], [{'text_id': 14}, {'text_id': 24}, {'text_id': 41}, {'text_id': 53}, {'text_id': 97}])

        #
        # Test bigger sample sizes
        #
        # Default select with sample size approx. 25%
        res = list( view_collection.select().sample(25, seed=55, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 22)
        self.assertEqual(len(res[0]), 2)
        expected_text_ids = [4, 14, 19, 24, 31, 35, 37, 39, 40, 41, 43, 44, 45, 47, 53, 54, 75, \
                             86, 88, 92, 93, 97]
        self.assertListEqual( [t[1].meta['text_id'] for t in res], expected_text_ids )
        # Default select with sample size approx. 50%
        res = list( view_collection.select().sample(50, seed=555, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 51)
        self.assertEqual(len(res[0]), 2)
        expected_text_ids = [2, 3, 4, 7, 8, 9, 11, 13, 14, 17, 18, 19, 24, 25, 28, 29, 31, 33, 37, 39, 41, 47, \
                             49, 51, 52, 55, 56, 57, 58, 60, 63, 65, 67, 68, 70, 72, 73, 74, 75, 79, 80, 81, 82, \
                             83, 85, 86, 87, 90, 92, 97, 98]
        self.assertListEqual( [t[0] for t in res], expected_text_ids )
        # Default select with sample size approx. 75%
        res = list( view_collection.select().sample(75, seed=555, method='BERNOULLI', construction='JOIN') )
        self.assertEqual(len(res), 72)
        self.assertEqual(len(res[0]), 2)
        expected_text_ids = [1, 2, 3, 4, 7, 8, 9, 10, 11, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 25, 28, 29, \
                             31, 33, 34, 37, 39, 40, 41, 44, 46, 47, 48, 49, 51, 52, 53, 55, 56, 57, 58, 60, \
                             61, 62, 63, 64, 65, 67, 68, 70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 84, 85, \
                             86, 87, 88, 89, 90, 92, 94, 97, 98]
        self.assertListEqual( [t[0] for t in res], expected_text_ids )


if __name__ == '__main__':
    unittest.main()
