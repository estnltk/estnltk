import regex as re
from estnltk.taggers import Vocabulary


def test_empty_vocabulary():
    pass
    Vocabulary(mapping={}, key='', attributes=[''])


def test_to_lower():
    voc = Vocabulary.from_records(key='color', attributes=('color', 'value type', 'example'),
                                  records=[
                                      {'example': 'string', 'value type': 'str', 'color': 'LightSteelBlue'},
                                      {'example': 12345, 'value type': 'int', 'color': 'Moccasin'},
                                      {'example': True, 'value type': 'int', 'color': 'Moccasin'},
                                      {'example': 0.123, 'value type': 'float', 'color': 'Cyan'},
                                      {'example': ('pi', 3, .14), 'value type': 'tuple', 'color': 'LightPink'},
                                      {'example': list('LIST'), 'value type': 'list', 'color': 'OrangeRed'},
                                      {'example': re.compile('pattern'), 'value type': 're.Pattern', 'color': 'Yellow'},
                                      {'example': set('set'), 'value type': 'other', 'color': 'White'},
                                  ])
    voc_lower = voc.to_lower()
    assert set(voc_lower) == {'orangered', 'white', 'cyan', 'yellow', 'lightpink', 'moccasin', 'lightsteelblue'}
