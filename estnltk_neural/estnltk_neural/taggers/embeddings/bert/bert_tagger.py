from typing import MutableMapping, List
import os

import torch
import numpy as np

from transformers import BertTokenizer, logging, BertModel

from estnltk.downloader import get_resource_paths

logging.set_verbosity(30)
from estnltk import Text
from estnltk.taggers import Tagger
from estnltk import Layer


class BertTagger(Tagger):
    """Tags BERT embeddings."""

    def __init__(self, bert_location: str = None, sentences_layer: str = 'sentences',
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
            # Try to get the resources path for berttagger. Attempt to download, if missing
            resources_path = get_resource_paths("berttagger", only_latest=True, download_missing=True)
            if resources_path is None:
                raise Exception( "BertTagger's resources have not been downloaded. "+\
                                 "Use estnltk.download('berttagger') to get the missing resources. "+\
                                 "Alternatively, you can specify the directory containing BERT model "+\
                                 "via parameter bert_location at creating BertTagger." )
            self.bert_location = resources_path
        else:
            self.bert_location = bert_location
        if method not in ('concatenate', 'add', 'all'):
            msg = "Method can be 'concatenate', 'add' or 'all'."
            raise Exception(msg)
        self.method = method
        self.output_layer = output_layer
        self.input_layers = [sentences_layer]

        self.bert_model = BertModel.from_pretrained(self.bert_location, output_hidden_states=True)
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_location)

        self.output_attributes = ['token', 'bert_embedding']

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

            embeddings = get_embeddings(sent_text, self.bert_model, self.tokenizer, self.method, self.bert_layers)[
                         1:-1]  # first one is cls token, and last one is sep token
            tokens = self.tokenizer.tokenize(sent_text)

            assert len(tokens) == len(embeddings)
            if self.token_level:  # annotates tokens

                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_init = packed[0], packed[1]

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

                    # Symbol '\xad' is invisible to bert tokenizer;
                    # Remove it from the word span, otherwise alignment fails;
                    if word.count('\xad') > 0:
                        if word == '\xad':
                            # Skip the whole word span
                            if len(word_spans) > i+1:
                                i += 1
                                word_span = word_spans[i]
                                start = word_span[0]
                                end = word_span[1]
                                word = word_span[2]
                        elif len(word) > word.count('\xad'):
                            # Skip inside word span
                            removed_chars = word.count('\xad')
                            word = word.replace('\xad', '')
                            #end -= removed_chars
                    shift_start = -1
                    if token_init == '[UNK]':
                        token_end = end  # if token was UNK, set the end to word end
                        #
                        # Guard: check if the next token and the next word span match?
                        # If not, then there is a misalignment between tokens and word 
                        # spans, for instance:
                        #     word span:  '💁!💁💁?'
                        #     tokens:     '[UNK]', '!', '[UNK]', '?'
                        # or
                        #     word span:  '☏???'
                        #     tokens:     '[UNK]', '???'
                        # In case of a misalignment, move incrementally inside word_span.
                        #
                        next_token = tokens[j+1].replace('#', '') if j+1 < len(tokens) else None
                        next_word = word_spans[i+1][2] if i+1 < len(word_spans) else None
                        if (next_token is not None and next_word is not None and \
                            not startswith_relaxed(next_word, next_token)) or \
                            next_word is None and next_token is not None:
                            cur_word_chars = [c for c in word]
                            if next_token[0] in cur_word_chars:
                                # shift pointer inside word_span
                                indx = cur_word_chars.index(next_token[0])
                                token_end = start + indx
                                shift_start = indx
                            elif next_token == '[UNK]':
                                # shift pointer inside word_span
                                indx = 1
                                token_end = start + indx
                                shift_start = indx
                    else:
                        token = token_init.strip()  # if not, then len(token)
                        token_end = start + len(token.replace('#', ''))
                        # replace and keep the next part of word for later use
                        word = replace_relaxed(word, token.replace('#', ''), replacement='', count=1)

                    if len(word) != 0:
                        if word[0] == ' ' and end > token_end + 1: # check if is multiword
                            token_end += 1
                            word = word[1:]
                        elif len(token.replace('#', '')) > len(word) and \
                             startswith_relaxed(token.replace('#', ''), word, remove_from_token=True): 
                            # Check if tokenizations diverge, and there's an 
                            # overflow, such as:
                            #     word span:  'ni'
                            #     tokens:     '##nile'
                            # If so, then find next word span that starts within bert token
                            token_cut = (token.replace('#', ''))[len(word):]
                            invisible_tokens = []
                            shift_i = i+1
                            while shift_i < len(word_spans):
                                next_word = word_spans[shift_i][2]
                                if next_word == '\xad':
                                    # Skip invisible token '\xad'
                                    invisible_tokens.append(word_spans[shift_i])
                                else:
                                    # Ordinary token
                                    if startswith_relaxed(next_word, token_cut):
                                        i = shift_i
                                        word_span = word_spans[i]
                                        start = word_span[0] - len(token_cut)
                                        if invisible_tokens:
                                            # Skip invisible tokens
                                            for invisible_token in invisible_tokens:
                                                start -= len(invisible_token[2])
                                        end = word_span[1]
                                        word = word_span[2]
                                        word = replace_relaxed(word, token_cut, replacement='', count=1)
                                        token_end = word_span[0] + len(token_cut)
                                    break
                                shift_i += 1
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

            else:  # annotates full words, adding the token level embeddings together
                collected_tokens = []
                collected_embeddings = []
                counter = word_spans[0][0]
                word = word_spans[0][2]
                for j, packed in enumerate(zip(embeddings, tokens)):
                    token_emb, token_init = packed[0], packed[1]
                    span = word_spans[i]
                    length = span[1] - span[0]
                    # Symbol '\xad' is invisible to bert tokenizer;
                    # Remove it from the word span, otherwise alignment fails;
                    if word.count('\xad') > 0 and len(word) > word.count('\xad'):
                        removed_chars = word.count('\xad')
                        word = word.replace('\xad', '')
                        counter += removed_chars
                        length -= removed_chars
                    if length == len(
                            token_init.replace('#', '')) or token_init == '[UNK]':  # Full word token or UNK token
                        #
                        # Guard: check if the next token and the next word span match?
                        # If not, then there is a misalignment between tokens and word 
                        # spans, for instance:
                        #     word span:  '💁!💁💁?'
                        #     tokens:     '[UNK]', '!', '[UNK]', '?'
                        # or
                        #     word span:  '☏???'
                        #     tokens:     '[UNK]', '???'
                        # In case of a misalignment, move incrementally inside word_span.
                        #
                        shift_inside_word_span = False
                        next_token = (tokens[j+1]).replace('#', '') if j+1 < len(tokens) else None
                        next_word = word_spans[i+1][2] if i+1 < len(word_spans) else None
                        if (token_init == '[UNK]' and ((next_token is not None and 
                            next_word is not None and not startswith_relaxed(next_word, next_token)) or \
                            next_word is None and next_token is not None)):
                            cur_word_chars = [c for c in word]
                            if next_token[0] in cur_word_chars:
                                # shift pointer inside word_span
                                indx = cur_word_chars.index(next_token[0])
                                counter += indx
                                word = word[indx:]
                                collected_embeddings.append(token_emb)
                                collected_tokens.append(token_init)
                                shift_inside_word_span = True
                            elif next_token == '[UNK]' and length > 1:
                                # shift pointer inside word_span
                                indx = 1
                                counter += indx
                                word = word[indx:]
                                collected_embeddings.append(token_emb)
                                collected_tokens.append(token_init)
                                shift_inside_word_span = True
                        if not shift_inside_word_span:
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
                            if len(word_spans) > i+1 and word == '\xad':
                                # Symbol '\xad' seems to be invisible to 
                                # bert tokenizer; skip it, but mark with
                                # last embedding for layer consistency
                                attributes2 = {'token': [], 'bert_embedding': embedding}
                                embeddings_layer.add_annotation((word_spans[i][0], 
                                                                 word_spans[i][1]),
                                                                 **attributes2)
                                i += 1
                                counter = word_spans[i][0]
                                word = word_spans[i][2]
                    elif length > len(token_init) and not token_init.startswith('#') and counter == span[0]:
                        # first in many tokens
                        collected_embeddings.append(token_emb)
                        collected_tokens.append(token_init)
                        counter += len(token_init)
                        word = word[len(token_init):]
                    elif (length > len(token_init.replace('#', '')) and counter >= span[0]):
                        # in the middle or at the end of the word span
                        collected_embeddings.append(token_emb)
                        collected_tokens.append(token_init)
                        add_length = len(token_init.replace('#', ''))
                        # Check if tokenizations diverge, so adding results 
                        # in an overflow, such as:
                        #     word span:  'ni'
                        #     tokens:     '##nile'
                        if counter + add_length > span[1]:
                            # If so, then find next word span that starts within bert token
                            token_cut = (token_init.replace('#', ''))[len(word):]
                            shift_i = i+1
                            invisible_tokens = []
                            while shift_i < len(word_spans):
                                next_word = word_spans[shift_i][2]
                                if next_word == '\xad':
                                    # Invisible token '\xad'
                                    invisible_tokens.append( word_spans[shift_i] )
                                else:  
                                    # Ordinary token
                                    if startswith_relaxed(next_word, token_cut):
                                        # Add invisible tokens, if any
                                        if invisible_tokens:
                                            for invisible_token in invisible_tokens:
                                                attributes2 = {'token': [], 'bert_embedding': embedding}
                                                embeddings_layer.add_annotation((invisible_token[0], 
                                                                                 invisible_token[1]),
                                                                                 **attributes2)
                                        # Add previously collected embeddings
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
                                        # Keep last tokens and embeddings
                                        collected_embeddings = collected_embeddings[-1:]
                                        collected_tokens = collected_tokens[-1:]

                                        i = shift_i
                                        span = word_spans[i]
                                        counter = word_spans[i][0] + len(token_cut)
                                        word = word_spans[i][2]
                                        word = replace_relaxed(word, token_cut, replacement='', count=1)

                                    break
                                shift_i += 1
                        else:
                            counter += add_length
                            word = word[add_length:]
                        if counter == span[1] or counter + span[2].count(' ') == span[1]:  # check if in the end of the word
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
                            if len(word_spans) > i+1 and word == '\xad':
                                # Symbol '\xad' seems to be invisible to 
                                # bert tokenizer; skip it, but mark with
                                # last embedding for layer consistency
                                attributes2 = {'token': [], 'bert_embedding': embedding}
                                embeddings_layer.add_annotation((word_spans[i][0], 
                                                                 word_spans[i][1]),
                                                                 **attributes2)
                                i += 1
                                counter = word_spans[i][0]
                                word = word_spans[i][2]
        return embeddings_layer


