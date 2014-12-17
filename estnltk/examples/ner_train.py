# -*- coding: utf-8 -*-
''' An example illustrating how to train a NER model. '''

from __future__ import unicode_literals, print_function
import os
import bz2
import json

from estnltk import NerTrainer, nersettings
from estnltk.core import CORPORA_PATH


CORPUS_FILE = os.path.join(CORPORA_PATH, 'estner_sample.json.bz2')
MODEL_DIR = 'test_model'

# Load the training corpus
corpus = open(CORPUS_FILE, 'rb').read()
corpus= bz2.decompress(corpus)
corpus = json.loads(corpus.decode('utf-8'))
documents = corpus['documents']

# Train and save the model
trainer = NerTrainer(nersettings)
trainer.train(documents, MODEL_DIR)
