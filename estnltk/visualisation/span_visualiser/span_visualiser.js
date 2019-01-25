for (var element of document.getElementsByClassName("overlapping-span")) {
    element.addEventListener("click",function() {show_conflicting_spans(element);})
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
    console.log(span_element.parentElement.parentElement.getBoundingClientRect())
    console.log(spantable.getBoundingClientRect())
    spantable.style.left = span_element.getBoundingClientRect().left-span_element.parentElement.parentElement.parentElement.getBoundingClientRect().left + 'px'
    spantable.style.top = span_element.getBoundingClientRect().top-spantable.getBoundingClientRect().top+span_element.parentElement.parentElement.parentElement.getBoundingClientRect().height+ 'px'
    spantable.parentElement.style.height = spantable.parentElement.style.height+"100px"

    // remove the table when clicked on again
    spantable.addEventListener('click', function () {
        let element = this.parentElement
        element.removeChild(this)  //deleting the table
    })
}
