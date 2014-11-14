# -*- encoding: utf8 -*-
import re
import operator
import time
from subprocess import Popen, PIPE
from cStringIO import StringIO

from ner import Token, Sentence, Document

def estmorf_preprocess(text):
    """ Returns documents of sentences """
    text_snts = _to_t3mesta(text)
    t3mesta_snts = _t3mesta_process(text_snts)
    snts = _tokenize(t3mesta_snts)
    doc = Document()
    doc.snts = snts
    doc.tokens = reduce(operator.add, snts, [])
    _set_token_positions(doc.tokens, text)
    return doc

def _to_t3mesta_old(text):
    """ 
    1. Bring sentences to new line
    2. Split punctuation:
        Just imagine... Yes, It's true?
            --> ['Just imagine', '...', 'Yes', ',', "It's true", '?', '']
    """
    
    # Sentence tokenize:
    snts = re.split(r"(\S.+?[\.!?])(?=\s+[A-Z]|$)", text)
    # Word tokenize:
    for i, snt in enumerate(snts):
        toks = re.split(r"(?<=\w)([^\w\s]+)(?:\s|$)", snt)
        snts[i] = " ".join(toks).strip()
    return "\n\n".join(snts)

def _to_t3mesta(text):
    """ 
    1. Bring sentences to new line
    2. Split punctuation:
        'Just imagine... Yes, It's true?' --> 'Just imagine ... Yes , It's true ?' 
    """
    # Sentence tokenize:
    snts = snt_tokenize(text)
    snts = [snt.strip() for snt in snts]
    snts = [snt for snt in snts if snt] 
    # Split punctuation:
    for i, snt in enumerate(snts):
        snts[i] = split_puctuation(snt)
    return snts

snt_pat = re.compile(r'\n|(?<=[\!\.\?])\s+(?=[A-Z]|$)', re.M)
def snt_tokenize(text):
    snts = snt_pat.split(text)
    return snts

pun_pat_after = re.compile(r'(?<=\w)([^\w\s]+)(?=\s|$)', re.U)
pun_pat_before = re.compile(r'(?:^|(?<=\s))([^\w\s]+)(?=\w)', re.U)
pun_split = re.compile(r'(?<=[^\w\-])([^\w\s])(?=[^\w\s\-])', re.U)
def split_puctuation(text):
    text = pun_pat_before.sub(r'\1 ', text)
    text = pun_pat_after.sub(r' \1', text)
    text = pun_split.sub(r'\1 ', text)
    return text

def _tokenize(t3mesta_snts):
    tok_pat = re.compile(r"(?P<word>.+?)    (?P<lemma>.+?) //(?P<morph>.+?),? //")
    snts = []
    for t3mesta_snt in t3mesta_snts:
        snt = Sentence()
        for line in t3mesta_snt.split('\n'):
            match = tok_pat.search(line)
            if match:
                token = Token()
                token.word = match.group('word')
                token.lemma = match.group('lemma')
                token.morph  = match.group('morph')
                if len(snt) > 0:
                    token.prew = snt[-1]
                    snt[-1].next = token
                snt.append(token)
            else:
                raise ValueError('Invalid line "%s"' % line)
        snts.append(snt)
    return snts


def _set_token_positions(tokens, text):
    next_idx = 0
    for token in tokens:
        idx = text.index(token.word, next_idx)
        next_idx = idx + len(token.word)
        token.start_pos, token.end_pos = idx, next_idx



def _t3mesta_process(snts):
    import settings
    process = Popen("t3mesta -Y -cio utf8 +1 +ignoretag".split(), bufsize=-1, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    input_text = "\n<s>\n".join(snts)
    stdout, stderr = process.communicate(input_text.encode('utf8'))
    if stderr:
        raise Exception("t3mesta error! stderr: %s" % stderr)
    t3mesta_snts = stdout.decode('utf8').split("<s>")
    t3mesta_snts = [snt.strip() for snt in t3mesta_snts]
    t3mesta_snts = [snt for snt in t3mesta_snts if snt]
    return t3mesta_snts

def _t3mesta_process_fast(snts):
    from threading  import Thread
    from cStringIO import StringIO
    import sys
    import os
    p = Popen(settings.t3mesta_cmd.split(), stdin=PIPE, stdout=PIPE)
    def worker(input):
        print input.read()
    Thread(target=worker, args=(p.stdout,)).start()
    for i, snt in enumerate(snts):
        print i, snt
        p.stdin.write(snt)
        p.stdin.flush()
    
#    for snt in snts:
#        print >> p.stdin, snt
#    print os.read(pipe_read, 1)
#    p.stdin.flush()
#    print mystdout.getvalue() + "YPYP"

if __name__ == "__main__":
    t = u"Kopsude CT-uuringul 11.04.12 tbc muutused.Pöördus pulmonoloogi juurde 12.04.12 ( dr. O.Popova ) saadetud Kose tbc os. uuringuks ja raviks. "
    print estmorf_preprocess(t)
    import sys
    sys.exit()
    
    fnm = "C:/Documents and Settings/AT/projects/ut/estner/res/test_text/sample3.txt"
    text = open(fnm).read().decode("utf8")
    snts = _to_t3mesta(text)[:5]
#    doc = estmorf_preprocess(text)
    _t3mesta_process_fast(snts)
    import sys
    import cProfile
    cProfile.run('_t3mesta_process_fast(text)')
    sys.exit()
