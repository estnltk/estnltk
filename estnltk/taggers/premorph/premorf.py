from functools import partial
from typing import List

from estnltk.text import Layer, Text
from estnltk.taggers import Tagger

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

class WordNormalizingTagger(Tagger):
    layer_name = 'normalized_words'
    attributes = ['normal']
    depends_on = ['words']
    parameters = {}

    def __init__(self):
        self.word_normalizing_rewriter = WordNormalizingRewriter()

    def tag(self, text: Text) -> Text:
        source_layer = text['words']  # type: Layer

        source_attributes = ['text']
        target_attributes = ['normal']

        rewriting_template = partial(source_layer.rewrite,
                                     source_attributes=source_attributes,
                                     target_attributes=target_attributes,
                                     name=self.layer_name,
                                     ambiguous=False)

        normalizing_layer = rewriting_template(rules=self.word_normalizing_rewriter)

        text[self.layer_name] = merge([normalizing_layer])

        return text
