import unittest
import random

from estnltk import logger
from estnltk import Text
from estnltk.storage.postgres import PostgresStorage, layer_table_identifier
from estnltk.storage.postgres import create_schema, delete_schema, count_rows
from estnltk.storage import postgres as pg
from estnltk.taggers import VabamorfTagger
from estnltk.finite_grammar import ngram_fingerprint, phrase_list_generator
from estnltk.storage.postgres.queries.layer_ngram_query import LayerNgramQuery

logger.setLevel('DEBUG')


def get_random_collection_name():
    return 'collection_{}'.format(random.randint(1, 1000000))


class TestLayerNgramQuery(unittest.TestCase):
    def setUp(self):
        schema = "test_schema"
        self.storage = PostgresStorage(pgpass_file='~/.pgpass', schema=schema, dbname='test_db')

        create_schema(self.storage)

    def tearDown(self):
        delete_schema(self.storage)
        self.storage.close()

    def test_layer_ngram_query(self):
        collection = self.storage[get_random_collection_name()]
        collection.create()

        id1 = 1
        id2 = 2

        with collection.insert() as collection_insert:
            text1 = Text("Ööbik laulab puu otsas.").tag_layer(["sentences"])
            collection_insert(text1, key=id1)

            text2 = Text("Mis kell on?").tag_layer(["sentences"])
            collection_insert(text2, key=id2)

        layer1 = "layer1"
        layer2 = "layer2"
        tagger1 = VabamorfTagger(disambiguate=False, output_layer=layer1)
        tagger2 = VabamorfTagger(disambiguate=False, output_layer=layer2)

        collection.create_layer(tagger=tagger1, ngram_index={"lemma": 2})
        collection.create_layer(tagger=tagger2, ngram_index={"partofspeech": 3})

        self.assertEqual(
            count_rows(self.storage, table_identifier=layer_table_identifier(self.storage, collection.name, layer1)), 2)
        self.assertEqual(
            count_rows(self.storage, table_identifier=layer_table_identifier(self.storage, collection.name, layer2)), 2)

        res = list(collection.select(query=LayerNgramQuery({
            layer1: {"lemma": [("otsas", ".")]}})))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], id1)

        res = list(collection.select(query=LayerNgramQuery({
            layer1: {"lemma": [("mis", "kell")]}})))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], id2)

        res = list(collection.select(query=LayerNgramQuery({
            layer1: {"lemma": [("mis",)]}})))
        self.assertEqual(len(res), 1)

        res = list(collection.select(query=LayerNgramQuery({
            layer1: {
                "lemma": [[("mis", "kell")],  # "mis-kell" OR "otsas-."
                          [("otsas", ".")]]
            }})))
        self.assertEqual(len(res), 2)

        res = list(collection.select(query=LayerNgramQuery({
            layer1: {
                "lemma": [[("mis", "kell"),  # "mis-kell" AND "otsas-."
                           ("otsas", ".")]]
            }})))
        self.assertEqual(len(res), 0)

        # "Ööbik laulab puu otsas." ->[['H', 'S'], ['V'], ['S', 'S'], ['D', 'K', 'V', 'S'], ['Z']]
        # "Mis kell on?" -> [['P', 'P'], ['S'], ['V', 'V'], ['Z']]
        res = list(collection.select(query=LayerNgramQuery({
            layer2: {"partofspeech": [("S", "V", "S")]}})))  # Ööbik laulab puu
        self.assertEqual(len(res), 1)

        res = list(collection.select(query=LayerNgramQuery({
            layer2: {"partofspeech": [("S", "V")]}})))  # 2-grams are also indexed
        self.assertEqual(len(res), 2)

        res = list(collection.select(query=LayerNgramQuery({
            layer2: {"partofspeech": [[("S", "V", "S")],  # "Ööbik laulab puu" OR "Mis kell on"
                                      [("P", "S", "V")]]}})))
        self.assertEqual(len(res), 2)

        res = list(collection.select(query=LayerNgramQuery({
            layer2: {"partofspeech": [[("S", "V", "S"), ("S", "D", "Z")]]}})))  # "Ööbik laulab puu" AND "puu otsas ."
        self.assertEqual(len(res), 1)

        res = list(collection.select(query=LayerNgramQuery({
            layer1: {"lemma": [("puu", "otsas")]},
            layer2: {"partofspeech": [("S", "V", "S")]},  # "laulma-puu-otsas"
        })))
        self.assertEqual(len(res), 1)

        collection.delete()



    def test_layer_ngram_query_on_layer_wo_ngram_index(self):
        # Test an invalid query: LayerNgramQuery on a layer that does not have ngram_index columns
        collection = self.storage[get_random_collection_name()]
        collection.create()
        
        with collection.insert() as collection_insert:
            text1 = Text("Kass tiksus mansardkorrusel.").tag_layer(["sentences"])
            collection_insert(text1)
            text2 = Text("Kas kuubik kerib pinget ?").tag_layer(["sentences"])
            collection_insert(text2)
        
        collection.create_layer( tagger=VabamorfTagger(disambiguate=False) )
        
        # Attempt to make LayerNgramQuery on a layer that misses ngram_index
        # This should rise an Exception
        with self.assertRaises( Exception ):
            res = list( collection.select( query = LayerNgramQuery( {'morph_analysis': {"lemma": [("kass",)]}} ) ) )
        
        collection.delete()


