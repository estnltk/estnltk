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
    """Tags EstRobertA embeddings.
    
       TODO: processing logic of RobertaTagger is almost identical to that of BertTagger,
       so RobertaTagger should become BertTagger's subclass.
    """

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

    def tokenize_with_bert(self, text_str, include_spanless=True):
        '''Tokenizes input text_str with self.tokenizer and returns a list of token spans.
           Each token span is a triple (start, end, token). 
           If include_spanless==True (default), then special "spanless" tokens (e.g. 
           <s>, </s>) will also be included with their respective start/end indexes 
           set to None.
        '''
        tokens = []
        batch_encoding = self.tokenizer(text_str)
        for token_id, token in enumerate(batch_encoding.tokens()):
            char_span = batch_encoding.token_to_chars(token_id)
            if char_span is not None:
                tokens.append( (char_span.start, char_span.end, token) )
            elif include_spanless:
                tokens.append( (None, None, token) )
        return tokens

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        sentences_layer = layers[self.input_layers[0]]
        embeddings_layer = Layer(name=self.output_layer, text_object=text, 
                                 attributes=self.output_attributes,
                                 ambiguous=(not self.token_level and self.method == 'all'))

        for k, sentence in enumerate(sentences_layer):
            sent_text = sentence.enclosing_text
            embeddings = get_embeddings(sent_text, self.bert_model, self.tokenizer, self.method, self.bert_layers)
            tokens = self.tokenize_with_bert(sent_text)
            assert len(tokens) == len(embeddings)
            if self.token_level:
                # annotates bert tokens
                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_span = packed[0], packed[1]
                    if token_span[0] is None and token_span[1] is None:
                        # Skip special tokens (e.g. [CLS], [SEP])
                        continue
                    if self.method == 'all':
                        embedding = []
                        for tok_emb in token_emb:
                            emb = []
                            for e in tok_emb:
                                emb.append(float(e))
                            embedding.append(emb)
                    else:
                        embedding = [float(t) for t in token_emb]
                    attributes = {'token': token_span[2], 'bert_embedding': embedding}
                    start = sentence.start + token_span[0]
                    end   = sentence.start + token_span[1]
                    embeddings_layer.add_annotation((start, end), **attributes)
            else:
                # annotates full words, adding the token level embeddings together
                word_spans = []
                for word in sentence:
                    word_spans.append((word.start, word.end, word.text))
                # Find locations of all bert tokens inside word spans
                word_id = 0
                collected_tokens = []
                collected_embeddings = []
                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_span = packed[0], packed[1]
                    if token_span[0] is None and token_span[1] is None:
                        # Skip special tokens (e.g. [CLS], [SEP])
                        continue
                    start = sentence.start + token_span[0]
                    end   = sentence.start + token_span[1]
                    current_word = word_spans[word_id]
                    if current_word[0] <= start and end <= current_word[1]:
                        # if bert's token falls within the current word,
                        # then simply record the embedding
                        collected_tokens.append( token_span[2] )
                        collected_embeddings.append( token_emb )
                    elif current_word[1] <= start:
                        # if bert's token begins after the word: 
                        # 1) finish the previous word
                        if collected_tokens and collected_embeddings:
                            # add annotation
                            if self.method == 'all':
                                assert embeddings_layer.ambiguous
                                for cur_token, tok_embs in zip(collected_tokens, collected_embeddings):
                                    token_embs = []
                                    for embs in tok_embs:
                                        token_embs_emb = []
                                        for emb in embs:
                                            token_embs_emb.append(float(emb))
                                        token_embs.append(token_embs_emb)
                                    attributes = {'token': cur_token, 'bert_embedding': token_embs}
                                    embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                    **attributes)
                            else:
                                embedding = [float(t) for t in np.sum(collected_embeddings, 0)]
                                attributes = {'token': collected_tokens, 'bert_embedding': embedding}
                                embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                **attributes)
                        collected_tokens = []
                        collected_embeddings = []
                        # 2) take the next word or words. 
                        # note: in rare cases, the bert token overlaps and 
                        # stretches beyond the next word, so we take all 
                        # following words covered by the bert token.
                        word_id += 1
                        while word_id < len(word_spans):
                            current_word = word_spans[word_id]
                            collected_tokens.append( token_span[2] )
                            collected_embeddings.append( token_emb )
                            # Check the stopping criteria
                            if end <= current_word[1]:
                                # If the word ends with or after the bert token,
                                # then end the cycle (pick the next bert token)
                                break
                            # If the stopping criteria was not met then:
                            # Collect embedding and complete the given word
                            if collected_tokens and collected_embeddings:
                                # add annotation
                                if self.method == 'all':
                                    assert embeddings_layer.ambiguous
                                    for cur_token, tok_embs in zip(collected_tokens, collected_embeddings):
                                        token_embs = []
                                        for embs in tok_embs:
                                            token_embs_emb = []
                                            for emb in embs:
                                                token_embs_emb.append(float(emb))
                                            token_embs.append(token_embs_emb)
                                        attributes = {'token': cur_token, 'bert_embedding': token_embs}
                                        embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                        **attributes)
                                else:
                                    embedding = [float(t) for t in np.sum(collected_embeddings, 0)]
                                    attributes = {'token': collected_tokens, 'bert_embedding': embedding}
                                    embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                    **attributes)
                                collected_tokens = []
                                collected_embeddings = []
                            word_id += 1
                    elif current_word[0] <= start and end > current_word[1]:
                        # partial overlap #1: the bert token overlaps and stretches 
                        # beyond the word token:
                        #
                        #    wwww
                        #    bbbbbbb
                        #
                        #    wwww
                        #      bbbbb
                        #
                        #    www ww ..
                        #      bbbbbbbbb
                        #
                        # Strategy 'keep_all': add embedding to the current word and 
                        # also to following words covered by the bert token
                        while word_id < len(word_spans):
                            current_word = word_spans[word_id]
                            collected_tokens.append( token_span[2] )
                            collected_embeddings.append( token_emb )
                            # Check the stopping criteria
                            if end < current_word[1]:
                                # If the word stretches beyond the bert token,
                                # then end the cycle (pick the next bert token)
                                break
                            # If the stopping criteria was not met then:
                            # Collect embedding and complete the given word
                            if collected_tokens and collected_embeddings:
                                # add annotation
                                if self.method == 'all':
                                    assert embeddings_layer.ambiguous
                                    for cur_token, tok_embs in zip(collected_tokens, collected_embeddings):
                                        token_embs = []
                                        for embs in tok_embs:
                                            token_embs_emb = []
                                            for emb in embs:
                                                token_embs_emb.append(float(emb))
                                            token_embs.append(token_embs_emb)
                                        attributes = {'token': cur_token, 'bert_embedding': token_embs}
                                        embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                        **attributes)
                                else:
                                    embedding = [float(t) for t in np.sum(collected_embeddings, 0)]
                                    attributes = {'token': collected_tokens, 'bert_embedding': embedding}
                                    embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                    **attributes)
                                collected_tokens = []
                                collected_embeddings = []
                            word_id += 1
                    elif start < current_word[0] and end <= current_word[1]:
                        # partial overlap #2: the bert token starts before and 
                        # overlaps the word token:
                        #
                        #       wwww
                        #    bbbbbbb
                        #
                        #       wwww
                        #  bbbbbbb
                        #
                        #  .. ww wwww  (covered by partial overlap #1)
                        #  bbbbbbbb
                        #
                        # Strategy 'keep_all': add embedding to the current word, but
                        # do not complete the word (unless it's end has been reached)
                        collected_tokens.append( token_span[2] )
                        collected_embeddings.append( token_emb )
                        if end == current_word[1]:
                            # add annotation
                            if self.method == 'all':
                                assert embeddings_layer.ambiguous
                                for cur_token, tok_embs in zip(collected_tokens, collected_embeddings):
                                    token_embs = []
                                    for embs in tok_embs:
                                        token_embs_emb = []
                                        for emb in embs:
                                            token_embs_emb.append(float(emb))
                                        token_embs.append(token_embs_emb)
                                    attributes = {'token': cur_token, 'bert_embedding': token_embs}
                                    embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                    **attributes)
                            else:
                                embedding = [float(t) for t in np.sum(collected_embeddings, 0)]
                                attributes = {'token': collected_tokens, 'bert_embedding': embedding}
                                embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                                **attributes)
                            collected_tokens = []
                            collected_embeddings = []
                
                # Finish the last word
                if collected_tokens and collected_embeddings:
                    # add annotation
                    if self.method == 'all':
                        assert embeddings_layer.ambiguous
                        for cur_token, tok_embs in zip(collected_tokens, collected_embeddings):
                            token_embs = []
                            for embs in tok_embs:
                                token_embs_emb = []
                                for emb in embs:
                                    token_embs_emb.append(float(emb))
                                token_embs.append(token_embs_emb)
                            attributes = {'token': cur_token, 'bert_embedding': token_embs}
                            embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                            **attributes)
                    else:
                        embedding = [float(t) for t in np.sum(collected_embeddings, 0)]
                        attributes = {'token': collected_tokens, 'bert_embedding': embedding}
                        embeddings_layer.add_annotation((current_word[0], current_word[1]),
                                                        **attributes)
        if not self.token_level:
            # Check that each word got an embedding
            assert len(embeddings_layer) == sum([len(s) for s in sentences_layer])
        return embeddings_layer


def get_embeddings(sentence: str, model, tokenizer, method, bert_layers):
    input_data = tokenizer(sentence)
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
