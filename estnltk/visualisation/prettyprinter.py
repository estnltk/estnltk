from IPython.display import display_html
from estnltk import Layer

def decompose_to_elementary_spans (layer,text):
    spanindexes = []
    
    for s in layer.spans:
        spanstart = s.start
        spanend = s.end
        spanindexes.append(spanstart)
        spanindexes.append(spanend)
    
    html_spans=[]
    
    spanindexes = sorted(set(spanindexes))
    
    if spanindexes[0]!=0:
        spanindexes.insert(0,0)
    if spanindexes[-1]!=len(text):
        spanindexes.append(len(text))
    
    for i in range(len(spanindexes)-1):
        span_text = text[spanindexes[i]:spanindexes[i+1]]
        html_spans.append([spanindexes[i],spanindexes[i+1],span_text])
    
    for i, html_span in enumerate(html_spans):
        span_list=[]
        span_start = html_span[0]
        span_end = html_span[1]
        for s in layer.spans:
            if span_start in range (s.start,s.end):
                span_list.append(s)
        html_span.append(span_list)
        del html_span[0:2]

    return html_spans


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
