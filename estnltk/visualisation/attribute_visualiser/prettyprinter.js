// var text_id is given a value previously and it works as an index keeping count which version of the text is displayed

/* Opening section: find all elements from the document with the corresponding class names and
attach listeners to them so that an appropriate table would be opened whenever one of them is opened
 */
var elements = document.getElementsByClassName("overlapping-span"+text_id);
for (let i = 0; i < elements.length; i++) {
    //check if a listener is already attached, if not then add it
    if (typeof elements.item(i).onclick != "function") {
        elements.item(i).addEventListener("click", function () {
            show_conflicting_spans(elements.item(i));
        })
    }
}

var plain_elements = document.getElementsByClassName("plain-span"+text_id);
for (let i = 0; i < plain_elements.length; i++) {
    //check if a listener is already attached, if not then add it
    if (typeof plain_elements.item(i).onclick != "function") {
        plain_elements.item(i).addEventListener("click", function () {
            attribute_table(plain_elements.item(i));
        })
    }
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
    let table_elements = document.getElementsByClassName("tables"+text_id);
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


/*
 Helpers for annotationtable function
 */
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

var accepted_array = [];
for (let i = 0; i < document.getElementsByClassName("span"+text_id).length; i++) {
    accepted_array.push([]); //populate the list with "empty" values
}

function export_data(name) {
    // exporting data, this function is triggered by clicking the "Export data" button"
    if (name==="") {
        name = "display";
    }
    let var_name = name+".accepted_array";
    let var_value = accepted_array.join(" ");
    let command = var_name + " = '" + var_value + "'";
    let annotationCommand = name+".chosen_annotations" + " = '" + chosenSpans + "'";
    console.log("Executing Command: " + command);
    var kernel = IPython.notebook.kernel;
    // the corresponding commands are executed in the kernel
    kernel.execute(command);
    kernel.execute(annotationCommand);
    // enable jupyter keyboard shortcuts again
    Jupyter.keyboard_manager.enable()
}

//not in use right now, used to be for iterable spans but that was replaced by annotations
function transform_array(array) {
    // helper function to make the exportable array more foolproof
    let new_array = []
    for (let i = 0; i < array.length; i++) {
        let number = array[i] - 1
        new_array[i] = elements.item(i).getAttribute("span_index" + number)
    }
    return new_array
}


try {
    var visible_index = -1;
} catch (ex) {
    // if visible index already has a value then we should do nothing
}

try {
    var annotation_index = 0;
} catch (e) {
}

try {
    var specific_annotation = 0;
} catch (e) {
}

//since this script might be loaded on the page many times but we don't want the script
//to increase the indexes multiple times per one click, this will make sure that there
//is exactly one keydown listener per notebook
if (typeof keydownListener === 'undefined') {
    var keydownListener = false;
}

if (typeof a_or_d_listener === 'undefined') {
    var a_or_d_listener = false;
}

//move with j and k keys (on hold till we find an application for it)
/*if (!keydownListener) {
    document.addEventListener("keydown", function (event) {
        if (event.key === "j") {
            visible_index--;
            toggle_visibility();
        }
        if (event.key === "k") {
            visible_index++;
            toggle_visibility();
        }
    });
    keydownListener = true;
}*/

if (!keydownListener) {
//move with arrow keys
    document.addEventListener("keydown", function (event) {
        if (event.key === "ArrowLeft") {
            let annotationColumns = document.getElementsByClassName("iterable-annotation-table"+text_id)
            try {
                if (annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation + 1).style.border === '2px solid yellow') {
                    annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation + 1).style.border = 'none'
                }
            } catch (e) {

            }
            if (specific_annotation===0) {
                // check if it's the first annotation of the span and move to the previous span
                annotation_index--;
                toggle_annotation_visibility();
                try {
                    specific_annotation = annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.length - 2;
                } catch (e) {
                    specific_annotation = 0;
                }
            } else {
                specific_annotation--
            }
            if (annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === 'none'){
                annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = '2px solid yellow'
            }
        }
        if (event.key === "ArrowRight") {
            let annotationColumns = document.getElementsByClassName("iterable-annotation-table"+text_id)
            if (annotation_index<0){
                annotation_index = 0;
                toggle_annotation_visibility();
                specific_annotation = 0;
            } else if (annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.length-2===specific_annotation) {
                // check if it's the last annotation of the span and move to the next span
                if (annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === '2px solid yellow'){
                    annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = 'none'
                }
                annotation_index++;
                toggle_annotation_visibility();
                specific_annotation = 0;
            } else {
                if (annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === '2px solid yellow'){
                    annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = 'none'
                }
                //if it isn't the last annotation then focus the next annotation
                specific_annotation++
            }
            if (annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === 'none' || annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === ''){
                annotationColumns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = '2px solid yellow'
            }
        }
        if (event.key === "1"){
            accepted_array[annotation_index][specific_annotation] = 1;
            let annotation_columns = document.getElementsByClassName("iterable-annotation-table"+text_id);
            annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = '2px solid green';
            if (annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.length-2===specific_annotation) {
                // check if it's the last annotation of the span and move to the next span
                annotation_index++;
                toggle_annotation_visibility();
                specific_annotation = 0;
            } else {
                //if it isn't the last annotation then focus the next annotation
                specific_annotation++
            }
            if (annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === 'none' || annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === ''){
                annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = '2px solid yellow'
            }
        } if (event.key === "2"){
            accepted_array[annotation_index][specific_annotation] = 2;
            let annotation_columns = document.getElementsByClassName("iterable-annotation-table"+text_id);
            annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = '2px solid red';
            if (annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.length-2===specific_annotation) {
                // check if it's the last annotation of the span and move to the next span
                annotation_index++;
                toggle_annotation_visibility();
                specific_annotation = 0;
            } else {
                //if it isn't the last annotation then focus the next annotation
                specific_annotation++
            }
            if (annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === 'none' || annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border === ''){
                annotation_columns.item(annotation_index).firstChild.firstChild.firstChild.childNodes.item(specific_annotation+1).style.border = '2px solid yellow'
            }
        }
    });

    //prevent the creation of other listeners
    keydownListener = true
}

