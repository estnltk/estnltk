if (typeof start === 'undefined') {
    var start;
}
document.addEventListener('click', function (e) {
    Jupyter.keyboard_manager.disable();
    if (start != undefined) {
        start.style.backgroundColor = null;
    }
    let startid = e.target.id;
    start = document.getElementById(startid);
    start.focus();
    start.style.backgroundColor = 'white';
    document.onkeydown = checkKey;
}, false);

function move(sibling) {
    if (sibling != null) {
        start.style.backgroundColor = '';
        start.style.border = '';
        sibling.focus();
        sibling.style.backgroundColor = 'white';
        sibling.style.border = "thin dotted blue";
        start = sibling;
    }
}

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
        let sibling = start.previousElementSibling;
        move(sibling);
    } else if (e.keyCode == '39') {
        // right arrow
        e.preventDefault();
        let sibling = start.nextElementSibling;
        move(sibling);
    } else if (e.keyCode == '32') {
        // Space key for opening dropdown
        let sibling = start.firstElementChild;
        move(sibling);
    } else if (e.keyCode == '16') {
        //Shift for going back (for leaving dropdown)
        let sibling = start.parentElement;
        move(sibling);
        e.preventDefault();
        //e.preventDefault();
    } else if (e.keyCode == '13') {
        // Enter key for dropdown choices
        let sibling = start.firstElementChild;
        move(sibling);
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

function visibility() {
    let tableColumns = document.getElementsByClassName('iterable-table');
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
    visible_index--;
    visibility();
};

document.getElementById('next').onclick = function () {
    visible_index++;
    visibility();
};

function select_values() {
    let selectElements = document.getElementsByClassName('syntax_choice');
    let selectValues = [];
    for (let i = 0; i < selectElements.length; i=i+2) {
        let value_list = {};
        value_list['id'] = i/2 + 1;
        if (isNaN(parseInt(selectElements[i].options[selectElements[i].selectedIndex].text[0]))) {
            value_list['head'] = parseInt(selectElements[i + 1].options[selectElements[i + 1].selectedIndex].text[0]);
            value_list['deprel'] = selectElements[i].options[selectElements[i].selectedIndex].text;
        } else {
            value_list['head'] = parseInt(selectElements[i].options[selectElements[i].selectedIndex].text[0]);
            value_list['deprel'] = selectElements[i + 1].options[selectElements[i + 1].selectedIndex].text;
        }
        console.log(value_list);
        selectValues.push(JSON.stringify(value_list));
    }
    console.log(selectElements);
    console.log(selectValues);
    return selectValues;
}

let saved_dict = {};
saved_dict[visible_index] = select_values();

document.getElementById('save').onclick = function () {
    let export_values = select_values();
    console.log(export_values);
    saved_dict[visible_index] = export_values;
    console.log(saved_dict);
    let command = "all_values = " + JSON.stringify(saved_dict);
    var kernel = IPython.notebook.kernel;
    // the corresponding commands are executed in the kernel
    kernel.execute(command);
    console.log(command);
    // enable jupyter keyboard shortcuts again
    Jupyter.keyboard_manager.enable()
};