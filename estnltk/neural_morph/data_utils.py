import os
import math
import random
from pprint import pformat
from collections import Counter

import numpy as np

from .general_utils import get_logger

UNK = "$UNK$"
NUM = "$NUM$"
NONE = "O"

SOS = "$SOS$"
EOS = "$EOS$"
PAD = "$PAD$"


class DataBuilder(object):
    def __init__(self, config):
        self.config = config

        processing_word = get_processing_word(lowercase=config.lowercase, use_words=True)

        self.dev = CoNLLDataset(config.filename_dev, processing_word)
        self.test = CoNLLDataset(config.filename_test, processing_word)
        self.train = CoNLLDataset(config.filename_train, processing_word)

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
                             lowercase=self.config.lowercase)

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

    def handle_vocab_analyses(self, vocab_analyses_train, vocab_analyses_dev, vocab_analyses_test):
        # treats analysis variants as flat-tags
        vocab_tags = vocab_analyses_train
        vocab_tags = [PAD, UNK] + list(vocab_tags)

        write_vocab(vocab_tags, self.config.filename_analysis)
        print("Saved vocab of %d analyses" % len(vocab_tags))

    def handle_vocab_chars(self):
        # Build and save character vocab
        train = CoNLLDataset(self.config.filename_train)
        vocab_chars = get_char_vocab(train)
        write_vocab(vocab_chars, self.config.filename_chars)
        print("Saved vocab of %d characters" % len(vocab_chars))

    def handle_vocab_words(self, vocab_words_train, vocab_words_dev, vocab_words_test):
        if self.config.use_pretrained:
            vocab_embeddings = load_embeddings_vocab(self.config.filename_embeddings,
                                                     lowercase=self.config.lowercase)
            if self.config.keep_train_vocab:
                # keep all train words + dev and test words which have pre-trained embeddings
                # need to train UNK word separately
                vocab = vocab_words_train | (vocab_words_dev & vocab_embeddings) | (vocab_words_test & vocab_embeddings)
            else:
                # keep only words which have pre-trained embeddings
                vocab = (vocab_words_train | vocab_words_dev | vocab_words_test) & vocab_embeddings
        else:
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
        write_vocab(vocab_tags, self.config.filename_tags)
        print("Saved vocab of %d tags" % len(vocab_tags))


class ConfigHolder:
    def __init__(self, config):
        for k, v in config.__dict__.items():
            if not k.startswith('__') and not callable(v):
                setattr(self, k, v)

        # 1. vocabulary
        self.vocab_words = load_vocab(self.filename_words)
        self.vocab_tags = load_vocab(self.filename_tags)
        self.vocab_chars = load_vocab(self.filename_chars)
        self.vocab_singletons = load_vocab(self.filename_singletons) if self.train_singletons else None
        self.vocab_analysis = load_vocab(self.filename_analysis)

        self.nwords = len(self.vocab_words)
        self.nchars = len(self.vocab_chars)
        self.ntags = len(self.vocab_tags)
        self.nanalyses = len(self.vocab_analysis)

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
        self.processing_analysis = get_processing_word(self.vocab_analysis,
                                                       use_words=True,
                                                       lowercase=False,
                                                       allow_unk=True)

        # 3. get pre-trained embeddings
        self.embeddings = load_trimmed_embeddings(self.filename_embeddings_trimmed) if self.use_pretrained else None

        self.logger = get_logger(self.path_log)

    def __str__(self):
        conf = {}
        for k, v in self.__dict__.items():
            if not k.startswith('__') and not callable(v):
                conf[k] = v
        return pformat(conf)


def embed_vocabulary(vocab, fasttext_filename, output_filename, dim, lowercase=False):
    """Saves glove vectors in numpy array

    Args:
        vocab: dict {word: index}
        fasttext_filename: (str) a path to the original fastText embeddings text file
        output_filename: a path where to store embedded vocabulary
        dim: (int) dimension of embeddings
        lowercase: (bool) lowercase word for vocabulary lookup
    """
    embeddings = np.random.normal(scale=2.0 / (dim + len(vocab)),
                                  size=(len(vocab), dim))
    n = 0
    with open(fasttext_filename, encoding="utf-8") as f:
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
    np.savez_compressed(output_filename, embeddings=embeddings)


