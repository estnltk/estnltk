import os
import math
import random
import pickle
import numpy as np
from pprint import pformat
from collections import Counter
from _collections import OrderedDict, defaultdict

from ..general_utils import get_logger

UNK = "$UNK$"
NUM = "$NUM$"
NONE = "O"
DUMMY_ANALYSIS_TAG = "POS=DUMMY"

SOS = "$SOS$"
EOS = "$EOS$"
PAD = "$PAD$"

MISSING_CATEGORY_STR = "MISSING"
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

        self.logger = get_logger(self.path_log)
        if self.analysis_embeddings == "tag" or self.analysis_embeddings == "input_attention_tag":
            self.vocab_analysis = load_vocab(self.filename_analysis)
            self.nanalyses = len(self.vocab_analysis)
            print("Loaded analyses:", self.nanalyses, "from file", self.filename_analysis)
            self.processing_analysis = get_processing_word(self.vocab_analysis,
                                                           use_words=True,
                                                           lowercase=False,
                                                           allow_unk=True)
        elif self.analysis_embeddings == "input_attention_category":
            self.vocab_analysis = load_vocab(self.filename_analysis)
            self.nanalyses = len(self.vocab_analysis)
            self.processing_analysis = get_processing_analyses_input_attention_category(self.vocab_analysis)
        elif self.analysis_embeddings == "category":
            self.vocab_analysis = load_category_analysis_dict(self.filename_analysis)
            self.processing_analysis = get_processing_category_analyses(self.vocab_analysis)
    
    def load_tag_vocab(self, filename_tags):
        return load_vocab(filename_tags)

    def __str__(self):
        conf = {}
        for k, v in self.__dict__.items():
            if not k.startswith('__') and not callable(v):
                conf[k] = v
        return pformat(conf)


class CoNLLDataset():
    def __init__(self, filename, processing_word=None, processing_tag=None, processing_analysis=None, max_iter=None,
                 shuffle=False, use_buckets=False, batch_size=None, sort=False, use_dummy_analysis=None,
                 use_analysis_dropout=False, analysis_dropout_method=None, analysis_dropout_keep_prob=1.0):
        """
        Args:
            filename: path to the file
            processing_words: (optional) function that takes a word as input
            processing_tags: (optional) function that takes a tag as input
            max_iter: (optional) max number of sentences to yield
            ...
        """
        self.filename = filename
        self.processing_word = processing_word
        self.processing_tag = processing_tag
        self.processing_analysis = processing_analysis
        self.max_iter = max_iter
        self.shuffle = shuffle
        self.sort = sort
        self.use_buckets = use_buckets
        self.batch_size = batch_size
        self.use_dummy_analysis = use_dummy_analysis

        self.use_analysis_dropout = use_analysis_dropout
        self.analysis_dropout_method = analysis_dropout_method
        self.analysis_dropout_keep_prob = analysis_dropout_keep_prob
        self.length = None

    def parse_line(self, line):
        ls = line.split("\t")
        word, tag, analyses = ls[0], ls[1], ls[2:]
        analyses = [a.strip() for a in analyses]

        if self.use_analysis_dropout is True and len(analyses) > 0:
            if random.random() >= self.analysis_dropout_keep_prob:
                analyses = []

        if self.processing_word is not None:
            word = self.processing_word(word)
        if self.processing_tag is not None:
            tag = self.processing_tag(tag)
        if self.processing_analysis is not None:
            analyses = [self.processing_analysis(anal) for anal in analyses]

        return word, tag, analyses
    
    def __iter__(self):
        sentences = self.read_sentences_from_file()
        if self.shuffle:
            random.shuffle(list(sentences))
            n = 0
            for words, tags, analyses in sentences:
                yield words, tags, analyses
                n += 1
        elif self.sort:
            sentences = list(sentences)
            sentences.sort(key=lambda item: len(item[0]))
            for words, tags, analyses in sentences:
                yield words, tags, analyses
        elif self.use_buckets:
            assert self.batch_size is not None
            sentences = list(sentences)
            sentences.sort(key=lambda item: (len(item[0]), random.random()))
            nbuckets = math.ceil(len(sentences) / self.batch_size)
            bucket_list = list(range(nbuckets))
            random.shuffle(bucket_list)
            n = 0
            for bucket in bucket_list:
                offset = bucket * self.batch_size
                for words, tags, analyses in sentences[offset: offset + self.batch_size]:
                    yield words, tags, analyses
                    n += 1
            assert n == len(sentences), "n=%d, snt-num=%d" % (n, len(sentences))
        else:
            for words, tags, analyses in sentences:
                yield words, tags, analyses

    def read_sentences_from_file(self):
        niter = 0
        with open(self.filename, encoding="utf-8") as f:
            words, tags, analyses = [], [], []
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    if len(words) != 0:
                        niter += 1
                        if self.max_iter is not None and niter > self.max_iter:
                            break
                        yield words, tags, analyses
                        words, tags, analyses = [], [], []
                else:
                    word, tag, analyses_ = self.parse_line(line)
                    words += [word]
                    tags += [tag]
                    analyses += [analyses_]

    def __len__(self):
        """Iterates once over the corpus to set and store length"""
        if self.length is None:
            self.length = 0
            for _ in self:
                self.length += 1
        return self.length


