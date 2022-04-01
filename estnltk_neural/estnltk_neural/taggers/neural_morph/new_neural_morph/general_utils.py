import os
from pprint import pprint
import importlib.util
import numpy as np

# =================================================================
#   Configuration handling
# =================================================================

def load_config_from_file(config_module_path):
    spec = importlib.util.spec_from_file_location("config", config_module_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


def get_model_path_from_dir(directory):
    """
    Checks if the given directory could contain NeuralMorphTagger's model.
    Returns path to the model's 'output' directory if a model directory 
    was found. Otherwise, returns None.
    """
    if directory is not None and os.path.isdir(directory):
        data_dir    = os.path.join(directory, 'output/data')
        results_dir = os.path.join(directory, 'output/results')
        if os.path.isdir(data_dir) and os.path.isdir(results_dir):
            # Model directory structure:
            #  output/data/*
            #  output/results/*
            return os.path.join(directory, 'output')
        else:
            dir_content = list(os.listdir(directory))
            if len(dir_content) == 1:
                subdir = dir_content[0]
                data_dir = \
                    os.path.join(directory, subdir+'/output/data')
                results_dir = \
                    os.path.join(directory, subdir+'/output/results')
                if os.path.isdir(data_dir) and \
                   os.path.isdir(results_dir):
                    # Model directory structure:
                    #  emb_cat_sum/output/data/*
                    #  emb_cat_sum/output/results/*
                    #  or 
                    #  emb_tag_sum/output/data/*
                    #  emb_tag_sum/output/results/*
                    return os.path.join(directory, subdir+'/output')
    # Expected structure not found ...
    return None


def override_config_paths_from_model_dir(config, model_dir):
    """
    Updates file paths in the configuration according to the 
    given model directory. 
    Note that the updating takes place only when given directory 
    is appropriate model directory, i.e. contains subfolders
    "output/data/*" and "output/results/*".
    Note also that this function does not check for the existence
    of model files.
    Returns config.
    """
    if isinstance(model_dir, str):
        out_dir = get_model_path_from_dir(model_dir)
        if out_dir is not None:
            # override configuration
            config.out_dir = out_dir
            config.out_dir = out_dir
            
            config.out_data_dir = os.path.join(out_dir, "data")
            config.dir_output = os.path.join(out_dir, "results")
            
            config.dir_model = os.path.join(config.dir_output, "model.weights")
            config.path_log = os.path.join(config.dir_output, "log.txt")
            config.training_log = os.path.join(config.dir_output, "training.log")
            
            config.filename_embeddings_trimmed = os.path.join(config.out_data_dir, "embeddings.npz")
            
            config.filename_words = os.path.join(config.out_data_dir, "words.txt")
            config.filename_tags = os.path.join(config.out_data_dir, "tags.txt")
            config.filename_chars = os.path.join(config.out_data_dir, "chars.txt")
            config.filename_analysis = os.path.join(config.out_data_dir, "analysis.txt")
            config.filename_singletons = os.path.join(config.out_data_dir, "singletons.txt")
    return config


# =================================================================
#   Model utils
# =================================================================

def _pad_sequences(sequences, pad_tok, max_length):
    """
    Args:
        sequences: a generator of list or tuple
        pad_tok: the char to pad with

    Returns:
        a list of list where each sublist has same length
    """
    sequence_padded, sequence_length = [], []

    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_length] + [pad_tok] * max(max_length - len(seq), 0)
        sequence_padded += [seq_]
        sequence_length += [min(len(seq), max_length)]

    return sequence_padded, sequence_length


def pad_sequences(sequences, pad_tok, nlevels=1):
    """
    Args:
        sequences: a generator of list or tuple
        pad_tok: the char to pad with
        nlevels: "depth" of padding, for the case where we have characters ids

    Returns:
        a list of list where each sublist has same length

    """
    if nlevels == 1:
        max_length = max(map(lambda x: len(x), sequences))
        sequence_padded, sequence_length = _pad_sequences(sequences, pad_tok, max_length)
    elif nlevels == 2:
        max_length_word = max([max(map(lambda x: len(x), seq))
                               for seq in sequences])
        sequence_padded, sequence_length = [], []
        for seq in sequences:
            # all words are same length now
            sp, sl = _pad_sequences(seq, pad_tok, max_length_word)
            sequence_padded += [sp]
            sequence_length += [sl]

        max_length_sentence = max(map(lambda x: len(x), sequences))
        sequence_padded, _ = _pad_sequences(sequence_padded,
                                            [pad_tok] * max_length_word, max_length_sentence)
        sequence_length, _ = _pad_sequences(sequence_length, 0,
                                            max_length_sentence)

    return sequence_padded, sequence_length


def create_numpy_embeddings_matrix(dim1, dim2):
    limit = np.sqrt(6 / (dim1 + dim2))
    M = np.random.uniform(low=-limit, high=limit,
                          size=[dim1, dim2]).astype(np.float32)
    M[0, :] = 0.0  # padding vector
    return M


def print_config(config):
    res = {}
    for k, v in config.__dict__.items():
        if not k.startswith('__') and not callable(v):
            res[k] = v
    pprint(res)