def get_singletons(dataset):
    """
    Returns a list of words which occur exactly once in the dataset.
    """
    counter = Counter(word for words, _, _ in dataset for word in words)
    singletons = [word for word, cnt in counter.items() if cnt == 1]
    return singletons


class CoNLLDataset:
    def __init__(self,
                 filename,
                 processing_word=None,
                 processing_tag=None,
                 processing_analysis=None,
                 max_iter=None,
                 shuffle=False,
                 use_buckets=False,
                 batch_size=None,
                 sort=False
                 ):
        """
        Initialises a CoNLL dataset.

        Args:
            filename: path to the file
            processing_word: (callable) optionally process word
            processing_tag: (callable) optionally process tag
            processing_analysis: (callable) optionally process analyses
            max_iter: (optional) max number of sentences to read
            shuffle: (bool) shuffle sentences
            use_buckets: (bool) organise sentences in buckets of similar size for faster training
            batch_size: (int) number of sentences in one batch
            sort: (bool) sort sentences by length to accelerate inference
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
        self.length = None

    def parse_line(self, line):
        ls = line.split("\t")
        word, tag, analyses = ls[0], ls[1], ls[2:]

        if self.processing_word is not None:
            word = self.processing_word(word)
        if self.processing_tag is not None:
            tag = self.processing_tag(tag)
        if self.processing_analysis is not None:
            analyses = [self.processing_analysis(anal) for anal in analyses]

        return word, tag, analyses

    def __iter__(self):
        """
        Yields:
            tuple (words, tags, analyses):
                words: list of raw words
                tags: list of raw tags
                analyse: list of raw analyses
        """
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
        """Returns the corpus length in the number of sentences"""
        if self.length is None:
            self.length = 0
            for _ in self:
                self.length += 1
        return self.length


def get_processing_word(vocab_words=None,
                        vocab_chars=None,
                        vocab_singletons=None,
                        singleton_p=0.5,
                        lowercase=False,
                        use_words=False,
                        use_chars=False,
                        allow_unk=True):
    """
    Returns a function which transforms a word into
    a tuple of (list of char ids, word id).

    Args:
        vocab_words: (set) word vocabulary
        vocab_chars: (set) character vocabulary
        vocab_singletons: (set) singleton vocabulary
        singleton_p: (float) probability of replacing singletons with UNK
        lowercase: (bool) lowercase word for vocabulary lookup
        use_words: (bool) output word id
        use_chars: (bool) output character ids
        allow_unk: (bool) allow OOV words

    Returns:
        tuple (character ids, word id)

    """

    def f(word):
        # get chars of words
        if use_chars is True:
            char_ids = []
            for char in word:
                # ignore OOV chars
                if char in vocab_chars:
                    char_ids += [vocab_chars[char]]

        if use_words is True:
            # pre-process word
            if lowercase:
                word = word.lower()
            if word.isdigit():
                word = NUM

            # Get word id
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
                        raise Exception("Unknown key is not allowed. Check that your vocabulary is correct.")

        if use_chars is True and use_words is True:
            return char_ids, word
        elif use_chars is True:
            return char_ids
        elif use_words is True:
            return word
        else:
            raise RuntimeError("One of 'use_words' or 'use_chars' must be True")

    return f


def get_vocab(dataset):
    """Build vocabulary from a dataset

    Args:
        dataset: (CoNLLDataset) a dataset object

    Returns:
        (tuple): a sets of all the words, tags and analyses in the dataset

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
    """Build char vocabulary from a dataset

    Args:
        dataset: an iterator over sentences

    Returns:
        set: all the characters in the dataset

    """
    vocab_char = set()
    for sentence, _, _ in dataset:
        for word in sentence:
            vocab_char.update(word)
    return vocab_char


