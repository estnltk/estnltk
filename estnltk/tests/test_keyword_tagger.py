from estnltk import Text
from estnltk.taggers import KeywordTagger
from estnltk.taggers import RegexTagger


def test_keyword_tagger():
    text = Text('aa bb cc dd aa')
    k = KeywordTagger(
        ['aa'], layer_name='keywords',
        return_layer=False
    )
    k.tag(text)

    assert text['keywords'] == [{'end': 2, 'start': 0}, {'end': 14, 'start': 12}]


    text = Text('aa bb cc dd aa')
    k = KeywordTagger(
        ['aa'], layer_name='keywords',
        return_layer=True
    )
    assert k.tag(text) == [{'end': 2, 'start': 0}, {'end': 14, 'start': 12}]


def test_regex_tagger():
    text = Text('aa bb cc dd aa')
    k = RegexTagger(
        ['aa'], layer_name='keywords',
        return_layer=False
    )
    k.tag(text)

    assert [{'start':i['start'], 'end':i['end']} for i in  text['keywords']] == [{'end': 2, 'start': 0}, {'end': 14, 'start': 12}]


    text = Text('aa bb cc dd aa')
    k = RegexTagger(
        ['aa'], layer_name='keywords',
        return_layer=True
    )
    assert [{'start':i['start'], 'end':i['end']} for i in k.tag(text)] == [{'end': 2, 'start': 0}, {'end': 14, 'start': 12}]