class DataBuilder():
    def __init__(self, config):
        self.config = config

        processing_word = get_processing_word(lowercase=config.lowercase, use_words=True)

        self.dev = CoNLLDataset(config.filename_dev, processing_word)
        self.test = CoNLLDataset(config.filename_test, processing_word)
        self.train = CoNLLDataset(config.filename_train, processing_word)

    def handle_vocab_analyses(self, vocab_analyses_train, vocab_analyses_dev, vocab_analyses_test):
        if self.config.analysis_embeddings == "tag" or self.config.analysis_embeddings == "input_attention_tag":
            # treats analysis variants as flat-tags
            vocab_tags = vocab_analyses_train
            vocab_tags = [PAD, UNK, DUMMY_ANALYSIS_TAG] + list(vocab_tags)

            write_vocab(vocab_tags, self.config.filename_analysis)
            print("Saved vocab of %d analyses" % len(vocab_tags))
        elif self.config.analysis_embeddings == "input_attention_category":
            vocab_analyses = [PAD] + list(set(cat for tag in vocab_analyses_train for cat in tag.split("|")))
            print("vocab_analyses ({}): {}".format(len(vocab_analyses), vocab_analyses))
            write_vocab(vocab_analyses, self.config.filename_analysis)
        elif self.config.analysis_embeddings == "category":
            vocab_analyses = list(vocab_analyses_train | vocab_analyses_dev | vocab_analyses_test)
            category2idx_dict = create_category_analysis_dict(vocab_analyses)
            print("vocab_analysis ({}): {}".format(len(vocab_analyses), vocab_analyses))
            print("category2idx_dict: {}".format(category2idx_dict))
            # Save vocab
            write_category_analysis_dict(category2idx_dict, self.config.filename_analysis)
    
    def run(self):
        # Build Word and Tag vocab
        vocab_words_train, vocab_tags_train, vocab_analyses_train = get_vocab(self.train)
        vocab_words_dev, vocab_tags_dev, vocab_analyses_dev = get_vocab(self.dev)
        vocab_words_test, vocab_tags_test, vocab_analyses_test = get_vocab(self.test)

        self.create_directories()
        self.handle_vocab_words(vocab_words_train, vocab_words_dev, vocab_words_test)
        self.handle_vocab_tags(vocab_tags_train, vocab_tags_dev, vocab_tags_test)
        self.handle_vocab_analyses(vocab_analyses_train, vocab_analyses_dev, vocab_analyses_test)
        self.handle_vocab_chars()

        # save singletons
        if self.config.train_singletons is True:
            singletons = get_singletons(self.train)
            write_vocab(singletons, self.config.filename_singletons)
            print("Saved %d singletons" % len(singletons))

        # Trim embedding vectors
        if self.config.use_pretrained:
            vocab = load_vocab(self.config.filename_words)
            embed_vocabulary(vocab, self.config.filename_embeddings,
                             self.config.filename_embeddings_trimmed,
                             self.config.dim_word,
                             lowercase=self.config.lowercase,
                             case_insensitive=self.config.case_insensitive_embedding_lookup)

    def create_directories(self):
        # create data output directory
        if not os.path.exists(self.config.out_data_dir):
            os.makedirs(self.config.out_data_dir)

        # create model output directory
        if not os.path.exists(self.config.dir_output):
            os.makedirs(self.config.dir_output)

        # create training log file
        if not os.path.exists(self.config.training_log):
            f = open(self.config.training_log, "w")
            f.close()

    def handle_vocab_chars(self):
        # Build and save char vocab
        train = self.CoNLLDatasetClass(self.config.filename_train)
        vocab_chars = get_char_vocab(train)
        write_vocab(vocab_chars, self.config.filename_chars)
        print("Saved vocab of %d characters" % len(vocab_chars))

    def handle_vocab_words(self, vocab_words_train, vocab_words_dev, vocab_words_test):
        if self.config.use_pretrained:
            vocab_embeddings = load_embeddings_vocab(self.config.filename_embeddings,
                                                     lowercase=self.config.lowercase,
                                                     merge_case=self.config.case_insensitive_embedding_lookup)
            if self.config.keep_train_vocab:
                # keep all train words + dev and test words which have pre-trained embeddings
                # need to train UNK word separately
                vocab = vocab_words_train | (vocab_words_dev & vocab_embeddings) | (vocab_words_test & vocab_embeddings)
            else:
                # keep only words which have pre-trained embeddings
                vocab = (vocab_words_train | vocab_words_dev | vocab_words_test) & vocab_embeddings
        else:
            # TODO: why include dev, test words in vocab?
            vocab = vocab_words_train
        vocab.add(UNK)
        vocab.add(NUM)
        vocab = [PAD] + list(vocab)

        write_vocab(vocab, self.config.filename_words)
        print("Saved vocab of %d words" % len(vocab))

    def handle_vocab_tags(self, vocab_tags_train, vocab_tags_dev, vocab_tags_test):
        vocab_tags = vocab_tags_train
        for sym in [EOS, SOS, PAD, UNK]:
            if sym in vocab_tags:
                raise ValueError('Special symbol "%s" is already present in tag vocabulary' % sym)
        vocab_tags = [PAD, SOS, EOS, UNK] + list(vocab_tags)
        # Save vocab
        write_vocab(vocab_tags, self.config.filename_tags)
        print("Saved vocab of %d tags" % len(vocab_tags))

