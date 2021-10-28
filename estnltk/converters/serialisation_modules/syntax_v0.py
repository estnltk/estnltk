from . import default


__version__ = 'syntax_v0'


def layer_to_dict(layer):
    layer_dict = {
        'name': layer.name,
        'attributes': layer.attributes,
        'parent': layer.parent,
        'enveloping': layer.enveloping,
        'ambiguous': layer.ambiguous,
        'serialisation_module': __version__,
        'meta': layer.meta
    }

    spans = []
    attributes = [attr for attr in layer.attributes if attr not in {'parent_span', 'children'}]
    for span in layer:
        annotation_dicts = [{attr: annotation[attr] for attr in attributes} for annotation in span.annotations]
        spans.append({'base_span': span.base_span.raw(),
                      'annotations': annotation_dicts})
    layer_dict['spans'] = spans
    return layer_dict


def dict_to_layer(layer_dict: dict, text_object=None):
    assert layer_dict['serialisation_module'] == __version__
    assert 'parent_span' in layer_dict['attributes']
    assert 'children' in layer_dict['attributes']
    layer = default.dict_to_layer(layer_dict, text_object)
    layer.serialisation_module = __version__
    # Normally, we would apply here SyntaxDependencyRetagger to produce
    # values for 'parent_span' & 'children'.
    # However, in a stripped-down version of EstNLTK, the retagger is 
    # not available, so we add None values in place of 'parent_span' & 
    # 'children'
    for span in layer:
        for annotation in span.annotations:
            annotation['parent_span'] = None
            annotation['children'] = None
    return layer
