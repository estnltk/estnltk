import os

# Set data / output directories
current_dir = os.path.dirname(os.path.abspath(__file__))
try:
    data_dir = "" # os.environ['DATA_DIR']
    out_dir = os.path.join(current_dir, "output")
    embeddings_dir = "" # os.environ['EMBEDDINGS_DIR']
except KeyError:
    print("Environment variable 'DATA_DIR','OUT_DIR' and 'EMBEDDINGS_DIR' are required.")
    raise

out_data_dir = os.path.join(out_dir, "data")
dir_output = os.path.join(out_dir, "results")
dir_model = os.path.join(dir_output, "model.weights")
path_log = os.path.join(dir_output, "log.txt")
training_log = os.path.join(dir_output, "training.log")

# Input
## characters
dim_char = 100  # checked
use_char_embeddings = True
# analysis
analysis_embeddings = "category"  # None | tag | category | input_attention_tag | attention_tag | attention_category
analysis_embeddings_combination = "sum"  # mean | sum
analysis_attention_project = False # True = concatenate
use_analysis_dropout = False
analysis_dropout_method = "random"  # random or first
analysis_dropout_keep_prob = 1.0
attention = None  # None | analysis-tag | analysis-category
dim_analysis = 10
## words
dim_word = 300
use_word_embeddings = True
lowercase = True  # lowercase corpus and embeddings
filename_embeddings = os.path.join(embeddings_dir, "emb.vec")
filename_embeddings_trimmed = os.path.join(out_data_dir, "embeddings.npz")
use_pretrained = True and use_word_embeddings
case_insensitive_embedding_lookup = False and not lowercase
train_singletons = True and use_word_embeddings
singleton_p = 0.5
keep_train_vocab = True
embeddings_dropout = 0.5  # checked
use_embeddings_batch_normalization = False

# data
filename_train = os.path.join(data_dir, "train.ttm")
filename_dev = os.path.join(data_dir, "dev.ttm")
filename_test = os.path.join(data_dir, "test.ttm")

# vocab
filename_words = os.path.join(out_data_dir, "words.txt")
filename_tags = os.path.join(out_data_dir, "tags.txt")
filename_chars = os.path.join(out_data_dir, "chars.txt")
filename_analysis = os.path.join(out_data_dir, "analysis.txt")
filename_singletons = os.path.join(out_data_dir, "singletons.txt")




# training
train_embeddings = True
l2_loss_weight = 0  # 0.0005
batch_size = 20  # checked
batching_queque_size = 1000
lr_method = "sgd"  # sgd | adam | adagrad | rmsprop | momentum
lr = 1.0  # checked, optimal [1, 2] fr sql. TODO: test with decay. Run lr=1 for > 100 iterations.
lr_decay = 0.98
lr_decay_step = 2500
lr_decay_strategy = "exponential"  # "on-no-improvement" | "step" | "exponential" | None
momentum = 0.9
clip = 5  # if negative, no clipping
shuffle_train_data = False
sort_train_data = False
bucket_train_data = True

nepoch_no_imprv = 50
max_updates = 2500 * 250  # not needed ?
max_epochs = 400

max_iter = None  # if not None, max number of examples in Dataset
train_sentences_to_eval = 100

# encoder
lstm_layers_num = 1
hidden_size_char = 150  # lstm on chars, checked
hidden_size_lstm = 400  # lstm on word embeddings, checked. TODO: eval 300, 400+
encoder_lstm_input_dropout = 0.5
encoder_lstm_output_dropout = 0.5
encoder_lstm_state_dropout = 0.7
encoder_lstm_use_recurrent_drouout = False
encoder_lstm_dropout_output = 1.0
use_encoder_lstm_batch_norm = False

# decoder
use_crf = False  # if crf, training is 1.7x slower on CPU

# evaluation
eval_batch_size = 200

tf_session_config = {}

use_input_attention = False
