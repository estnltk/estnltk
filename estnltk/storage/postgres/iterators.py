

def find_examples(collection, layer, attributes, return_text, return_count=False, **kwargs):
    """Find examples for attribute value tuples in the collection."""
    if return_count:
        raise NotImplementedError('return_count=True not yet implemented')
    else:
        examples = set()
        for key, text in collection.select(layers=[layer], **kwargs):
            for span_pos, span in enumerate(text[layer]):
                for annotation in span.annotations:
                    example = tuple(getattr(annotation, attr) for attr in attributes)
                    if example not in examples:
                        examples.add(example)
                        if return_text:
                            yield example, key, span_pos, text
                        else:
                            yield example, key, span_pos
