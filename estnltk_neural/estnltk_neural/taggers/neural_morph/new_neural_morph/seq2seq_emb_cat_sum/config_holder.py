import pickle
import numpy as np
from pprint import pformat

from estnltk_neural.helpers.neural_morph_logger import neural_morph_logger

UNK = "$UNK$"
NUM = "$NUM$"
MISSING_CATEGORY_ID = 0


class ConfigHolder():
    def __init__(self, config):
        for k, v in config.__dict__.items():
            if not k.startswith('__') and not callable(v):
                setattr(self, k, v)

        # 1. vocabulary
        self.vocab_words = load_vocab(self.filename_words)
        self.vocab_tags = self.load_tag_vocab(self.filename_tags)
        self.vocab_chars = load_vocab(self.filename_chars)
        self.vocab_singletons = load_vocab(self.filename_singletons) if self.train_singletons else None

        self.nwords = len(self.vocab_words)
        self.nchars = len(self.vocab_chars)
        self.ntags = len(self.vocab_tags)

        # 2. get processing functions that map str -> id
        self.processing_word_train = get_processing_word(self.vocab_words,
                                                         self.vocab_chars,
                                                         vocab_singletons=self.vocab_singletons,
                                                         singleton_p=self.singleton_p,
                                                         lowercase=self.lowercase,
                                                         use_words=self.use_word_embeddings,
                                                         use_chars=self.use_char_embeddings)
        self.processing_word_infer = get_processing_word(self.vocab_words,
                                                         self.vocab_chars,
                                                         lowercase=self.lowercase,
                                                         use_words=self.use_word_embeddings,
                                                         use_chars=self.use_char_embeddings)
        self.processing_tag = get_processing_word(self.vocab_tags,
                                                  use_words=True,
                                                  lowercase=False,
                                                  allow_unk=True)
        # don't process analyses by default
        self.processing_analysis = lambda x: None

        # 3. get pre-trained embeddings
        self.embeddings = get_trimmed_glove_vectors(self.filename_embeddings_trimmed) if self.use_pretrained else None

        self.logger = neural_morph_logger(self.path_log)
        
        if self.analysis_embeddings == "attention_tag" or self.analysis_embeddings == "tag":
            self.vocab_analysis = load_vocab(self.filename_analysis)
            self.nanalyses = len(self.vocab_analysis)
            self.processing_analysis = get_processing_word(self.vocab_analysis,
                                                           use_words=True,
                                                           lowercase=False,
                                                           allow_unk=True)
        elif self.analysis_embeddings == "attention_category":
            self.vocab_analysis = load_vocab(self.filename_analysis)
            self.nanalyses = len(self.vocab_analysis)
            self.processing_analysis = get_processing_analyses_attention_category(self.vocab_analysis)

        elif self.analysis_embeddings == "category":
            self.vocab_analysis = load_category_analysis_dict(self.filename_analysis)
            self.processing_analysis = get_processing_analyses_category(self.vocab_analysis)
    
    def load_tag_vocab(self, filename_tags):
        return load_vocab(filename_tags)

    def __str__(self):
        conf = {}
        for k, v in self.__dict__.items():
            if not k.startswith('__') and not callable(v):
                conf[k] = v
        return pformat(conf)


def get_processing_word(vocab_words=None, vocab_chars=None, vocab_singletons=None, singleton_p=0.5,
                        lowercase=False, use_words=False, use_chars=False, allow_unk=True):
    """Return lambda function that transform a word (string) into list,
    or tuple of (list, id) of int corresponding to the ids of the word and
    its corresponding characters.

    Args:
        vocab: dict[word] = idx

    Returns:
        f("cat") = ([12, 4, 32], 12345)
                 = (list of char ids, word id)

    """

    def f(word):
        # 0. get chars of words
        if use_chars is True:
            char_ids = []
            for char in word:
                # ignore chars out of vocabulary
                if char in vocab_chars:
                    char_ids += [vocab_chars[char]]

        if use_words is True:
            # 1. preprocess word
            if lowercase:
                word = word.lower()
            if word.isdigit():
                word = NUM

            # 2. get id of word
            if vocab_words is not None:
                if word in vocab_words:
                    if vocab_singletons is not None and word in vocab_singletons and np.random.rand() < singleton_p:
                        word = vocab_words[UNK]
                        assert allow_unk is True
                    else:
                        word = vocab_words[word]
                else:
                    if allow_unk:
                        word = vocab_words[UNK]
                    else:
                        raise Exception("Unknow key is not allowed. Check that your vocab (tags?) is correct")

        # 3. return tuple char ids, word id
        if use_chars is True and use_words is True:
            return char_ids, word
        elif use_chars is True:
            return char_ids
        elif use_words is True:
            return word
        else:
            raise RuntimeError("Either 'use_words' or 'use_chars' must be true")

    return f


def load_embeddings_vocab(filename, lowercase=False, merge_case=False):
    """Load vocab from file

    Args:
        filename: path to the glove vectors

    Returns:
        vocab: set() of strings
    """
    vocab = set()
    with open(filename, encoding="utf-8") as f:
        for line in f:
            word = line.strip().split(" ")[0]
            if lowercase:
                vocab.add(word.lower())
            elif merge_case:
                vocab.add(word)
                vocab.add(word.lower())
            else:
                vocab.add(word)
    print("- done glove. {} tokens".format(len(vocab)))
    return vocab


def load_vocab(filename):
    """Loads vocab from a file

    Args:
        filename: (string) the format of the file must be one word per line.

    Returns:
        d: dict[word] = index

    """
    d = dict()
    with open(filename, encoding="utf-8") as f:
        for idx, word in enumerate(f):
            word = word.strip()
            d[word] = idx
    return d


def get_trimmed_glove_vectors(filename):
    """
    Args:
        filename: path to the npz file

    Returns:
        matrix of embeddings (np array)

    """
    with np.load(filename) as data:
        return data["embeddings"]


def get_processing_analyses_attention_category(vocab_categories):
    def f(tag):
        cats = tag.split("|")
        return [vocab_categories[c] for c in cats if c in vocab_categories]

    return f


def get_processing_analyses_category(vocab_tags):
    """
    :param tag2idx:
    :param morph_categories:
    :return: list of ids for each category
    """

    def f(tag):
        """
        tags is a string of a form "POS=Noun|CASE=Nom|..."
        """
        tags = tag.split("|")
        word_cat2tag_dict = {t.split("=")[0]: t for t in tags}
        cat_ids = []
        for cat in vocab_tags:
            if cat in word_cat2tag_dict:
                tid = vocab_tags[cat][word_cat2tag_dict[cat]]
            else:
                tid = MISSING_CATEGORY_ID
            cat_ids.append(tid)
        return cat_ids

    return f


def load_category_analysis_dict(filename):
    with open(filename, 'rb') as f:
        tag_dict = pickle.load(f)
        return tag_dict