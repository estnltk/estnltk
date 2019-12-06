from estnltk.tests import new_text
from estnltk.visualisation.attribute_visualiser.attribute_visualisation import DisplayAttributes
from estnltk.core import abs_path


def test_html():
    display = DisplayAttributes(name="display")
    result = display.html_output(new_text(5).layer_1)
    file = abs_path(
        "tests/test_visualisation/expected_outputs/attribute_visualiser_outputs/attribute_visualiser_html.txt")
    with open(file, encoding="UTF-8") as expected_file:
        expected = expected_file.read()
    print(result)
    print("-----")
    print(expected)
    assert result == expected


def test_javascript():
    display = DisplayAttributes()
    js = display.insert_script_tag()
    file = abs_path(
        "tests/test_visualisation/expected_outputs/attribute_visualiser_outputs/attribute_visualiser_js.txt")
    with open(file, encoding="UTF-8") as expected_file:
        expected = expected_file.read()
    assert js == expected


def test_mark_chosen_spans_no_choices():
    display = DisplayAttributes(name="display")
    assert display.mark_chosen_spans() == None


def test_mark_chosen_spans():
    display = DisplayAttributes(name="display")
    display.html_displayed = True
    display.accepted_array = [['1'], ['2'],
                              ['1', '1', '2'],
                              ['1'],
                              ['2'],
                              ['1'],
                              ['1'],
                              ['2'],
                              ['1', '2', '1'],
                              ['1'],
                              ['1'],
                              ['2', '2', '2'],
                              ['1'],
                              ['2'],
                              ['1'],
                              ['2'],
                              ['1'],
                              ['1', '1', '2']]
    display.original_layer = new_text(5).layer_1
    new_layer = str(display.mark_chosen_spans())  # Layer with an extra attribute to show if the span was chosen
    file = abs_path(
        "tests/test_visualisation/expected_outputs/attribute_visualiser_outputs/mark_chosen_spans_output.txt")
    with open(file, encoding="UTF-8") as expected_file:
        expected = expected_file.read()
    assert new_layer == expected

def test_delete_chosen_spans():
    display = DisplayAttributes(name="display")
    display.html_displayed = True
    display.accepted_array = [['1'], ['2'],
                              ['1', '1', '2'],
                              ['1'],
                              ['2'],
                              ['1'],
                              ['1'],
                              ['2'],
                              ['1', '2', '1'],
                              ['1'],
                              ['1'],
                              ['2', '2', '2'],
                              ['1'],
                              ['2'],
                              ['1'],
                              ['2'],
                              ['1'],
                              ['1', '1', '2']]
    display.original_layer = new_text(5).layer_1
    new_layer = str(display.delete_chosen_spans())  # Layer where not chosen spans are deleted
    file = abs_path(
        "tests/test_visualisation/expected_outputs/attribute_visualiser_outputs/delete_chosen_spans_output.txt")
    with open(file, encoding="UTF-8") as expected_file:
        expected = expected_file.read()
    assert new_layer == expected