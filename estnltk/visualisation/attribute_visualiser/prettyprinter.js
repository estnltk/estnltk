var elements = document.getElementsByClassName("overlapping-span");
for (let i = 0; i < elements.length; i++) {
    elements.item(i).addEventListener("click", function () {
        show_conflicting_spans(elements.item(i));
    })
}

var plain_elements = document.getElementsByClassName("plain-span");
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
            let spanIndex = JSON.parse(span_element.getAttribute("span_index" + i));
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
                for (let annotation of annotations) {
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
                annotationtable.addEventListener("keydown", function (event) {
                    console.log("here")
                    //if cell is selected, listen to number keys
                    Jupyter.keyboard_manager.disable()
                    try {
                        if (!isNaN(parseInt(event.key))) {
                            let clicked = parseInt(event.key)
                            if (data.length > clicked) {
                                console.log("There is no span with this number")
                            } else {
                                chosenSpans[spanIndex] = clicked;
                            }
                        }
                    } catch (e) {
                    }

                });
                //delete table after clicking
                annotationtable.addEventListener("click", function () {
                    annotationtable.parentElement.removeChild(annotationtable)
                })

                let spancontent = '<table><tr>';
                for (let j = 0; j < attributeData.length; j++) {
                    spancontent += '<td>';
                    spancontent += '<table class="attribute-names-table">';
                    for (let k = 0; k < attributeData[j].length; k++) {
                        spancontent += '<tr><td>';
                        spancontent += attributeData[j][k];
                        spancontent += '</td></tr>'
                    }
                    spancontent += '</table></td>'
                }
                for (let j = 0; j < data.length; j++) {
                    spancontent += '<td>';
                    spancontent += '<table class="attribute-column"'
                    if (chosenSpans[spanIndex] === j) {
                        spancontent += ' style="border: 2px solid red;"'
                    }
                    spancontent += '" onClick=assignValue(';
                    spancontent += spanIndex;
                    spancontent += ',';
                    spancontent += j;
                    spancontent += ')>'
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

try {
    var chosenSpans = [];
} catch (ex) {
    // if chosenSpans already has a value then we should do nothing
}

function assignValue(spanNumber, value) {
    // function is used by annotationtable function tables to give values to chosenSpans list
    while (chosenSpans.length < spanNumber) {
        chosenSpans.push(-1)
    }
    chosenSpans[spanNumber] = value
    console.log(chosenSpans)

}

function assignValueToIterTable(spanNumber, value, table) {
    // function is used by annotationtable function tables to give values to chosenSpans list
    while (chosenSpans.length < spanNumber) {
        chosenSpans.push(-1)
    }
    chosenSpans[spanNumber] = value
    for (let childTable of table.parentElement.parentElement.children) {
        childTable.firstChild.style.border = "none"
    }
    table.style.border = "2px solid red"

}

function show_conflicting_spans(span_element) {
    //function for displaying overlapping spans

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
    let table_elements = document.getElementsByClassName("tables");
    for (let i = 0; i < table_elements.length; i++) {
        table_elements.item(i).addEventListener("click", function () {
            this.parentElement.removeChild(this)
        })
    }
    return spantable;
}


function table_builder(contents) {
    //helper function to build a table with two columns
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
    //function for non-overlapping spans

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
    accepted_array.push(0); //populate the list with "empty" values
}

function export_data() {
    // exporting data, this function is triggered by clicking the "Export data" button"
    var var_name = "display.accepted_array";
    var var_value = transform_array(accepted_array);
    var command = var_name + " = '" + var_value + "'";
    let annotationCommand = "display.chosen_annotations" + " = '" + chosenSpans + "'";
    console.log("Executing Command: " + command);
    var kernel = IPython.notebook.kernel;
    // the corresponding commands are executed in the kernel
    kernel.execute(command);
    kernel.execute(annotationCommand);
    // enable jupyter keyboard shortcuts again
    Jupyter.keyboard_manager.enable()
}

function transform_array(array) {
    // helper function to make the exportable array more foolproof
    let new_array = []
    for (let i = 0; i < array.length; i++) {
        let number = array[i]-1
        new_array[i] = elements.item(i).getAttribute("span_index"+number)
    }
    return new_array
}


try {
    var visible_index = 0;
} catch (ex) {
    // if visible index already has a value then we should do nothing
}

try {
    var annotation_index = -1;
} catch (e) {

}

if (typeof keydownListener === 'undefined') {
    var keydownListener = false;
}

if (typeof a_or_d_listener === 'undefined') {
    var a_or_d_listener = false;
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

if (!a_or_d_listener) {
//move with a and d keys
    document.addEventListener("keydown", function (event) {
        if (event.key === "a") {
            annotation_index--;
            toggle_annotation_visibility();
        }
        if (event.key === "d") {
            annotation_index++;
            toggle_annotation_visibility();
        }
    });
    a_or_d_listener = true
}

function toggle_visibility() {
    let tableColumns = document.getElementsByClassName("iterable-table")
    for (let i = 0; i < tableColumns.length; i++) {
        if (i !== visible_index) {
            tableColumns.item(i).style.display = "none"
        } else {
            tableColumns.item(i).style.display = "block"
        }
    }
}

function toggle_annotation_visibility() {
    let annotationColumns = document.getElementsByClassName("iterable-annotation-table")
    for (let i = 0; i < annotationColumns.length; i++) {
        if (i !== annotation_index) {
            annotationColumns.item(i).style.display = "none"
        } else {
            annotationColumns.item(i).style.display = "block"
        }
    }
}

function open_spans() {
    // this creates all the spans that the user can navigate using left and right arrow keys
    // all the possible span tables are created and then their visibility is changed with toggle_visibility()
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

function create_all_annotation_tables() {
    // this creates all the annotations that the user can navigate using a and d keys
    // all the possible annotation tables are created and then their visibility is changed with toggle_annotation_visibility()
    let all_spans = document.getElementsByClassName("span");
    for (let i = 0; i < all_spans.length; i++) {
        let span_element = all_spans.item(i)
        let index = 0
        while (true) {
            if (span_element.hasAttribute("span_index" + index)) {
                if (JSON.parse(span_element.getAttribute("span_info" + index)).length > 1) {
                    //table_creation todo
                    let data = [];
                    let annotations = JSON.parse(span_element.getAttribute("span_info" + index))
                    let spanIndex = JSON.parse(span_element.getAttribute("span_index" + index));
                    let firstAnnotation = annotations[0]
                    let attributeList = []
                    let attributeData = []
                    for (var key of Object.keys(firstAnnotation)) {
                        attributeList.push(key)
                    }
                    attributeData.push(attributeList)
                    let annotationInfo
                    //add attribute values
                    for (let annotation of annotations) {
                        annotationInfo = []
                        for (let key of Object.keys(firstAnnotation)) {
                            annotationInfo.push(annotation[key])
                        }
                        data.push(annotationInfo)
                    }
                    let annotationtable = document.createElement('div');
                    span_element.parentElement.appendChild(annotationtable);
                    annotationtable.classList.add('alt-tables');
                    annotationtable.classList.add('iterable-annotation-table');
                    //position the table
                    annotationtable.style.left = span_element.getBoundingClientRect().left - annotationtable.parentElement.parentElement.getBoundingClientRect().left + 'px';
                    annotationtable.style.top = span_element.getBoundingClientRect().top - annotationtable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';

                    let spancontent = '<table><tr>';
                    for (let j = 0; j < attributeData.length; j++) {
                        spancontent += '<td>';
                        spancontent += '<table class="attribute-names-table">';
                        for (let k = 0; k < attributeData[j].length; k++) {
                            spancontent += '<tr><td>';
                            spancontent += attributeData[j][k];
                            spancontent += '</td></tr>'
                        }
                        spancontent += '</table></td>'
                    }
                    for (let j = 0; j < data.length; j++) {
                        spancontent += '<td>';
                        spancontent += '<table class="attribute-column"'
                        spancontent += '" onClick=assignValueToIterTable(';
                        spancontent += spanIndex;
                        spancontent += ',';
                        spancontent += j;
                        spancontent += ',this';
                        spancontent += ')>'
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
                index++;
            } else {
                break;
            }
        }

    }
}

open_spans();
toggle_visibility();
create_all_annotation_tables();
toggle_annotation_visibility();

document.addEventListener("keydown", function (event) {
    //if cell is selected, listen to number keys
    if (elements.item(0).parentElement.parentElement.parentElement.parentElement.parentElement.classList.contains("selected")) {
        Jupyter.keyboard_manager.disable()
        try {
            if (!isNaN(parseInt(event.key))) {
                let clicked = parseInt(event.key)
                if (!elements.item(visible_index).hasAttribute("span_index"+(clicked-1))) {
                    console.log("There is no span with this number")
                    accepted_array[visible_index] = 0
                } else {
                    accepted_array[visible_index] = clicked
                }
                let tableColumns = document.getElementsByClassName("iterable-table")
                for (let i = 0; i < tableColumns.item(visible_index).firstElementChild.firstElementChild.children.length; i++) {
                    //highlight the chosen span
                    if (i === clicked - 1) {
                        tableColumns.item(visible_index).firstElementChild.firstElementChild.children.item(i).firstElementChild.style.border = "2px solid red"
                    } else {
                        tableColumns.item(visible_index).firstElementChild.firstElementChild.children.item(i).firstElementChild.style.border = "none";
                    }
                }
            }
        } catch (e) {
        }
    }
});