def startswith_relaxed(word_str: str, token_str: str, remove_from_token=False) -> bool:
    '''
    Relaxed version of string.startswith for determining 
    if EstNLTK's word_str starts with EstBert's token_str. 
    Before comparison, takes care of the required character 
    normalization: converts word_str to lowercase and 
    removes common diacritics/accents from letters.
    '''
    word_str = word_str.lower()
    word_str = word_str.replace('ö', 'o')
    word_str = word_str.replace('õ', 'o')
    word_str = word_str.replace('ä', 'a')
    word_str = word_str.replace('ü', 'u')
    word_str = word_str.replace('š', 's')
    word_str = word_str.replace('ž', 'z')
    if remove_from_token:
        token_str = token_str.lower()
        token_str = token_str.replace('ö', 'o')
        token_str = token_str.replace('õ', 'o')
        token_str = token_str.replace('ä', 'a')
        token_str = token_str.replace('ü', 'u')
        token_str = token_str.replace('š', 's')
        token_str = token_str.replace('ž', 'z')
    return word_str.startswith(token_str)


def replace_relaxed(word_str: str, token_str: str,
                    replacement:str='', count=1) -> str:
    '''
    Relaxed version of str.replace for deleting 
    EstBert's token_str inside EstNLTK's word_str.
    Before the replacement, takes care of the required 
    character normalization: converts word_str to 
    lowercase and removes common diacritics/accents 
    from letters.
    '''
    original_word_str = word_str
    word_str = word_str.lower()
    word_str = word_str.replace('ö', 'o')
    word_str = word_str.replace('õ', 'o')
    word_str = word_str.replace('ä', 'a')
    word_str = word_str.replace('ü', 'u')
    word_str = word_str.replace('š', 's')
    word_str = word_str.replace('ž', 'z')
    index = word_str.find(token_str)
    if index > -1:
        return original_word_str[:index] +\
               original_word_str[index+len(token_str):]
    else:
        return original_word_str


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
