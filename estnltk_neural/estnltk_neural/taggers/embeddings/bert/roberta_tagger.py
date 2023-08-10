import os
from typing import MutableMapping, List

import numpy as np
import torch
from transformers import logging
from transformers import AutoTokenizer
from transformers import AutoModel

logging.set_verbosity(30)
from estnltk import Text
from estnltk.taggers import Tagger
from estnltk import Layer


class RobertaTagger(Tagger):
    """Tags EstRobertA embeddings."""

    def __init__(self, bert_location: str = 'EMBEDDIA/est-roberta', sentences_layer: str = 'sentences',
                 token_level: bool = True,
                 output_layer: str = 'roberta_embeddings', bert_layers: List[int] = None, method='concatenate'):

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
            raise Exception( "RobertaTagger's model location not provided. "+\
                             "Please pass huggingface_hub repo_id or local path to the model directory "+\
                             "via parameter bert_location when creating RobertaTagger." )
        else:
            self.bert_location = bert_location
        if method not in ('concatenate', 'add', 'all'):
            msg = "Method can be 'concatenate', 'add' or 'all'."
            raise Exception(msg)
        self.method = method
        self.output_layer = output_layer
        self.input_layers = [sentences_layer]

        self.bert_model = AutoModel.from_pretrained(self.bert_location, output_hidden_states=True)
        self.tokenizer = AutoTokenizer.from_pretrained(self.bert_location)

        self.output_attributes = ('token', 'bert_embedding')

        self.token_level = token_level
        self.bert_layers = bert_layers

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        sentences_layer = layers[self.input_layers[0]]
        embeddings_layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes,
                                 ambiguous=True)

        for k, sentence in enumerate(sentences_layer):
            word_spans = []

            for word in sentence:
                word_spans.append((word.start, word.end, word.text))
            sent_text = sentence.enclosing_text

            start, i, end, word_span, word = word_spans[0][0], 0, word_spans[0][1], word_spans[0], word_spans[0][2]

            embeddings = get_embeddings(sent_text, self.bert_model, self.tokenizer, self.method, 
                                        self.bert_layers)[1:-1]  # first one is <s> token, and last one is </s> token
            tokens = self.tokenizer.tokenize(sent_text)

            assert len(tokens) == len(embeddings)

            if self.token_level:  
                # annotates bert tokens

                #  Example of tokenization difference:
                # EstBert:     'muusikamaailmalt' -> ['muu', '##sika', '##maa', '##ilm', '##alt']
                # EstRobertA:  'muusikamaailmalt' -> ['▁muusika', 'maa', 'il', 'malt']
                
                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_init = packed[0], packed[1]

                    if token_init == '▁...' and word.startswith('…'):
                        # est-roberta's tokenizer replaces … with ...
                        # replace it back
                        token_init = '▁…'

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

                    shift_start = -1
                    if token_init == '<unk>':
                        token_end = end  # if token was UNK, set the end to word end
                        #
                        # Guard: check if the next token and the next word span match?
                        # If not, then there is a misalignment between tokens and word 
                        # spans, for instance:
                        #     word span:  '💁!💁💁?'
                        #     tokens:     '<unk>', '!', '<unk>', '?'
                        # or
                        #     word span:  '☏???'
                        #     tokens:     '<unk>', '???'
                        # In case of a misalignment, move incrementally inside word_span.
                        #
                        next_token = tokens[j+1].replace('▁', '') if j+1 < len(tokens) else None
                        next_word = word_spans[i+1][2] if i+1 < len(word_spans) else None
                        if (next_token is not None and next_word is not None and \
                            not next_word.startswith(next_token)) or \
                            next_word is None and next_token is not None:
                            cur_word_chars = [c for c in word]
                            if next_token[0] in cur_word_chars:
                                # shift pointer inside word_span
                                indx = cur_word_chars.index(next_token[0])
                                token_end = start + indx
                                shift_start = indx
                    else:
                        token = token_init.strip()  # if not, then len(token)
                        token_end = start + len(token.replace('▁', ''))
                        word = word.replace(token.replace('▁', ''), '', 1)  # keep the next part of word for later use

                    if len(word) != 0:
                        if word[0] == ' ' and end > token_end + 1:  # check if is multiword
                            token_end += 1
                            word = word[1:]

                    embeddings_layer.add_annotation((start, token_end), **attributes)
                    if shift_start == -1:
                        # shift the current pointer by full word_span length
                        start = token_end
                    else:
                        # shift the current pointer incrementally inside word_span
                        start = start + shift_start
                        word = word[shift_start:]
                    if start == end:  # new word starts
                        i += 1
                        if len(word_spans) > i:  # update the values for the next word
                            word_span = word_spans[i]
                            start = word_span[0]
                            end = word_span[1]
                            word = word_span[2]

            else:
                # annotates full words, adding the token level embeddings together
                collected_tokens = []
                collected_embeddings = []
                counter = word_spans[0][0]
                word = word_spans[0][2]

                #  Example of tokenization difference:
                # EstBert:     'muusikamaailmalt' -> ['muu', '##sika', '##maa', '##ilm', '##alt']
                # EstRobertA:  'muusikamaailmalt' -> ['▁muusika', 'maa', 'il', 'malt']

                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_init = packed[0], packed[1]
                    if token_init == '▁...':
                        if word.startswith('…'):
                            # est-roberta's tokenizer replaces … with ...
                            # replace it back
                            token_init = '▁…'
                        elif word == '.':
                            # handle tokenization difference:
                            #    word spans:    '.', '.', '.'
                            #    tokens:        ▁...
                            while word == '.':
                                # Full word token
                                if self.method == 'all':
                                    embedding = [[float(e) for e in le] for le in token_emb]
                                else:
                                    embedding = [float(e) for e in token_emb]
                                attributes = {'token': token_init, 'bert_embedding': embedding}
                                embeddings_layer.add_annotation((word_spans[i][0], word_spans[i][1]),
                                                                **attributes)
                                collected_tokens, collected_embeddings = [], []
                                i += 1
                                if len(word_spans) > i:
                                    counter = word_spans[i][0]
                                    word = word_spans[i][2]
                                else:
                                    break
                    span = word_spans[i]
                    length = span[1] - span[0]
                    if length == len(token_init.replace('▁', '')) or token_init == '<unk>':
                        #
                        # Guard: check if the next token and the next word span match?
                        # If not, then there is a misalignment between tokens and word 
                        # spans, for instance:
                        #     word span:  '💁!💁💁?'
                        #     tokens:     '<unk>', '!', '<unk>', '?'
                        # or
                        #     word span:  '☏???'
                        #     tokens:     '<unk>', '???'
                        # In case of a misalignment, move incrementally inside word_span.
                        #
                        shift_inside_word_span = False
                        next_token = (tokens[j+1]).replace('▁', '') if j+1 < len(tokens) else None
                        next_word = word_spans[i+1][2] if i+1 < len(word_spans) else None
                        if (next_token is not None and next_word is not None and \
                            not next_word.startswith(next_token)) or \
                            next_word is None and next_token is not None:
                            cur_word_chars = [c for c in word]
                            if next_token[0] in cur_word_chars:
                                # shift pointer inside word_span
                                indx = cur_word_chars.index(next_token[0])
                                counter += indx
                                word = word[indx:]
                                collected_embeddings.append(token_emb)
                                collected_tokens.append(token_init)
                                shift_inside_word_span = True
                        if not shift_inside_word_span:
                            # Full word token or UNK token
                            if self.method == 'all':
                                embedding = [[float(e) for e in le] for le in token_emb]
                            else:
                                embedding = [float(e) for e in token_emb]
                            attributes = {'token': token_init, 'bert_embedding': embedding}
                            embeddings_layer.add_annotation((word_spans[i][0], word_spans[i][1]),
                                                            **attributes)
                            collected_tokens, collected_embeddings = [], []
                            i += 1
                            if len(word_spans) > i:
                                counter = word_spans[i][0]
                                word = word_spans[i][2]
                    elif length > len(token_init.replace('▁', '')) and token_init.startswith('▁') and counter == span[0]:
                        # first in many tokens
                        collected_embeddings.append(token_emb)
                        collected_tokens.append(token_init)
                        counter += len(token_init.replace('▁', ''))
                    elif (length > len(token_init.replace('▁', '')) and counter >= span[0]):
                        # in the middle (or at the end) of a token
                        collected_embeddings.append(token_emb)
                        collected_tokens.append(token_init)
                        add_length = len(token_init.replace('▁', ''))
                        counter += add_length
                        word = word[add_length:]
                        if counter == span[1] or \
                           counter + span[2].count(' ') == span[1]:  
                            # check if in the end of the word
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
                            collected_embeddings = []
                            collected_tokens = []

                            i += 1
                            if len(word_spans) > i:
                                counter = word_spans[i][0]
                                word = word_spans[i][2]

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
