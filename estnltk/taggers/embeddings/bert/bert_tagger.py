import torch
from typing import MutableMapping, List
from transformers import BertTokenizer, BertForPreTraining, logging

logging.set_verbosity(30)
from estnltk.text import Text
from estnltk.taggers import Tagger
from estnltk.layer.layer import Layer
import numpy as np


class BertTagger(Tagger):
    """Tags BERT embeddings."""

    def __init__(self, bert_location: str, sentences_layer: str = 'sentences',
                 token_level: bool = True,
                 output_layer: str = 'bert_embeddings', bert_layers: List[int] = None, method='concatenate'):

        if bert_layers is None:
            bert_layers = [-4, -3, -2, -1]
        else:
            for layer in bert_layers:
                if abs(layer) > 12:
                    msg = "BERT base model only has 12 layers of transformer encoder, chose layers from (-12..-1). It " \
                          "is reasonable to choose layers from the last layers, for example [-4, -3, -2, -1]: last 4 " \
                          "layers. "
                    raise Exception(msg)
        self.conf_param = ('bert_location', 'bert_model', 'tokenizer', 'method', 'token_level', 'bert_layers')
        if bert_location is None:
            msg = "Directory containing BERT model must be specified."
            raise Exception(msg)
        else:
            self.bert_location = bert_location
        if method not in ('concatenate', 'add', 'all'):
            msg = "Method can be 'concatenate', 'add' or 'all'."
            raise Exception(msg)
        self.method = method
        self.output_layer = output_layer
        self.input_layers = [sentences_layer]

        self.bert_model = BertForPreTraining.from_pretrained(pretrained_model_name_or_path=self.bert_location,
                                                             output_hidden_states=True,
                                                             from_tf=True)
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_location)

        self.output_attributes = ['token', 'bert_embedding']

        self.token_level = token_level
        self.bert_layers = bert_layers

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        sentences_layer = layers[self.input_layers[0]]
        embeddings_layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                                 ambiguous=True)

        start, i = 0, 0
        word_spans = []

        for k, sentence in enumerate(sentences_layer):

            for word in sentence:
                word_spans.append((word.start, word.end, word.text))
            sent_text = sentence.enclosing_text

            embeddings = get_embeddings(sent_text, self.bert_model, self.tokenizer, self.method, self.bert_layers)[
                         1:-1]  # first one in start token, and last one is sep token
            tokens = self.tokenizer.tokenize(sent_text)
            assert len(tokens) == len(embeddings)
            if k != 0:  # move the start manually when next sentence starts
                start = word_spans[i][0]

            if self.token_level:  # annotates tokens
                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_init = packed[0], packed[1]

                    if not token_init.startswith("#") and j != 0:  # move to next word
                        if start == word_spans[i][1]:  # BERT's wordpiece tokenizer can tokenize differently
                            i += 1  # next word starts
                            word_span = word_spans[i]
                            start = word_span[0]  # the start id of this word
                    if self.method == 'all':
                        embedding = []
                        for tok_emb in token_emb:
                            emb = []
                            for e in tok_emb:
                                emb.append(float(e))
                            embedding.append(emb)
                    else:
                        embedding = [float(t) for t in token_emb]

                    attributes = {'token': token_init, 'bert_embedding': embedding}
                    token = token_init.strip()
                    embeddings_layer.add_annotation((start, start + len(token.replace('#', ''))), **attributes)
                    start += len(token.replace('#', ''))  # adding token length to the current pointer

                i += 1  # move the pointer manually

            else:  # annotates full words, adding the token level embedding together
                collected_tokens = []
                collected_embeddings = []
                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_init = packed[0], packed[1]

                    if i == 0 and j == 0:
                        start = 0
                        collected_embeddings.append(token_emb)
                        collected_tokens.append(token_init)
                        start += len(token_init)

                    if i != 0 and j == 0:
                        collected_tokens = [token_init]
                        collected_embeddings = [token_emb]
                        start = word_spans[i][0]

                        start += len(token_init)

                    if not token_init.startswith("#") and j != 0:  # move to next word
                        if start == word_spans[i][1]:  # BERT's wordpiece tokenizer can tokenize differently

                            if collected_embeddings:
                                if self.method == 'all':
                                    embedding = []
                                    for tok_embs in collected_embeddings:
                                        token_embs = []
                                        for embs in tok_embs:
                                            token_embs_emb = []
                                            for emb in embs:
                                                token_embs_emb.append(float(emb))
                                            token_embs.append(token_embs_emb)
                                        embedding.append(token_embs)
                                else:
                                    embedding = [float(t) for t in np.sum(collected_embeddings, 0)]

                                attributes = {'token': collected_tokens, 'bert_embedding': embedding}
                                embeddings_layer.add_annotation((word_spans[i][0], word_spans[i][1]),
                                                                **attributes)

                            i += 1  # next word starts
                            start = word_spans[i][0]  # the start id of this word
                            collected_embeddings = [token_emb]
                            collected_tokens = [token_init]
                            start += len(token_init)
                        else:
                            start += len(token_init)
                            collected_tokens.append(token_init)
                            collected_embeddings.append(token_emb)
                    elif token_init.startswith("#"):
                        collected_tokens.append(token_init)
                        collected_embeddings.append(token_emb)
                        start += len(token_init.replace("#", ''))

                if collected_tokens:
                    if self.method == 'all':
                        embedding = []
                        for tok_embs in collected_embeddings:
                            token_embs = []
                            for embs in tok_embs:
                                token_embs_emb = []
                                for emb in embs:
                                    token_embs_emb.append(float(emb))
                                token_embs.append(token_embs_emb)
                            embedding.append(token_embs)
                    else:
                        embedding = [float(t) for t in np.sum(collected_embeddings, 0)]

                    attributes = {'token': collected_tokens, 'bert_embedding': embedding}
                    embeddings_layer.add_annotation((word_spans[i][0], word_spans[i][1]),
                                                    **attributes)

                i += 1  # move the pointer manually

        return embeddings_layer


