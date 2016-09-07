# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..syntax.parsers import MaltParser
from ..names import *


class MaltParserSupportTest(unittest.TestCase):

    def test_maltparser_sent1(self):
        mparser = MaltParser( )
        text = Text('Jänes oli parajasti põllu peal.')
        text.tag_analysis()
        text_parsed = mparser.parse_text( text )
        parsing_results = [ w[PARSER_OUT] for w in text_parsed[LAYER_CONLL] ]
        #print(parsing_results)
        self.assertListEqual( parsing_results, \
            [[['@SUBJ', 1]], [['ROOT', -1]], [['@ADVL', 1]], [['@P>', 4]], [['@ADVL', 1]], [['xxx', 4]]] )

    def test_maltparser_sent2(self):
        mparser = MaltParser( )
        text = Text('Suurt hunti nähes ta ehmus ja pani jooksu.')
        text.tag_analysis()
        text_parsed = mparser.parse_text( text )
        parsing_results = [ w[PARSER_OUT] for w in text_parsed[LAYER_CONLL] ]
        #print(parsing_results)
        self.assertListEqual( parsing_results, \
            [[['@AN>', 1]], [['@ADVL', 2]], [['ROOT', -1]], [['@SUBJ', 2]], [['@ADVL', 2]], [['@J', 6]], [['@FMV', 2]], [['@ADVL', 6]], [['xxx', 7]]] )

    def test_maltparser_sent3(self):
        mparser = MaltParser()
        text = Text('Saksamaal Bonnis leidis aset kummaline juhtum murdvargaga, kes kutsus endale ise politsei.')
        text.tag_analysis()
        text_parsed = mparser.parse_text( text )
        parsing_results = [ w[PARSER_OUT] for w in text_parsed[LAYER_CONLL] ]
        #print(parsing_results)
        self.assertListEqual( parsing_results, \
            [[['@NN>', 1]], [['@SUBJ', 2]], [['ROOT', -1]], [['@NN>', 5]], [['@AN>', 5]], [['@NN>', 6]], [['@OBJ', 2]], [['xxx', 6]], [['@SUBJ', 9]], [['@FMV', 2]], [['@ADVL', 9]], [['@<NN', 10]], [['@ADVL', 9]], [['xxx', 12]]] )

    def test_maltparser_sent1_with_text(self):
        text = Text('Jänes oli parajasti põllu peal.')
        text.tag_syntax() # Assuming MaltParser is set as the default parser
        expected_layer = [ {'end': 5, 'sent_id': 0, 'start': 0, 'parser_out': [['@SUBJ', 1]]}, \
                           {'end': 9, 'sent_id': 0, 'start': 6, 'parser_out': [['ROOT', -1]]}, \
                           {'end': 19, 'sent_id': 0, 'start': 10, 'parser_out': [['@ADVL', 1]]}, \
                           {'end': 25, 'sent_id': 0, 'start': 20, 'parser_out': [['@P>', 4]]}, \
                           {'end': 30, 'sent_id': 0, 'start': 26, 'parser_out': [['@ADVL', 1]]}, \
                           {'end': 31, 'sent_id': 0, 'start': 30, 'parser_out': [['xxx', 4]]} ]
        self.assertListEqual( text[LAYER_CONLL], expected_layer )

    def test_maltparser_sent1_with_text_trees(self):
        text = Text('Jänes oli parajasti põllu peal.')
        trees = text.syntax_trees() # Assuming MaltParser is set as the default parser
        self.assertEqual( len(trees), 1 )
        self.assertDictEqual( trees[0].syntax_token, \
            {'end': 9, 'sent_id': 0, 'start': 6, 'parser_out': [['ROOT', -1]]} )
        self.assertDictEqual( trees[0].token, \
            {'end': 9, 'start': 6, 'analysis': [{'form': 's', 'root_tokens': ['ole'], 'lemma': 'olema', 'partofspeech': 'V', 'root': 'ole', 'clitic': '', 'ending': 'i'}], 'text': 'oli'} )


    def test_maltparser_text_splitting_and_trees(self):
        text = Text('Jänes oli põllu peal. Hunt jooksis metsas. Karuott magas laanes.')
        trees = text.syntax_trees() # Assuming MaltParser is set as the default parser
        self.assertEqual( len(trees), 3 )
        
        # Split the input text into smaller texts by sentences:
        trees_from_small_texts = []
        for sentence in text.split_by( SENTENCES ):
            # Try to make trees also from the smaller text
            sent_trees = sentence.syntax_trees()
            trees_from_small_texts.extend( sent_trees )
        self.assertEqual( len(trees_from_small_texts), 3 )


    def test_maltparser_return_depgraph1(self):
        mparser = MaltParser( )
        text = Text('Kohtusid suur hunt ja kuri lammas. Auhinnaks oli ilus valge tekk.')
        text.tag_analysis()
        dep_graphs = mparser.parse_text(text, return_type="dep_graphs", augment_words=True)
        
        treeStr = str(dep_graphs[0].tree()).strip()
        self.assertEqual(treeStr, '(Kohtusid (hunt suur (lammas ja kuri .)))')
        
        treeStr = str(dep_graphs[1].tree()).strip()
        self.assertEqual(treeStr, '(oli Auhinnaks (tekk ilus valge .))')

