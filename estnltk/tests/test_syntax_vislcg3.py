# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..syntax.parsers import VISLCG3Parser
from ..syntax.vislcg3_syntax import VISLCG3Pipeline
from ..names import *


class VislCG3ParserTest(unittest.TestCase):

    def get_vislcg_cmd(self):
        ''' Provides VISLCG3 command.
            (!) If 'vislcg3' is not in your system's PATH, you should provide 
                here VISLCG3 executable with a full path in order to execute 
                the tests;
        '''
        return 'vislcg3'


    def test_vislcg3parser_sent1(self):
        parser = VISLCG3Parser( vislcg_cmd = self.get_vislcg_cmd() )
        text = Text('Jänes oli parajasti põllu peal.')
        text_parsed = parser.parse_text( text )
        parsing_results = [ w[PARSER_OUT] for w in text_parsed[LAYER_VISLCG3] ]
        self.assertListEqual( parsing_results, \
            [[['@SUBJ', 1]], [['@FMV', -1]], [['@ADVL', 1]], [['@P>', 4]], [['@ADVL', 1]], [['xxx', 4]]] )


    def test_vislcg3parser_sent2(self):
        parser = VISLCG3Parser( vislcg_cmd = self.get_vislcg_cmd() )
        text = Text('Suurt hunti nähes ta ehmus ja pani jooksu.')
        text_parsed = parser.parse_text( text )
        parsing_results = [ w[PARSER_OUT] for w in text_parsed[LAYER_VISLCG3] ]
        self.assertListEqual( parsing_results, \
            [[['@AN>', 1]], [['@OBJ', 2]], [['@ADVL', 4]], [['@SUBJ', 4]], [['@FMV', -1]], [['@J', 6]], [['@FMV', 4]], [['@ADVL', 6]], [['xxx', 7]]] )


    def test_vislcg3parser_sent3(self):
        parser = VISLCG3Parser( vislcg_cmd = self.get_vislcg_cmd() )
        text = Text('Saksamaal Bonnis leidis aset kummaline juhtum murdvargaga, kes kutsus endale ise politsei.')
        text_parsed = parser.parse_text( text )
        parsing_results = [ w[PARSER_OUT] for w in text_parsed[LAYER_VISLCG3] ]
        self.assertListEqual( parsing_results, \
            [[['@ADVL', 2]], [['@<NN', 2], ['@ADVL', 2]], [['@FMV', -1]], [['@OBJ', 2]], [['@AN>', 5]], [['@SUBJ', 2]], [['@ADVL', 2], ['@<NN', 2]], [['xxx', 6]], [['@SUBJ', 9]], [['@FMV', 6]], [['@ADVL', 9]], [['@ADVL', 9]], [['@OBJ', 9]], [['xxx', 12]]] )

    def test_vislcg3parser_sent1_with_text(self):
        parser = VISLCG3Parser( vislcg_cmd = self.get_vislcg_cmd() )
        text = Text('Jänes oli parajasti põllu peal.', syntactic_parser=parser )
        text.tag_syntax() 
        expected_layer = [{'end': 5, 'sent_id': 0, 'parser_out': [['@SUBJ', 1]], 'start': 0}, \
                          {'end': 9, 'sent_id': 0, 'parser_out': [['@FMV', -1]], 'start': 6}, \
                          {'end': 19, 'sent_id': 0, 'parser_out': [['@ADVL', 1]], 'start': 10}, \
                          {'end': 25, 'sent_id': 0, 'parser_out': [['@P>', 4]], 'start': 20}, \
                          {'end': 30, 'sent_id': 0, 'parser_out': [['@ADVL', 1]], 'start': 26}, \
                          {'end': 31, 'sent_id': 0, 'parser_out': [['xxx', 4]], 'start': 30}]
        #print(text[LAYER_VISLCG3])
        self.assertListEqual( text[LAYER_VISLCG3], expected_layer )
        
    def test_vislcg3parser_sent1_with_text_trees(self):
        parser = VISLCG3Parser( vislcg_cmd = self.get_vislcg_cmd() )
        text = Text('Jänes oli parajasti põllu peal.', syntactic_parser=parser )
        trees = text.syntax_trees()
        self.assertEqual( len(trees), 1 )
        self.assertDictEqual( trees[0].syntax_token, \
            {'end': 9, 'sent_id': 0, 'parser_out': [['@FMV', -1]], 'start': 6} )
        self.assertDictEqual( trees[0].token, \
            {'end': 9, 'start': 6, 'analysis': [{'form': 's', 'root_tokens': ['ole'], 'lemma': 'olema', 'partofspeech': 'V', 'root': 'ole', 'clitic': '', 'ending': 'i'}], 'text': 'oli'} )


    def test_vislcg3parser_return_depgraph1(self):
        parser = VISLCG3Parser( vislcg_cmd = self.get_vislcg_cmd() )
        text = Text('Kohtusid suur hunt ja kuri lammas. Auhinnaks oli ilus valge tekk.')
        dep_graphs = parser.parse_text( text, return_type="dep_graphs" )
        
        treeStr = str(dep_graphs[0].tree()).strip()
        self.assertEqual(treeStr, '(Kohtusid (hunt suur (lammas ja kuri .)))')

        treeStr = str(dep_graphs[1].tree()).strip()
        self.assertEqual(treeStr, '(oli Auhinnaks (tekk ilus valge .))')


    def test_reading_from_cg3_file_1(self):
        test_cg3_string = \
