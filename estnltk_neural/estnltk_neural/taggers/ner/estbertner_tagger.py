from transformers import BertTokenizer, BertForTokenClassification
from transformers import pipeline

from estnltk_core.taggers import MultiLayerTagger

from estnltk.downloader import get_resource_paths

from estnltk import Text, Layer, EnvelopingBaseSpan, ElementaryBaseSpan

from typing import MutableMapping

class EstBERTNERTagger(MultiLayerTagger):
    """ EstNLTK wrapper for the huggingface EstBERTNER model."""
    conf_param = ('model_location', 'nlp','tokenizer','input_layers','output_layers',
                  'output_layers_to_attributes','custom_words_layer')

    def __init__(self, model_location: str = None,output_layer: str = 'estbertner',custom_words_layer=None,
                 words_output_layer ='nerwords'):
        """Note that if a custom layer is chosen, it is not checked whether the word segmentation in that layer
        matches the segmentation done by the NER tagger. If the segmentations do not match, it will lead to wrong tags
        in the output."""


        if model_location is None:
            # Try to get the resources path for berttagger. Attempt to download, if missing
            resources_path = get_resource_paths("estbertner", only_latest=True, download_missing=True)
            if resources_path is None:
                raise Exception( "EstBERTNER's resources have not been downloaded. "+\
                                 "Use estnltk.download('estbertner') to get the missing resources. "+\
                                 "Alternatively, you can specify the directory containing the model "+\
                                 "via parameter model_location at creating the tagger." )
            self.model_location = resources_path

        else:
            self.model_location = model_location

        tokenizer = BertTokenizer.from_pretrained(self.model_location)
        bertner = BertForTokenClassification.from_pretrained(self.model_location)

        self.nlp = pipeline("ner", model=bertner, tokenizer=tokenizer)
        self.tokenizer = tokenizer

        self.input_layers = []
        self.output_layers = [output_layer]

        self.output_layers_to_attributes = {self.output_layers[0]: ["nertag"]}

        if custom_words_layer is None:
            self.output_layers.append(words_output_layer)
            self.output_layers_to_attributes[self.output_layers[1]] = []
        else:
            self.input_layers = [custom_words_layer]

        self.custom_words_layer = custom_words_layer


    def create_word_ner_layer(self, text):
        layer = Layer(name=self.output_layers[1], attributes=self.output_layers_to_attributes[self.output_layers[1]], text_object=text)
        current_idx = 0
        for word in self.tokenizer.tokenize(text.text):
            if word.startswith('##'):
                word = word[2:]
            if word != "[UNK]":
                while text.text[current_idx:current_idx + len(word)].lower().replace('õ','o').replace('ä','a').replace('ö','o').replace('ü','u').replace('ž','z').replace('š','s') != word.lower().replace('õ','o').replace('ä','a').replace('ö','o').replace('ü','u').replace('ž','z').replace('š','s'):
                    current_idx += 1
                layer.add_annotation(ElementaryBaseSpan(current_idx, current_idx + len(word)))
                current_idx += len(word)
            else:
                layer.add_annotation(ElementaryBaseSpan(current_idx,current_idx))
        return layer

    def _make_layers(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        response = self.nlp(text.text)
        if self.custom_words_layer is None:
            nerwordslayer = self.create_word_ner_layer(text)
        nerlayer = Layer(name=self.output_layers[0], attributes=self.output_layers_to_attributes[self.output_layers[0]],
                         text_object=text,
                         enveloping=self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1])
        nerlayer.text_object = text
        entity_spans = []
        entity_type = None
        words = self.input_layers[0] if len(self.input_layers) > 0 else self.output_layers[1]
        if self.custom_words_layer is None:
            labels = ['O'] * len(nerwordslayer)
            for word in response:
                labels[word['index'] - 1] = word['entity']
            for span, label in zip(nerwordslayer, labels):
                if entity_type is None:
                    entity_type = label[2:]
                if label == "O":
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][
                                                       0]: entity_type})
                        entity_spans = []
                    continue
                if label[0] == "B" or entity_type != label[2:]:
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][
                                                       0]: entity_type})
                        entity_spans = []
                entity_type = label[2:]
                entity_spans.append(span.base_span)

            return {self.output_layers[1]: nerwordslayer, self.output_layers[0]: nerlayer}
        else:
            labels = ['O'] * len(getattr(text, words))
            for word in response:
                labels[word['index'] - 1] = word['entity']
            for span, label in zip(getattr(text, words), labels):
                if entity_type is None:
                    entity_type = label[2:]
                if label == "O":
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][
                                                       0]: entity_type})
                        entity_spans = []
                    continue
                if label[0] == "B" or entity_type != label[2:]:
                    if entity_spans:
                        nerlayer.add_annotation(EnvelopingBaseSpan(entity_spans),
                                                **{self.output_layers_to_attributes[self.output_layers[0]][
                                                       0]: entity_type})
                        entity_spans = []
                entity_type = label[2:]
                entity_spans.append(span.base_span)
            return {self.output_layers[0]: nerlayer}
