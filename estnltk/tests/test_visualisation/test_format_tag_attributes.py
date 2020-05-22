from estnltk.visualisation.core import format_tag_attributes

def test_format_tag_attributes_empty():
    result = format_tag_attributes({})
    expected = ''

    assert result == expected

def test_format_tag_attributes_id_given():
    result = format_tag_attributes({'id': 6})
    expected = 'id="6"'

    assert result == expected


def test_format_tag_attributes_class_given():
    result = format_tag_attributes({'id': 6, 'class': 'syntax_choice'})
    assert result in {'id="6" class="syntax_choice"', 'class="syntax_choice" id="6"'}