def anylsis_category2matrix(sequences, category_idx, max_sentence_length):
    """
    :param labels: batch of labels. For each word it contains a tuple (`category id`, `attribute id`)
    """
    assert isinstance(category_idx, (int, np.int32, np.int64))
    m = np.zeros([len(sequences), max_sentence_length],
                 dtype=np.int32)
    for i in range(len(sequences)):
        for j in range(len(sequences[i])):
            word_labels = sequences[i][j]
            m[i, j] = word_labels[category_idx]
    return m


def embed_vocabulary(vocab, glove_filename, trimmed_filename, dim,
                     lowercase=False,
                     case_insensitive=False):
    """Saves glove vectors in numpy array

    Args:
        vocab: dictionary vocab[word] = index
        glove_filename: a path to a glove file
        trimmed_filename: a path where to store a matrix in npy
        dim: (int) dimension of embeddings

    """
    if lowercase is True:
        assert case_insensitive is False

    embeddings = np.random.normal(scale=2.0 / (dim + len(vocab)),
                                  size=(len(vocab), dim))
    n = 0
    if case_insensitive is True:
        processed = set()

        with open(glove_filename, encoding="utf-8") as f:
            for line in f:
                line = line.strip().split(' ')
                word = line[0]
                word_idx = None
                if word in vocab:
                    word_idx = vocab[word]
                    processed.add(word)
                else:
                    word_lower = word.lower()
                    if word_lower in vocab and word_lower not in processed:
                        word_idx = vocab[word_lower]
                if word_idx is not None:
                    embedding = [float(x) for x in line[1:]]
                    embeddings[word_idx] = np.asarray(embedding)
                    n += 1
    else:
        with open(glove_filename, encoding="utf-8") as f:
            for line in f:
                line = line.strip().split(" ")
                word = line[0]
                if lowercase:
                    word = word.lower()
                if word in vocab:
                    word_idx = vocab[word]
                    embedding = [float(x) for x in line[1:]]
                    embeddings[word_idx] = np.asarray(embedding)
                    n += 1
    print("Found %d embeddings for vocabulary of %d words." % (n, len(vocab)))
    np.savez_compressed(trimmed_filename, embeddings=embeddings)


def get_singletons(dataset):
    counter = Counter(word for words, _, _ in dataset for word in words)
    singletons = [word for word, cnt in counter.items() if cnt == 1]
    return singletons

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


def get_vocab(dataset):
    """Build vocabulary from a dataset

    Args:
        dataset: a dataset objects

    Returns:
        a set of all the words, tags and analyses in the dataset

    """
    vocab_words = set()
    vocab_tags = set()
    vocab_analysis = set()
    for words, tags, analyses in dataset:
        vocab_words.update(words)
        if isinstance(tags[0], (str, bytes)):
            vocab_tags.update(tags)
        else:
            for tag in tags:
                vocab_tags.update(tag)
        for word_analyses in analyses:
            vocab_analysis.update(word_analyses)
    return vocab_words, vocab_tags, vocab_analysis


