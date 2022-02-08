from estnltk.visualisation.core import value_cell
from collections import OrderedDict

def test_empty_value():
    result = value_cell(None)
    expected = '<td></td>'

    assert result == expected

def test_string_value():
    result = value_cell('abc')
    expected = '<td>abc</td>'

    assert result == expected

def test_number_value():
    result = value_cell(1 / 2)
    expected = '<td>0.5</td>'

    assert result == expected

def test_list_with_numbers():
    result = value_cell([1,2,4])
    expected = '<td>1 2 4</td>'

    assert result == expected

def test_list_with_strings():
    result = value_cell(['a', 'b', 'c'])
    expected = '<td>a b c</td>'

    assert result == expected

def test_ordered_dict():
    result = value_cell(OrderedDict([('indic', ''), ('pres', ''), ('ps3', ''), ('sg', '')]))
    expected = '<td>indic pres ps3 sg</td>'

    assert result == expected

def test_tag_value():
    result = value_cell("<td>")
    expected = '<td>&lt;td&gt;</td>'

    assert result == expected