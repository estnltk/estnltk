from typing import Union
from itertools import product, chain

from estnltk_core.layer.base_layer import BaseLayer


def build_ngrams(layer: Union[BaseLayer, 'Layer'], attribute: str, n: int, sep: str='-'):
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
    """Used with finite grammar ngram_fingerprint."""
    return list(chain(*[build_ngrams(layer, attribute, i, sep) for i in range(1, n + 1)]))
