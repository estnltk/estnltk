from estnltk_core.taggers import MultiLayerTagger
from estnltk import Text, Layer, EnvelopingBaseSpan, ElementaryBaseSpan

from typing import MutableMapping

import requests



class NerWebTagger(MultiLayerTagger):
    '''
    NER tagger using the TartuNLP web API
    IMPORTANT: Using this tagger means that the data will be processed by the public TartuNLP API. This means that the
    text will be uploaded and can be read by a third party.
    '''
    conf_param = ['custom_words_layer','url','nerwords_output_layer','input_layers','output_layers',
                  'output_layers_to_attributes']

    def __init__(self, url='https://api.tartunlp.ai/bert/ner/v1', ner_output_layer=None, custom_words_layer=None, tokens_output_layer ='nertokens'):
        '''
        Note that if a custom layer is chosen, it is not checked whether the word segmentation in that layer
        matches the segmentation done by the NER tagger. If the segmentations do not match, it will lead to wrong tags
        in the output.

        Parameters
        ----------
        url: str
            URL of the web service. Defaults to the TartuNLP neural NER web API URL. 
        ner_output_layer: str
            NER output layer name. 
        custom_words_layer: str
            name of the words layer from which the NER layer envelops. 
            If None, the words layer is created based on the segmentation done by the NER tagger. 
        tokens_output_layer: str
            name of the tokens layer created by the NER tagger if no custom layer is specified. 
        '''
        output_layers = ['ner'] if ner_output_layer is None else [ner_output_layer]

        self.url = url
        self.output_layers = output_layers
        self.output_layers_to_attributes = {output_layers[0]: ["nertag"]}
        if custom_words_layer is None:
            self.output_layers.append(tokens_output_layer)
            self.output_layers_to_attributes[output_layers[1]] = []
            self.input_layers = []
        else:
            self.input_layers = [custom_words_layer]
        self.custom_words_layer = custom_words_layer

    def create_word_ner_layer(self, text, response):
        layer = Layer(name=self.output_layers[1], attributes=self.output_layers_to_attributes[self.output_layers[1]], text_object=text)
        current_idx = 1
        for snt in response['result']:
            current_idx -= 1
            for word in snt:
                while text.text[current_idx:current_idx + len(word['word'])] != word['word'] and current_idx < len(text.text):
                    current_idx += 1
                layer.add_annotation(ElementaryBaseSpan(current_idx, current_idx + len(word['word'])))
                current_idx += len(word['word'])
        return layer

    def _make_layers(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        response = self.post_request(text)
        if self.custom_words_layer is None:
            nerwordslayer = self.create_word_ner_layer(text,response)
        nerlayer = Layer(name=self.output_layers[0], attributes=self.output_layers_to_attributes[self.output_layers[0]],
                         text_object=text,
                         enveloping = self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1])
        nerlayer.text_object=text
        labels = [word['ner'] for snt in response['result'] for word in snt]
        entity_spans = []
        entity_type = None
        words = self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1]
        if self.custom_words_layer is None:
            for span, label in zip(nerwordslayer, labels):
                if entity_type is None:
                    entity_type = label[2:]
                if label == "O":
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][0]: entity_type})
                        entity_spans = []
                    continue
                if label[0] == "B" or entity_type != label[2:]:
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][0]: entity_type})
                        entity_spans = []
                entity_type = label[2:]
                entity_spans.append(span.base_span)

            return {self.output_layers[1]: nerwordslayer, self.output_layers[0]: nerlayer}
        else:
            for span, label in zip(getattr(text,words), labels):
                if entity_type is None:
                    entity_type = label[2:]
                if label == "O":
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][0]: entity_type})
                        entity_spans = []
                    continue
                if label[0] == "B" or entity_type != label[2:]:
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][0]: entity_type})
                        entity_spans = []
                entity_type = label[2:]
                entity_spans.append(span.base_span)
            return {self.output_layers[0]: nerlayer}

    def post_request(self, text: Text):
        data = {
            'text': text.text
        }
        resp = requests.post(self.url, json=data)
        resp.raise_for_status()
        return resp.json()
