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
            [[['@AN>', 1]], [['@OBJ', 2]], [['@FMV', 4]], [['@SUBJ', 2]], [['ROOT', -1]], [['@J', 6]], [['@FMV', 4]], [['@ADVL', 6]], [['xxx', 7]]] )
            

    def test_maltparser_sent3(self):
        mparser = MaltParser()
        text = Text('Saksamaal Bonnis leidis aset kummaline juhtum murdvargaga, kes kutsus endale ise politsei.')
        text.tag_analysis()
        text_parsed = mparser.parse_text( text )
        parsing_results = [ w[PARSER_OUT] for w in text_parsed[LAYER_CONLL] ]
        #print(parsing_results)
        self.assertListEqual( parsing_results, \
            [[['@NN>', 1]], [['@ADVL', 2]], [['ROOT', -1]], [['@OBJ', 2]], [['@AN>', 5]], [['@SUBJ', 2]], [['@ADVL', 2]], [['xxx', 6]], [['@SUBJ', 9]], [['@FMV', 2]], [['@ADVL', 9]], [['@<NN', 10]], [['@OBJ', 9]], [['xxx', 12]]] )
            

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
        for sid, sentence in enumerate( list( text.split_by( SENTENCES ) ) ):
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


    def test_reading_from_conll_file_1(self):
        test_conll_string = \
'''1	Ken	Ken	H	H	sg|n	4	@SUBJ	_	_
2	ja	ja	J	J	_	3	@J	_	_
3	Tolk	Tolk	H	H	sg|n	1	@SUBJ	_	_
4	käivad	käi	V	V	vad	0	ROOT	_	_
5	närviliselt	närviliselt	D	D	_	4	@ADVL	_	_
6	ringi	ringi	D	D	_	4	@Vpart	_	_
7	.	.	Z	Z	_	6	xxx	_	_

1	Ken	Ken	H	H	sg|n	4	@SUBJ	_	_
2	ja	ja	J	J	_	3	@J	_	_
3	Tolk	Tolk	H	H	sg|n	1	@SUBJ	_	_
4	lähevad	mine	V	V	vad	0	ROOT	_	_
5	edasi	edasi	D	D	_	4	@Vpart	_	_
6	Spiritisse	Spirit	H	H	sg|ill	4	@ADVL	_	_
7	.	.	Z	Z	_	6	xxx	_	_
'''
        # Create a temporary file (with conll format content)
        import codecs
        import tempfile
        import os
        temp_input_file = \
            tempfile.NamedTemporaryFile(prefix='test_conll_in.', mode='w', delete=False)
        temp_input_file.close()
        # We have to open separately here for writing, because Py 2.7 does not support
        # passing parameter   encoding='utf-8'    to the NamedTemporaryFile;
        out_f = codecs.open(temp_input_file.name, mode='w', encoding='utf-8')
        out_f.write( test_conll_string )
        out_f.close()
        
        from estnltk.syntax.utils import read_text_from_conll_file
        text = read_text_from_conll_file( temp_input_file.name )
        os.remove(temp_input_file.name)
        self.assertTrue( LAYER_CONLL in text )
        self.assertTrue( len(text.sentence_texts) == 2 )
        conll_layer    = [ w[PARSER_OUT] for w in text[LAYER_CONLL] ]
        expected_layer = [[['@SUBJ', 3]], [['@J', 2]], [['@SUBJ', 0]], [['ROOT', -1]], [['@ADVL', 3]], [['@Vpart', 3]], [['xxx', 5]], [['@SUBJ', 3]], [['@J', 2]], [['@SUBJ', 0]], [['ROOT', -1]], [['@Vpart', 3]], [['@ADVL', 3]], [['xxx', 5]]]
        #print(conll_layer)
        self.assertListEqual( conll_layer, expected_layer )
        