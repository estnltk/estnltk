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

let start;
document.addEventListener('click', function (e) {
    Jupyter.keyboard_manager.disable();
    if (start != undefined) {
        start.style.backgroundColor = null;
        start.style.color = null;
    }
    let startid = e.target.id;
    start = document.getElementById(startid);
    start.focus();
    start.style.backgroundColor = 'pink';
    start.style.color = 'white';
    document.onkeydown = checkKey;
}, false);

function move(sibling) {
    if (sibling != null) {
        start.focus();
        start.style.backgroundColor = '';
        start.style.color = '';
        sibling.focus();
        sibling.style.backgroundColor = 'pink';
        sibling.style.color = 'white';
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
        let index = Array.from(start.parentElement.parentElement.children).indexOf(start.parentElement);
        //console.log(start);
        //console.log(start.parentElement.parentElement.children);
        //console.log(index);
        let sibling = start.parentElement.parentElement.parentElement.parentElement.previousElementSibling.firstElementChild.firstElementChild.children.item(index).firstElementChild;
        move(sibling);
    } else if (e.keyCode == '39') {
        // right arrow
        e.preventDefault();
        let index = Array.from(start.parentElement.parentElement.children).indexOf(start.parentElement);
        let sibling = start.parentElement.parentElement.parentElement.parentElement.nextElementSibling.firstElementChild.firstElementChild.children.item(index).firstElementChild;
        move(sibling);
    } else if (e.keyCode == '32') {
        // Space key for opening dropdown
        let sibling = start.firstElementChild;
        move(sibling);
    } else if (e.keyCode == '16') {
        //Shift for going back (for leaving dropdown)
        console.log(start);
        let sibling = start.parentElement;
        move(sibling);
        e.preventDefault();
        //e.preventDefault();
    } else if (e.keyCode == '13') {
        // Enter key for dropdown choices
        console.log(start.tagName);
        console.log(start.id);
        //console.log(start.options[start.selectedIndex]);
        //console.log(start.id.innerHTML);
        //let optionid = start.id;
        let sibling = start.firstElementChild;
        get_select_value(start.id);
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

function export_data() {
    //TODO
}