'''"<s>"

"<Keni>"
	"Ken" L0 S prop sg gen @ADVL #1->4
"<&amp;>"
	"&" L0 J crd @J #2->3
"<Tolgiga>"
	"Tolk" Lga S prop sg kom @ADVL #3->1
"<saab>"
	"saa" Lb V main indic pres ps3 sg ps af @FMV #4->0
"<alati>"
	"alati" L0 D @ADVL #5->4
"<kõvasti>"
	"kõvasti" L0 D @OBJ #6->4
"<pulli>"
	"pull" L0 S com sg part @<Q #7->6
"<.>"
	"." Z Fst #8->8
"</s>"

"<s>"

"<Nüüd>"
	"nüüd" L0 D @ADVL #1->0
"<tagasi>"
	"tagasi" L0 D @ADVL #2->1
"<Decoltesse>"
	"Decolte" Lsse S prop sg ill @ADVL #3->1
"<.>"
	"." Z Fst #4->4
"</s>"

'''
        # Create a temporary file (with cg3 format content)
        import codecs
        import tempfile
        import os
        temp_input_file = \
            tempfile.NamedTemporaryFile(prefix='test_cg3_in.', mode='w', delete=False)
        temp_input_file.close()
        # We have to open separately here for writing, because Py 2.7 does not support
        # passing parameter   encoding='utf-8'    to the NamedTemporaryFile;
        out_f = codecs.open(temp_input_file.name, mode='w', encoding='utf-8')
        out_f.write( test_cg3_string )
        out_f.close()
        
        from estnltk.syntax.utils import read_text_from_cg3_file
        text = read_text_from_cg3_file( temp_input_file.name )
        os.remove(temp_input_file.name)
        self.assertTrue( LAYER_VISLCG3 in text )
        self.assertTrue( len(text.sentence_texts) == 2 )
        cg3_layer    = [ w[PARSER_OUT] for w in text[LAYER_VISLCG3] ]
        #print(cg3_layer)
        expected_layer = [[['@ADVL', 3]], [['@J', 2]], [['@ADVL', 0]], [['@FMV', -1]], [['@ADVL', 3]], [['@OBJ', 3]], [['@<Q', 5]], [['xxx', 6]], [['@ADVL', -1]], [['@ADVL', 0]], [['@ADVL', 0]], [['xxx', 2]]]
        self.assertListEqual( cg3_layer, expected_layer )

