from estnltk.visualisation.core import dropdown_cell
import pytest

def test_empty_list():
    with pytest.raises(ValueError):
        "".join(dropdown_cell([]))

def test_dropdown_creation_from_list():
    values = [(1, 'a'), (2, 'b'), (3, 'c')]
    result = "".join(dropdown_cell(values))
    expected = '<td><select><option value="1">a</option><option value="2">b</option><option value="3">c</option></select></td>'

    assert result == expected

def test_dropdown_creation_from_list_with_default():
    values = [(1, 'a'), (2, 'b'), (3, 'c')]
    result = "".join(dropdown_cell(values, 1))
    expected = '<td><select><option value="2">b</option><option value="1">a</option><option value="3">c</option></select></td>'

    assert result == expected

def test_dropdown_creation_when_index_too_large():
    values = [(1, 'a'), (2, 'b'), (3, 'c')]
    result = "".join(dropdown_cell(values, 3))
    expected = '<td><select><option value="1">a</option><option value="2">b</option><option value="3">c</option></select></td>'

    assert result == expected

def test_dropdown_creation_tag():
    result = "".join(dropdown_cell([(1, '</option>')]))
    expected = '<td><select><option value="1">&lt;/option&gt;</option></select></td>'

    assert result == expected

def test_dropdown_creation_with_class():
    values = [(1, 'a'), (2, 'b'), (3, 'c')]
    result = "".join(dropdown_cell(values, 0, 'class="syntax_choice"'))
    expected = '<td><select class="syntax_choice"><option value="1">a</option><option value="2">b</option><option value="3">c</option></select></td>'

    assert result == expected

def test_dropdown_creation_with_class_and_id():
    values = [(1, 'a'), (2, 'b'), (3, 'c')]
    result = "".join(dropdown_cell(values, 0, 'class="syntax_choice" id="5"'))
    expected = '<td><select class="syntax_choice" id="5"><option value="1">a</option><option value="2">b</option><option value="3">c</option></select></td>'

    assert result == expected