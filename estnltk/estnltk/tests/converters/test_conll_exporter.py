import pkgutil
import pytest

from estnltk.common import abs_path

def check_if_conllu_is_available():
    # Check if conllu is available
    return pkgutil.find_loader("conllu") is not None


@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_sentence_to_conll():
    from estnltk.converters.conll.conll_importer import conll_to_text
    from estnltk.converters.conll.conll_exporter import sentence_to_conll
    
    file = abs_path('tests/converters/test_conll.conll')

    text = conll_to_text(file, 'conll')

    expected = """1	See	see	P	P	dem|sg|nom	2	@SUBJ	_	_
2	oli	ole	V	V	indic|impf|ps3|sg	0	ROOT	_	_
3	rohkem	rohkem	D	D	_	2	@OBJ	_	_
4	kui	kui	J	Jc	_	5	@J	_	_
5	10	10	N	N	card|sg|nom	3	@ADVL	_	_
6	protsenti	protsent	S	S	sg|part	5	@<Q	_	_
7	kogu	kogu	A	A	_	10	@AN>	_	_
8	Hansapanka	Hansa_pank	S	H	sg|adit	9	@ADVL	_	_
9	paigutatud	paiguta=tud	A	A	partic	10	@AN>	_	_
10	rahast	raha	S	S	sg|el	5	@ADVL	_	_
11	.	.	Z	Z	Fst	10	@Punc	_	_

"""

    assert sentence_to_conll(sentence_span=text.sentences[1], conll_layer=text.conll) == expected
