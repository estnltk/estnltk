from lxml import etree
from estnltk import ElementaryBaseSpan
from estnltk import Layer, Text

from estnltk.taggers.standard.morph_analysis.morf_common import NORMALIZED_TEXT, ESTNLTK_MORPH_ATTRIBUTES

def import_TCF(string:str=None, file:str=None):
    if file:
        text_tree = etree.parse(file).getroot()
    else:
        text_tree = etree.fromstring(string)

    text_corpus = text_tree.find('{http://www.dspin.de/data/textcorpus}TextCorpus')

    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}text')
    assert element is not None, "no text tag in the file '"+file+"'"
    t = element.text
    if t is None:
        t = ''
    text = Text(t)

    # words layer
    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}tokens')
    if element is not None:
        id_to_token = {}
        layer = Layer(name='words', attributes=['normalized_form'], ambiguous=True)
        for token in element:
            annotation = layer.add_annotation(ElementaryBaseSpan(int(token.get('start')), int(token.get('end'))))
            id_to_token[token.get('ID')] = annotation.span
        text.add_layer(layer)

    # sentences layer
    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}sentences')
    if element is not None:
        layer = Layer(enveloping='words',
                      name='sentences')
        for sentence in element:
            spans = [id_to_token[token_id] for token_id in sentence.get('tokenIDs').split()]
            layer.add_annotation(spans)
        text.add_layer(layer)

    # clauses layer
    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}clauses')
    if element is not None:
        layer = Layer(enveloping='words',
                      name='clauses')
        for clause in element:
            spans = [id_to_token[token_id] for token_id in clause.get('tokenIDs').split()]
            layer.add_annotation(spans)
        text.add_layer(layer)

    # chunk layers: verb_chains, time_phrases
    element = text_corpus.find('{http://www.dspin.de/data/textcorpus}chunks')
    if element is not None:
        layer_vp = Layer(enveloping='words',
                         name='verb_chains')
        layer_tmp = Layer(enveloping='words',
                          name='time_phrases')
        for line in element:
            chunk_type = line.get('type')
            if chunk_type == 'VP':
                spans = [id_to_token[token_id] for token_id in line.get('tokenIDs').split()]
                layer_vp.add_annotation(spans)
            elif chunk_type == 'TMP':
                spans = [id_to_token[token_id] for token_id in line.get('tokenIDs').split()]
                layer_tmp.add_annotation(spans)
        text.add_layer(layer_vp)
        text.add_layer(layer_tmp)

    # morph_analysis layer
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
    
        #morph_attributes = list( ESTNLTK_MORPH_ATTRIBUTES )
        morph_attributes = [NORMALIZED_TEXT] + list(ESTNLTK_MORPH_ATTRIBUTES)
        morph = Layer(name='morph_analysis',
                      parent='words',
                      ambiguous=True,
                      attributes=morph_attributes
                      )
        for word, analyses in zip(text.words, morph_analysis_records):
            for analysis in analyses:
                if NORMALIZED_TEXT in morph.attributes:
                    analysis[NORMALIZED_TEXT] = word.text
                morph.add_annotation(word, **analysis)

        text.add_layer(morph)

    return text
