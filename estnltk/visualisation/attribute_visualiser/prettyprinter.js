var elements = document.getElementsByClassName("overlapping-span");
for (let i = 0; i < elements.length; i++) {
    elements.item(i).addEventListener("click", function () {
        show_conflicting_spans(elements.item(i));
    })
}

var plain_elements = document.getElementsByClassName("span");
for (let i = 0; i < plain_elements.length; i++) {
    plain_elements.item(i).addEventListener("click", function () {
        attribute_table(plain_elements.item(i));
    })
}

function show_conflicting_spans(span_element) {
    var spancounter = 0
    for (let i = 0; i < 500; i++) {
        if (span_element.hasAttribute("span_info" + i)) {
            spancounter++
        } else {
            break
        }
    }

    let spantable = document.createElement('div');
    spantable.classList.add('tables');

    data = span_element.getAttribute("span_texts")
    data = data.split(",")
    var spancontent = '<table>';
    for (let row of data) {
        spancontent+='<tr><td>'
        spancontent+=row
        spancontent+='</td></tr>'
    }
    spancontent += '</table>';

    spantable.innerHTML = spancontent;
    span_element.parentElement.appendChild(spantable);

    // Increase the size of the cell so the tables would fit
    spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 90) + 'px';
    // Position the table directly below the corresponding text
    spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px';
    spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';

    // Add listeners for to create the following tables
    for (let i = 0; i < spantable.getElementsByTagName("tr").length; i++) {
        spantable.getElementsByTagName("tr").item(i).addEventListener('click', function () {
            var data = [];
            if (JSON.parse(span_element.getAttribute("span_info" + i)).length===1){
                let attributes = (JSON.parse(span_element.getAttribute("span_info"+i)))[0]
                for (var key of Object.keys(attributes)) {
                    data.push(key, attributes[key])
                }
                let annotationstable = document.createElement('div');
                annotationstable.classList.add('tables');
                //delete table after clicking
                annotationstable.addEventListener("click", function () {
                    annotationstable.parentElement.removeChild(annotationstable)
                })
                //position the table
                annotationstable.style.left = spantable.style.left
                annotationstable.style.top = spantable.style.top
                annotationstable.innerHTML = table_builder(data)
                span_element.parentElement.appendChild(annotationstable)
            } else {
                let annotationtable = document.createElement('div');
                annotationtable.classList.add('tables');
                //position the table
                annotationtable.style.left = spantable.style.left
                annotationtable.style.top = spantable.style.top
                //delete table after clicking
                annotationtable.addEventListener("click", function () {
                    annotationtable.parentElement.removeChild(annotationtable)
                })

                var spancontent = '<table>';
                for (let j = 0; j < JSON.parse(span_element.getAttribute("span_info" + i)).length; j++) {
                    spancontent += '<tr><td>';
                    spancontent += "annotation"
                    spancontent += '</td></tr>'
                }
                spancontent += '</table>';

                annotationtable.innerHTML = spancontent;
                span_element.parentElement.appendChild(annotationtable);
                for (let j = 0; j < annotationtable.getElementsByTagName("tr").length; j++) {
                    annotationtable.getElementsByTagName("tr").item(j).addEventListener('click',function () {
                        let attributes = JSON.parse(span_element.getAttribute("span_info" + i))[j]
                        for (var key of Object.keys(attributes)) {
                            data.push(key, attributes[key])
                        }
                        let annotationstable = document.createElement('div');
                        annotationstable.classList.add('tables');
                        //position the table
                        annotationstable.style.left = spantable.style.left
                        annotationstable.style.top = spantable.style.top
                        annotationstable.innerHTML = table_builder(data)
                        span_element.parentElement.appendChild(annotationstable)
                        //delete table after clicking
                        annotationstable.addEventListener("click", function () {
                            annotationstable.parentElement.removeChild(annotationstable)
                        })
                    })

                }
            }


        })
    }

    //this deletes the original "span" table
    var elements = document.getElementsByClassName("tables");
    for (let i = 0; i < elements.length; i++) {
        elements.item(i).addEventListener("click", function () {
            this.parentElement.removeChild(this)
        })
    }


}


function span_table(span) {
    var data = span.getAttribute("span_info");
    data = data.split(",");
    var content = '<table>';
    for (let row of data) {
        content += '<tr><td>';
        content += row;
        content += '</td></tr>'
    }
    content += '</table>';

    return content
}

function table_builder(contents) {
    var table = '<table>';
    for (let i = 0; i < contents.length; i++) {
        if (i % 2 === 0) {
            table += '<tr><td>';
            table += contents[i];
            table += '</td>'
        } else {
            table += '<td>';
            table += contents[i];
            table += '</td></tr>'
        }
    }
    table += '</table>';

    return table
}

function attribute_table(span_element) {

    //extract the attributes from the span info string
    var data = []
    let info = JSON.parse(span_element.getAttribute("span_info0"))[0]
    for (let infoElement of Object.keys(info)) {
        var attrName = infoElement
        var attrValue = info[infoElement]
        data.push(attrName, attrValue)
    }

    let spantable = document.createElement('div');
    spantable.classList.add('tables');
    spantable.innerHTML = table_builder(data);
    span_element.parentElement.appendChild(spantable);

    // Increase the size of the cell so the tables would fit
    spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 200) + 'px';
    // Position the table directly below the corresponding text
    spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px';
    spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';

    // Remove the table when clicked on again
    spantable.addEventListener('click', function () {
        let element = this.parentElement;
        element.removeChild(this)
    })
}

function export_data(){
    var elements = document.getElementsByClassName('span');
    var var_name = elements[0].innerHTML;
    var var_value = document.getElementsByClassName('span')[0].getAttribute("span_info0");
    var command = var_name + " = '" + var_value + "'";
    console.log("Executing Command: " + command);

    var kernel = IPython.notebook.kernel;
    kernel.execute(command);
}

