#
#  Serialization for phrases extracted from a syntax layer.
#  Used by PhraseExtractor.
#
#  Based on:  https://github.com/estnltk/syntax_experiments/tree/5ecdebed69632b0b06d01bf868483a214f00e3d3/collection_splitting/serialisation_module
#
from estnltk_core.converters.default_serialisation import dict_to_layer as default_dict_to_layer

from estnltk_core import Span 
from estnltk_core.layer.layer import Layer


__version__ = 'syntax_phrases_v0'


def layer_to_dict(layer):
    layer_dict = {
        'name': layer.name,
        'attributes': layer.attributes,
        'secondary_attributes': layer.secondary_attributes,
        'parent': layer.parent,
        'enveloping': layer.enveloping,
        'ambiguous': layer.ambiguous,
        'serialisation_module': __version__,
        'meta': layer.meta
    }
    attributes = []
    for attr in layer.attributes:
        if attr != "root":
            attributes.append(attr)
    spans = []
    for span in layer:
        annotation_dict = [{attr: annotation[attr] for attr in attributes} for annotation in span.annotations]
        spans.append({'base_span': span.base_span.raw(),
                      'annotations': annotation_dict})
    layer_dict['spans'] = spans

    return layer_dict


def dict_to_layer(layer_dict: dict, text_object=None):
    if text_object is None:
        raise ValueError(f'(!) Parameter text_object is required by {__version__}.dict_to_layer().')
    layer = default_dict_to_layer(layer_dict, text_object)
    for span in layer:
        for annotation in span.annotations:
            annotation["root"] = text_object[layer.enveloping].spans[annotation["root_id"]-1]
    return layer
    
