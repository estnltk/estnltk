from IPython.display import display_html
from estnltk import Layer


def find_spans (text, layer_name):
    layer = getattr(text, layer_name)
    spancount = len(layer.spans)
    spanindexes = []
    text=text.text
    attributes = layer.attributes    
    
    for s in layer.spans:
        spanstart = s.start
        spanend = s.end
        spanindexes.append(spanstart)
        spanindexes.append(spanend)
    
    html_spans=[]
    
    spanindexes = sorted(set(spanindexes))
    
    for i in range(len(spanindexes)-1):
        html_spans.append([spanindexes[i],spanindexes[i+1]])
            
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

    assert len(html_spans)==len(printable)
    
    for i, attributes in enumerate(printable):
        if len(attributes)==0:
            printable.remove(attributes)
            html_spans.remove(html_spans[i])
            textspans.remove(textspans[i])
            texts.remove(texts[i])

    return html_spans,printable,textspans,texts


def add_spans(text,layer):
    t = text.text
    fun_output = find_spans(text,layer)
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
        result = add_spans(text, layer.name)
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
