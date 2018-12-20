from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans
from estnltk.tests import new_text

def test_css():
    display = DisplaySpans(styling="indirect")
    result = display.span_decorator.css()
    expected = ('<style>\n.span {\n    background-color: yellow;\n}\n\n.overlapping-span {\n    background-color: red;'
                '\n}\n\n.spanline {\n    background-color: blue;\n    position: relative;\n    height: 3px;\n    '
                'margin-left: 0px;\n}\n\n.tables {\n    position: absolute;\n    width: fit-content;\n    width: -moz'
                '-fit-content;\n    border: 1px solid black;\n}\n\n.maintext{0} {\n    position: relative;\n}\n\n.tables'
                ' tbody tr:nth-child(even) {\n    background-color: lightgray;\n}\n\n.tables tbody tr:nth-child(odd) '
                '{\n    background-color: beige;\n}\n\n.tables tbody tr:hover {\n    background-color: ivory;\n}\n</style>')
    assert result == expected

def test_html():
    display = DisplaySpans(styling="indirect")
    result = display.html_output(new_text(5).layer_1)
    expected = ('<script>\nvar elements = document.getElementsByClassName("overlapping-span")\nfor (let i = 0; i < ele'
                'ments.length; i++){\n    elements.item(i).addEventListener("click",function() {intermediate_table'
                '(elements.item(i));})\n}\n\nfunction intermediate_table(span_element) {\n    console.log(span_element)'
                '\n    let spantable = document.createElement(\'div\')\n    spantable.classList.add(\'tables\')\n    '
                'spantable.innerHTML = span_table(span_element)\n    span_element.parentElement.appendChild(spantable)'
                '\n\n    //Position the element below the text\n    spantable.style.left = "0px";\n    spantable.style.'
                'top = "0px";\n    spantable.style.left = span_element.getBoundingClientRect().left-spantable.getBound'
                'ingClientRect().left + \'px\'\n    spantable.style.top = span_element.getBoundingClientRect().top-sp'
                'antable.getBoundingClientRect().top+span_element.getBoundingClientRect().height+ \'px\'\n    spantable'
                '.parentElement.style.height = spantable.parentElement.style.height+"100px"\n\n    spantable.addEvent'
                'Listener(\'click\', function () {\n        let element = this.parentElement\n        element.remove'
                'Child(this)  //deleting the table\n    })\n}\n\nfunction span_table (span) {{\n    data = span.get'
                'Attribute("span_info")\n    data = data.split(",")\n    var content = \'<table>\'\n    for (let row'
                ' of data) {\n        content+=\'<tr><td>\'\n        content+=row\n        content+=\'</td></tr>\'\n'
                '    }\n    content += \'</table>\'\n\n    return content\n}}</script><style>\n.span {\n    background'
                '-color: yellow;\n}\n\n.overlapping-span {\n    background-color: red;\n}\n\n.spanline {\n    '
                'background-color: blue;\n    position: relative;\n    height: 3px;\n    margin-left: 0px;\n}\n\n.'
                'tables {\n    position: absolute;\n    width: fit-content;\n    width: -moz-fit-content;\n    '
                'border: 1px solid black;\n}\n\n.maintext{0} {\n    position: relative;\n}\n\n.tables tbody tr:nth-chi'
                'ld(even) {\n    background-color: lightgray;\n}\n\n.tables tbody tr:nth-child(odd) {\n    background'
                '-color: beige;\n}\n\n.tables tbody tr:hover {\n    background-color: ivory;\n}\n</style><span span_'
                'info=Sada>Sada</span> <span span_info=kaks,kakskümmend>kaks</span><span span_info=kakskümmend,kümme>'
                'kümme</span><span span_info=kakskümmend>nd</span> <span span_info=kolm>kolm</span>.<span span_info= '
                'Neli> Neli</span> <span span_info=tuhat>tuhat</span> <span span_info=viis,viissada>viis</span><span '
                'span_info=viissada,sada>sada</span> <span span_info=kuus,kuuskümmend>kuus</span><span span_info='
                'kuuskümmend,kümme>kümme</span><span span_info=kuuskümmend>nd</span> <span span_info=seitse>seitse'
                '</span> <span span_info=koma>koma</span> <span span_info=kaheksa>kaheksa</span>. <span span_info='
                'Üheksa,Üheksakümmend>Üheksa</span><span span_info=Üheksakümmend,kümme>kümme</span><span span_info='
                'Üheksakümmend>nd</span> tuhat.')
    assert expected == result