'''

Example:

    from estnltk.taggers.syntax.conll_morph_to_str import *
    from estnltk.taggers.syntax.conll_morph_tagger import ConllMorphTagger
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

'''

def conll_to_str(text):
    conll_str = ''
    for sent in text.sentences.conll_morph:
        for i, word in enumerate(sent.words):
            conll_str += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n' % (
                word.id[0], word.form[0], word.lemma[0], word.upostag[0], word.xpostag[0], word.feats[0], word.head[0],
                word.deprel[0], word.deps[0], word.misc[0])
        conll_str += '\n'
    return conll_str

def write_conll_to_file(filename, conll_str):
    with open(filename, 'w') as f:
        f.write(conll_to_str(conll_str))
