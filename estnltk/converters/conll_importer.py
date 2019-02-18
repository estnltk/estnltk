from collections import defaultdict
from conllu import parse_incr
from estnltk import Span, Layer, Text


def add_layer_from_conll(file: str, text: Text, syntax_layer: str):
    assert 'words' in text.layers
    assert syntax_layer not in text.layers

    words = text.words
    len_words = len(words)

    syntax = Layer(name=syntax_layer,
                   text_object=text,
                   attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                               'misc', 'parent_span', 'children'],
                   ambiguous=False,
                   )

    sentence_start = 0
    word_index = 0

    with open(file, "r", encoding="utf-8") as data_file:

        for sentence in parse_incr(data_file):
            id_to_span = {}
            id_to_children = defaultdict(list)

            for w in sentence:
                token = w['form']

                if word_index >= len_words:
                    raise Exception("can't match file with words layer")
                while token != words[word_index].text:
                    word_index += 1
                    if word_index >= len_words:
                        raise Exception("can't match file with words layer")

                w_span = words[word_index]
                span = Span(w_span.start, w_span.end, text_object=text)

                w['head'] = w['head']
                w['parent_span'] = None
                id_to_span[w['id']] = span
                id_to_children[w['head']].append(w['id'])

                syntax.add_annotation(span, **w)
                word_index += 1

            for index in range(sentence_start, len(syntax)):
                span = syntax[index]
                span.parent_span = id_to_span.get(span.head)
                span.children = tuple(id_to_span[c_id] for c_id in id_to_children[span.id])

            sentence_start = len(syntax)

    text[syntax_layer] = syntax

    return text


def conll_to_text(file: str, syntax_layer: str = 'conll_syntax') -> Text:
    text = Text()

    words = Layer(name='words',
                  text_object=text,
                  attributes=[],
                  ambiguous=False,
                  )

    syntax = Layer(name=syntax_layer,
                   text_object=text,
                   attributes=['id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                               'misc', 'parent_span', 'children'],
                   ambiguous=False,
                   )
    cur = 0
    t = []

    sentence_start = 0

    with open(file, "r", encoding="utf-8") as data_file:

        for sentence in parse_incr(data_file):
            id_to_span = {}
            id_to_children = defaultdict(list)

            for w in sentence:
                token = w['form']
                t.append(token)
                len_w = len(token)
                span = Span(cur, cur+len_w, text_object=text)
                words.add_annotation(span)

                w['head'] = w['head']
                w['parent_span'] = None
                id_to_span[w['id']] = span
                id_to_children[w['head']].append(w['id'])

                syntax.add_annotation(span, **w)
                cur += len_w + 1

            for index in range(sentence_start, len(syntax)):
                span = syntax[index]
                span.parent_span = id_to_span.get(span.head)
                span.children = tuple(id_to_span[c_id] for c_id in id_to_children[span.id])

            sentence_start += len(sentence)

    text.set_text(' '.join(t))
    text['words'] = words
    text[syntax_layer] = syntax

    return text
