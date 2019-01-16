from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from estnltk.tests import new_text

def test_css():
    display = DisplaySpans(styling="indirect")
    result = display.css()
    expected_file = open("expected_outputs/indirect_plain_span_visualiser_outputs/css_test_input.txt",encoding="UTF-8")
    expected = expected_file.readline()
    #python escapes backslashes in readline() and it messes up the test, this fixes that
    expected = expected.replace("\\n", "\n")
    expected = expected.replace("\\'", "\'")
    expected = expected.replace("'", "")
    result = result.replace("'", "")
    assert result == expected

def test_html():
    display = DisplaySpans(styling="indirect")
    result = display.html_output(new_text(5).layer_1)
    expected_file = open("expected_outputs/indirect_plain_span_visualiser_outputs/html_test_input.txt",encoding="UTF-8")
    expected = expected_file.readline()
    expected = expected.replace("\\n", "\n")
    expected = expected.replace("\\'", "\'")
    expected = expected.replace("'", "")
    result = result.replace("'", "")
    assert expected == result