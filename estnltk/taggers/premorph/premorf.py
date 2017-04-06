from functools import partial
from typing import List

from estnltk.text import Layer, Text


def merge(layers: List[Layer]) -> Layer:
    # all layers must be from the same parent
    assert len(set(i.parent for i in layers)) == 1

    assert len(layers) > 0
    assert len(set(i.name for i in layers)) == 1
    assert len(set(tuple(i.attributes) for i in layers)) == 1

    recs = {}

    for layer in layers:
        records = layer.to_records()
        for record in records:
            recs[(record['start'], record['end'])] = record

    result = Layer(
        parent=layer.parent,
        ambiguous=False,
        name=layer.name,
        attributes=layer.attributes

    ).from_records(records=sorted(recs.values(), key=lambda x: x['start']), rewriting=True)
    return result

from estnltk.rewriting.premorph.word_normalizing import WordNormalizingRewriter

class WordNormalizingTagger:
    def __init__(self):
        pass

    def tag(self, text: Text) -> Text:
        source_layer = text['words']  # type: Layer

        source_attributes = ['text']
        target_attributes = ['normal']

        rewriting_template = partial(source_layer.rewrite,
                                     source_attributes=source_attributes,
                                     target_attributes=target_attributes,
                                     name='normalized',
                                     ambiguous=False)

        normalizing_layer = rewriting_template(rules=WordNormalizingRewriter())

        text['normalized'] = merge([normalizing_layer])

        return text
