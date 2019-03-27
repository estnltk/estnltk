from collections import defaultdict
from conllu import parse_incr
from estnltk import Span, Layer, Text, LambdaAttribute


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
                   attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                               'misc', 'parent_span', 'children', 'parent_deprel'],
                   ambiguous=False,
                   )

    sentence_start = 0
    word_index = 0

    with open(file, "r", encoding="utf-8") as data_file:

        for conll_sentence in parse_incr(data_file):
            #id_to_span = {}
            id_to_children = defaultdict(list)
            id_to_deprel = {}
            for conll_word in conll_sentence:
                token = conll_word['form']

                if word_index >= len_words:
                    raise Exception("can't match file with words layer")
                while token != words[word_index].text:
                    word_index += 1
                    if word_index >= len_words:
                        raise Exception("can't match file with words layer")

                w_span = words[word_index]
                span = Span(w_span.start, w_span.end)

                #id_to_span[conll_word['id']] = span
                id_to_deprel[conll_word['id']] = conll_word['deprel']
                id_to_children[conll_word['head']].append(conll_word['id'])

                # add values for 'id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc'
                syntax.add_annotation(span, **conll_word)
                word_index += 1

            # add values for 'parent_span', 'children', 'parent_deprel'
            for index in range(sentence_start, len(syntax)):
                annotation = syntax[index][0]

                if annotation.head == 0:
                    annotation.parent_span = LambdaAttribute('lambda a: None')
                else:
                    annotation.parent_span = LambdaAttribute('lambda a: a.layer[{}]'.format(annotation.head+sentence_start-1))

                annotation.children = LambdaAttribute('lambda a: tuple([{}])'.format(', '.join(('a.layer[{}]'.format(c_id+sentence_start-1) for c_id in id_to_children[annotation.id]))))

                annotation.parent_deprel = id_to_deprel.get(annotation.head)
            sentence_start = len(syntax)

    text[syntax_layer] = syntax

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
                  ambiguous=False,
                  )

    syntax = Layer(name=syntax_layer,
                   text_object=text,
                   attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                               'misc', 'parent_span', 'children', 'parent_deprel'],
                   ambiguous=False,
                   )
    cur = 0
    t = []

    sentence_start = 0

    with open(file, "r", encoding="utf-8") as data_file:

        for sentence in parse_incr(data_file):
            id_to_span = {}
            id_to_deprel = {}
            id_to_children = defaultdict(list)

            for w in sentence:
                token = w['form']
                t.append(token)
                len_w = len(token)
                span = Span(cur, cur+len_w, text_object=text)
                words.add_annotation(span)

                w['head'] = w['head']
                w['parent_span'] = None
                w['parent_deprel'] = None
                id_to_span[w['id']] = span
                id_to_deprel[w['id']] = w['deprel']
                id_to_children[w['head']].append(w['id'])

                syntax.add_annotation(span, **w)
                cur += len_w + 1

            for index in range(sentence_start, len(syntax)):
                span = syntax[index]
                span.parent_span = LambdaAttribute('lambda a: a.layer[{}]'.format(span.head-1))
                span.parent_deprel = id_to_deprel.get(span.head)
                span.children = tuple(id_to_span[c_id] for c_id in id_to_children[span.id])

            sentence_start += len(sentence)

    text.set_text(' '.join(t))
    text['words'] = words
    text[syntax_layer] = syntax

    return text
