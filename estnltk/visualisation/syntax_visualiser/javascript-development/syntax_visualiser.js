//uus js fail ülevalt
//uus javascript fail currentelement

//tabel divi klass estnltk-syntax-editor


function get_select_value(element) {
    let selectedValueId = document.getElementById(element).value;
    //let selectedValue = selectedValueId.options[selectedValueId.selectedIndex].text;
    //let selectedValue = selectedValueId.target.options[selectedValueId.target.selectedIndex].text;
    //console.log(selectedValueId.options);
    console.log(selectedValueId);
    //return selectedValue;
}

function selecting_value(event, column) {
    //let attributes = JSON.parse();
    if (event.keyCode == '13'|| event.which == '13') {
        let value = get_select_value(column);
        console.log(value);
    }
}

//Jupyter.notebook.get_selected_cell().element[0].style.height = '400px';

if (typeof start === 'undefined') {
    var start;
}
document.addEventListener('click', function (e) {
    Jupyter.keyboard_manager.disable();
    if (start != undefined) {
        start.style.backgroundColor = null;
        //start.style.color = null;
        //start.style.color = null;
    }
    let startid = e.target.id;
    start = document.getElementById(startid);
    start.focus();
    start.style.backgroundColor = 'pink';
    //start.style.color = 'white';
    document.onkeydown = checkKey;
}, false);

function move(sibling) {
    if (sibling != null) {
        //start.focus();
        start.style.backgroundColor = '';
        //start.style.color = '';
        sibling.focus();
        sibling.style.backgroundColor = 'pink';
        //sibling.style.color = 'white';
        start = sibling;
    }
}

//onkeydown uus js fail
function checkKey(e) {
    e = e || window.event;
    if (e.keyCode == '38') {
        // up arrow
        e.preventDefault();
        let idx = start.cellIndex;
        let nextrow = start.parentElement.previousElementSibling;
        if (nextrow != null) {
            let sibling = nextrow.cells[idx];
            move(sibling);
        }
    } else if (e.keyCode == '40') {
        // down arrow
        e.preventDefault();
        let idx = start.cellIndex;
        let nextrow = start.parentElement.nextElementSibling;
        if (nextrow != null) {
            let sibling = nextrow.cells[idx];
            move(sibling);
        }
    } else if (e.keyCode == '37') {
        // left arrow
        e.preventDefault();
        //let index = start.cellIndex;
        let index = Array.from(start.parentElement.parentElement.children).indexOf(start.parentElement);
        //console.log(start);
        //console.log(start.parentElement.parentElement.children);
        //console.log(index);
        //let sibling = start.parentElement.previousElementSibling;
        //let sibling = start.parentElement.parentElement.parentElement.parentElement.previousElementSibling.firstElementChild.firstElementChild.children.item(index).firstElementChild;
        let sibling = start.previousElementSibling;
        move(sibling);
    } else if (e.keyCode == '39') {
        // right arrow
        e.preventDefault();
        //let index = Array.from(start.parentElement.parentElement.children).indexOf(start.parentElement);
        //let sibling = start.parentElement.parentElement.parentElement.parentElement.nextElementSibling.firstElementChild.firstElementChild.children.item(index).firstElementChild;
        let sibling = start.nextElementSibling;
        move(sibling);
    } else if (e.keyCode == '32') {
        // Space key for opening dropdown
        let sibling = start.firstElementChild;
        move(sibling);
    } else if (e.keyCode == '16') {
        //Shift for going back (for leaving dropdown)
        //console.log(start);
        let sibling = start.parentElement;
        move(sibling);
        e.preventDefault();
        //e.preventDefault();
    } else if (e.keyCode == '13') {
        // Enter key for dropdown choices
        //console.log(start.tagName);
        //console.log(start.id);
        //console.log(start.options[start.selectedIndex]);
        //console.log(start.id.innerHTML);
        //let optionid = start.id;
        let sibling = start.firstElementChild;
        //get_select_value(start.id);
        move(sibling);
        //console.log(optionid.options[optionid.selectedIndex].text);
        //e.preventDefault();
        //start.blur();
        //let index = Array.from(start.parentElement.parentElement.children).indexOf(start.parentElement);
        //let sibling = start.parentElement.children.item(index);
        //let sibling = start.closest('td');
        //move(sibling);
    }
}

