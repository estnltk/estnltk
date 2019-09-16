"""
Trains a multi-class model.

Usage: train.py --config=CONFIG-MODULE-PATH

"""
import os
import sys

from docopt import docopt

from estnltk.neural_morph.general_utils import load_config_from_file
from estnltk.neural_morph.data_utils import DataBuilder, ConfigHolder, CoNLLDataset
from estnltk.neural_morph.model import Model

args = docopt(__doc__)

config = load_config_from_file(args['--config'])

if os.path.exists(config.model_dir):
    print("Output directory '%s' already exists." % config.model_dir)
    sys.exit()

data_builder = DataBuilder(config)
data_builder.run()

config_holder = ConfigHolder(config)
model = Model(config_holder)
model.build()

train = CoNLLDataset(config_holder.filename_train,
                     config_holder.processing_word_train,
                     config_holder.processing_tag,
                     config_holder.processing_analysis,
                     config_holder.max_iter,
                     use_buckets=config.bucket_train_data,
                     batch_size=config.batch_size,
                     shuffle=config.shuffle_train_data,
                     sort=config.sort_train_data,
                     )
test = CoNLLDataset(config_holder.filename_dev,
                    config_holder.processing_word_infer,
                    config_holder.processing_tag,
                    config_holder.processing_analysis,
                    sort=True)
train_eval = CoNLLDataset(config_holder.filename_train,
                          config_holder.processing_word_infer,
                          config_holder.processing_tag,
                          config_holder.processing_analysis,
                          sort=True,
                          max_iter=config_holder.train_sentences_to_eval)

model.train(train, test, train_eval)
model.close_session()
