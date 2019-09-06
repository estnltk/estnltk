from estnltk.taggers.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from . import default_v1


def layer_to_dict(layer):
    layer_dict = {
        'name': layer.name,
        'attributes': layer.attributes,
        'parent': layer.parent,
        'enveloping': layer.enveloping,
        'ambiguous': layer.ambiguous,
        'dict_converter_module': layer.dict_converter_module,
        'meta': layer.meta
    }

    spans = []
    attributes = [attr for attr in layer.attributes if attr not in {'parent_span', 'children'}]
    for span in layer:
        annotation_dict = [{attr: annotation[attr] for attr in attributes} for annotation in span.annotations]
        spans.append({'base_span': span.base_span.raw(),
                      'annotations': annotation_dict})
    layer_dict['spans'] = spans

    return layer_dict


def dict_to_layer(layer_dict: dict, text_object=None):
    layer = default_v1.dict_to_layer(layer_dict, text_object)

    retagger = SyntaxDependencyRetagger(layer.name)
    retagger.change_layer(text_object, {layer.name: layer})

    return layer