if (typeof visible_index === 'undefined') {
    var visible_index = 0;
}
else {
    visible_index = 0;
}

if (typeof current_element === 'undefined') {
    var current_element = all_tables[visible_index];
}
else {
    current_element = all_tables[visible_index];
}

var table_holder = document.createElement('table');
table_holder.classList.add("iterable-table");
table_holder.innerHTML = current_element;
document.getElementById("previous").parentElement.appendChild(table_holder);
//let tableColumns = document.getElementsByClassName('iterable-table');
//tableColumns.item(visible_index).style.display = "block";

function visibility() {
    //let tableColumns = document.getElementsByTagName("table");
    let tableColumns = document.getElementsByClassName('iterable-table');
    //console.log(tableColumns);
    //let visible_table = document.getElementById(visible_index);
    //visible_table.style.display = 'block';
    for (let i = 0; i < tableColumns.length; i++) {
        if (i !== visible_index) {
            tableColumns.item(i).style.display = "none";
        } else {
            tableColumns.item(i).style.display = "block";
        }
    }
    var new_table = document.createElement('table');
    new_table.classList.add("iterable-table");
    new_table.innerHTML = all_tables[visible_index];
    table_holder.parentNode.replaceChild(new_table, table_holder);
    table_holder = new_table;
}

visibility();

document.getElementById('previous').onclick = function () {
    //tableColumns.item(visible_index).style.display = "none";
    visible_index--;
    //tableColumns.item(visible_index).style.display = "block";
    visibility();
};

document.getElementById('next').onclick = function () {
    //tableColumns.item(visible_index).style.display = "none";
    visible_index++;
    //tableColumns.item(visible_index).style.display = "block";
    visibility();
};

function select_values() {
    let selectElements = document.getElementsByClassName('syntax_choice');
    //let selectValues = selectElements.options[selectElements.selectedIndex].text;
    let selectValues = [];
    for (let i = 0; i < selectElements.length; i=i+2) {
        let thing = {};
        thing['id'] = i/2 + 1;
        if (isNaN(parseInt(selectElements[i].options[selectElements[i].selectedIndex].text[0]))) {
            thing['head'] = selectElements[i + 1].options[selectElements[i + 1].selectedIndex].text[0];
            thing['deprel'] = selectElements[i].options[selectElements[i].selectedIndex].text;
        } else {
            thing['head'] = selectElements[i].options[selectElements[i].selectedIndex].text[0];
            thing['deprel'] = selectElements[i + 1].options[selectElements[i + 1].selectedIndex].text;
        }
        console.log(thing);
        selectValues.push(JSON.stringify(thing));
    }
    console.log(selectElements);
    console.log(selectValues);
    return selectValues;
}

let saved_list = {};

document.getElementById('save').onclick = function () {
    let export_values = select_values();
    console.log(export_values);
    let command = "dropdown_values = '" + export_values + "'";
    /*if (saved_list.length > visible_index) {
        saved_list[visible_index] = export_values;
    } else {
        saved_list.push(export_values);
    }*/
    saved_list[visible_index] = export_values;
    console.log(saved_list);
    //console.log("Executing Command: " + command);
    let commandtest = "all_values = " + JSON.stringify(saved_list);
    var kernel = IPython.notebook.kernel;
    // the corresponding commands are executed in the kernel
    //kernel.execute(command);
    kernel.execute(commandtest);
    console.log(commandtest);
    // enable jupyter keyboard shortcuts again
    Jupyter.keyboard_manager.enable()
};