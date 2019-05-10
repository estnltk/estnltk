from collections import defaultdict
from estnltk import Tagger, Layer, EnvelopingSpan


class SyntaxErrorCountTagger(Tagger):
    """Tag sliding las scores"""

    conf_param = ['window']

    def __init__(self, layer_a: str, layer_b: str, output_layer: str = 'error_counts', window: int = 3):
        assert window > 0
        self.input_layers = [layer_a, layer_b]
        self.output_layer = output_layer
        self.output_attributes = ['deprel_sequence',  'both_errors', 'link_errors', 'label_errors',]
        self.window = window

    def _make_layer(self, text, layers, status):
        layer_a = layers[self.input_layers[0]]
        layer_b = layers[self.input_layers[1]]

        aggregate_deprels = defaultdict(list)

        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                      enveloping=layer_a.name)

        for spans, deprels, LASes, UASes, LAs in by_sentences(layer_a, layer_b):
            len_s = len(spans)
            window = min(len_s, self.window)

            for start in range(1 - window, len_s):
                end = start + window
                start = max(0, start)
                end = min(len_s, end)

                deprel_sequence = tuple(deprels[start:end])
                LAS = sum(LASes[start:end]) #/ (end - start)
                UAS = sum(UASes[start:end]) #/ (end - start)
                LA = sum(LAs[start:end]) #/ (end - start)
                aggregate_deprels[deprel_sequence].append((LAS, UAS, LA))

                span = EnvelopingSpan(spans=spans[start:end],
                                      layer=layer,
                                      attributes={'deprel_sequence': deprel_sequence,
                                                  'both_errors': LAS,
                                                  'link_errors': UAS,
                                                  'label_errors': LA})
                layer.add_span(span)

        layer.meta['aggregate_deprel_sequences'] = dict(aggregate_deprels)

        return layer


def by_sentences(layer_a, layer_b):
    spans = None
    deprels = []
    LASes = []
    UASes = []
    LAs = []
    for a, b in zip(layer_a, layer_b):
        if a.id == 1:
            if spans is not None:
                yield (spans, deprels, LASes, UASes, LAs)
            spans = []
            deprels = []
            LASes = []
            UASes = []
            LAs = []

        spans.append(a)
        deprels.append(a.deprel)
        LASes.append(compare_LAS(a, b))
        UASes.append(compare_UAS(a, b))
        LAs.append(compare_LA(a, b))

    yield (spans, deprels, LASes, UASes, LAs)


def compare_LAS(span_a, span_b):
    if span_a.deprel != span_b.deprel:
        if span_a.parent_span is None or span_b.parent_span is None:
            if span_a.parent_span is None and span_b.parent_span is None:
                return 0
            else:
                return 1    
        elif span_a.parent_span.start == span_b.parent_span.start and span_a.parent_span.end == span_b.parent_span.end:
            return 0
        else:
             return 1   
    return 0
    
def compare_UAS(span_a, span_b):
    if span_a.deprel == span_b.deprel:
        if span_a.parent_span is None or span_b.parent_span is None:
            if span_a.parent_span is None and span_b.parent_span is None:
                return 0
            else:
                return 1    
        elif span_a.parent_span.start == span_b.parent_span.start and span_a.parent_span.end == span_b.parent_span.end:
            return 0
        else:
            return 1
    return 0        
        
    #return 0  
    
def compare_LA(span_a, span_b):
    if span_a.deprel == span_b.deprel:
       
        return 0
        #
        #    return 1
    else:
        if span_a.parent_span is None or span_b.parent_span is None:
            if span_a.parent_span is None and span_b.parent_span is None:  
                return 1
        elif span_a.parent_span.start == span_b.parent_span.start and span_a.parent_span.end == span_b.parent_span.end:
            return 1        
    return 0      