def get_char_vocab(dataset):
    """Build char vocabulary from an iterable of datasets objects

    Args:
        dataset: a iterator yielding tuples (sentence, tags)

    Returns:
        a set of all the characters in the dataset

    """
    vocab_char = set()
    for words, _, _ in dataset:
        for word in words:
            vocab_char.update(word)
    return vocab_char


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


def export_trimmed_glove_vectors(vocab, glove_filename, trimmed_filename, dim, lowercase=False):
    """Saves glove vectors in numpy array

    Args:
        vocab: dictionary vocab[word] = index
        glove_filename: a path to a glove file
        trimmed_filename: a path where to store a matrix in npy
        dim: (int) dimension of embeddings

    """
    embeddings = np.zeros([len(vocab), dim])
    with open(glove_filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip().split(' ')
            word = line[0]
            if lowercase:
                word = word.lower()
            embedding = [float(x) for x in line[1:]]
            if word in vocab:
                word_idx = vocab[word]
                embeddings[word_idx] = np.asarray(embedding)

    np.savez_compressed(trimmed_filename, embeddings=embeddings)


def get_trimmed_glove_vectors(filename):
    """
    Args:
        filename: path to the npz file

    Returns:
        matrix of embeddings (np array)

    """
    with np.load(filename) as data:
        return data["embeddings"]


def write_vocab(vocab, filename):
    """Writes a vocab to a file

    Writes one word per line.

    Args:
        vocab: iterable that yields word
        filename: path to vocab file

    Returns:
        write a word per line

    """
    with open(filename, "w", encoding="utf-8") as f:
        for i, word in enumerate(vocab):
            print(word, file=f)
            #if i != len(vocab) - 1:
            #    f.write("{}\n".format(word))
            #else:
            #    f.write(word)


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


def labels2one_hot(sequences, ntags):
    batch_size = len(sequences)
    max_sentence_length = max(len(s) for s in sequences)

    m = np.zeros((batch_size, max_sentence_length, ntags), dtype=np.int32)
    for i in range(len(sequences)):
        for j in range(len(sequences[i])):
            for k in sequences[i][j]:
                m[i, j, k] = 1.
    return m


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


def minibatches(data, minibatch_size):
    """
    Args:
        data: generator of (sentence, tags) tuples
        minibatch_size: (int)

    Yields:
        list of tuples

    """
    x_batch, y_batch, z_batch = [], [], []
    for (x, y, z) in data:
        if len(x_batch) == minibatch_size:
            yield x_batch, y_batch, z_batch
            x_batch, y_batch, z_batch = [], [], []

        if type(x[0]) == tuple:
            x = zip(*x)
        x_batch += [x]
        y_batch += [y]
        z_batch += [z]

    if len(x_batch) != 0:
        yield x_batch, y_batch, z_batch



def load_category_analysis_dict(filename):
    with open(filename, 'rb') as f:
        tag_dict = pickle.load(f)
        return tag_dict


def write_category_analysis_dict(category_dict, filename):
    with open(filename, 'wb') as f:
        pickle.dump(category_dict, f)


def get_processing_analyses_input_attention_category(vocab_categories):
    def f(tag):
        return [vocab_categories[c] for c in tag.split("|") if c in vocab_categories]

    return f


def get_processing_category_analyses(vocab_tags):
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


def create_category_analysis_dict(tags):
    """
    :return: dict
        {category-key -> {category-key-value -> category-key-value-id}}
    """
    cat2tag_dict = defaultdict(set)
    for tag in tags:
        for cat_kv in tag.split("|"):
            cat_k = cat_kv.split("=")[0]
            cat2tag_dict[cat_k].add(cat_kv)

    # add dummy tag
    for cat_kv in DUMMY_ANALYSIS_TAG.split("|"):
        cat_k = cat_kv.split("=")[0]
        cat2tag_dict[cat_k].add(cat_kv)

    for cat_k, tag_set in cat2tag_dict.items():
        cat2tag_dict[cat_k] = [MISSING_CATEGORY_STR] + list(tag_set)

    tag2idx = defaultdict(lambda: dict())
    for cat_k, tag_list in cat2tag_dict.items():
        for i, tag in enumerate(tag_list):
            tag2idx[cat_k][tag] = i
    tag2idx = OrderedDict(tag2idx)
    return tag2idx
