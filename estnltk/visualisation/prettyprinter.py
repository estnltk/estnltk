from IPython.display import display_html
from estnltk import Layer


def decompose_to_elementary_spans (layer,text):
    spanindexes = []
    attributes = layer.attributes    
    
    for s in layer.spans:
        spanstart = s.start
        spanend = s.end
        spanindexes.append(spanstart)
        spanindexes.append(spanend)
    
    html_spans=[]
    
    spanindexes = sorted(set(spanindexes))
    
    for i in range(len(spanindexes)-1):
        span_text = text[spanindexes[i]:spanindexes[i+1]]
        html_spans.append(span_text)
            
    printable=[]
    textspans=[]
    texts=[]
    
    for i, html_span in enumerate(html_spans):
        printable.append([])
        textspans.append([])
        texts.append([])
        for s in layer.spans:
            if html_span[0] in range(s.start,s.end):
                textspans[i].append([s.start,s.end])
                texts[i].append(s.text)
                for attribute in attributes:
                    printable[i].append(getattr(s,attribute))
                    
    for i, html_span in enumerate(html_spans):
        span_list=[]
        span_start = html_span[0]
        span_end = html_span[1]
        for s in layer.spans:
            if span_start in range (s.start,s.end):
                span_list.append(s)
        html_span.append(span_list)

    assert len(html_spans)==len(printable)
    
    for i, attributes in enumerate(printable):
        if len(attributes)==0:
            printable.remove(attributes)
            html_spans.remove(html_spans[i])
            textspans.remove(textspans[i])
            texts.remove(texts[i])

    return html_spans

def decorate(html_spans):
    spans = []
    
    for i in range(len(html_spans)):
        coordinates = []
        coordinates.append(html_spans[i][0])
        coordinates.append(html_spans[i][1])
        spans.append(coordinates)
        
    #contents_without_attributes = fun_output[1]
    #spans_in_html_spans = fun_output[2]
    #texts = fun_output[3]
    #attributes = getattr(text,layer).attributes
    #contents = []
    
    #for content in contents_without_attributes:
    #    new_content=[]
    #    for i in range(len(content)):
    #        new_content.append(attributes[i%len(attributes)])
    #        new_content.append(content[i])
    #    contents.append(new_content)
    
    #tabledata=[]
    
    #for content in contents_without_attributes:
    #    for i in range(len(attributes)):
    #        tabledata.append(attributes[i])
    #        tabledata.append(content[i])
    
    texts = []
    
    for span in html_spans:
        content=[]
        span_info = span[2]
        for i in range(len(span_info)):
            content.append(span_info[i].text)
        texts.append(content)
    
    fragments = []
    last_end = 0
    style='background-color:blue;'
    
    for i, (s, e) in enumerate(spans):
        fragments.append(text[last_end:s])
        fragments.append('<span class="span')
        if len(html_spans[i][2])>1:
            fragments.append(" overlapping-span")
        fragments.append('"; onclick="visualise{0}(')
        fragments.append(str(html_spans[i][2]).replace('"','').replace('{','(').replace('}',')').replace(':',','))
        fragments.append(',')
        fragments.append(str(i))
        fragments.append(',')
        fragments.append("["+str(html_spans[i][0])+","+str(html_spans[i][1])+"]")
        fragments.append(", this,")
        fragments.append(str(texts[i]))
        fragments.append(')"; indexes="')
        fragments.append("["+str(html_spans[i][0])+","+str(html_spans[i][1])+"]")
        fragments.append('"; span_exists = ""; ')
        fragments.append('style = "')
        fragments.append(style)
        fragments.append('">')
        fragments.append(text[s:e])
        fragments.append('</span>')
        last_end = e
    fragments.append(text[last_end:])
    return ''.join(fragments)

def add_spans(text,layer):
    t = text.text
    fun_output = decompose_to_elementary_spans(text,layer)
    spans = fun_output[0]

    contents_without_attributes = fun_output[1]
    spans_in_html_spans = fun_output[2]
    texts = fun_output[3]
    attributes = getattr(text,layer).attributes
    contents = []
    
    for content in contents_without_attributes:
        new_content=[]
        for i in range(len(content)):
            new_content.append(attributes[i%len(attributes)])
            new_content.append(content[i])
        contents.append(new_content)
    
    tabledata=[]
    
    for content in contents_without_attributes:
        for i in range(len(attributes)):
            tabledata.append(attributes[i])
            tabledata.append(content[i])
    
    fragments = []
    last_end = 0
    
    for i, (s, e) in enumerate(spans):
        fragments.append(t[last_end:s])
        fragments.append('<span class="span')
        if len(contents[i])/2>len(attributes):
            fragments.append(" overlapping-span")
        fragments.append('"; onclick="visualise{0}(')
        fragments.append(str(contents[i]).replace('"',''))
        fragments.append(',')
        fragments.append(str(i))
        fragments.append(',')
        fragments.append(str(spans_in_html_spans[i]))
        fragments.append(", this,")
        fragments.append(str(texts[i]))
        fragments.append(')"; indexes="')
        fragments.append(str(spans_in_html_spans[i]))
        fragments.append('"; span_exists = "";>')
        fragments.append(t[s:e])
        fragments.append('</span>')
        last_end = e
    fragments.append(t[last_end:])
    return ''.join(fragments)

css_file = open("prettyprinter.css","r")
css = css_file.read()
js_file = open("prettyprinter.js","r")
js = js_file.read()

t = '''
<html>
<style>
{2}
</style>
<body>

<p class="maintext{0}">{1}<br><br><br></p>

<script>
{3}
</script>

</body>
</html>
'''


class EstnltkDisplay:
    """Fancy display for estnltk objects."""

    _text_id = 0

    def layer_to_html(self, text, layer, text_id):
        layer = getattr(text, layer.name)
        result = decorate(decompose_to_elementary_spans(layer), text.text)
        print(result)
        result = result.format(text_id).replace("\n","<br>")
        return t.format(text_id,result,css,js).format(text_id)

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