def load_embeddings_vocab(filename, lowercase=False):
    """Load embedding vocabulary from file

    Args:
        filename: (str) path to fastText embeddings text file
        lowercase: (bool) if True, adds a lowercased word

    Returns:
        set of str: vocabulary
    """
    vocab = set()
    with open(filename, encoding="utf-8") as f:
        for line in f:
            word = line.strip().split(" ")[0]
            if lowercase:
                vocab.add(word.lower())
            else:
                vocab.add(word)
    return vocab


def load_vocab(filename):
    """Loads vocabulary from a file

    Args:
        filename: (str) the format of the file must be one word per line.

    Returns:
        d: dict[word] = index
    """
    d = dict()
    with open(filename, encoding="utf-8") as f:
        for idx, word in enumerate(f):
            word = word.strip()
            d[word] = idx
    return d


def load_trimmed_embeddings(filename):
    """Loads trimmed embeddings from file.

    Args:
        filename: path to the trimmed embeddings file (npz)

    Returns:
        (numpy.array) a matrix of embeddings
    """
    with np.load(filename) as data:
        return data["embeddings"]


def write_vocab(vocab, filename):
    """
    Writes a vocab to a file, one word per line.

    Args:
        vocab: iterable over words
        filename: output file name
    """
    with open(filename, "w", encoding="utf-8") as f:
        for word in vocab:
            print(word, file=f)


def pad_batch(batch, pad_id, levels=1):
    """
    Pads sentences in the batch.

    Args:
        batch: a generator of sentences
        pad_id: (int) id to pad with
        levels: (int) dimension of padding (1 or 2)

    Returns:
        a list of sequences of the same length

    """
    if levels == 1:
        max_length = max(map(lambda x: len(x), batch))
        sequence_padded, sequence_length = _pad_batch(batch, pad_id, max_length)
    elif levels == 2:
        max_length_word = max([max(map(lambda x: len(x), seq))
                               for seq in batch])
        sequence_padded, sequence_length = [], []
        for seq in batch:
            sp, sl = _pad_batch(seq, pad_id, max_length_word)
            sequence_padded += [sp]
            sequence_length += [sl]

        max_length_sentence = max(map(lambda x: len(x), batch))
        sequence_padded, _ = _pad_batch(sequence_padded,
                                        [pad_id] * max_length_word, max_length_sentence)
        sequence_length, _ = _pad_batch(sequence_length, 0,
                                        max_length_sentence)

    return sequence_padded, sequence_length


def _pad_batch(batch, pad_id, max_length):
    """
    Args:
        batch: a generator of sentences
        pad_id: the char to pad with
        max_length: (int) length of the longest sequence in the batch
    Returns:
        a list of sequences of the same length
    """
    sequence_padded, sequence_length = [], []

    for seq in batch:
        seq = list(seq)
        seq_ = seq[:max_length] + [pad_id] * max(max_length - len(seq), 0)
        sequence_padded += [seq_]
        sequence_length += [min(len(seq), max_length)]

    return sequence_padded, sequence_length


def create_numpy_embeddings_matrix(dim1, dim2):
    """
    Randomly initialises a 2-dimensional embeddings matrix.
    Padding embedding (index = 0) is initialised with zeros.
    """
    limit = np.sqrt(6 / (dim1 + dim2))
    M = np.random.uniform(low=-limit, high=limit,
                          size=[dim1, dim2]).astype(np.float32)
    M[0, :] = 0.0  # padding vector
    return M


def iter_minibatches(dataset, batch_size):
    """
    Creates mini batches of the given size from the input dataset.

    Args:
        dataset: (CoNLLDataset) iterator of tuples (sentence, tags, analyses)
        batch_size: (int)

    Yields:
        list of tuples

    """
    x_batch, y_batch, z_batch = [], [], []
    for (x, y, z) in dataset:
        if len(x_batch) == batch_size:
            yield x_batch, y_batch, z_batch
            x_batch, y_batch, z_batch = [], [], []

        if type(x[0]) == tuple:
            x = zip(*x)
        x_batch += [x]
        y_batch += [y]
        z_batch += [z]

    if len(x_batch) != 0:
        yield x_batch, y_batch, z_batch
