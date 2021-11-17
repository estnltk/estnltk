from typing import List
from conllu import parse_incr
from estnltk import Layer, Text, ElementaryBaseSpan
from estnltk.taggers import SyntaxDependencyRetagger


def add_layer_from_conll(file: str, text: Text, syntax_layer: str):
    """
    Reads a file in conll format, creates a new syntax layer and adds it to the Text object that must have the
    words layer. The new syntax layer is aligned with the existing words layer. If this fails, an exception is raised.
    :param file: str
        name of the conll file
    :param text: Text
        Text object with words layer.
    :param syntax_layer: str
        name for the syntax layer
    :return: Text
        Text object with the new synax layer.
    """
    assert 'words' in text.layers
    assert syntax_layer not in text.layers

    words = text.words
    len_words = len(words)

    syntax = Layer(name=syntax_layer,
                   text_object=text,
                   attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'],
                   ambiguous=False,
                   )

    word_index = 0

    with open(file, "r", encoding="utf-8") as data_file:

        for conll_sentence in parse_incr(data_file, fields=('id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')):
            for conll_word in conll_sentence:
                token = conll_word['form']

                if word_index >= len_words:
                    raise Exception("can't match file with words layer")
                while token != words[word_index].text:
                    word_index += 1
                    if word_index >= len_words:
                        raise Exception("can't match file with words layer")

                w_span = words[word_index]

                # add values for 'id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'
                syntax.add_annotation((w_span.start, w_span.end), **conll_word)
                word_index += 1

    text.add_layer(syntax)

    SyntaxDependencyRetagger(conll_syntax_layer=syntax_layer).retag(text)

    return text


def conll_to_text(file: str, syntax_layer: str = 'conll_syntax') -> Text:
    """
    Reads file in conll format and creates a Text object with words and syntax layers.

    :param file: str
        name of the conll file
    :param syntax_layer: str
        name of the syntax layer
    :return: Text
    """

    text = Text()

    words = Layer(name='words',
                  text_object=text,
                  attributes=[],
                  ambiguous=True
                  )

    sentences = Layer(name='sentences',
                      text_object=text,
                      attributes=[],
                      enveloping='words',
                      ambiguous=False
                      )

    syntax = Layer(name=syntax_layer,
                   text_object=text,
                   attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'],
                   ambiguous=False
                   )
    cur = 0
    t = []

    sentence_start = 0

    with open(file, "r", encoding="utf-8") as data_file:

        for sentence in parse_incr(data_file, fields=('id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')):
            for w in sentence:
                token = w['form']
                t.append(token)
                len_w = len(token)
                base_span = ElementaryBaseSpan(cur, cur+len_w)
                words.add_annotation(base_span)

                syntax.add_annotation(base_span, **w)
                cur += len_w + 1

            sentences.add_annotation(words[sentence_start:])
            sentence_start += len(sentence)

    text.text = ' '.join(t)
    text.add_layer(words)
    text.add_layer(sentences)
    text.add_layer(syntax)

    SyntaxDependencyRetagger(conll_syntax_layer=syntax_layer).retag(text)

    return text


