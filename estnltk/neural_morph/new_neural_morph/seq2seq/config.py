import os
from ..common_config import *

# training
l2_loss_weight = 0  # 0.0005
batch_size = 5  # checked
lr_method = "sgd"  # sgd | adam | adagrad | rmsprop | momentum
lr = 1.0  # checked, optimal [1, 2]. TODO: test with decay. Run lr=1 for > 100 iterations.
lr_decay = 1.
lr_decay_strategy = None  # "on-no-improvement" | "step" | "exponential" | None

nepoch_no_imprv = 50
max_epochs = 400

# decoder
dim_tag = 150  # checked
tag_embeddings_dropout = 0.5
decoder_maximum_iterations = 12  # find maximum from the training corpus
attention = None  # None | analysis-tag | analysis-category | char | sentence . Set to None to disable attention
attention_mechanism = "luong"  # bahdanau | luong
trainer = "basic"  # scheduled | basic
scheduled_trainer_sampling_prob = .2
use_crf = False  # if crf, training is 1.7x slower on CPU

# evaluation
eval_batch_size = 200
