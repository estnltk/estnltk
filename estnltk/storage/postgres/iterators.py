
def find_examples(collection, layer, attributes, output_layers=None, return_text=False, return_count=False, **kwargs):
    """Find examples for attribute value tuples in the collection.

    collection: PgCollection
        instance of the EstNLTK PostgreSQL collection
    layer: str
        layer name
    attributes: Sequence[str]
        attribute names which values are extracted for the examples
    output_layers: Sequence[str]
        names of the layers that are attached to the Text object if return_text is True
    return_count: bool
        return number of occurrences in the collection for each example
    :returns
        Tuple(example, key, span_pos, text, count) where
        example is a tuple of attribute values that correspond to attributes parameter
        key is the collection id of the Text object
        span_pos is the index of the span in the Text object
        text is the Text object returned if return_text is True
        count is the number occurrences of the example in the collection returned if return_count is True
    """
    if not return_text:
        output_layers = None
    if output_layers is None:
        output_layers = [layer]
    elif layer not in output_layers:
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


def filter_fragmets(collection, fragmented_layer: str, ngram_query, filter):
    """

    :param fragments:
    :param ngram_query:
    :param filter:
        filter ja ngram_query on alternatiivsed ?
    :return:
    fragments
    """
    pass
