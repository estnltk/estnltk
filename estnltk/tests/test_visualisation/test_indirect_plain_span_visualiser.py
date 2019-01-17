from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from estnltk.tests import new_text
from estnltk.core import rel_path

def test_css():
    display = DisplaySpans(styling="indirect")
    result = display.css()
    file = rel_path("tests/test_visualisation/expected_outputs/indirect_plain_span_visualiser_outputs/css_test_input.txt")
    with open(file,encoding="UTF-8") as expected_file:
        expected = expected_file.read()
    # python escapes backslashes in readline() and it messes up the test, this fixes that
    expected = expected.replace("\\n", "\n")
    expected = expected.replace("\\'", "\'")
    expected = expected.replace("'", "")
    result = result.replace("'", "")
    assert result == expected

def test_html():
    display = DisplaySpans(styling="indirect")
    result = display.html_output(new_text(5).layer_1)
    file = rel_path(
        "tests/test_visualisation/expected_outputs/indirect_plain_span_visualiser_outputs/html_test_input.txt")
    with open(file,encoding="UTF-8") as expected_file:
        expected = expected_file.read()
    # python escapes backslashes in readline() and it messes up the test, this fixes that
    expected = expected.replace("\\n", "\n")
    expected = expected.replace("\\'", "\'")
    expected = expected.replace("'", "")
    result = result.replace("'", "")
    assert expected == result
