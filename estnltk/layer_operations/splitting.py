from estnltk.text import Span, SpanList, Layer, Text
import networkx as nx

def extract_sections(text,
                    sections:list,
                    layers_to_keep:list=None,
                    trim_overlapping:bool=False):
    '''
    layers_to_keep
        List of layer names to be kept. 
        The dependencies must also be included, that is, if a layer in the list
        has a parent or is enveloping, then the parent or enveloped layer
        must also be included.
        If None (default), all layers are kept
    trim_overlapping
        If False (default), overlapping spans are not kept.
        If True, overlapping spans are trimmed to fit the boundaries.
    '''
    if layers_to_keep:
        for layer in layers_to_keep:
            parent = text[layer].parent
            enveloping = text[layer].enveloping
            if parent:
                assert parent in layers_to_keep, 'parent of '+layer+' missing in layers_to keep: '+parent
            if enveloping:
                assert enveloping in layers_to_keep, 'enveloping of '+layer+' missing in layers_to keep: '+enveloping
    result = []
    for start, end in sections:
        map_spans = {}
        new_text = Text(text.text[start:end])
        for layer in text.list_layers():
            layer_name = layer.name
            if layers_to_keep is not None:
                if layer_name not in layers_to_keep:
                    continue
            attributes = layer.attributes
            parent = layer.parent
            enveloping = layer.enveloping
            ambiguous = layer.ambiguous
            new_layer = Layer(name=layer.name,
                              attributes=attributes,
                              parent=parent,
                              enveloping=enveloping,
                              ambiguous=ambiguous)
            new_layer._base = layer._base
            new_text[layer_name] = new_layer
    
            if parent:
                if ambiguous:
                    for span in layer.spans:
                        span_parent = map_spans.get(span.parent)
                        if span_parent:
                            for sp in span:
                                new_span = span_parent.mark(layer_name)
                                for attr in attributes:
                                    setattr(new_span, attr, getattr(sp, attr))
                                map_spans[sp] = new_span
                else:
                    raise NotImplementedError('not ambiguous layer with parent: '+ layer_name)
            elif enveloping:
                if ambiguous:
                    raise NotImplementedError('ambiguous enveloping layer: '+ layer_name)
                else:
                    for span in layer.spans:
                        span_start = span.start
                        span_end = span.end
                        if trim_overlapping:
                            span_start = max(span_start, start)
                            span_end = min(span_end, end)
                            if span_start >= span_end:
                                continue
                        elif span_start < start or end < span_end:
                            continue
                        new_span = SpanList(layer=new_layer)
                        for s in span:
                            parent = map_spans.get(s)
                            if parent:
                                new_span.spans.append(parent)
                        for attr in attributes:
                            setattr(new_span, attr, getattr(sp, attr))
                        new_layer.add_span(new_span)
                        map_spans[span] = new_span
            else:
                if ambiguous:
                    raise NotImplementedError('ambiguous layer: '+ layer_name)
                else:
                    for span in layer.spans:
                        span_start = span.start
                        span_end = span.end
                        if trim_overlapping:
                            span_start = max(span_start, start)
                            span_end = min(span_end, end)
                            if span_start >= span_end:
                                continue
                        elif span_start < start or end < span_end:
                            continue
                        new_span = Span(span_start-start, span_end-start)
                        for attr in attributes:
                            setattr(new_span, attr, getattr(span, attr))
                        new_layer.add_span(new_span)
                        map_spans[span] = new_span
        result.append(new_text)
    return result

def extract_section(text,
                    start:int,
                    end:int,
                    layers_to_keep:list=None,
                    trim_overlapping:bool=False):
    return extract_sections(text, [(start, end)], layers_to_keep, trim_overlapping)[0]


def layers_to_keep_default(text, layer):
    graph = nx.DiGraph()
    for layer_name, layer_object in text.layers.items():
        if layer_object.enveloping:
            graph.add_edge(layer_name, layer_object.enveloping)
        elif layer_object.parent:
            graph.add_edge(layer_name, layer_object.parent)
            graph.add_edge(layer_object.parent, layer_name)
    return nx.descendants(graph, layer) | {layer}


def split_by(text, layer, layers_to_keep=None, trim_overlapping=False):
    if layers_to_keep is None:
        layers_to_keep = layers_to_keep_default(text, layer)
    sections = [(element.start, element.end) for element in text[layer]]
    return extract_sections(text, sections, layers_to_keep, trim_overlapping)


def split_by_sentences(text, layers_to_keep=None, trim_overlapping=False):
    return split_by(text, 'sentences', layers_to_keep, trim_overlapping)
