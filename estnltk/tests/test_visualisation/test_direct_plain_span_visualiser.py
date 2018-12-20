from estnltk.tests import new_text
from estnltk.visualisation.span_visualiser.fancy_span_visualisation import DisplaySpans

def test_html():
    display = DisplaySpans()
    result = display.html_output(new_text(5).layer_1)
    expected = ('<script>\nvar elements = document.getElementsByClassName("overlapping-span")\nfor (let i = 0; i < '
                'elements.length; i++){\n    elements.item(i).addEventListener("click",function() {intermediate_table'
                '(elements.item(i));})\n}\n\nfunction intermediate_table(span_element) {\n    console.log(span_element)'
                '\n    let spantable = document.createElement(\'div\')\n    spantable.classList.add(\'tables\')\n    '
                'spantable.innerHTML = span_table(span_element)\n    span_element.parentElement.appendChild(spantable)'
                '\n\n    //Position the element below the text\n    spantable.style.left = "0px";\n    spantable.style'
                '.top = "0px";\n    spantable.style.left = span_element.getBoundingClientRect().left-spantable.getBoun'
                'dingClientRect().left + \'px\'\n    spantable.style.top = span_element.getBoundingClientRect().top-'
                'spantable.getBoundingClientRect().top+span_element.getBoundingClientRect().height+ \'px\'\n    spanta'
                'ble.parentElement.style.height = spantable.parentElement.style.height+"100px"\n\n    spantable.addEv'
                'entListener(\'click\', function () {\n        let element = this.parentElement\n        element.remo'
                'veChild(this)  //deleting the table\n    })\n}\n\nfunction span_table (span) {{\n    data = span.get'
                'Attribute("span_info")\n    data = data.split(",")\n    var content = \'<table>\'\n    for (let row '
                'of data) {\n        content+=\'<tr><td>\'\n        content+=row\n        content+=\'</td></tr>\'\n  '
                '  }\n    content += \'</table>\'\n\n    return content\n}}</script><span style=background:yellow;>S'
                'ada</span> <span style=background:red; class=overlapping-span  span_info=kaks,kakskümmend>kaks</span>'
                '<span style=background:red; class=overlapping-span  span_info=kakskümmend,kümme>kümme</span><span '
                'style=background:yellow;>nd</span> <span style=background:yellow;>kolm</span>.<span style=background'
                ':yellow;> Neli</span> <span style=background:yellow;>tuhat</span> <span style=background:red; class'
                '=overlapping-span  span_info=viis,viissada>viis</span><span style=background:red; class=overlapping'
                '-span  span_info=viissada,sada>sada</span> <span style=background:red; class=overlapping-span  span'
                '_info=kuus,kuuskümmend>kuus</span><span style=background:red; class=overlapping-span  span_info=kuus'
                'kümmend,kümme>kümme</span><span style=background:yellow;>nd</span> <span style=background:yellow;>se'
                'itse</span> <span style=background:yellow;>koma</span> <span style=background:yellow;>kaheksa</span>.'
                ' <span style=background:red; class=overlapping-span  span_info=Üheksa,Üheksakümmend>Üheksa</span><sp'
                'an style=background:red; class=overlapping-span  span_info=Üheksakümmend,kümme>kümme</span><span '
                'style=background:yellow;>nd</span> tuhat.')
    assert result == expected