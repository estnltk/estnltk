"""

Converts conll_morph_layer to CONLL-U.

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

from conllu.serializer import serialize_field

def conll_to_str(text, conll_morph_layer=None, preserve_ambiguity=True, serialize=True):
    '''
    TODO: relocate to converters.conll
    TODO: add documentation
    TODO: rename conll_morph_layer --> layer
    TODO: make sentences and words layer names changable
    
    For Maltparser, use settings preserve_ambiguity=False and serialize=False.
    ''' 
    input_layer = None
    if conll_morph_layer is not None:
        input_layer = text[conll_morph_layer]
    else:
        input_layer = text['conll_morph']
    conll_str = ''
    text_conll_morph_get = input_layer.get
    layer_has_form = 'form' in input_layer.attributes
    for sent in text.sentences:
        for i, word in enumerate(sent.words):
            for aid, annotation in enumerate(text_conll_morph_get(word.base_span).annotations):
                annotation_id = annotation.id
                annotation_form = word.text if not layer_has_form else annotation.form
                annotation_lemma = annotation.lemma
                annotation_upostag = annotation.upostag
                annotation_xpostag = annotation.xpostag
                annotation_feats = annotation.feats
                annotation_head = annotation.head
                annotation_deprel = annotation.deprel
                annotation_deps = annotation.deps
                annotation_misc = annotation.misc
                if serialize:
                    annotation_id      = serialize_field( annotation_id )
                    annotation_form    = serialize_field( annotation_form )
                    annotation_lemma   = serialize_field( annotation_lemma )
                    annotation_upostag = serialize_field( annotation_upostag )
                    annotation_xpostag = serialize_field( annotation_xpostag )
                    annotation_feats   = serialize_field( annotation_feats )
                    annotation_head    = serialize_field( annotation_head )
                    annotation_deprel  = serialize_field( annotation_deprel )
                    annotation_deps    = serialize_field( annotation_deps )
                    annotation_misc    = serialize_field( annotation_misc )
                conll_str += '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n' % (
                    annotation_id, annotation_form, annotation_lemma, annotation_upostag, annotation_xpostag, 
                    annotation_feats, annotation_head, annotation_deprel, annotation_deps, annotation_misc)
                if aid == 0 and not preserve_ambiguity:
                    # Quit 
                    break
        conll_str += '\n'
    return conll_str


# TODO: Remove this method altogether
def write_conll_to_file(filename, conll):
    with open(filename, 'w') as f:
        if isinstance(conll, str):
            f.write(conll)
        else:
            f.write(conll_to_str(conll))

