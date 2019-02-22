var elements = document.getElementsByClassName("overlapping-span")
for (let i = 0; i < elements.length; i++) {
    elements.item(i).addEventListener("click", function () {
        show_conflicting_spans(elements.item(i));
    })
}

var plain_elements = document.getElementsByClassName("span")
for (let i = 0; i < plain_elements.length; i++) {
    plain_elements.item(i).addEventListener("click", function () {
        attribute_table(plain_elements.item(i));
    })
}

function show_conflicting_spans(span_element) {
    let spantable = document.createElement('div')
    spantable.classList.add('tables')

    // Prepare the contents of the span table
    data = span_element.getAttribute("span_info")
    data = data.split(",")
    console.log(data)
    var spancontent = '<table>'
    for (let row of data) {
        spancontent += '<tr><td>'
        spancontent += row
        spancontent += '</td></tr>'
    }
    spancontent += '</table>'
    spantable.innerHTML = spancontent
    span_element.parentElement.appendChild(spantable)

    // Increase the size of the cell so the tables would fit
    spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 90) + 'px'
    // Position the table directly below the corresponding text
    spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px'
    spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px'

    // Remove the table when clicked on again
    spantable.addEventListener('click', function () {
        let element = this.parentElement
        element.removeChild(this)
    })
}

function span_table(span) {
    data = span.getAttribute("span_info")
    data = data.split(",")
    var content = '<table>'
    for (let row of data) {
        content += '<tr><td>'
        content += row
        content += '</td></tr>'
    }
    content += '</table>'

    return content
}

function table_builder(contents) {
    var table = '<table>'
    for (let i = 0; i < contents.length; i++) {
        if (i % 2 === 0) {
            table += '<tr><td>'
            table += contents[i]
            table += '</td>'
        } else {
            table += '<td>'
            table += contents[i]
            table += '</td></tr>'
        }
    }
    table += '</table>'

    return table
}

function attribute_table(span_element) {

    //extract the attributes from the span info string
    var attribute_info = span_element.getAttribute("span_info")
    attribute_info = attribute_info.substr(attribute_info.indexOf('{') + 1)
    attribute_info = attribute_info.substr(0, attribute_info.indexOf('}'))
    var attributes = attribute_info.split("'")
    var final_attributes = []
    for (let i = 0; i < attributes.length; i++) {
        if (i % 2 === 1) {
            final_attributes.push(attributes[i])
        }
    }

    let spantable = document.createElement('div')
    spantable.classList.add('tables')
    spantable.innerHTML = table_builder(final_attributes)
    span_element.parentElement.appendChild(spantable)

    // Increase the size of the cell so the tables would fit
    spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 200) + 'px'
    // Position the table directly below the corresponding text
    spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px'
    spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px'

    // Remove the table when clicked on again
    spantable.addEventListener('click', function () {
        let element = this.parentElement
        element.removeChild(this)
    })
}

