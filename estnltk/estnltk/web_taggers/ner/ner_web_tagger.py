import functools

from estnltk.taggers import Tagger
from estnltk import Text, Layer, EnvelopingBaseSpan, ElementaryBaseSpan

from typing import MutableMapping

import requests


def create_word_ner_layer(func):
    @functools.wraps(func)
    def words_layer_creation_wrapper(*args, **kwargs):
        self = args[0]
        text = args[1]
        response = self.post_request(text)
        if self.input_layers != [self.custom_words_layer]:
            wordnertagger = NerWordsTagger(response, self.nerwords_output_layer)
            wordnertagger.tag(text)
        #TODO Very dirty hack to pass the response to make_layer, to fix
        args = list(args)
        args.append(response)
        args = tuple(args)

        func(*args, **kwargs)

    return words_layer_creation_wrapper

class NerWordsTagger(Tagger):
    '''
    Class for creating the words layer corresponding to the output of the NER from the TartuNLP API
    '''
    conf_param = ['response']

    def __init__(self, response, output_layer='nerwords'):
        self.output_layer = output_layer
        self.response = response
        self.input_layers = []
        self.output_attributes = []

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        layer = Layer(name=self.output_layer, attributes=self.output_attributes, text_object=text)
        current_idx = 1
        for snt in self.response['result']:
            current_idx -= 1
            for word in snt:
                while text.text[current_idx:current_idx+len(word['word'])] != word['word']:
                    current_idx += 1
                layer.add_annotation(ElementaryBaseSpan(current_idx, current_idx+len(word['word'])))
                current_idx += len(word['word'])
        return layer



class NerWebTagger(Tagger):
    '''
    NER tagger using the TartuNLP web API
    IMPORTANT: Using this tagger means that the data will be processed by the public TartuNLP API. This means that the
    text will be uploaded and can be read by a third party.
    '''
    conf_param = ['custom_words_layer','url','nerwords_output_layer']

    def __init__(self, output_layer='ner', custom_words_layer=None,nerwords_output_layer = 'nerwords'):
        '''
        Note that if a custom layer is chosen, it is not checked whether the word segmentation in that layer
        matches the segmentation done by the NER tagger. If the segmentations do not match, it will lead to wrong tags
        in the output.

        Parameters
        ----------
        output_layer: str - output layer name
        custom_words_layer: str - name of the words layer from which the NER layer envelops.
            If None, the words layer is created based on the segmentation done by the NER tagger.
        nerwords_output_layer: str - name of the words layer created by the NER tagger if no custom layer is specified
        '''
        self.url = 'https://api.tartunlp.ai/bert/ner/v1'
        self.output_layer = output_layer
        self.output_attributes = ["nertag"]
        self.input_layers = []
        self.nerwords_output_layer = nerwords_output_layer
        self.custom_words_layer = custom_words_layer
        if custom_words_layer:
            self.input_layers = [custom_words_layer]
        else:
            self.input_layers = [nerwords_output_layer]

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, attributes=self.output_attributes, text_object=None, enveloping = self.input_layers[0])

    @create_word_ner_layer
    def tag(self, text, status: dict = None):
        super(NerWebTagger, self).tag(text,status)

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        response = status
        nerlayer = self._make_layer_template()
        nerlayer.text_object=text
        labels = [word['ner'] for snt in response['result'] for word in snt]
        entity_spans = []
        entity_type = None
        words = self.input_layers[0]

        for span, label in zip(getattr(text, words), labels):
            if entity_type is None:
                entity_type = label[2:]
            if label == "O":
                if entity_spans:
                    nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                            **{self.output_attributes[0]: entity_type})
                    entity_spans = []
                continue
            if label[0] == "B" or entity_type != label[2:]:
                if entity_spans:
                    nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                            **{self.output_attributes[0]: entity_type})
                    entity_spans = []
            entity_type = label[2:]
            entity_spans.append(span.base_span)

        return nerlayer


    def post_request(self, text: Text):
        data = {
            'text': text.text
        }
        resp = requests.post(self.url, json=data)
        resp.raise_for_status()
        return resp.json()
