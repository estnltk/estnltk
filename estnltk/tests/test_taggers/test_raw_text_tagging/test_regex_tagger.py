from estnltk import Text
from estnltk.taggers import RegexTagger


def test_validator():
    def validator(m):
        return not m.group(0).startswith('0')

    vocabulary = [
        {'_regex_pattern_': '\d+',
         '_validator_': validator,
         'comment': 'starts with non-zero'},
        {'_regex_pattern_': '\d+',
         '_validator_': "lambda m: m.group(0).startswith('0')",
         'comment': 'starts with zero'}
    ]

    regex_tagger = RegexTagger(layer_name='numbers', vocabulary=vocabulary, attributes=['comment'])
    text = Text('3209 n  0930 093 2304209 093402')
    regex_tagger.tag(text)
    assert text.numbers.text == ['3209', '0930', '093', '2304209', '093402']
    assert text.numbers.comment == ['starts with non-zero', 'starts with zero', 'starts with zero',
                                    'starts with non-zero', 'starts with zero']
