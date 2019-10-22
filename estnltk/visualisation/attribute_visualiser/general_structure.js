var estnltk = estnltk || {};

estnltk['attribute_visualiser'] = estnltk['attribute_visualiser'] || {};
estnltk.attribute_visualiser = {'DisplayCell':DisplayCell};

function DisplayCell(text_id, visible_index, annotation_index, specific_annotation) {
    this.text_id = text_id;
    this.visible_index = visible_index;
    this.annotation_index = annotation_index;
    this.specific_annotation = specific_annotation;
    this.cell_id = Jupyter.notebook.get_selected_cell().cell_id;
    var chosenSpans = [];
    var keydownListener = false;

    this.accepted_array = [];
    for (let i = 0; i < document.getElementsByClassName("span" + this.text_id).length; i++) {
        this.accepted_array.push([]); //populate the list with "empty" values
    }

    this.add_initial_listeners = function () {
        let elements = document.getElementsByClassName("overlapping-span" + this.text_id);
        for (let i = 0; i < elements.length; i++) {
            //check if a listener is already attached, if not then add it
            let _this = this;
            if (typeof elements.item(i).onclick != "function") {
                elements.item(i).addEventListener("click", function () {
                    _this.show_conflicting_spans(elements.item(i));
                })
            }
        }

        let plain_elements = document.getElementsByClassName("plain-span" + this.text_id);
        for (let i = 0; i < plain_elements.length; i++) {
            //check if a listener is already attached, if not then add it
            if (typeof plain_elements.item(i).onclick != "function") {
                let _this = this;
                plain_elements.item(i).addEventListener("click", function () {
                    _this.attribute_table(plain_elements.item(i));
                })
            }
        }
    };

    this.show_conflicting_spans = function (span_element) {
        //function for displaying overlapping spans

        let spantable = document.createElement('div');
        spantable.classList.add('tables');

        let data = span_element.getAttribute("span_texts");
        data = data.split(",");
        let spancontent = '<table>';
        for (let row of data) {
            spancontent += '<tr><td>';
            spancontent += row;
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
        this.annotation_table(spantable, span_element);

        //this deletes the original "span" table and the annotation table with multiple columns
        let table_elements = document.getElementsByClassName("tables");
        for (let i = 0; i < table_elements.length; i++) {
            table_elements.item(i).addEventListener("click", function () {
                this.parentElement.removeChild(this)
            })
        }
        return spantable;
    };

    this.table_builder = function (contents) {
        //helper function to build a table with two columns
        let table = '<table>';
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
    };

    this.attribute_table = function (span_element) {
        //function for non-overlapping spans

        //extract the attributes from the span info string
        let data = [];
        let info = JSON.parse(span_element.getAttribute("span_info0"))[0];
        for (let infoElement of Object.keys(info)) {
            let attrName = infoElement;
            let attrValue = info[infoElement];
            data.push(attrName, attrValue)
        }

        let spantable = document.createElement('div');
        spantable.classList.add('tables');
        spantable.innerHTML = this.table_builder(data);
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
    };

    this.annotation_table = function (spantable, span_element) {
        for (let i = 0; i < spantable.getElementsByTagName("tr").length; i++) {
            let _this = this;
            spantable.getElementsByTagName("tr").item(i).addEventListener('click', function () {
                let data = [];
                let annotations = JSON.parse(span_element.getAttribute("span_info" + i));
                let spanIndex = JSON.parse(span_element.getAttribute("span_index" + i));
                let firstAnnotation = annotations[0];
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
                    });
                    //position the table
                    annotationstable.style.left = spantable.style.left;
                    annotationstable.style.top = spantable.style.top;
                    annotationstable.innerHTML = _this.table_builder(data);
                    span_element.parentElement.appendChild(annotationstable)
                } else { //add attributes
                    let attributeList = [];
                    let attributeData = [];
                    for (let key of Object.keys(firstAnnotation)) {
                        attributeList.push(key)
                    }
                    attributeData.push(attributeList);
                    let annotationInfo;
                    //add attribute values
                    for (let annotation of annotations) {
                        annotationInfo = [];
                        for (let key of Object.keys(firstAnnotation)) {
                            annotationInfo.push(annotation[key])
                        }
                        data.push(annotationInfo)
                    }
                    let annotationtable = document.createElement('div');
                    annotationtable.classList.add('tables');
                    annotationtable.classList.add('column-tables');
                    //position the table
                    annotationtable.style.left = spantable.style.left;
                    annotationtable.style.top = spantable.style.top;
                    annotationtable.addEventListener("keydown", function (event) {
                        //if cell is selected, listen to number keys
                        Jupyter.keyboard_manager.disable();
                        try {
                            if (!isNaN(parseInt(event.key))) {
                                let clicked = parseInt(event.key);
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
                    });

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
                        spancontent += '<table class="attribute-column"';
                        if (chosenSpans[spanIndex] === j) {
                            spancontent += ' style="border: 2px solid red;"'
                        }
                        spancontent += '" onClick=assignValue(';
                        spancontent += spanIndex;
                        spancontent += ',';
                        spancontent += j;
                        spancontent += ')>';
                        for (let k = 0; k < data[j].length; k++) {
                            spancontent += '<tr><td>';
                            spancontent += data[j][k];
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
    };

    this.assignValue = function (spanNumber, value) {
        // function is used by annotationtable function tables to give values to chosenSpans list
        while (chosenSpans.length < spanNumber) {
            chosenSpans.push(-1)
        }
        chosenSpans[spanNumber] = value

    };

    this.assignValueToIterTable = function (spanNumber, value, table) {
        // function is used by annotationtable function tables to give values to chosenSpans list
        while (chosenSpans.length < spanNumber) {
            chosenSpans.push(-1)
        }
        chosenSpans[spanNumber] = value;
        for (let childTable of table.parentElement.parentElement.children) {
            childTable.firstChild.style.border = "none"
        }
        table.style.border = "2px solid red"

    };

    this.export_data = function (name) {
        // exporting data, this function is triggered by clicking the "Export data" button"
        if (name === "") {
            name = "display";
        }
        let var_name = name + ".accepted_array";
        let var_value = JSON.stringify(this.accepted_array);
        let command = var_name + " = " + var_value;
        let annotationCommand = name + ".chosen_annotations" + " = " + JSON.stringify(chosenSpans);
        console.log("Executing Command: " + command);
        var kernel = IPython.notebook.kernel;
        // the corresponding commands are executed in the kernel
        kernel.execute(command);
        kernel.execute(annotationCommand);
        // enable jupyter keyboard shortcuts again
        Jupyter.keyboard_manager.enable()
    };
    let object = this;

    //TODO proovi panna keydown parentelement divi kulge
    if (!keydownListener) {
        //move with arrow keys
        document.addEventListener("keydown", function (event) {
            if (object.cell_id === Jupyter.notebook.get_selected_cell().cell_id) {
                let selected_cell = object.text_id;
                if (event.key === "ArrowLeft") {
                    let annotationColumns = document.getElementsByClassName("iterable-annotation-table" + selected_cell);
                    try {
                        if (annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === '2px solid yellow') {
                            annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = 'none'
                        }
                    } catch (e) {

                    }
                    if (object.specific_annotation === 0) {
                        // check if it's the first annotation of the span and move to the previous span
                        object.annotation_index--;
                        object.toggle_annotation_visibility();
                        try {
                            object.specific_annotation = annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.length - 2;
                        } catch (e) {
                            object.specific_annotation = 0;
                        }
                    } else {
                        object.specific_annotation--
                    }
                    if (annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === 'none') {
                        annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = '2px solid yellow'
                    }
                }
                if (event.key === "ArrowRight") {
                    let annotationColumns = document.getElementsByClassName("iterable-annotation-table" + selected_cell);
                    if (object.annotation_index < 0) {
                        object.annotation_index = 0;
                        object.toggle_annotation_visibility();
                        object.specific_annotation = 0;
                    } else if (annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.length - 2 === object.specific_annotation) {
                        // check if it's the last annotation of the span and move to the next span
                        if (annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === '2px solid yellow') {
                            annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = 'none'
                        }
                        object.annotation_index++;
                        object.toggle_annotation_visibility();
                        object.specific_annotation = 0;
                    } else {
                        if (annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === '2px solid yellow') {
                            annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = 'none'
                        }
                        //if it isn't the last annotation then focus the next annotation
                        object.specific_annotation++
                    }
                    if (annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === 'none' || annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === '') {
                        annotationColumns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = '2px solid yellow'
                    }
                } else if (event.key === "1" || event.key === "2") {
                    object.accepted_array[object.annotation_index][object.specific_annotation] = event.key;
                    let annotation_columns = document.getElementsByClassName("iterable-annotation-table" + selected_cell);
                    if (event.key === "1") {
                        annotation_columns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = '2px solid green';
                    } else {
                        annotation_columns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = '2px solid red';
                    }
                    if (annotation_columns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.length - 2 === object.specific_annotation) {
                        // check if it's the last annotation of the span and move to the next span
                        object.annotation_index++;
                        object.toggle_annotation_visibility();
                        object.specific_annotation = 0;
                    } else {
                        //if it isn't the last annotation then focus the next annotation
                        object.specific_annotation++
                    }
                    if (annotation_columns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === 'none' || annotation_columns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border === '') {
                        annotation_columns.item(object.annotation_index).firstChild.firstChild.firstChild.childNodes.item(object.specific_annotation + 1).style.border = '2px solid yellow'
                    }
                }
            }
        });

        //prevent the creation of other listeners
        keydownListener = true
    }

    this.toggle_visibility = function () {
        let tableColumns = document.getElementsByClassName("iterable-table" + this.text_id);
        for (let i = 0; i < tableColumns.length; i++) {
            if (i === this.visible_index) {
                tableColumns.item(i).style.display = "block"
            } else {
                tableColumns.item(i).style.display = "none"
            }
        }
    };

    this.toggle_annotation_visibility = function () {
        let selected_cell = this.text_id;
        let annotationColumns = document.getElementsByClassName("iterable-annotation-table" + selected_cell);
        for (let i = 0; i < annotationColumns.length; i++) {
            if (i === this.annotation_index) {
                annotationColumns.item(i).style.display = "block"
            } else {
                annotationColumns.item(i).style.display = "none"
            }
        }
    };

    this.open_spans = function () {
        // this creates all the spans that the user can navigate using left and right arrow keys
        // all the possible span tables are created and then their visibility is changed with toggle_visibility()
        let overlapped = document.getElementsByClassName("overlapping-span" + this.text_id);
        for (let i = 0; i < overlapped.length; i++) {
            let span_element = overlapped.item(i);
            let spantable = document.createElement('div');
            spantable.classList.add('tables');

            let spantexts = span_element.getAttribute("span_texts");
            let data = spantexts.split(",");
            let spancontent = '<table>';
            for (let row of data) {
                spancontent += '<tr><td>';
                spancontent += row;
                spancontent += '</td></tr>'
            }
            spancontent += '</table>';

            spantable.innerHTML = spancontent;
            span_element.parentElement.appendChild(spantable);
            spantable.classList.add('iterable-table' + this.text_id);

            // Increase the size of the cell so the tables would fit
            spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0, spantable.parentElement.style.height.length - 2)), span_element.offsetTop + 90) + 'px';
            // Position the table directly below the corresponding text
            spantable.style.left = span_element.getBoundingClientRect().left - spantable.parentElement.parentElement.getBoundingClientRect().left + 'px';
            spantable.style.top = span_element.getBoundingClientRect().top - spantable.parentElement.parentElement.getBoundingClientRect().top + 20 + 'px';
        }

    };

    this.create_all_annotation_tables = function () {
        // this creates all the annotations that the user can navigate using left and right keys
        // all the possible annotation tables are created and then their visibility is changed with toggle_annotation_visibility()
        let all_spans = document.getElementsByClassName("span" + this.text_id);
        let viewed_annotations = new Set();
        for (let i = 0; i < all_spans.length; i++) {
            let span_element = all_spans.item(i);
            let index = 0;
            while (true) {
                if (span_element.hasAttribute("span_index" + index)) {
                    let spanIndex = JSON.parse(span_element.getAttribute("span_index" + index));
                    if (!viewed_annotations.has(spanIndex)) {
                        viewed_annotations.add(spanIndex);
                        let data = [];
                        let annotations = JSON.parse(span_element.getAttribute("span_info" + index));
                        let firstAnnotation = annotations[0];
                        let attributeList = [];
                        let attributeData = [];
                        for (var key of Object.keys(firstAnnotation)) {
                            attributeList.push(key)
                        }
                        attributeData.push(attributeList);
                        let annotationInfo;
                        //add attribute values
                        for (let annotation of annotations) {
                            annotationInfo = [];
                            for (let key of Object.keys(firstAnnotation)) {
                                annotationInfo.push(annotation[key])
                            }
                            data.push(annotationInfo)
                        }
                        let annotationtable = document.createElement('div');
                        span_element.parentElement.appendChild(annotationtable);
                        annotationtable.classList.add('alt-tables');
                        annotationtable.classList.add('iterable-annotation-table' + this.text_id);

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
                            spancontent += '<table class="attribute-column"';
                            spancontent += '" onClick=assignValueToIterTable(';
                            spancontent += spanIndex;
                            spancontent += ',';
                            spancontent += j;
                            spancontent += ',this';
                            spancontent += ')>';
                            for (let k = 0; k < data[j].length; k++) {
                                spancontent += '<tr><td>';
                                spancontent += data[j][k];
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
        let created_tables = document.getElementsByClassName("iterable-annotation-table" + this.text_id);
        created_tables.item(0).firstChild.firstChild.firstChild.childNodes.item(1).style.border = '2px solid yellow'
    };

    this.add_initial_listeners();
    this.open_spans();
    this.toggle_visibility();
    this.create_all_annotation_tables();
    this.toggle_annotation_visibility();

}