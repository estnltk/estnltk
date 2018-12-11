

def find_examples(collection, layer, attributes, output_layers=None, return_text=False, return_count=False, **kwargs):
    """Find examples for attribute value tuples in the collection."""
    if output_layers is None:
        output_layers = [layer]
    if layer not in output_layers:
        output_layers.append(layer)

    if return_count:
        raise NotImplementedError('return_count=True not yet implemented')
    else:
        examples = set()
        for key, text in collection.select(layers=output_layers, **kwargs):
            for span_pos, span in enumerate(text[layer]):
                for annotation in span.annotations:
                    example = tuple(getattr(annotation, attr) for attr in attributes)
                    if example not in examples:
                        examples.add(example)
                        if return_text:
                            yield example, key, span_pos, text
                        else:
                            yield example, key, span_pos