def conll_to_texts_list(file: str, syntax_layer: str = 'conll_syntax', postcorrect_sent_ids: bool=True) -> List[Text]:
    """
    Reads file in conll format and creates separate Text objects according to 
    file names read from the 'sent_id' attributes in the metadata.
    Each Text object will have words, sentences and syntax layers.
    Use this method to import documents separately from conllu files of the 
        https://github.com/UniversalDependencies/UD_Estonian-EDT
    corpus.

    :param file: str
        name of the conll file
    :param syntax_layer: str
        name of the syntax layer
    :param postcorrect_sent_ids: bool
        if True, then postcorrections 
        will be applied to broken 
        'sent_id'-s;
    :return: List[Text]
    """
    texts = []
    words_layers = []
    sentences_layers = []
    syntax_layers = []
    texts.append( Text() )
    words = Layer(name='words',
                  text_object=texts[-1],
                  attributes=[],
                  ambiguous=True
                  )
    words_layers.append( words )
    sentences = Layer(name='sentences',
                      text_object=texts[-1],
                      attributes=[],
                      enveloping='words',
                      ambiguous=False
                      )
    sentences_layers.append( sentences )
    syntax = Layer(name=syntax_layer,
                   text_object=texts[-1],
                   attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'],
                   ambiguous=False
                   )
    syntax_layers.append( syntax )
    
    broken_fnames = ['ntea_AA_05_6', 'ntea_dr8047']
    def _split_into_fname_and_counter( sent_id_str ):
        '''Splits sent_id from the metadata into file name and counter, e.g. 
             sent_id = 'aja_ee200110_2698' ==> ('aja_ee200110', '_2698')
             sent_id = 'aja_epl20061216_1' ==> ('aja_epl20061216', '_1')
             sent_id = 'tea_AA_05_6_90'    ==> ('tea_AA_05_6', '_90')
           Returns results in a tuple.
        '''
        j = -1
        for i in range( len(sent_id_str)-1, -1, -1 ):
            if sent_id_str[i] == '_':
                j = i
                break
        return (sent_id_str[:j], sent_id_str[j:]) if j != -1 else (sent_id_str, '')
    
    cur = 0
    t = []
    sentence_start = 0
    last_fname = None
    last_sent_id = '##start##'
    with open(file, "r", encoding="utf-8") as data_file:
        for sentence in parse_incr(data_file, fields=('id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')):
            cur_sent_id = sentence.metadata.get('sent_id', None)
            if not last_sent_id == '##start##':
                # Determine if we need to create a new document
                if isinstance(last_sent_id, str) and isinstance(cur_sent_id, str):
                    # Separate fname from the sentence counter 
                    last_fname, _ = _split_into_fname_and_counter( last_sent_id )
                    cur_fname, _  = _split_into_fname_and_counter( cur_sent_id )
                    if postcorrect_sent_ids:
                        # Manually correct some broken file names
                        # (remove redundant letter 'n' from the start)
                        if last_fname in broken_fnames:
                            last_fname = last_fname[1:]
                        if cur_fname in broken_fnames:
                            cur_fname = cur_fname[1:]
                    if last_fname != cur_fname:
                        # New document needs to be created
                        # 1) Finalize the previous Text object
                        assert len(t) > 0
                        texts[-1].meta['file_prefix'] = last_fname
                        texts[-1].text = ' '.join(t)
                        texts[-1].add_layer(words_layers[-1])
                        texts[-1].add_layer(sentences_layers[-1])
                        texts[-1].add_layer(syntax_layers[-1])
                        SyntaxDependencyRetagger(conll_syntax_layer=syntax_layer).retag( texts[-1] )
                        # 2) Initiate a new Text object
                        cur = 0
                        t = []
                        sentence_start = 0
                        texts.append( Text() )
                        words = Layer(name='words',
                                      text_object=texts[-1],
                                      attributes=[],
                                      ambiguous=False
                                      )
                        words_layers.append( words )
                        sentences = Layer(name='sentences',
                                          text_object=texts[-1],
                                          attributes=[],
                                          enveloping='words',
                                          ambiguous=False
                                          )
                        sentences_layers.append( sentences )
                        syntax = Layer(name=syntax_layer,
                                       text_object=texts[-1],
                                       attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'],
                                       ambiguous=False
                                       )
                        syntax_layers.append( syntax )
                        
            # Load sentence content
            for w in sentence:
                token = w['form']
                t.append(token)
                len_w = len(token)
                base_span = ElementaryBaseSpan(cur, cur+len_w)
                words_layers[-1].add_annotation(base_span)

                syntax_layers[-1].add_annotation(base_span, **w)
                cur += len_w + 1

            sentences_layers[-1].add_annotation(words[sentence_start:])
            sentence_start += len(sentence)
            last_sent_id = cur_sent_id
    
    # Finalize the Text object
    assert len(t) > 0
    texts[-1].meta['file_prefix'] = last_fname
    texts[-1].text = ' '.join(t)
    texts[-1].add_layer(words_layers[-1])
    texts[-1].add_layer(sentences_layers[-1])
    texts[-1].add_layer(syntax_layers[-1])
    SyntaxDependencyRetagger(conll_syntax_layer=syntax_layer).retag( texts[-1] )
    
    return texts

