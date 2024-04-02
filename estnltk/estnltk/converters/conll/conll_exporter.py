from collections import OrderedDict

from conllu import TokenList
from conllu.serializer import serialize_field


def layer_to_conll(text, layer, sentences_layer='sentences', validate_layer=True, preserve_ambiguity=True, serialize=True, add_ending_tab=False):
    '''
    Converts layer to CONLLU format string. Conversion is done sentence by sentence. 
    Assumes that 1) the convertable layer (or one of its parents) is enveloped by the sentences layer 
    and, 2) the convertable layer has CONLL attributes. CONLL attributes are: ('id', 'form', 
    'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc').
    Attribute 'form' can also be missing, in that case, it's value will be replace by span.text.

    Legacy: for running Maltparser's models, use settings preserve_ambiguity=False, serialize=False 
    and add_ending_tab=True. Otherwise, you should not change parameters serialize and add_ending_tab.

    Parameters
    ----------
    text: EstNLTK Text object
        The text which layer is converted to CONLL-format.
    layer: str
        Name of the convertable layer. The layer must attached to the given 
        Text object and it must have CONLL fields/attributes.
        Layer (or one of its parents) must be enveloped by sentences layer. 
    sentences_layer: str
        Name of the sentences layer. 
        Spans enveloped by sentences layer must correspond to base spans of the 
        convertable layer.
        Defaults to 'sentences'.
    validate_layer: boolean
        If True, then validates that the convertable layer has required CONLL 
        attributes, and throws exception if some of the attributes are missing.
        (Default: True)
    preserve_ambiguity: boolean
        If True, then in case of ambiguous annotations, all annotations will be 
        written to the output CONLL string. Otherwise, only first annotation will 
        by written in case of ambiguity.
        (Default: True)
    serialize: boolean
        If True, then values of all attributes will be serialized using 
        conllu.serializer.serialize_field. Otherwise, no serialization is 
        performed. 
        This is a legacy option, only Maltparser models change it.
        (Default: True)
    add_ending_tab: boolean
        If True, then adds TAB value at the end of each annotation line. 
        This is a legacy option, only Maltparser models change it.
        (Default: False)

    Returns
    -------
    Convertable layer as CONLL-format string.
    '''
    if layer not in text.layers:
        raise ValueError('(!) Input Text object misses required layer {!r}.'.format(layer))
    if sentences_layer not in text.layers:
        raise ValueError('(!) Input Text object misses required layer {!r}.'.format(sentences_layer))
    CONLL_ATTRIBUTES = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']
    convertable_layer = text[layer]
    if validate_layer:
        missing_attributes = []
        for attr in CONLL_ATTRIBUTES:
            if attr == 'form':
                # Attribute 'form' can be replaced by span.text
                continue
            if attr not in convertable_layer.attributes:
                missing_attributes.append(attr)
        if missing_attributes:
            raise ValueError('(!) Input layer {!r} is missing conll fields: {!r}'.format(layer, missing_attributes) )
    layer_has_form = 'form' in convertable_layer.attributes
    text_conll_str = []
    for sentence in text[sentences_layer]:
        for i, word in enumerate(sentence):
            for aid, annotation in enumerate(convertable_layer.get(word.base_span).annotations):
                # Fetch attribute values. Serialize if required
                attribute_values = []
                for conll_attr in CONLL_ATTRIBUTES:
                    attr_value = None
                    if conll_attr == 'form':
                        if not layer_has_form:
                            attr_value = word.text
                        else:
                            attr_value = annotation[conll_attr]
                    else:
                        attr_value = annotation[conll_attr]
                    if serialize:
                        attr_value = serialize_field( attr_value )
                    attribute_values.append( attr_value )
                # Construct conllu line
                assert len(attribute_values) == 10
                conll_line = '\t'.join( attribute_values )
                if add_ending_tab:
                    # TODO: This is used by Maltparser models, not sure why.
                    # we should get rid of it in future
                    conll_line += '\t'
                text_conll_str.append( conll_line )
                if aid == 0 and not preserve_ambiguity:
                    # Take only first annotation
                    break
        # Empty line separates two sentences
        text_conll_str.append( '' )
    # Double newline at the end
    text_conll_str.append( '' )
    return '\n'.join( text_conll_str )


