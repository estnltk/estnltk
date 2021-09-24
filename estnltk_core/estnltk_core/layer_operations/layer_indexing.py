from itertools import product, chain

from estnltk_core.layer.layer import Layer


def build_ngrams(layer: Layer, attribute: str, n: int, sep: str='-'):
    unigrams = getattr(layer, attribute)
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


def create_ngram_fingerprint_index(layer: Layer, attribute: str, n: int, sep: str= '-'):
    """Used with finite grammar ngram_fingerprint."""
    return list(chain(*[build_ngrams(layer, attribute, i, sep) for i in range(1, n + 1)]))
