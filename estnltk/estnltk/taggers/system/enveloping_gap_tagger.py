from typing import Sequence

from estnltk import Layer
from estnltk.taggers import Tagger


def default_decorator(gap):
    return {}


class EnvelopingGapTagger(Tagger):
    """ Tags gaps: all spans that are not covered by any span of any enveloping input layer.
    Here, a gap is a maximal SpanList of consequtive spans of enveloped 
    layer that are not enveloped by any input layer. All input layers 
    must be enveloping the same layer. The resulting gaps layer of these 
    layers is an unambiguous enveloping layer. 
    
    Example:
    <pre>
     text:                  'Üks kaks kolm neli viis kuus seitse .'
     words_layer:           'Üks'kaks'kolm'neli'viis'kuus'seitse'.'
     env_layer_1_spans:     'Üks'kaks'    'neli'                   
     env_layer_2_spans:                   'neli'viis'              
     gaps:                           'kolm'         'kuus'seitse'.'
    </pre>
    In the example above, layers 'env_layer_1' and 'env_layer_1' are 
    enveloping the 'words' layer. So, EnvelopingGapTagger finds out, 
    which spans of the 'words' layer are not enveloped by 'env_layer_1' 
    and 'env_layer_1'.

    The resulting spans can be annotated with a decorator function. 
    The decorator function takes spans of the gap as an input and 
    should return corresponding annotation as a dictionary.
    
    If the decorator function is not specified, default_decorator is 
    used, which returns {} on any input. This means that each 
    annotation obtains default values of the layer (None values, if 
    defaults are not set).
    """
    conf_param = ['decorator', 'layers_with_gaps', 'enveloped_layer']

    def __init__(self,
                 output_layer: str,
                 layers_with_gaps: Sequence[str],
                 enveloped_layer: str,
                 output_attributes: Sequence=(),
                 decorator: callable=None):
        self.layers_with_gaps = layers_with_gaps
        self.enveloped_layer = enveloped_layer
        self.input_layers = list(layers_with_gaps) + [enveloped_layer]
        self.output_layer = output_layer
        assert bool(output_attributes) == bool(decorator),\
            'decorator without attributes or attributes without decorator'
        self.output_attributes = tuple(output_attributes)
        self.decorator = decorator or default_decorator

    def _make_layer_template(self):
        return Layer( name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=None,
                      parent=None,
                      enveloping=self.enveloped_layer,
                      ambiguous=False )

    def _make_layer(self, text, layers, status):
        layers_with_gaps = [layers[name] for name in self.layers_with_gaps]
        assert all(layer.enveloping == self.enveloped_layer for layer in layers_with_gaps)
        enveloped = layers[self.enveloped_layer]
        layer = self._make_layer_template()
        layer.text_object = text
        decorator = self.decorator
        for gap in enveloping_gaps(layers_with_gaps, enveloped):
            layer.add_annotation(gap, **decorator(gap))
        return layer


def enveloping_gaps(layers, enveloped):
    cover = {bs for layer in layers for span in layer for bs in span.base_span}

    spans = iter(enveloped)
    s = next(spans)
    while s:
        while s.base_span in cover:
            s = next(spans)
        gap = []
        while s.base_span not in cover:
            gap.append(s)
            try:
                s = next(spans)
            except StopIteration:
                s = None
                break
        yield gap
