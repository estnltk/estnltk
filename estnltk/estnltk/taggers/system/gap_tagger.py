from typing import Sequence

from collections import defaultdict

from estnltk import Layer
from estnltk.taggers import Tagger

def default_decorator(gap):
    return {}

class GapTagger(Tagger):
    """ Tags gaps: text regions that are not covered by any span of given input layers.
   
    GapTagger has two working modes:
    *) Default mode: look for sequences of consecutive characters
       not covered by input layers;
    *) EnvelopingGap mode: look for sequences of enveloped layer's 
       spans not enveloped by input (enveloping) layers;
    Use enveloping_mode=True to initialize GapTagger in 
    EnvelopingGap mode, otherwise the default mode is used.
    
    Default mode
    =============
    In the default mode, a gap is a maximal span of consecutive 
    characters (including whitespace) that are not covered by any 
    span of any input layer. 
    A character is covered by a span if it lays between the start 
    and end of that span. 
    This means that gaps between spans of enveloping spans are not 
    considered.
    
    Example:
    <pre>
     text:                  'Üks kaks kolm neli viis kuus seitse.'
     layer_1_spans:             'kaks'kolm'         'kuus'      
     layer_2_spans:             'kaks'kolm neli'               '.'
     gaps:                  'Üks '  ' '       ' viis '  ' seitse'
    </pre>
    
    Gaps can be trimmed by trim function and annotated by decorator 
    function.
    The decorator function takes string of the gap as an input and 
    should return corresponding annotation as a dictionary.
    The trim function takes string of the gap as an input and is 
    expected to return a trimmed variant of the input (characters 
    can be removed from left and right side of the string). If the 
    trim function returns an empty string, the gap will be discarded.
    
    EnvelopingGap mode
    ==================
    In the EnvelopingGap mode, a gap is a maximal SpanList of consecutive 
    spans of the enveloped layer that are not enveloped by any input layer. 
    All input layers must be enveloping the same layer. The resulting gaps 
    layer of these layers is an unambiguous enveloping layer. 
    
    Example:
    <pre>
     text:                  'Üks kaks kolm neli viis kuus seitse .'
     words_layer:           'Üks'kaks'kolm'neli'viis'kuus'seitse'.'
     env_layer_1_spans:     'Üks'kaks'    'neli'                   
     env_layer_2_spans:                   'neli'viis'              
     gaps:                           'kolm'         'kuus'seitse'.'
    </pre>
    In the example above, layers 'env_layer_1' and 'env_layer_1' are 
    enveloping the 'words' layer. So, GapTagger finds out, which spans 
    of the 'words' layer are not enveloped by 'env_layer_1' and 
    'env_layer_1'.

    The resulting spans can be annotated with a decorator function. 
    The decorator function takes spans of the gap as an input and 
    should return corresponding annotation as a dictionary.
    
    If the decorator function is not specified, default_decorator is 
    used, which returns {} on any input. This means that each 
    annotation obtains default values of the layer (None values, if 
    defaults are not set).
    """
    conf_param = ['decorator', 'trim', 'ambiguous',
                  'enveloping_mode', 'enveloped_layer',
                  '_layers_with_gaps']

    def __init__(self,
                 output_layer: str,
                 input_layers: Sequence[str],
                 trim: callable=None,
                 output_attributes: Sequence=(),
                 decorator: callable=None,
                 ambiguous:bool=False,
                 enveloping_mode:bool=False,
                 enveloped_layer:str=None):
        if not enveloping_mode:
            # Default mode: look for sequences of consecutive characters
            # not covered by input layers
            self.enveloping_mode = False
            self.input_layers = input_layers
            self.output_layer = output_layer
            self.trim = trim
            assert bool(output_attributes) == bool(decorator),\
                'decorator without attributes or attributes without decorator'
            self.output_attributes = tuple(output_attributes)
            self.decorator = decorator
            self.ambiguous = ambiguous
            if enveloped_layer is not None:
                raise ValueError( ('Cannot set enveloped_layer={!r} if enveloping=False.'+\
                                   '').format(enveloped_layer))
            self.enveloped_layer = None
            self._layers_with_gaps = None
        else:
            # EnvelopingGap mode: look for sequences of enveloped layer's 
            # spans not enveloped by input (enveloping) layers
            self.enveloping_mode = True
            if enveloped_layer is None:
                raise ValueError( 'Unexpected value enveloped_layer=None. Please '+\
                                  'provide the named of the enveloped layer if you '+\
                                  'want to use the EnvelopingGap mode.' )
            self.enveloped_layer = enveloped_layer
            self._layers_with_gaps = [l for l in input_layers if l != enveloped_layer]
            self.input_layers = list(self._layers_with_gaps) + [enveloped_layer]
            self.output_layer = output_layer
            assert bool(output_attributes) == bool(decorator),\
                'decorator without attributes or attributes without decorator'
            self.output_attributes = tuple(output_attributes)
            self.decorator = decorator or default_decorator
            if trim is not None:
                raise ValueError('Cannot set trim function in the EnvelopingGap mode.')
            self.trim = None
            if ambiguous:
                raise ValueError('Cannot set ambiguous=True in the EnvelopingGap mode.')
            self.ambiguous = False

    def _make_layer_template(self):
        return Layer( name=self.output_layer,
                      attributes=self.output_attributes,
                      text_object=None,
                      parent=None,
                      enveloping=self.enveloped_layer,
                      ambiguous=self.ambiguous )

    def _make_layer(self, text, layers, status):
        new_layer = self._make_layer_template()
        new_layer.text_object = text
        if not self.enveloping_mode:
            # Default mode: look for sequences of consecutive characters
            # not covered by input layers
            raw_text = text.text
            layers = [layers[layer] for layer in self.input_layers]
            for start, end in find_gaps(layers, len(raw_text)):
                assert start < end, (start, end)
                if self.trim:
                    t = self.trim(raw_text[start:end])
                    start_new = raw_text.find(t, start)
                    if start_new < start:
                        raise ValueError('misbehaving trim function: "{}"->"{}"'.format(raw_text[start:end], t))
                    start = start_new
                    end = start + len(t)
                if start < end:
                    decorations = {}
                    if self.decorator:
                        decorations = self.decorator(raw_text[start:end])
                    new_layer.add_annotation((start, end), **decorations)
        else:
            # EnvelopingGap mode: look for sequences of enveloped layer's 
            # spans not enveloped by input (enveloping) layers
            layers_with_gaps = [layers[name] for name in self._layers_with_gaps]
            for layer in layers_with_gaps:
                if layer.enveloping != self.enveloped_layer:
                    raise ValueError(('Unexpected enveloping layer: input layer {!r} should be enveloping {!r},'+\
                                      ' not {!r}').format(layer.name, self.enveloped_layer, layer.enveloping))
            enveloped = layers[self.enveloped_layer]
            decorator = self.decorator
            for gap in find_enveloping_gaps(layers_with_gaps, enveloped):
                new_layer.add_annotation( gap, **decorator(gap) )
        return new_layer


def find_gaps(layers, text_length):
    if text_length == 0:
        return
    cover_change = defaultdict(int)
    for layer in layers:
        for span in layer:
            cover_change[span.start] += 1
            cover_change[span.end] -= 1
    if not cover_change:
        yield (0, text_length)
        return
    indexes = sorted(cover_change)
    if indexes[0] > 0:
        yield (0, indexes[0])
    cover = 0
    for i, j in zip(indexes, indexes[1:]):
        cover += cover_change[i]
        assert cover >= 0
        if not cover:
            yield (i, j)
    assert not cover + cover_change[indexes[-1]]
    if indexes[-1] < text_length:
        yield (indexes[-1], text_length)


def find_enveloping_gaps(layers, enveloped):
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