def enc_layer_to_conll(text, enc_layer, extended_feats=True, separate_feats=False):
    '''
    Converts ENC morphosyntactic layer to CONLLU format string. 
    Assumes that the convertable layer has ENC morphosyntactic attributes: ('id', 'lemma', 
    'xpostag', 'feats', 'extended_feats', 'head', 'deprel'). 

    Parameters
    ----------
    text: EstNLTK Text object
        The text which layer is converted to CONLL-format. 
    layer: str
        Name of the convertable layer. The layer must attached to the given 
        Text object and it must have ENC morphosyntactic attributes.
    extended_feats: boolean
        If True, then the CONLL 'feats' field will be filled in with 
        values of layer's 'extended_feats' attribute. Layer's 'extended_feats' 
        contains CG morphosyntactic categories. 
        Otherwise, the CONLL 'feats' field will be filled in with 
        layer's 'feats' attribute. Layer's 'feats' contains Vabamorf's  
        morphological categories.
        (Default: True)
    separate_feats: boolean
        If True, then CONLL 'feats' field will contain morphosyntactic 
        categories separated by '|'. 
        Otherwise, CONLL 'feats' field will contain morphosyntactic 
        categories separated by whitespace. 
        (Default: False)

    Returns
    -------
    Convertable layer as CONLL-format string.
    '''
    if enc_layer not in text.layers:
        raise ValueError('(!) Input Text object misses required layer {!r}.'.format(enc_layer))
    convertable_layer = text[enc_layer]
    missing_attributes = []
    for attr in ('id', 'lemma', 'xpostag', 'feats', 'extended_feats', 'head', 'deprel'):
        if attr not in convertable_layer.attributes:
            missing_attributes.append(attr)
        if missing_attributes:
            raise ValueError('(!) Input ENC layer {!r} is missing attributes: {!r}'.format(enc_layer, missing_attributes) )
    CONLL_ATTRIBUTES = \
        ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']
    i = 0
    text_conll_str = []
    starts_new_sentence = False
    while i < len(convertable_layer):
        syntax_span = convertable_layer[i]
        annotation = syntax_span.annotations[0]
        # Check if this spans starts a new sentence
        if str(annotation['id']) == '1':
            starts_new_sentence = True
        else:
            starts_new_sentence = False
        # Fetch attribute values. Serialize if required
        attribute_values = []
        for conll_attr in CONLL_ATTRIBUTES:
            attr_value = None
            if conll_attr == 'form':
                attr_value = syntax_span.text
            elif conll_attr == 'upostag':
                attr_value = annotation['xpostag']
            elif conll_attr == 'feats':
                if extended_feats:
                    attr_value = annotation['extended_feats']
                else:
                    attr_value = annotation['feats']
            elif conll_attr in ['deps', 'misc']:
                attr_value = ''
            else:
                attr_value = annotation[conll_attr]
            attr_value = serialize_field( attr_value )
            if conll_attr == 'feats':
                if separate_feats and isinstance(attr_value, str):
                    # Split str feats into subparts and separate by '|'
                    attr_value = '|'.join( attr_value.split(' ') )
            attribute_values.append( attr_value )
        # Construct conllu line
        assert len(attribute_values) == 10
        conll_line = '\t'.join( attribute_values )
        if starts_new_sentence and len(text_conll_str) > 0:
            # Empty line separates two sentences
            text_conll_str.append( '' )
        text_conll_str.append( conll_line )
        i += 1
    # Double newline at the end
    text_conll_str.append( '' )
    return '\n'.join( text_conll_str )


def sentence_to_conll(sentence_span, conll_layer, udpipe=False):
    '''
    Converts given sentence span to CONLLU format string.
    TODO: subject to deprecation. replace usages of this function with layer_to_conll and remove it.
    '''
    get_conll = conll_layer.get
    tokens = []
    for word in sentence_span:
        a = get_conll(word).annotations[0]
        token = OrderedDict([('id', a.id),
                             ('form', a.text),
                             ('lemma', a.lemma),
                             ('upostag', a.upostag),
                             ('xpostag', a.xpostag),
                             ('feats', a.feats),
                             ('head', a.head),
                             ('deprel', a.deprel),
                             ('deps', a.deps),
                             ('misc', a.misc)])
        tokens.append(token)
    result = TokenList(tokens).serialize()
    if udpipe:
        return result
    return result.replace('=|', '|').replace('=\t', '\t')
