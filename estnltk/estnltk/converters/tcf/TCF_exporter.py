from lxml import etree
from lxml.builder import ElementMaker
from estnltk import Text


def export_TCF(t: Text, file:str=None, version='0.4'):
    """
    Export Text to TCF XML format for
    https://weblicht.sfs.uni-tuebingen.de/weblicht/
    
    As a side-effect equips Text object with token layer.

    file: str
        If not None, saves the result in file.
    
    version: str
        '0.4' produces xml that works with current TCF version 'v0.4'
        '0.5' produces xml for future TCF version. This includes layers for 
            clauses, verb_chains and time_phrases.  

    Returns: str
        TCF xml string.
    """

    assert version in {'0.4', '0.5'}, 'Unknown version: ' + str(version)
    
    text_tree = etree.Element('D-Spin', xmlns="http://www.dspin.de/data", version=version)
    doc = etree.ElementTree(text_tree)
    
    etree.SubElement(text_tree, 'MetaData', xmlns="http://www.dspin.de/data/metadata")
    
    etree.SubElement(text_tree, 'TextCorpus', xmlns="http://www.dspin.de/data/textcorpus", lang="et")
    
    etree.SubElement(text_tree[1], 'text').text = t.text

    E = ElementMaker(namespace='http://www.dspin.de/data/textcorpus',
                     nsmap={'tc':'http://www.dspin.de/data/textcorpus'})

    token_ids = {}
    if 'words' in t.layers and version in {'0.4', '0.5'}:
        token_ids = {word.base_span: 't'+str(i) for i, word in enumerate(t.words)}
        tokens = E('tokens')
        for word in t.words:
            tokens.append(E('token', word.text, {'ID': token_ids[word.base_span], 'start': str(word.start), 'end': str(word.end)}))
        text_tree[1].append(tokens)

    if 'sentences' in t.layers and version in {'0.4', '0.5'}:
        sentences = E('sentences')
        for i, sentence in enumerate(t.sentences):
            token_IDs = ' '.join((token_ids[word] for word in sentence.base_span))
            sentences.append(E('sentence', {'ID': 's'+str(i), 'tokenIDs': token_IDs}))
        text_tree[1].append(sentences)

    if 'morph_analysis' in t.layers and version in {'0.4', '0.5'}:
        lemmas = E('lemmas')
        for analysis in t.morph_analysis:
            token_id = token_ids[analysis.base_span]
            for a in analysis.annotations:
                # kas nii on õige toimida mitmese märgendiga? (' '.join...)
                lemmas.append(E('lemma', a.lemma, {'ID':token_id.replace('t', 'l'),'tokenIDs':token_id}))
        text_tree[1].append(lemmas)
        
        postags = E('POStags', {'tagset':''})
        for analysis in t.morph_analysis:
            token_id = token_ids[analysis.base_span]
            for a in analysis.annotations:
                # kas nii on õige toimida mitmese märgendiga? (' '.join...)
                postags.append(E('tag', a.partofspeech, {'tokenIDs':token_id}))
        text_tree[1].append(postags)
        
        morphology = E('morphology')
        for analysis in t.morph_analysis:
            token_id = token_ids[analysis.base_span]
            for a in analysis.annotations:
                # kas nii on õige toimida mitmese märgendiga?
                features = E('fs')
                features.append(E('f', a.form, {'name':'form'}))
                features.append(E('f', a.root, {'name':'root'}))
                features.append(E('f', ' '.join(a.root_tokens), {'name':'root_tokens'}))
                features.append(E('f', a.ending, {'name':'ending'}))
                features.append(E('f', a.clitic, {'name':'clitic'}))
                tag = E('tag', features)
                morphology.append(E('analysis', tag, {'tokenIDs':token_id}))
        text_tree[1].append(morphology)

    if 'clauses' in t.layers and version in {'0.5'}:
        element_maker = E('clauses')
        for i, clause in enumerate(t.clauses):
            token_IDs = ' '.join((token_ids[word] for word in clause.base_span))
            element_maker.append(E('clause',  {'tokenIDs':token_IDs}))
        text_tree[1].append(element_maker)

    element_maker = E('chunks',{'tagset':''})
    chunk = False
    count = 0
    if 'verb_chains' in t.layers and version in {'0.5'}:
        chunk = True
        for phrase in t.verb_chains:
            token_IDs = ' '.join((token_ids[token] for token in phrase.base_span))
            element_maker.append(E('chunk',  {'ID':'ch'+str(count), 'type':'VP', 'tokenIDs':token_IDs}))
            count += 1
    if 'time_phrases' in t.layers and version in {'0.5'}:
        chunk = True
        for phrase in t.time_phrases:
            token_IDs = ' '.join((token_ids[token] for token in phrase.base_span))
            element_maker.append(E('chunk',  {'ID':'ch'+str(count), 'type':'TMP', 'tokenIDs':token_IDs}))
            count += 1
    if chunk:
        text_tree[1].append(element_maker)

    if file is not None:
        doc.write(file, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    return etree.tostring(text_tree, encoding='unicode', pretty_print=True)