def get_embeddings(sentence: str, model, tokenizer, method, bert_layers):
    input_data = tokenizer.encode_plus(sentence)
    input_ids = input_data.get('input_ids')
    token_vecs_cat = []
    if len(input_ids) > 512:  # maximum sequence length can be 512
        msg = "Input sentence is too big (%s), splitting the sentence." % len(input_ids)
        print(msg)
        collected_input_ids = []
        while True:
            collected_input_ids.append(input_ids[:512])
            input_ids = input_ids[512:]
            if len(input_ids) <= 512:
                collected_input_ids.append(input_ids)
                break
    else:
        collected_input_ids = [input_ids]

    for i, input_ids in enumerate(collected_input_ids):

        segments_ids = [1] * len(input_ids)
        tokens_tensor = torch.tensor([input_ids])
        segments_tensors = torch.tensor([segments_ids])

        with torch.no_grad():
            outputs = model(tokens_tensor, segments_tensors)
            hidden_states = outputs[2]
        token_embeddings = torch.stack(hidden_states, dim=0)
        token_embeddings = torch.squeeze(token_embeddings, dim=1)
        token_embeddings = token_embeddings.permute(1, 0, 2)

        for token in token_embeddings:
            if method == 'concatenate':  # concatenate the vectors
                layers = [token[i] for i in bert_layers]
                cat_vec = torch.cat(layers, dim=0)
                token_vecs_cat.append(np.asarray(cat_vec))

            if method == 'add':  # elementwise addition
                layers = [np.asarray(token[i]) for i in bert_layers]
                sum_vec = np.sum(layers, 0)
                token_vecs_cat.append(np.asarray(sum_vec))

            if method == 'all':  # return all
                layers = [np.asarray(token[i]) for i in bert_layers]
                token_vecs_cat.append(layers)

    return token_vecs_cat
