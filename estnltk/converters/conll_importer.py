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

        for conll_sentence in parse_incr(data_file):
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

    text[syntax_layer] = syntax

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
                  ambiguous=False
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

        for sentence in parse_incr(data_file):
            for w in sentence:
                token = w['form']
                t.append(token)
                len_w = len(token)
                base_span = ElementaryBaseSpan(cur, cur+len_w)
                words.add_annotation(base_span)

                syntax.add_annotation(base_span, **w)
                cur += len_w + 1

            sentences.add_span(words[sentence_start:])
            sentence_start += len(sentence)

    text.set_text(' '.join(t))
    text['words'] = words
    text['sentences'] = sentences
    text[syntax_layer] = syntax

    SyntaxDependencyRetagger(conll_syntax_layer=syntax_layer).retag(text)

    return text
