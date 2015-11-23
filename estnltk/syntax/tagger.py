# -*- coding: utf-8 -*-
""" This module uses Kaili's and Tiina's syntax tagger and adds relevant layers to the Text objects.
Note that the vislcg3, perl, awk and tagger09 programs must be installed and should be referenced via PATH
environment variable.

Check out these resources if you have no idea what this file is about:

* https://korpused.keeleressursid.ee/syntaks/index.php?keel=ee
* http://kodu.ut.ee/~kaili/grammatika/
* http://math.ut.ee/~tiinapl/CGParser.tar.gz
* http://kodu.ut.ee/~kaili/thesis/pt3_4.html
* http://kodu.ut.ee/~kaili/Korpus/pindmine/labels.pdf

"""
from __future__ import unicode_literals, print_function, absolute_import


import tempfile
import os
from subprocess import Popen, PIPE

from ..core import PACKAGE_PATH, as_unicode
from ..names import *


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
    """Kaili-s and Tiinas syntax tagger wrapper."""

    def tag_text(self, text):
        """ Tag the given text instance. """
        if len(text[TEXT]) == 0:
            return text
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as fp:
            # convert the text to old format and save it as a temporary file
            convert_to_old(fp, text)
            fp.seek(0)

            # execute all the programs on the input
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

            # parse the output
            result = as_unicode(p12.communicate()[0])
            tokens = parse_result(result)

            # add it to the words and return the text
            return add_layer(text, tokens)


def parse_variant(line):
    """ Every syntax analysis result variant is stored on a seprate line.
    This function parses the file and creates a dictionary of the parsed results.

    Keys:
    syntax - list of syntactic tokens
    intermediate - list of GC intermediate tokens (might be relevant?)
    link - the dependency grammar style link between two words
    form - as there can be ambiguity, this is the form outputted by the script.
    """
    syntax = set()
    link = None
    form = []
    intermediate = set()
    for tok in line.split():
        if tok.startswith('@'):
            syntax.add(tok)
        elif tok.startswith('<') and tok.endswith('>'):
            intermediate.add(tok)
        elif tok.startswith('#'):
            link = tok
        else:
            form.append(tok)
    return {SYNTAX: list(sorted(syntax)),
            INTERMEDIATE: list(sorted(intermediate)),
            FORM: ' '.join(form[3:]),
            LINK: link}


def parse_result(result):
    """ Parse the result into a list of elements.
    The number of elements should match the number of words in the input.
    """
    words = []
    variants = []
    for line in result.splitlines():
        if len(line) > 1 and line[0] == '\t': # this is some kind of variant
            variants.append(parse_variant(line))
        else:
            if len(variants) > 0:
                words.append(variants)
                variants = []
    if len(variants) > 0:
        words.append(variants)
    return words


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


def add_layer(text, result):
    if len(text[WORDS]) != len(result):
        raise Exception('The number of parsed results <{0}> does not match the number of words <{1}>!'.format(len(result), len(text[WORDS])))
    for w, r in zip(text[WORDS], result):
        w[SYNTAX] = r
    return text

