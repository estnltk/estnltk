#
#   Original source:
#      https://github.com/estnltk/smart-search/blob/469f54a1382d5cb2e717cdc7224774b7678a647e/demod/toovood/riigi_teataja_pealkirjaotsing/01_dokumentide_indekseerimine/estnltk_patches/tests/test_local_token_splitter.ipynb
#
import regex as re

from estnltk import Text
from estnltk.taggers.standard.morph_analysis.proxy import MorphAnalyzedToken
from estnltk.taggers.standard.text_segmentation.local_token_splitter import LocalTokenSplitter

SUBSCRIPT_SYMBOLS = '[₀₁₂₃₄₅₆₇₈₉₊₋]'
SUPERSCRIPT_SYMBOLS = '[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]'

def find_split(text, match):
    return match.start()

def split_if_prefix_is_word(text, match):
    if NUMBER.match(text[0:match.start()]):
        return -1
    return match.start() if MorphAnalyzedToken(text[0:match.start()]).is_word else -1

NUMBER = re.compile('^[0-9]+$')

def split_if_prefix_is_number(text, match):
    return match.start() if NUMBER.match(text[0:match.start()]) else -1


def test_local_tokens_splitter_smoke():
    # Smoke test for LocalTokenSplitter
    token_splitter = LocalTokenSplitter(
        split_rules=[
            (re.compile(f'[0-9]$'), split_if_prefix_is_word),
            (re.compile(f'({SUPERSCRIPT_SYMBOLS})$'), find_split),
            (re.compile(fr'\.$'), split_if_prefix_is_number)
    ])
    
    # Create xample input
    text = Text('Esimene peatükk1 Arno3 isaga4 xxx5 koolijõudis⁷, olid1 tunnid juba 1934. ja 12 alanud.')
    # Add the default tokens layer
    text.tag_layer('tokens')
    unsplit_tokens = \
        ['Esimene', 'peatükk1', 'Arno3', 'isaga4', 'xxx5', 'koolijõudis⁷', \
         ',', 'olid1', 'tunnid', 'juba', '1934', '.', 'ja', '12', 'alanud', '.']
    assert unsplit_tokens == [t.text for t in text.tokens]
    
    # Apply token splitter on text
    token_splitter.retag( text )
    
    split_tokens = \
        ['Esimene', 'peatükk', '1', 'Arno', '3', 'isaga', '4', 'xxx5', 'koolijõudis', 
         '⁷', ',', 'olid', '1', 'tunnid', 'juba', '1934', '.', 'ja', '12', 'alanud', '.']

    assert split_tokens == [t.text for t in text.tokens]         
