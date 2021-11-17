from typing import List

from estnltk import Text, Layer, ElementaryBaseSpan

from estnltk.taggers import VabamorfTagger


def conll_to_ner_labelling(filename: str, ner_layer: str = 'wordner') -> Text:
    """
    Converts a CONLL-file with NER labelling into a Text object with the NER-layer.
    The created EstNLTK Text object will include the following layers: words, sentences,
    compound_tokens, wordner, morph_analysis.
    The words and sentences layers are created from the words in the file. The wordner layer
    is created from the NER-tags in the file.
    The morph_analysis layer is added with VabamorfTagger. The compound_tokens layer is left
    empty but is needed for VabamorfTagger to work.

    Parameters
    ---------
    filename: str
        Name of the CONLL-file to be converted to a Text object with a NER layer.
    ner_layer: str
        Name of the NER-layer.
    Returns
    -------
    Text object created from the file.
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

    ner = Layer(name=ner_layer,
                text_object=text,
                attributes=['nertag'],
                ambiguous=False
                )

    comp = Layer(name='compound_tokens',
                 text_object=text,
                 attributes=['type', 'normalized'],
                 ambiguous=False
                 )

    cur = 0
    t = []

    sentence_start = 0

    with open(filename, "r", encoding="UTF-8") as f:
        for sentence in parse_incr(f, fields=('word', 'lemma', 'morph', 'nertag')):
            for w in sentence:
                token = w['word']
                t.append(token)
                len_w = len(token)
                base_span = ElementaryBaseSpan(cur, cur+len_w)
                words.add_annotation(base_span)

                ner.add_annotation(base_span, **{'nertag': w['nertag']})
                cur += len_w + 1

            sentences.add_annotation(words[sentence_start:])
            sentence_start += len(sentence)

    text.text = ' '.join(t)
    text.add_layer(words)
    text.add_layer(sentences)
    text.add_layer(ner)
    text.add_layer(comp)

    vabamorf_tagger = VabamorfTagger()
    vabamorf_tagger(text)

    return text


def conll_to_ner_labelling_lists(filename: str, ner_layer: str = 'wordner') -> List[Text]:
    """
    Converts CONLL-file with NER-labelling into a list of Text objects with NER-layers.
    Each Text object is one sentence from the file.

    Parameters
    ----------
    filename:
        Name of the CONLL-file to be converted to a list of Text objects.
    ner_layer:
        Name of NER-layer.

    Returns
    -------
    List of Text objects created from the file.
    """
    texts = [Text()]

    words_layers = []
    sentence_layers = []
    ner_layers = []
    comp_layers = []

    words = Layer(name='words',
                  text_object=texts[-1],
                  attributes=[],
                  ambiguous=True
                  )
    words_layers.append(words)

    sentences = Layer(name='sentences',
                      text_object=texts[-1],
                      attributes=[],
                      enveloping='words',
                      ambiguous=False
                      )
    sentence_layers.append(sentences)

    ner = Layer(name=ner_layer,
                text_object=texts[-1],
                attributes=['nertag'],
                ambiguous=False
                )
    ner_layers.append(ner)

    comp = Layer(name='compound_tokens',
                 text_object=texts[-1],
                 attributes=['type', 'normalized'],
                 ambiguous=False
                 )
    comp_layers.append(comp)

    cur = 0
    t = []

    sentence_start = 0

    vabamorf_tagger = VabamorfTagger()

    with open(filename, "r", encoding="UTF-8") as f:
        for sentence in parse_incr(f, fields=('word', 'lemma', 'morph', 'nertag')):
            for i, w in enumerate(sentence):
                token = w['word']
                t.append(token)
                len_w = len(token)
                base_span = ElementaryBaseSpan(cur, cur + len_w)
                words_layers[-1].add_annotation(base_span)

                ner_layers[-1].add_annotation(base_span, **{'nertag': w['nertag']})

                cur += len_w + 1

                if i == len(sentence) - 1:
                    sentences.add_annotation(words[sentence_start:])
                    texts[-1].text = ' '.join(t)
                    texts[-1].add_layer(words_layers[-1])
                    texts[-1].add_layer(sentence_layers[-1])
                    texts[-1].add_layer(ner_layers[-1])
                    texts[-1].add_layer(comp_layers[-1])
                    vabamorf_tagger(texts[-1])

                    len_sent = len(words) - sentence_start
                    sentence_start += len_sent

                    texts.append(Text())

                    t = []
                    sentence_start = 0
                    cur = 0

                    words = Layer(name='words',
                                  text_object=texts[-1],
                                  attributes=[],
                                  ambiguous=True
                                  )
                    words_layers.append(words)

                    sentences = Layer(name='sentences',
                                      text_object=texts[-1],
                                      attributes=[],
                                      enveloping='words',
                                      ambiguous=False
                                      )
                    sentence_layers.append(sentences)

                    ner = Layer(name=ner_layer,
                                text_object=texts[-1],
                                attributes=['nertag'],
                                ambiguous=False
                                )
                    ner_layers.append(ner)

                    comp = Layer(name='compound_tokens',
                                 text_object=texts[-1],
                                 attributes=['type', 'normalized'],
                                 ambiguous=False
                                 )
                    comp_layers.append(comp)

    # Since there's a new Text object created and added to the list when
    # an empty string (empty lines in the list) is encountered, this will
    # also be the case for the final sentence, after which an empty Text
    # object will be created and appended to the list. This is removed here.
    texts = texts[:len(texts)-1]
    return texts


def parse_incr(file, fields):
    """
    Function that helps parse the CONLL-file.

    Parameters
    ----------
    file:
        _io.TextIOWrapper type, obtained from opening a file.
    fields:
        Names of tab-separated fields in the file. Each row must contain as many
        tab-separated columns as fields provided and fields must correspond to
        file (basically would act as a header)

    Returns
    -------
    List of sentences obtained from the file, where each sentence is a list that contains
    of dictionaries, each dictionary containing information (fields) about one word.
    """

    info = file.read().split('\n\n')
    sentences = []

    for snt in info:
        snt = snt.split('\n')
        sentence = []
        for w in snt:
            word = w.split('\t')
            if len(word) != len(fields):
                continue
            tok = {}
            for i, field in enumerate(fields):
                tok[field] = word[i]
            sentence.append(tok)
        if len(sentence) > 0:
            sentences.append(sentence)

    return sentences
