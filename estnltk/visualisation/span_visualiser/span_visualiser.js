var elements = document.getElementsByClassName("overlapping-span")
for (let i = 0; i < elements.length; i++){
    elements.item(i).addEventListener("click",function() {show_conflicting_spans(elements.item(i));})}

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

    // Increase the size of the cell so the tables would fit
    spantable.parentElement.style.height = Math.max(Number(spantable.parentElement.style.height.substring(0,spantable.parentElement.style.height.length-2)),span_element.offsetTop+90)+ 'px'
    // Position the table directly below the corresponding text
    spantable.style.left = span_element.getBoundingClientRect().left-spantable.parentElement.parentElement.getBoundingClientRect().left + 'px'
    spantable.style.top = span_element.getBoundingClientRect().top-spantable.parentElement.parentElement.getBoundingClientRect().top+20+ 'px'

    // Remove the table when clicked on again
    spantable.addEventListener('click', function () {
        let element = this.parentElement
        element.removeChild(this)
    })
}
