function intermediate_table{0} (indexes, position, data, position_top, html_span, index, texts) {{
  let spantable = document.createElement('div')
  spantable.setAttribute('id', 'table' + {0} + index)
  spantable.classList.add('tables')
  spantable.innerHTML = span_table{0}(indexes, data, texts)
  let textNode{0} = document.getElementsByClassName('maintext{0}')[0]
  textNode{0}.appendChild(spantable)
  let element = document.getElementById('table' + {0} + index)
  element.style.left = position + 'px'
  let textheight = position_top + 20
  element.style.top = textheight + 'px'
  let rows = element.children[0].rows
  element.addEventListener('click', function () {{
    this.parentElement.removeChild(this)
    let element = document.getElementById('newtable' + {0} + index)
    element.addEventListener('click', function () {{
      let spans = document.getElementsByClassName('span')
      for (var span of spans) {{
        span.classList.contains('overlapping-span') ? span.style.backgroundColor = 'red' : span.style.backgroundColor = 'yellow'
      }}
    }})
  }})
  var info_length = data.length / rows.length
  for (let i = 0; i < rows.length; i++) {{
    rows[i].addEventListener('click', function () {{
      let table_data = data.slice(i * info_length, i * info_length + info_length)
      table{0}(table_data, position, position_top, html_span, index)
    }})
  }}
}}

function span_table{0} (indexes, data, texts) {{
  var content = '<table>'
  for (let i = 0; i < texts.length; i++) {{
    content += "<tr><td onmouseover='highlight_span("
    content += indexes[i]
    content += ")' onmouseout = 'highlight_span("
    content += indexes[i]
    content += ")'  >"
    content += texts[i]
    content += '</td></tr>'
  }}
  content += '</table>'

  return content
}}

function highlight_span (start_index, end_index) {{
  let spans = document.getElementsByClassName('span')
  let index = start_index + ', ' + end_index
  for (var span of spans) {{
    if (span.getAttribute('indexes').includes(index)) {{
      if (span.style.backgroundColor !== 'green') {{
        span.style.backgroundColor = 'green'
      }} else {{
        span.classList.contains('overlapping-span') ? span.style.backgroundColor = 'red' : span.style.backgroundColor = 'yellow'
      }}
    }}
  }}
}}

function table_content (info) {{
  var content = '<table>'
  for (var i = 0; i < info.length; i += 2) {{
    var seperated_info = info[i + 1]
    content += '<tr><td>' + info[i] + '</td><td>'
    for (var j = 0; j < seperated_info.length; j += 1) {{
      content += '</td><td>' + seperated_info[j]
    }}
    content += '</td></tr>'
  }}
  content += '</table>'

  return content
}}

function table{0} (data, position, position_top, html_span, index) {{
  let tableplace = document.createElement('DIV')
  tableplace.setAttribute('id', 'newtable' + {0} + index)
  tableplace.classList.add('tables')
  tableplace.innerHTML = table_content(data)
  let textNode{0} = document.getElementsByClassName('maintext{0}')[0]
  textNode{0}.appendChild(tableplace)
  let new_table = document.getElementById('newtable' + {0} + index)
  new_table.style.left = position + 'px'
  let textheight = position_top + 20
  new_table.style.top = textheight + 'px'
  tableplace.onclick = function () {{
    this.parentElement.removeChild(this)
    html_span.setAttribute('span_exists', '')
  }}
}}

function visualise (data, index, indexes, span, texts) {{
  var span_already_exists = false;
  var span_position = span.getBoundingClientRect();
  var classList = span.classList;
  //let mainText = document.getElementsByClassName('maintext{0}')[0];
  //let textposition = mainText.getBoundingClientRect().left;
  //let textposition_top = mainText.getBoundingClientRect().top;
  //let position = span_position.left - textposition;
  //let position_top = span_position.top - textposition_top;
  if (!span_already_exists) {{
    if (classList.contains('overlapping-span')) {{
      intermediate_table{0}(indexes, position, data, position_top, span, index, texts)
      span.setAttribute('span_exists', true)
    }} else {{
      table{0}(data, position, position_top, span, index)
      span.setAttribute('span_exists', true)
    }}
  }} else {{
    let deletable = document.getElementById('table{0}' + index)
    deletable.parentElement.removeChild(deletable)
    span.classList.contains('overlapping-span') ? span.style.backgroundColor = 'red' : span.style.backgroundColor = 'yellow'
    span.setAttribute('span_exists', '')
  }}
}}
