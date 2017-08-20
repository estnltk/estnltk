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
        self._layer_name = 'normalized_words'
        self._attributes = ['normal']
        self._depends_on = ['words']
        self._conf= ''
        self.word_normalizing_rewriter = WordNormalizingRewriter()


    def tag(self, text: Text) -> Text:
        source_layer = text['words']  # type: Layer

        source_attributes = ['text']
        target_attributes = ['normal']

        rewriting_template = partial(source_layer.rewrite,
                                     source_attributes=source_attributes,
                                     target_attributes=target_attributes,
                                     name=self._layer_name,
                                     ambiguous=False)

        normalizing_layer = rewriting_template(rules=self.word_normalizing_rewriter)

        text[self._layer_name] = merge([normalizing_layer])

        return text

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self._layer_name,
                  'attributes':self._attributes,
                  'depends_on': self._depends_on,
                  'conf':self._conf}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'conf'])
        return df.to_html(index=False)