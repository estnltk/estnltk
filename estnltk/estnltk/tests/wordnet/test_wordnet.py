import pytest

from estnltk import get_resource_paths
from estnltk.wordnet.wordnet import Wordnet
from estnltk.wordnet.synset import Synset

# Try to get the resources for Wordnet. If missing, do nothing. It's up for the user to download the missing resources
WORDNET_RES_PATH = get_resource_paths("wordnet", only_latest=True, download_missing=False)

# Initialize only if resources have been downloaded
wn = Wordnet() if WORDNET_RES_PATH is not None else None

@pytest.mark.skipif(wn is None,
                    reason="Wordnet's resources have not been downloaded. Use estnltk.download('wordnet') to get the missing resources.")
def test_getitem_word():
    result = wn['king']
    king1 = [61958, 'king', 'estwn-et-61958-n', 'n', 2, 'king']
    king2 = [9954, 'king', 'estwn-et-9954-n', 'n', 1, 'king']
    expected = {Synset(wn, info) for info in [king1, king2]}

    assert set(result) == expected


@pytest.mark.skipif(wn is None,
                    reason="Wordnet's resources have not been downloaded. Use estnltk.download('wordnet') to get the missing resources.")
def test_getitem_word_and_pos():
    result = wn['king', 'n']
    king1 = [61958, 'king', 'estwn-et-61958-n', 'n', 2, 'king']
    king2 = [9954, 'king', 'estwn-et-9954-n', 'n', 1, 'king']
    expected = {Synset(wn, info) for info in [king1, king2]}

    assert set(result) == expected


@pytest.mark.skipif(wn is None,
                    reason="Wordnet's resources have not been downloaded. Use estnltk.download('wordnet') to get the missing resources.")
def test_getitem_word_and_int():
    assert wn['king', 1] == Synset(wn, [9954, 'king', 'estwn-et-9954-n', 'n', 1, 'king'])
