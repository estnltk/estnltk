# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from ..estner import settings as default_nersettings
from ..core import DEFAULT_NER_DATASET
from ..corpus import read_json_corpus
from ..ner import NerTrainer, NerTagger, DEFAULT_NER_MODEL_DIR
from pprint import pprint

def train_default_model():
    """Function for training the default NER model.

    NB! It overwrites the default model, so do not use it unless
    you know what are you doing.

    The training data is in file estnltk/corpora/estner.json.bz2 .
    The resulting model will be saved to estnltk/estner/models/default.bin
    """
    docs = read_json_corpus(DEFAULT_NER_DATASET)
    trainer = NerTrainer(default_nersettings)
    trainer.train(docs, DEFAULT_NER_MODEL_DIR)


if __name__ == '__main__':
    # todo: make this script capable of training and annotating corpora
    train_default_model()

