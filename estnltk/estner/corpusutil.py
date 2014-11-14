import re
import codecs
import sys
from estner.ner import Document, Token, Sentence

def docs2text(docs):
    for doc in docs:
        yield doc2cnll(doc)
        
def doc2cnll(doc):
    yield '<i=%d>' % doc.docid
    for snt in doc.snts:
        yield '<s>'
        for t in snt:
            yield ('%s\t%s\t%s\t%s' % (t.word, t.lemma, t.morph, t.predicted_label)).encode('utf8')
        yield '</s>'
    yield '</i>'

token_pat = re.compile(r"^(?P<word>.+)\t(?P<lemma>.+)\t(?P<morph>.+)\t(?P<label>.+)$")

def load_docs(fnm, num=1000000):
    document, snt = None, None
    doc_cnt = 0
    label_set = set(['B-PER', 'I-PER', 'O'])
    for ln in codecs.open(fnm, encoding="utf8"):
        ln = ln.rstrip()
        if not ln:
            continue
        elif ln == '<s>':
            snt = Sentence()
        elif ln == '</s>':
            document.snts.append(snt)
        elif ln.startswith('<i='):
            docid = int(ln[3:-1])
            document = Document()
            document.docid = docid 
        elif ln == '</i>':
            yield document
            doc_cnt += 1
            if doc_cnt >=  num:
                raise StopIteration()
        else:
            match = token_pat.search(ln)
            if match:
                token = Token()
                token.word = match.group("word")
                token.lemma = match.group("lemma")
                token.morph = match.group("morph")
                token.label = match.group("label")
                if token.label not in label_set:
                    raise Exception("Invalid token label '%s'." % ln.encode("utf8"))
            else:
                raise Exception("Invalid token '%s'." % ln.encode("utf8"))
            snt.append(token)
            token.sentence = snt 
            document.tokens.append(token)
            token.document = document
    raise StopIteration()

