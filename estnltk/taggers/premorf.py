from functools import partial
from typing import List

from estnltk.text import Layer, Text
from estnltk.vabamorf.morf import Vabamorf


class CopyTagger:
    def __init__(self):
        pass

    def tag(self, text: Text):
        text['words_copy'] = Layer('words_copy', parent='words', ambiguous=False, attributes=['text_copy'])
        for i in text.words:
            i.mark('words_copy').text_copy = i.text

        return text


class FilteringRewriter:
    def __init__(self, keyword: str):
        self.keyword = keyword.lower()

    def rewrite(self, record):

        result = {}
        for k, v in record.items():
            if k in ('start', 'end'):
                result[k] = v
            else:
                if v.lower() == self.keyword:
                    result['normal'] = v.split('-')[-1]
                else:
                    return None

        return result


class HyphenRemovingRewriter:
    def __init__(self):
        self.instance = Vabamorf.instance()

    def rewrite(self, record):
        token_0 = record['text_copy']

        if '-' not in token_0:
            return None

        analysis_0 = self.instance.analyze([token_0],
                                           guess=False, 
                                           propername=False, 
                                           disambiguate=False)[0]
        pos_tags_0 = [a['partofspeech'] for a in analysis_0['analysis']
                      if a['partofspeech']!='Z']

        token_1 = token_0.replace('-', '')
        analysis_1 = self.instance.analyze([token_1],
                                           guess=False, 
                                           propername=False, 
                                           disambiguate=False)[0]
        pos_tags_1 = [a['partofspeech'] for a in analysis_1['analysis']
                      if a['partofspeech']!='Z']
        if len(pos_tags_1) > len(pos_tags_0):
            record['normal'] = token_1
            return record


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


class WordNormalizingTagger:
    def __init__(self):
        pass

    def tag(self, text: Text) -> Text:
        source_layer = text['words_copy']  # type: Layer

        source_attributes = ['text_copy']
        target_attributes = ['normal']

        rewriting_template = partial(source_layer.rewrite,
                                     source_attributes=source_attributes,
                                     target_attributes=target_attributes,
                                     name='normalized',
                                     ambiguous=False)

        uku_layer = rewriting_template(rules=FilteringRewriter('u-u-uku'))
        sven_layer = rewriting_template(rules=FilteringRewriter('s-s-sven'))
        
        hyphen_removing_layer = rewriting_template(rules=HyphenRemovingRewriter())

        text['normalized'] = merge([uku_layer, sven_layer, hyphen_removing_layer])

        return text
