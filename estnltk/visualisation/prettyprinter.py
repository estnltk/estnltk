from IPython.display import display_html
from estnltk import Layer


def find_spans(text, layer_name):
    layer = getattr(text, layer_name)
    # spancount = len(layer.spans)
    spanindexes = []
    # text = text.text
    attributes = layer.attributes

    for s in layer.spans:
        spanstart = s.start
        spanend = s.end
        spanindexes.append(spanstart)
        spanindexes.append(spanend)

    html_spans = []

    spanindexes = sorted(set(spanindexes))

    for i in range(len(spanindexes) - 1):
        html_spans.append([spanindexes[i], spanindexes[i + 1]])

    printable = []
    textspans = []

    for i, html_span in enumerate(html_spans):
        printable.append([])
        textspans.append([])
        for s in layer.spans:
            if html_span[0] in range(s.start, s.end):
                textspans[i].append([s.start, s.end])
                for attribute in attributes:
                    printable[i].append(getattr(s, attribute))

    assert len(html_spans) == len(printable)

    for i, attributes in enumerate(printable):
        if len(attributes) == 0:
            printable.remove(attributes)
            html_spans.remove(html_spans[i])
            textspans.remove(textspans[i])

    return html_spans, printable, textspans


def add_spans(text, layer):
    t = text.text
    fun_output = find_spans(text, layer)
    spans = fun_output[0]

    contents_without_attributes = fun_output[1]
    spans_in_html_spans = fun_output[2]
    attributes = getattr(text, layer).attributes
    contents = []

    for content in contents_without_attributes:
        new_content = []
        for i in range(len(content)):
            new_content.append(attributes[i % len(attributes)])
            new_content.append(content[i])
        contents.append(new_content)

    tabledata = []

    for content in contents_without_attributes:
        for i in range(len(attributes)):
            tabledata.append(attributes[i])
            tabledata.append(content[i])

    fragments = []
    last_end = 0

    for i, (s, e) in enumerate(spans):
        fragments.append(t[last_end:s])
        fragments.append('<span class="span')
        if len(contents[i]) / 2 > len(attributes):
            fragments.append(" overlapping-span")
        fragments.append('"; onclick="visualise{0}(')
        fragments.append(str(contents[i]).replace('"', ''))
        fragments.append(',')
        fragments.append(str(i))
        fragments.append(',this.classList,')
        fragments.append(str(spans_in_html_spans[i]))
        fragments.append(',this.getBoundingClientRect())"; indexes="')
        fragments.append(str(spans_in_html_spans[i]))
        fragments.append('">')
        fragments.append(t[s:e])
        fragments.append('</span>')
        last_end = e
    fragments.append(t[last_end:])
    return ''.join(fragments)


t = '''
<html>
<style>

.span {{
    background-color: yellow;
}}

.overlapping-span {{
    background-color: red;
}}

.spanline {{
    background-color: blue;
    position: relative;
    height: 3px;
    margin-left: 0px;
}}

.tables {{
    position: absolute;
    width: fit-content;
    width: -moz-fit-content;
}}

#maintext{0} {{
    position: relative;
}}

.rendered_html tbody tr:nth-child(even) {{
    background-color: lightgray;
}}

.rendered_html tbody tr:nth-child(odd) {{
    background-color: beige;
}}

.rendered_html tbody tr:hover {{
    background-color: ivory;
}}

</style>
<body>

<p id="maintext{0}">{1}<br><br><br></p>

<script>

function intermediate_table{0}(indexes,position,data,position_top) {{
    let spantable = document.createElement("div");
    let tables = document.getElementsByClassName("tables");
    for (var table of tables) {{
        table.parentElement.removeChild(table);
    }}
    spantable.classList.add("tables");
    spantable.innerHTML = span_table{0}(indexes,position,data);
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
            table{0}(table_data,position,position_top);
        }})
    }}
}}

function span_table{0}(indexes,position,data) {{
    var content = "<table>";
    for (var index of indexes) {{
        content += "<tr><td onmouseover='highlight_span("
        content += index;
        content += ")' onmouseout = 'highlight_span("
        content += index;
        content += ")'  >span</td></tr>"
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

function table{0}(data, position,position_top) {{
    let tableplace = document.createElement("DIV");
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
    }}
}}

function visualise{0}(data,index,classList,indexes,span_position){{
    let textposition = maintext{0}.getBoundingClientRect().left;
    let textposition_top = maintext{0}.getBoundingClientRect().top;
    let spans = document.getElementsByClassName("span");
    let position = span_position.left-textposition;
    let position_top = span_position.top-textposition_top;
    if(classList.contains("overlapping-span")){{
        intermediate_table{0}(indexes,position,data,position_top)
    }} else {{
        table{0}(data,position,position_top);
    }}
}}

</script>

</body>
</html>
'''


class EstnltkDisplay:
    """Fancy display for estnltk objects."""

    _text_id = 0

    def layer_to_html(self, text, layer, text_id):
        result = add_spans(text, layer.name)
        result = result.format(text_id).replace("\n","<br>")
        return t.format(text_id,result)

    def display_layer(self, text, layer):
        self.__class__._text_id += 1
        html = self.layer_to_html(text, layer, self.__class__._text_id)
        display_html(html, raw=True)

    def __call__(self, obj):
        if isinstance(obj, Layer):
            self.display_layer(obj.text_object, obj)
        else:
            raise NotImplementedError('bla bla')


estnltk_display = EstnltkDisplay()
