from conllu import TokenList
from collections import OrderedDict

from estnltk import Text, Layer


def ner_labelling_to_conll(text: Text, ner_layer: Layer) -> str:
    """
    Converts the provided Text object and NER-layer into CONLL-format.
    The converted string includes all words in the text with necessary attributes (lemma, POS-tag, form, NER-tag).
    Different words are separated by '\n' so one word would be one row and in each row, attributes are separated
    by '\t'. This output can be written directly to a file and it will be a correct CONLL-file for NER tagging.

    Parameters
    ----------
    text: EstNLTK Text object
        The text that is converted to CONLL-format
    ner_layer:
        The layer with NER labels. Layer must include tags for all words in the text (wordner layer)
    Returns
    -------
    String in CONLL-format.
    """
    t = text.normalized_text
    root = text.root
    ending = text.ending
    pos = text.partofspeech
    form = text.form
    tokens = []

    for i, word in enumerate(text.words):
        lemma = '{}+{}'.format(root[i][0], ending[i][0])
        nertag = ner_layer.get(word).nertag
        postag = pos[i][0]
        if postag == 'Z':
            lemma = root[i][0]
            nertag += '\n'
        token = OrderedDict([('word', t[i][0]),
                             ('lemma', lemma),
                             ('partofspeech', '_{}_'.format(pos[i][0])),
                             ('form', form[i][0]),
                             ('nertag', nertag)])

        tokens.append(token)

    result = TokenList(tokens).serialize()
    return result.replace('=|', '|').replace('=\t', '\t')
