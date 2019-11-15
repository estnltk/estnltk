from estnltk.visualisation.core import header_cell

def test_header_cell_normal():
    result = header_cell("boo")
    expected = '<th>boo</th>'

    assert result == expected

def test_header_cell_tag():
    result = header_cell("</th>")
    expected = '<th>&lt;/th&gt;</th>'

    assert result == expected