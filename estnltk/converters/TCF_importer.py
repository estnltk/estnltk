from lxml import etree
from estnltk import Text
from estnltk.text import Span, Layer

def import_TCF(file):
    text_tree = etree.parse('out.xml').getroot()
    text_corpus = text_tree.find('{http://www.dspin.de/data/textcorpus}TextCorpus')

    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}text')
    if element is not None:
        t = element.text

    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}tokens')
    if element is not None:
        tokens = {}
        token_rec = []
        for token in element:
            token_rec.append({'start':int(token.get('start')), 'end':int(token.get('end')), 'ID': token.get('ID')})
            tokens[token.get('ID')] = token.text

    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}sentences')
    if element is not None:
        #print('sentences:')
        for sentence in element:
            sentence.get('tokenIDs')
            s = ' '.join((tokens[token_id] for token_id in sentence.get('tokenIDs').split()))
        #    print('\t', s)

    morph_analysis_list = []
    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}lemmas')
    if element is not None:
        for f in element:
            morph_analysis_list.append({'tokenID': f.get('tokenIDs'), 'lemma': f.text})

    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}POStags')
    if element is not None:
        for f, rec in zip(element, morph_analysis_list):
            assert rec['tokenID'] == f.get('tokenIDs')
            rec['partofspeech'] = f.text

    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}morphology')
    if element is not None:
        for analysis, rec in zip(element, morph_analysis_list):
            tag = analysis.find('{http://www.dspin.de/data/textcorpus}tag')
            fs = tag.find('{http://www.dspin.de/data/textcorpus}fs')

            form = fs.find('{http://www.dspin.de/data/textcorpus}f[@name="form"]').text
            root = fs.find('{http://www.dspin.de/data/textcorpus}f[@name="root"]').text
            root_tokens = fs.find('{http://www.dspin.de/data/textcorpus}f[@name="root_tokens"]').text
            if root_tokens is None:
                root_tokens = []
            else:
                root_tokens = root_tokens.split()
            ending = fs.find('{http://www.dspin.de/data/textcorpus}f[@name="ending"]').text
            clitic = fs.find('{http://www.dspin.de/data/textcorpus}f[@name="clitic"]').text
            if clitic is None:
                clitic = ''
            rec['form'] = form if form else ''
            rec['root'] = root if root else ''
            rec['root_tokens'] = root_tokens
            rec['ending'] = ending if ending else ''
            rec['clitic'] = clitic if clitic else ''

    morph_analysis_records = [[]]
    token_id = morph_analysis_list[0]['tokenID']
    for rec in morph_analysis_list:
        if rec['tokenID'] != token_id:
            morph_analysis_records.append([rec])
            token_id = rec['tokenID']
        else:
            morph_analysis_records[-1].append(rec)

    text = Text(t)

    text['words'] = Layer(name='words').from_records(token_rec, rewriting=True)

    morph_attributes = ['lemma', 'root', 'root_tokens', 'ending',
                        'clitic', 'form', 'partofspeech']
    morph = Layer(name='morf_analysis',
                  parent='words',
                  ambiguous=True,
                  attributes=morph_attributes
                  )
    for word, analyses in zip(text.words, morph_analysis_records):
        for analysis in analyses:
            span = morph.add_span(Span(parent=word))
            for attr in morph_attributes:
                setattr(span, attr, analysis[attr])

    text['morf_analysis'] = morph
    return text
