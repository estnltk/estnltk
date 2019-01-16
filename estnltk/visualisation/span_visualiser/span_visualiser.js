var elements = document.getElementsByClassName("overlapping-span")
for (let i = 0; i < elements.length; i++){
    elements.item(i).addEventListener("click",function() {show_conflicting_spans(elements.item(i));})
}

function show_conflicting_spans(span_element) {
    let spantable = document.createElement('div')
    spantable.classList.add('tables')

    // Prepare the contents of the span table
    data = span_element.getAttribute("span_info")
    data = data.split(",")
    var spancontent = '<table>'
    for (let row of data) {
        spancontent+='<tr><td>'
        spancontent+=row
        spancontent+='</td></tr>'
    }
    spancontent += '</table>'
    spantable.innerHTML = spancontent
    span_element.parentElement.appendChild(spantable)

    //Position the table directly below the corresponding text
    spantable.style.left = "0px";
    spantable.style.top = "0px";
    spantable.style.left = span_element.getBoundingClientRect().left-spantable.getBoundingClientRect().left + 'px'
    spantable.style.top = span_element.getBoundingClientRect().top-spantable.getBoundingClientRect().top+span_element.getBoundingClientRect().height+ 'px'
    spantable.parentElement.style.height = spantable.parentElement.style.height+"100px"

    // remove the table when clicked on again
    spantable.addEventListener('click', function () {
        let element = this.parentElement
        element.removeChild(this)  //deleting the table
    })
}

function span_table (span) {{
    data = span.getAttribute("span_info")
    data = data.split(",")
    var content = '<table>'
    for (let row of data) {
        content+='<tr><td>'
        content+=row
        content+='</td></tr>'
    }
    content += '</table>'

    return content
}}