function toggle_visibility() {
    let tableColumns = document.getElementsByClassName("iterable-table"+text_id)
    for (let i = 0; i < tableColumns.length; i++) {
        if (i !== visible_index) {
            tableColumns.item(i).style.display = "none"
        } else {
            tableColumns.item(i).style.display = "block"
        }
    }
}

function toggle_annotation_visibility() {
    let annotationColumns = document.getElementsByClassName("iterable-annotation-table"+text_id)
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
    let overlapped = document.getElementsByClassName("overlapping-span"+text_id);
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
        spantable.classList.add('iterable-table'+text_id)

        // Increase the size of the cell so the tables would fit
        spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 90) + 'px';
        // Position the table directly below the corresponding text
        spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px';
        spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';
    }

}

function create_all_annotation_tables() {
    // this creates all the annotations that the user can navigate using left and right keys
    // all the possible annotation tables are created and then their visibility is changed with toggle_annotation_visibility()
    let all_spans = document.getElementsByClassName("span"+text_id);
    let viewed_annotations = new Set();
    for (let i = 0; i < all_spans.length; i++) {
        let span_element = all_spans.item(i)
        let index = 0
        while (true) {
            if (span_element.hasAttribute("span_index" + index)) {
                let spanIndex = JSON.parse(span_element.getAttribute("span_index" + index));
                if (!viewed_annotations.has(spanIndex)) {
                    viewed_annotations.add(spanIndex)
                    let data = [];
                    let annotations = JSON.parse(span_element.getAttribute("span_info" + index))
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
                    annotationtable.classList.add('iterable-annotation-table'+text_id);
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
    let created_tables = document.getElementsByClassName("iterable-annotation-table"+text_id);
    created_tables.item(0).firstChild.firstChild.firstChild.childNodes.item(1).style.border = '2px solid yellow'
}

document.addEventListener("keydown", function (event) {
    let all_annotations = document.getElementsByClassName("iterable-annotation-table"+text_id);
    //if cell is selected, listen to number keys
    if (all_annotations.item(0).parentElement.parentElement.parentElement.parentElement.parentElement.classList.contains("selected")) {
        Jupyter.keyboard_manager.disable()
    }
});

open_spans();
toggle_visibility();
create_all_annotation_tables();
toggle_annotation_visibility();

