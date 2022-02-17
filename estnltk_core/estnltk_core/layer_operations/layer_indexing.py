from typing import Union
from itertools import product, chain

from estnltk_core.layer.base_layer import BaseLayer


def build_ngrams(layer: Union[BaseLayer, 'Layer'], attribute: str, n: int, sep: str='-'):
    """Generates all `n`-grams from `attribute` values of consecutive spans of `layer`.

    Example:

    >>> from estnltk import Text
    >>> from estnltk_core.layer_operations.layer_indexing import build_ngrams
    >>> text=Text('Kokk küttis ahju').tag_layer('morph_analysis')
    >>> # Generate bigrams from values of 'lemma' attribute
    >>>  build_ngrams(text["morph_analysis"], 'lemma', 2)
    ['kokk-kütma', 'kokk-küttima', 'kütma-ahi', 'küttima-ahi']

    """
    unigrams = layer[attribute]
    ngrams = set()
    is_ambiguous = layer.ambiguous
    for i in range(n, len(unigrams) + 1):
        slice = unigrams[i - n: i]
        if is_ambiguous:
            items = [sep.join(seq) for seq in product(*slice)]
            ngrams.update(items)
        else:
            item = sep.join(slice)
            ngrams.add(item)
    return list(ngrams)


def create_ngram_fingerprint_index(layer: Union[BaseLayer, 'Layer'], attribute: str, n: int, sep: str= '-'):
    """Generates N-gram fingerprint from values of the attribute (of given layer).

    More specifically, creates all N-grams (where N ranges 1 to `n`) from attribute
    values of consecutive spans of `layer`. Returns a list of value N-grams;
    values in each N-gram are joined by `sep` string (defaults to '-'). The order of
    N-grams in the returned list can be different from the order of spans in `layer`.

    Example:

    >>> from estnltk import Text
    >>> from estnltk_core.layer_operations import create_ngram_fingerprint_index
    >>> text=Text('Kokk küttis ahju').tag_layer('morph_analysis')
    >>> # Generate uniframs and bigrams from values of 'lemma' attribute
    >>> create_ngram_fingerprint_index(layer=text["morph_analysis"], attribute='lemma', n=2)
    ['kütma', 'kokk', 'küttima', 'ahi', 'kokk-küttima', 'küttima-ahi', 'kütma-ahi', 'kokk-kütma']

    Note that N-gram fingerprint also takes account of the ambiguities. In the previous
    example, the word 'küttis' remains ambiguous between lemmas 'kütma' ja 'küttima', so
    generated N-grams cover both variants.

    Used with finite grammar ngram_fingerprint."""
    return list(chain(*[build_ngrams(layer, attribute, i, sep) for i in range(1, n + 1)]))
