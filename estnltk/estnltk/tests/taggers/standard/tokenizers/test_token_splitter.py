import regex as re

from estnltk import Text
from estnltk.taggers.standard.text_segmentation.token_splitter import TokenSplitter

def test_tokens_splitting_1():
    # Test tokens splitting on the old language
    # case 1
    token_splitter = TokenSplitter(patterns=[re.compile(r'[0-9]*(?P<end>[0-9])[a-züõöä]+'),\
                                             re.compile(r'[a-züõöä]+(?P<end>[a-züõöä])[A-ZÜÕÖÄ][a-züõöä]+')])
    text=Text('Linnasekretär U.Jõgi luges linnawolikogu 20dets.1920a.koosoleku protokolli ette. '+\
           'Too oli krahwManteufelli maatüki müügi asjas.')
    expected_tokens = ['Linnasekretär', 'U', '.', 'Jõgi', 'luges', 'linnawolikogu', '20', 'dets', '.', \
                       '1920', 'a', '.', 'koosoleku', 'protokolli', 'ette', '.', \
                       'Too', 'oli', 'krahw', 'Manteufelli', 'maatüki', 'müügi', 'asjas', '.']
    text.tag_layer('tokens')
    token_splitter.retag( text )
    tokens = [t.text for t in text.tokens]
    assert tokens == expected_tokens
    # case 2
    token_splitter = TokenSplitter(patterns=[re.compile(r'(?P<end>Piebenomme)metsawaht'),\
                                             re.compile(r'(?P<end>talumees)Nikolai'),\
                                             re.compile(r'(?P<end>rannast)Leno')])
    text=Text('Piebenommemetsawaht ja talumeesNikolai leidsiva rannastLeno passunakuori.')
    expected_tokens = ['Piebenomme', 'metsawaht', 'ja', 'talumees', 'Nikolai', 'leidsiva', 'rannast', \
                       'Leno', 'passunakuori', '.']
    text.tag_layer('tokens')
    token_splitter.retag( text )
    tokens = [t.text for t in text.tokens]
    assert tokens == expected_tokens


def test_tokens_splitting_2():
    # Test tokens splitting on the Internet language
    token_splitter = TokenSplitter(patterns=[re.compile(r'(?P<end>ma|ise)[a-züõöä]+', re.I),\
                                             re.compile(r'(?P<end>ümber|välja)[a-züõöä]+')])
    # Note: the first rule, '(?P<end>ma|ise)[a-züõöä]+', is very suspicious -- 
    #       wouldn't recommend applying it on large scale ...
    text=Text('Mai tea, väljavalitud ja ümberlükatud asjad -- isetead mis teed nendega')
    expected_tokens = ['Ma', 'i', 'tea', ',', 'välja', 'valitud', 'ja', 'ümber', 'lükatud', \
                       'asjad', '-', '-', 'ise', 'tead', 'mis', 'teed', 'nendega']
    text.tag_layer('tokens')
    token_splitter.retag( text )
    tokens = [t.text for t in text.tokens]
    assert tokens == expected_tokens
