from conllu import TokenList

from collections import OrderedDict


def sentence_to_conll(sentence_span, conll_layer):
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

    return TokenList(tokens).serialize()
