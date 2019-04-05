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


function annotation_table(spantable, span_element) {
    for (let i = 0; i < spantable.getElementsByTagName("tr").length; i++) {
        spantable.getElementsByTagName("tr").item(i).addEventListener('click', function () {
            let data = [];
            let annotations = JSON.parse(span_element.getAttribute("span_info" + i))
            let firstAnnotation = annotations[0]
            //if there is only one annotation to show
            if (annotations.length === 1) {
                for (let key of Object.keys(firstAnnotation)) {
                    data.push(key, firstAnnotation[key])
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
            } else { //add attributes
                let attributeList = []
                let attributeData = []
                for (var key of Object.keys(firstAnnotation)) {
                    attributeList.push(key)
                }
                attributeData.push(attributeList)
                let annotationInfo
                //add attribute values
                for (var annotation of annotations) {
                    annotationInfo = []
                    for (let key of Object.keys(firstAnnotation)) {
                        annotationInfo.push(annotation[key])
                    }
                    data.push(annotationInfo)
                }
                let annotationtable = document.createElement('div');
                annotationtable.classList.add('tables');
                annotationtable.classList.add('column-tables');
                //position the table
                annotationtable.style.left = spantable.style.left
                annotationtable.style.top = spantable.style.top
                //delete table after clicking
                annotationtable.addEventListener("click", function () {
                    annotationtable.parentElement.removeChild(annotationtable)
                })

                var spancontent = '<table><tr>';
                for (let j = 0; j < attributeData.length; j++) {
                    spancontent += '<td>';
                    spancontent += '<table class="attribute-names-table">'
                    for (let k = 0; k < attributeData[j].length; k++) {
                        spancontent += '<tr><td>'
                        spancontent += attributeData[j][k]
                        spancontent += '</td></tr>'
                    }
                    spancontent += '</table></td>'
                }
                for (let j = 0; j < data.length; j++) {
                    spancontent += '<td>';
                    spancontent += '<table class="attribute-column">'
                    for (let k = 0; k < data[j].length; k++) {
                        spancontent += '<tr><td>'
                        spancontent += data[j][k]
                        spancontent += '</td></tr>'
                    }
                    spancontent += '</table></td>'
                }
                spancontent += '</tr></table>';

                annotationtable.innerHTML = spancontent;
                span_element.parentElement.appendChild(annotationtable);
            }


        })
    }
}

function show_conflicting_spans(span_element) {

    let spantable = document.createElement('div');
    spantable.classList.add('tables');

    let data = span_element.getAttribute("span_texts")
    data = data.split(",")
    var spancontent = '<table>';
    for (let row of data) {
        spancontent += '<tr><td>'
        spancontent += row
        spancontent += '</td></tr>'
    }
    spancontent += '</table>';

    spantable.innerHTML = spancontent;
    span_element.parentElement.appendChild(spantable);

    // Increase the size of the cell so the tables would fit
    spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 90) + 'px';
    // Position the table directly below the corresponding text
    spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px';
    spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';


    // Add listeners to create the following tables
    annotation_table(spantable, span_element);

    //this deletes the original "span" table and the annotation table with multiple columns
    var elements = document.getElementsByClassName("tables");
    for (let i = 0; i < elements.length; i++) {
        elements.item(i).addEventListener("click", function () {
            this.parentElement.removeChild(this)
        })
    }
    return spantable;
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

var accepted_array = [];
for (let i = 0; i < elements.length; i++) {
    accepted_array.push(0);
}
function export_data() {
    var var_name = "accepted_array";
    var var_value = accepted_array;
    var command = var_name + " = '" + var_value + "'";
    console.log("Executing Command: " + command);
    var kernel = IPython.notebook.kernel;
    kernel.execute(command);
}

function open_tables() {
    for (let element of elements) {
        for (let i = 0; i < 100; i++) {
            if (element.hasAttribute("span_info" + i)) {
                if (JSON.parse(element.getAttribute("span_info"+i)).length !== 1) {
                    let data = [];
                    let annotations = JSON.parse(element.getAttribute("span_info"+i))
                    let firstAnnotation = annotations[0]
                    //add attributes
                    let attributeList = []
                    let attributeData = []
                    for (var key of Object.keys(firstAnnotation)) {
                        attributeList.push(key)
                    }
                    attributeData.push(attributeList)
                    let annotationInfo
                    //add attribute values
                    for (var annotation of annotations) {
                        annotationInfo = []
                        for (let key of Object.keys(firstAnnotation)) {
                            annotationInfo.push(annotation[key])
                        }
                        data.push(annotationInfo)
                    }
                    let annotationtable = document.createElement('div');
                    annotationtable.classList.add('tables');
                    annotationtable.classList.add('column-tables');
                    element.parentElement.appendChild(annotationtable);
                    //position the table
                    // Increase the size of the cell so the tables would fit
                    annotationtable.parentElement.style.height = Math.max(Number(annotationtable.parentElement.style.height.substring(0, annotationtable.parentElement.style.height.length - 2)), element.offsetTop + 200) + 'px';
                    // Position the table directly below the corresponding text
                    annotationtable.style.left = element.getBoundingClientRect().left - annotationtable.parentElement.parentElement.getBoundingClientRect().left + 'px';
                    annotationtable.style.top = element.getBoundingClientRect().top - annotationtable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';
                    //delete table after clicking
                    annotationtable.addEventListener("click", function () {
                        //visible++;
                        toggle_visibility();
                    });

                    let spancontent = '<table><tr>';
                    for (let j = 0; j < attributeData.length; j++) {
                        spancontent += '<td>';
                        spancontent += '<table class="attribute-names-table">'
                        for (let k = 0; k < attributeData[j].length; k++) {
                            spancontent += '<tr><td>'
                            spancontent += attributeData[j][k]
                            spancontent += '</td></tr>'
                        }
                        spancontent += '</table></td>'
                    }
                    for (let j = 0; j < data.length; j++) {
                        spancontent += '<td>';
                        spancontent += '<table class="attribute-column">'
                        for (let k = 0; k < data[j].length; k++) {
                            spancontent += '<tr><td>'
                            spancontent += data[j][k]
                            spancontent += '</td></tr>'
                        }
                        spancontent += '</table></td>'
                    }
                    spancontent += '</tr></table>';

                    annotationtable.innerHTML = spancontent;

                }
            } else {
                break;
            }
        }

    }
}


//open_tables();

try{
    var visible_index = 0;
} catch (ex) {

}

if (typeof keydownListener === 'undefined') {
    // the variable is defined
    var keydownListener = false;
}

//move with arrow keys
if (!keydownListener) {
    document.addEventListener("keydown", function (event) {
        if (event.key === "ArrowLeft") {
            visible_index--;
            toggle_visibility();
        }
        if (event.key === "ArrowRight") {
            visible_index++;
            toggle_visibility();
        }
    });
    keydownListener = true;
}

function toggle_visibility() {
    let tableColumns = document.getElementsByClassName("iterable-table")
    for (let i = 0; i < tableColumns.length; i++) {
        if (i!==visible_index){
            tableColumns.item(i).style.display = "none"
        } else {
            tableColumns.item(i).style.display = "block"
        }
    }
}

function open_spans() {
    let overlapped = document.getElementsByClassName("overlapping-span");
    for (let i = 0; i < overlapped.length; i++) {
        let span_element = overlapped.item(i)
        let spantable = document.createElement('div');
        spantable.classList.add('tables');

        let data = span_element.getAttribute("span_texts")
        data = data.split(",")
        let spancontent = '<table>';
        for (let row of data) {
            spancontent += '<tr><td>'
            spancontent += row
            spancontent += '</td></tr>'
        }
        spancontent += '</table>';

        spantable.innerHTML = spancontent;
        span_element.parentElement.appendChild(spantable);
        spantable.classList.add('iterable-table')

        // Increase the size of the cell so the tables would fit
        spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 90) + 'px';
        // Position the table directly below the corresponding text
        spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px';
        spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';
    }

}

open_spans();
toggle_visibility();

document.addEventListener("keydown", function (event) {
    //if cell is selected, listen to number keys
    if (elements.item(0).parentElement.parentElement.parentElement.parentElement.parentElement.classList.contains("selected")){
        try {
            if (!isNaN(parseInt(event.key))) {
                accepted_array[visible_index] = event.key;
            }
        } catch (e) {
        }
    }
});

