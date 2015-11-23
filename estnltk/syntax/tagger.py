# -*- coding: utf-8 -*-
""" This module uses Kaili's and Tiina's syntax tagger and adds relevant layers to the Text objects.
Note that the vislcg3, perl, awk and tagger09 programs must be installed and should be referenced via PATH
environment variable.
"""
from __future__ import unicode_literals, print_function, absolute_import

import sys
import tempfile
import codecs
import os
from subprocess import Popen, PIPE

from ..core import PACKAGE_PATH, as_unicode
from ..text import Text
from ..names import SENTENCES, WORDS, ANALYSIS, TEXT, ENDING, ROOT, FORM, POSTAG


PATH = os.path.join(PACKAGE_PATH, 'syntax')

prog01 = ['perl', os.path.join(PATH, 'rtolkija.pl')]
prog02 = ['perl', os.path.join(PATH, 'tpron.pl')]
prog03 = ['perl', os.path.join(PATH, 'tcopyremover.pl')]
prog04 = ['awk', '-f', os.path.join(PATH, 'TTRELLID.AWK')]
prog05 = ['./tagger09', os.path.join(PATH, 'abileksikon06utf.lx'), 'stdin', 'stdout']
prog06 = ['perl', os.path.join(PATH, 'tcopyremover.pl')]
prog07 = ['perl', os.path.join(PATH, 'tkms2cg3.pl')]
prog08 = ['./vislcg3', '-o', '-g', os.path.join(PATH, 'clo_ub.rle')]
prog09 = ['./vislcg3', '-o', '-g', os.path.join(PATH, 'morfyhe_ub.rle')]
prog10 = ['./vislcg3', '-o', '-g', os.path.join(PATH, 'PhVerbs_ub.rle')]
prog11 = ['./vislcg3', '-o', '-g', os.path.join(PATH, 'pindsyn_ub.rle')]
prog12 = ['./vislcg3', '-o', '-g', os.path.join(PATH, 'strukt_ub.rle')]


class SyntaxTagger(object):

    def tag_text(self, text):
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as fp:
            convert_to_old(fp, text)
            fp.seek(0)
            p1 = Popen(prog01, stdin=fp, stdout=PIPE)
            p2 = Popen(prog02, stdin=p1.stdout, stdout=PIPE)
            p3 = Popen(prog03, stdin=p2.stdout, stdout=PIPE)
            p4 = Popen(prog04, stdin=p3.stdout, stdout=PIPE)
            p5 = Popen(prog05, stdin=p4.stdout, stdout=PIPE)
            p6 = Popen(prog06, stdin=p5.stdout, stdout=PIPE)
            p7 = Popen(prog07, stdin=p6.stdout, stdout=PIPE)
            p8 = Popen(prog08, stdin=p7.stdout, stdout=PIPE)
            p9 = Popen(prog09, stdin=p8.stdout, stdout=PIPE)
            p10 = Popen(prog10, stdin=p9.stdout, stdout=PIPE)
            p11 = Popen(prog11, stdin=p10.stdout, stdout=PIPE)
            p12 = Popen(prog12, stdin=p11.stdout, stdout=PIPE)

            p1.stdout.close()
            p2.stdout.close()
            p3.stdout.close()
            p4.stdout.close()
            p5.stdout.close()
            p6.stdout.close()
            p7.stdout.close()
            p8.stdout.close()
            p9.stdout.close()
            p10.stdout.close()
            p11.stdout.close()

            result = as_unicode(p12.communicate()[0])
            print (result)


def convert_to_old(fp, text):
    """Convert Estnltk JSON to oldskool t3mesta format.

    Parameters
    ----------
    fp: the file pointer/stream such as sys.stdout
        The file we will write the output.
    text: estnltk.text.Text
        The text instance to be converted.
    """
    for sentence in text.divide(WORDS, SENTENCES):
        fp.write('<s>\n\n')
        for word in sentence:
            fp.write(word[TEXT])
            fp.write('\n')
            for al in word[ANALYSIS]:
                if al[ENDING] == "":
                    toks = ["    ", al[ROOT].replace("\\", "\\\\"), "+0 //_", al[POSTAG], '_ ', al[FORM], " //\n"]
                else:
                    toks = ["    ", al[ROOT].replace("\\", "\\\\"), '+', al[ENDING],
                            " //_", al[POSTAG], '_ ', al[FORM], " //\n"]
                fp.write(''.join(toks))
        fp.write('</s>\n\n')


tagger = SyntaxTagger()
text = Text('Kes tasa sõuab, see võibolla jõuab kaugele, kui tema aerud ära ei mädane. See teine lause on siin niisama. Kuid mis siin ikka pikalt mõtiskleda, on nende asjadega nagu on.')
text.tag_analysis()
tagger.tag_text(text)


