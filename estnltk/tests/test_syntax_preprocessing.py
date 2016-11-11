# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import unittest

from ..text import Text
from ..syntax.syntax_preprocessing import SyntaxPreprocessing
from ..names import *

import json

class SyntaxPreprocessingTest(unittest.TestCase):


    def test_process_Text_1(self):
        text = Text('Mitmekesisus on elu vaieldamatu voorus.')
        preprocessor = SyntaxPreprocessing()
        result_lines = preprocessor.process_Text(text)
        #print(result_lines)
        self.assertListEqual( ['"<s>"', \
                           '"<Mitmekesisus>"', \
                           '    "mitme_kesisus" L0 S com sg nom cap  ', \
                           '"<on>"', \
                           '    "ole" L0 V mod indic pres ps3 sg ps af <FinV> <Intr>  ', \
                           '    "ole" L0 V aux indic pres ps3 sg ps af <FinV> <Intr>  ', \
                           '    "ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr>  ', \
                           '    "ole" L0 V mod indic pres ps3 pl ps af <FinV> <Intr>  ', \
                           '    "ole" L0 V aux indic pres ps3 pl ps af <FinV> <Intr>  ', \
                           '    "ole" L0 V main indic pres ps3 pl ps af <FinV> <Intr>  ', \
                           '"<elu>"', \
                           '    "elu" L0 S com sg gen  ', \
                           '    "elu" L0 S com sg nom  ', \
                           '    "elu" L0 S com sg part  ', \
                           '"<vaieldamatu>"', \
                           '    "vaieldamatu" L0 A pos sg gen  ', \
                           '    "vaieldamatu" L0 A pos sg nom  ', \
                           '"<voorus>"', \
                           '    "voor" Ls S com sg in  ', \
                           '    "voorus" L0 S com sg nom  ', \
                           '"<.>"', \
                           '    "." Z Fst  ', \
                           '"</s>"'], result_lines )


    def test_process_Text_2(self):
        text = Text('Mitmekesisus on elu vaieldamatu voorus.')
        preprocessor = SyntaxPreprocessing()
        result_lines = preprocessor.process_Text(text)
        # Text object should have an analysis layer after syntactic pre-processing
        # (Note: this layer still contains morph annotations that need a disambiguation)
        self.assertTrue( text.is_tagged(ANALYSIS) )


    def test_process_mrf_lines_1(self):
        mrf_lines = [ '<s>',\
        'Kolmandaks',\
        '    kolmandaks+0 //_D_  //',\
        '    kolmas+ks //_O_ sg tr //',\
        'kihutas',\
        '    kihuta+s //_V_ s //',\
        'end',\
        '    end+0 //_Y_ ? //',\
        '    ise+0 //_P_ sg p //',\
        'soomlane',\
        '    soomlane+0 //_S_ sg n //',\
        '</s>'
        ]
        preprocessor = SyntaxPreprocessing()
        result_lines = preprocessor.process_mrf_lines(mrf_lines)
        #print(result_lines)
        self.assertListEqual( ['"<s>"', \
                               '"<Kolmandaks>"', \
                               '    "kolmandaks" L0 D cap  ', \
                               '    "kolmas" Lks N ord sg tr roman cap  ', \
                               '    "kolmas" Lks N ord sg tr l cap  ', \
                               '"<kihutas>"', \
                               '    "kihuta" Ls V mod indic impf ps3 sg ps af <FinV> <NGP-P>  ', \
                               '    "kihuta" Ls V aux indic impf ps3 sg ps af <FinV> <NGP-P>  ', \
                               '    "kihuta" Ls V main indic impf ps3 sg ps af <FinV> <NGP-P>  ', \
                               '"<end>"', \
                               '    "end" L0 Y nominal   ', \
                               '    "ise" L0 P pos det refl sg part  ', \
                               '"<soomlane>"', \
                               '    "soomlane" L0 S com sg nom  ', \
                               '"</s>"'], result_lines )

                               
    def test_process_vm_json_1(self):
        json_str = \
        ''' {"sentences":[ {"words":
              [
                {"text": "Nii", "analysis": [{"root_tokens": ["nii"], "ending": "0", "clitic": "", "form": "", "root": "nii", "partofspeech": "D", "lemma": "nii"}], "start": 0, "end": 3},
                {"text": "nad", "analysis": [{"root_tokens": ["tema"], "ending": "d", "clitic": "", "form": "pl n", "root": "tema", "partofspeech": "P", "lemma": "tema"}], "start": 4, "end": 7},
                {"text": "tapsidki", "analysis": [{"root_tokens": ["tap"], "ending": "sid", "clitic": "ki", "form": "sid", "root": "tap", "partofspeech": "V", "lemma": "tapma"}, {"root_tokens": ["tapsi"], "ending": "d", "clitic": "ki", "form": "d", "root": "tapsi", "partofspeech": "V", "lemma": "tapsima"}], "start": 8, "end": 16},
                {"text": "meie", "analysis": [{"root_tokens": ["mina"], "ending": "0", "clitic": "", "form": "pl g", "root": "mina", "partofspeech": "P", "lemma": "mina"}, {"root_tokens": ["mina"], "ending": "0", "clitic": "", "form": "pl n", "root": "mina", "partofspeech": "P", "lemma": "mina"}], "start": 17, "end": 21},
                {"text": "Ferdinandi", "analysis": [{"root_tokens": ["Ferdinand"], "ending": "0", "clitic": "", "form": "adt", "root": "Ferdinand", "partofspeech": "H", "lemma": "Ferdinand"}, {"root_tokens": ["Ferdinand"], "ending": "0", "clitic": "", "form": "sg g", "root": "Ferdinand", "partofspeech": "H", "lemma": "Ferdinand"}, {"root_tokens": ["Ferdinand"], "ending": "0", "clitic": "", "form": "sg p", "root": "Ferdinand", "partofspeech": "H", "lemma": "Ferdinand"}, {"root_tokens": ["Ferdinandi"], "ending": "0", "clitic": "", "form": "sg g", "root": "Ferdinandi", "partofspeech": "H", "lemma": "Ferdinandi"}, {"root_tokens": ["Ferdinandi"], "ending": "0", "clitic": "", "form": "sg n", "root": "Ferdinandi", "partofspeech": "H", "lemma": "Ferdinandi"}, {"root_tokens": ["Ferdinant"], "ending": "0", "clitic": "", "form": "sg g", "root": "Ferdinant", "partofspeech": "H", "lemma": "Ferdinant"}], "start": 22, "end": 32},
                {"text": ".", "analysis": [{"root_tokens": ["."], "ending": "", "clitic": "", "form": "", "root": ".", "partofspeech": "Z", "lemma": "."}], "start": 32, "end": 33}
              ]
            } ]}
        '''
        preprocessor = SyntaxPreprocessing()
        result_lines = preprocessor.process_vm_json( json.loads(json_str) )
        #print(result_lines)
        self.assertListEqual( ['"<s>"', \
                               '"<Nii>"', \
                               '    "nii" L0 D cap  ', \
                               '"<nad>"', \
                               '    "tema" Ld P pers ps3 pl nom  ', \
                               '"<tapsidki>"', \
                               '    "tap" Lsidki V mod indic impf ps3 pl ps af <FinV> <NGP-P>  ', \
                               '    "tap" Lsidki V mod indic impf ps2 sg ps af <FinV> <NGP-P>  ', \
                               '    "tap" Lsidki V aux indic impf ps3 pl ps af <FinV> <NGP-P>  ', \
                               '    "tap" Lsidki V aux indic impf ps2 sg ps af <FinV> <NGP-P>  ', \
                               '    "tap" Lsidki V main indic impf ps3 pl ps af <FinV> <NGP-P>  ', \
                               '    "tap" Lsidki V main indic impf ps2 sg ps af <FinV> <NGP-P>  ', \
                               '    "tapsi" Ldki V mod indic pres ps2 sg ps af <FinV> <Intr>  ', \
                               '    "tapsi" Ldki V aux indic pres ps2 sg ps af <FinV> <Intr>  ', \
                               '    "tapsi" Ldki V main indic pres ps2 sg ps af <FinV> <Intr>  ', \
                               '"<meie>"', \
                               '    "mina" L0 P pers ps1 pl gen  ', \
                               '    "mina" L0 P pers ps1 pl nom  ', \
                               '"<Ferdinandi>"', \
                               '    "Ferdinand" L0 S prop sg adit cap  ', \
                               '    "Ferdinand" L0 S prop sg gen cap  ', \
                               '    "Ferdinand" L0 S prop sg part cap  ', \
                               '    "Ferdinandi" L0 S prop sg gen cap  ', \
                               '    "Ferdinandi" L0 S prop sg nom cap  ', \
                               '    "Ferdinant" L0 S prop sg gen cap  ', \
                               '"<.>"', \
                               '    "." Z Fst  ', \
                               '"</s>"'], result_lines )
