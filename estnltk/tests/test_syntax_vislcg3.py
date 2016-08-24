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


    def test_vislcg3parser_return_depgraph1(self):
        parser = VISLCG3Parser( vislcg_cmd = self.get_vislcg_cmd() )
        text = Text('Kohtusid suur hunt ja kuri lammas. Auhinnaks oli ilus valge tekk.')
        dep_graphs = parser.parse_text( text, return_type="dep_graphs" )
        
        treeStr = str(dep_graphs[0].tree()).strip()
        self.assertEqual(treeStr, '(Kohtusid (hunt suur (lammas ja kuri .)))')

        treeStr = str(dep_graphs[1].tree()).strip()
        self.assertEqual(treeStr, '(oli Auhinnaks (tekk ilus valge .))')