JSON.parse("{\"ambiguous\": true, \"attributes\": [\"lemma\", \"root\", \"root_tokens\", \"ending\", \"clitic\", \"form\", \"partofspeech\"], \"parent\": \"words\", \"spans\": [[{\"lemma\": \"mis\", \"root_tokens\": [\"mis\"], \"start\": 0, \"root\": \"mis\", \"ending\": \"0\", \"partofspeech\": \"P\", \"_index_\": 0, \"form\": \"pl n\", \"end\": 3, \"clitic\": \"\"}, {\"lemma\": \"mis\", \"root_tokens\": [\"mis\"], \"start\": 0, \"root\": \"mis\", \"ending\": \"0\", \"partofspeech\": \"P\", \"_index_\": 0, \"form\": \"sg n\", \"end\": 3, \"clitic\": \"\"}], [{\"lemma\": \"mis\", \"root_tokens\": [\"mis\"], \"start\": 4, \"root\": \"mis\", \"ending\": \"0\", \"partofspeech\": \"P\", \"_index_\": 1, \"form\": \"pl n\", \"end\": 7, \"clitic\": \"\"}, {\"lemma\": \"mis\", \"root_tokens\": [\"mis\"], \"start\": 4, \"root\": \"mis\", \"ending\": \"0\", \"partofspeech\": \"P\", \"_index_\": 1, \"form\": \"sg n\", \"end\": 7, \"clitic\": \"\"}]], \"_base\": \"words\", \"name\": \"morph_analysis\", \"enveloping\": null}")
JSON.parse("{\"ambiguous\": true, \"attributes\": [\"attr\", \"attr_1\"], \"parent\": null, \"spans\": [[{\"end\": 4, \"attr_1\": \"SADA\", \"attr\": \"L1-0\", \"start\": 0}], [{\"end\": 9, \"attr_1\": \"KAKS\", \"attr\": \"L1-1\", \"start\": 5}], [{\"end\": 16, \"attr_1\": \"KAKS\", \"attr\": \"L1-2\", \"start\": 5}, {\"end\": 16, \"attr_1\": \"KÜMME\", \"attr\": \"L1-2\", \"start\": 5}, {\"end\": 16, \"attr_1\": \"KAKSKÜMMEND\", \"attr\": \"L1-2\", \"start\": 5}], [{\"end\": 14, \"attr_1\": \"KÜMME\", \"attr\": \"L1-3\", \"start\": 9}], [{\"end\": 21, \"attr_1\": \"KOLM\", \"attr\": \"L1-4\", \"start\": 17}], [{\"end\": 27, \"attr_1\": \"NELI\", \"attr\": \"L1-5\", \"start\": 23}], [{\"end\": 33, \"attr_1\": \"TUHAT\", \"attr\": \"L1-6\", \"start\": 28}], [{\"end\": 38, \"attr_1\": \"VIIS\", \"attr\": \"L1-7\", \"start\": 34}], [{\"end\": 42, \"attr_1\": \"SADA\", \"attr\": \"L1-8\", \"start\": 34}, {\"end\": 42, \"attr_1\": \"VIIS\", \"attr\": \"L1-8\", \"start\": 34}, {\"end\": 42, \"attr_1\": \"VIISSADA\", \"attr\": \"L1-8\", \"start\": 34}], [{\"end\": 42, \"attr_1\": \"SADA\", \"attr\": \"L1-9\", \"start\": 38}], [{\"end\": 47, \"attr_1\": \"KUUS\", \"attr\": \"L1-10\", \"start\": 43}], [{\"end\": 54, \"attr_1\": \"KUUS\", \"attr\": \"L1-11\", \"start\": 43}, {\"end\": 54, \"attr_1\": \"KÜMME\", \"attr\": \"L1-11\", \"start\": 43}, {\"end\": 54, \"attr_1\": \"KUUSKÜMMEND\", \"attr\": \"L1-11\", \"start\": 43}], [{\"end\": 52, \"attr_1\": \"KÜMME\", \"attr\": \"L1-12\", \"start\": 47}], [{\"end\": 61, \"attr_1\": \"SEITSE\", \"attr\": \"L1-13\", \"start\": 55}], [{\"end\": 66, \"attr_1\": \"KOMA\", \"attr\": \"L1-14\", \"start\": 62}], [{\"end\": 74, \"attr_1\": \"KAHEKSA\", \"attr\": \"L1-15\", \"start\": 67}], [{\"end\": 82, \"attr_1\": \"ÜHEKSA\", \"attr\": \"L1-16\", \"start\": 76}], [{\"end\": 89, \"attr_1\": \"ÜHEKSA\", \"attr\": \"L1-17\", \"start\": 76}, {\"end\": 89, \"attr_1\": \"KÜMME\", \"attr\": \"L1-17\", \"start\": 76}, {\"end\": 89, \"attr_1\": \"ÜHEKSAKÜMMEND\", \"attr\": \"L1-17\", \"start\": 76}], [{\"end\": 87, \"attr_1\": \"KÜMME\", \"attr\": \"L1-18\", \"start\": 82}]], \"_base\": \"layer_1\", \"name\": \"layer_1\", \"enveloping\": null}")
