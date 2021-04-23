import torch  # pytorch-1.7.0
from transformers import AutoModelWithLMHead, AutoTokenizer  # transformers-3.1.0
from copy import deepcopy
from estnltk import Text


class BertAugmentor:
    "Augments sentences"
    def __init__(self, model_name: str = 'tartuNLP/EstBERT_512', sentences_layer: str = 'sentences'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelWithLMHead.from_pretrained(model_name, return_dict=True)
        self.sentences_layer = sentences_layer

    def augment(self, sentence: Text, mask, how_many: int, method: str = 'one') -> list:
        if method == 'one':
            predicted_texts = []
            for i, mask in enumerate(mask):
                if mask == 1:
                    seq = deepcopy([word.text for word in sentence.words])
                    seq[i] = '[MASK]'
                    sequence = ' '.join(seq)
                    input = self.tokenizer.encode(sequence, return_tensors="pt")
                    mask_token_index = torch.where(input == self.tokenizer.mask_token_id)[1]
                    token_logits = self.model(input).logits
                    mask_token_logits = token_logits[0, mask_token_index, :]
                    top_tokens = torch.topk(mask_token_logits, how_many * 10, dim=1).indices[0].tolist()
                    texts = []
                    for token in top_tokens:
                        decoded_token = self.tokenizer.decode([token])
                        if not decoded_token.startswith('##'):
                            texts.append(sequence.replace(self.tokenizer.mask_token, decoded_token))
                    predicted_texts.append(texts[:how_many])
            return predicted_texts
        elif method == 'many':
            seq = deepcopy([word.text for word in sentence.words])
            sequences = [deepcopy(seq) for i in range(how_many * 10)]
            for i, mask in enumerate(mask):
                if mask == 1:
                    seq[i] = '[MASK]'
                    for j, s in enumerate(sequences):
                        s[i] = '[MASK]'
                        sequences[j] = s
            sequence = ' '.join(seq)
            sequences = [' '.join(s) for s in sequences]
            input = self.tokenizer.encode(sequence, return_tensors="pt")
            mask_token_indeces = torch.where(input == self.tokenizer.mask_token_id)[1]
            token_logits = self.model(input).logits
            for index in mask_token_indeces:
                index = torch.LongTensor([index])
                mask_token_logits = token_logits[0, index, :]
                top_tokens = torch.topk(mask_token_logits, how_many * 10, dim=1).indices[0].tolist()
                i = 0
                for token in top_tokens:
                    decoded_token = self.tokenizer.decode([token])
                    if not decoded_token.startswith('##'):
                        sequences[i] = sequences[i].replace(self.tokenizer.mask_token, decoded_token, 1)
                        i += 1
            return sequences[:how_many]
        else:
            msg = 'Method should be \'many\' or \'one\'.'
            raise Exception(msg)
