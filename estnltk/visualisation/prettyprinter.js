function intermediate_table{0}(indexes,position,data,position_top,html_span,index,texts) {{
    let spantable = document.createElement("div");
    spantable.setAttribute("id","table"+{0}+index);
    spantable.classList.add("tables");
    spantable.innerHTML = span_table{0}(indexes,position,data,texts);
    let textNode{0} = document.getElementById("maintext{0}");
    textNode{0}.appendChild(spantable);
    let elements = document.getElementsByClassName("tables");
    elements[elements.length-1].style.left = position+"px";
    let textheight = position_top + 20;
    elements[elements.length-1].style.top = textheight+"px";
    let rows = elements[elements.length-1].children[0].rows;
    elements[elements.length-1].addEventListener("click", function(){{
        this.parentElement.removeChild(this);
        let elements = document.getElementsByClassName("tables");
        elements[elements.length-1].addEventListener("click", function(){{
            let spans = document.getElementsByClassName("span");
            for (var span of spans) {{
                span.classList.contains("overlapping-span") ? span.style.backgroundColor = "red" : span.style.backgroundColor = "yellow";
            }}
        }})
    }})
    var info_length = data.length/rows.length;
    for (let i = 0; i < rows.length; i++)  {{
        rows[i].addEventListener("click", function(){{
            let table_data = data.slice(i*info_length,i*info_length+info_length);
            table{0}(table_data,position,position_top,html_span,index);
        }})
    }}
}}

function span_table{0}(indexes,position,data,texts) {{
    var content = "<table>";
    for (let i = 0; i < texts.length; i++) {{
        content += "<tr><td onmouseover='highlight_span(";
        content += indexes[i];
        content += ")' onmouseout = 'highlight_span("
        content += indexes[i];
        content += ")'  >"
        content += texts[i];
        content += "</td></tr>";
    }}
    content += "</table>";

    return content;
}}

function highlight_span(start_index,end_index) {{
    let spans = document.getElementsByClassName("span");
    index = start_index+", "+end_index;
    for (var span of spans) {{
        if (span.getAttribute("indexes").includes(index)){{
            if (span.style.backgroundColor != "green"){{
                span.style.backgroundColor = "green";
            }} else {{
                span.classList.contains("overlapping-span") ? span.style.backgroundColor = "red" : span.style.backgroundColor = "yellow";
            }}
        }}
    }}
}}

function table_content(info) {{
    var content = "<table>";
    for (var i = 0; i < info.length; i+=2) {{
        var seperated_info = info[i+1];
        content += "<tr><td>" + info[i]+"</td><td>";
        for (var j = 0; j < seperated_info.length; j+=1) {{
            content += "</td><td>" + seperated_info[j];
        }}
        content += "</td></tr>";
    }}
    content += "</table>";
    
    return content;
}}

function table{0}(data, position,position_top,html_span,index) {{
    let tableplace = document.createElement("DIV");
    tableplace.setAttribute("id","table"+{0}+index);
    tableplace.classList.add("tables");
    tableplace.innerHTML = table_content(data);
    let textNode{0} = document.getElementById("maintext{0}");
    textNode{0}.appendChild(tableplace);
    let tables = document.getElementsByClassName("tables");
    tables[tables.length-1].style.left = position+"px";
    let textheight = position_top + 20;
    tables[tables.length-1].style.top = textheight+"px";
    tableplace.onclick = function () {{
        this.parentElement.removeChild(this);
        html_span.setAttribute("span_exists", "");
    }}
}}

function visualise{0}(data,index,indexes,span,texts){{
    var span_already_exists = span.getAttribute("span_exists");
    var span_position = span.getBoundingClientRect();
    var classList = span.classList;
    let textposition = maintext{0}.getBoundingClientRect().left;
    let textposition_top = maintext{0}.getBoundingClientRect().top;
    let spans = document.getElementsByClassName("span");
    let position = span_position.left-textposition;
    let position_top = span_position.top-textposition_top;
    if (!span_already_exists){{
        if(classList.contains("overlapping-span")){{
                intermediate_table{0}(indexes,position,data,position_top,span,index,texts);
                span.setAttribute("span_exists", true);
            }} else {{
                table{0}(data,position,position_top,span,index);
                span.setAttribute("span_exists", true);
            }}
    }} else {{
        let deletable = document.getElementById("table{0}"+index);
        deletable.parentElement.removeChild(deletable);
        span.classList.contains("overlapping-span") ? span.style.backgroundColor = "red" : span.style.backgroundColor = "yellow";
        span.setAttribute("span_exists", "");
    }}
}}