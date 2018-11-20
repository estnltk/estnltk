from estnltk.tests import new_text
from estnltk.visualisation.fancy_span_visualisation import DisplaySpans


def test_html():
    display = DisplaySpans()
    result = display.html_output(new_text(5).layer_1)
    expected = ('<span style=background:yellow;>Sada</span> <span style=background:red;>kaks</span><span style=background:red;>kümme</span>'
                '<span style=background:yellow;>nd</span> <span style=background:yellow;>kolm</span>.<span style=background:yellow;> Neli</span> '
                '<span style=background:yellow;>tuhat</span> <span style=background:red;>viis</span><span style=background:red;>sada</span> '
                '<span style=background:red;>kuus</span><span style=background:red;>kümme</span><span style=background:yellow;>nd</span> '
                '<span style=background:yellow;>seitse</span> <span style=background:yellow;>koma</span> <span style=background:yellow;>kaheksa</span>. '
                '<span style=background:red;>Üheksa</span><span style=background:red;>kümme</span><span style=background:yellow;>nd</span> tuhat.')
    assert result == expected

def test_css():
    display = DisplaySpans(styling="indirect")
    result = display.span_decorator.css()
    expected = ('<style>\n.span {\n    background-color: yellow;\n}\n\n.overlapping-span {\n    background-color: red;\n}\n\n.spanline {{\n    '
                'background-color: blue;\n    position: relative;\n    height: 3px;\n    margin-left: 0px;\n}}\n\n.tables {{\n    '
                'position: absolute;\n    width: fit-content;\n    width: -moz-fit-content;\n    border: 1px solid black;\n}}\n\n.maintext{0} '
                '{{\n    position: relative;\n}}\n\n.tables tbody tr:nth-child(even) {{\n    background-color: lightgray;\n}}\n\n.tables tbody '
                'tr:nth-child(odd) {{\n    background-color: beige;\n}}\n\n.tables tbody tr:hover {{\n    background-color: ivory;\n}}\n</style>')
    assert result == expected




