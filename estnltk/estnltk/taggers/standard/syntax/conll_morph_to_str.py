"""

Example:

    from estnltk.taggers.standard.syntax.conll_morph_to_str import *
    from estnltk.taggers.standard.syntax.conll_morph_tagger import ConllMorphTagger
    from estnltk import Text
    
    tagger = ConllMorphTagger(output_layer='conll_morph',
                              morph_extended_layer='morph_extended'
                              )
    
    text = Text('Igal aastal maandub Maale 26 000 enam kui sajagrammise massiga meteoriiti . \
    See innustab kirjutama edaspidi veel tihedamini . Samas lõpuaja 16.20 üle polnud väga põhjust nuriseda .')
    text.tag_layer(['morph_extended'])
    tagger.tag(text)
    write_conll_to_file('conll_sentences.conll', text)
    print(conll_to_str(text))

"""


def conll_to_str(text, conll_morph_layer=None):
    conll_str = ''
    if conll_morph_layer is not None:
        text_conll_morph_get = text[conll_morph_layer].get
    else:
        text_conll_morph_get = text.conll_morph.get
    for sent in text.sentences:
        for i, word in enumerate(sent.words):
            annotation = text_conll_morph_get(word.base_span).annotations[0]
            conll_str += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n' % (
                annotation.id, annotation.form, annotation.lemma, annotation.upostag, annotation.xpostag,
                annotation.feats, annotation.head, annotation.deprel, annotation.deps, annotation.misc)
        conll_str += '\n'
    return conll_str


def write_conll_to_file(filename, conll):
    with open(filename, 'w') as f:
        if isinstance(conll, str):
            f.write(conll)
        else:
            f.write(conll_to_str(conll))

