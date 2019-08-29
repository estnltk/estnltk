from ..common_data_utils import *

import pickle
from collections import defaultdict, OrderedDict


class ConfigHolder(BaseConfigHolder):
    def __init__(self, config):
        super().__init__(config)
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


class CoNLLDataset(BaseCoNLLDataset):
    def parse_line(self, line):
        ls = line.split("\t")
        word, tag, analyses = ls[0], ls[1].split('|'), ls[2:]
        if self.processing_word is not None:
            word = self.processing_word(word)
        if self.processing_tag is not None:
            tag = [self.processing_tag(t) for t in tag]
        if self.processing_analysis is not None:
            analyses = [self.processing_analysis(anal) for anal in analyses]
        return word, tag, analyses


class DataBuilder(BaseDataBuilder):
    def __init__(self, config):
        super().__init__(config, CoNLLDataset)

    def handle_vocab_analyses(self, vocab_analyses_train, vocab_analyses_dev, vocab_analyses_test):
        if (self.config.analysis_embeddings == "attention_tag" or
                    self.config.analysis_embeddings == "tag"):
            return super().handle_vocab_analyses(vocab_analyses_train, vocab_analyses_dev, vocab_analyses_test)
        elif self.config.analysis_embeddings == "attention_category":
            vocab_analyses = [PAD] + list(set(cat for tag in vocab_analyses_train for cat in tag.split("|")))
            print("vocab_analyses ({}): {}".format(len(vocab_analyses), vocab_analyses))
            write_vocab(vocab_analyses, self.config.filename_analysis)
        elif self.config.analysis_embeddings == "category":
            vocab_analyses = list(vocab_analyses_train)
            category2idx_dict = create_category_analysis_dict(vocab_analyses)
            print("vocab_categories ({}): {}".format(len(vocab_analyses), vocab_analyses))
            print("category2idx_dict: {}".format(category2idx_dict))
            # Save vocab
            write_category_analysis_dict(category2idx_dict, self.config.filename_analysis)


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


def write_category_analysis_dict(category_dict, filename):
    with open(filename, 'wb') as f:
        pickle.dump(category_dict, f)


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

    for cat_k, tag_set in cat2tag_dict.items():
        cat2tag_dict[cat_k] = [MISSING_CATEGORY_STR] + list(tag_set)

    tag2idx = defaultdict(lambda: dict())
    for cat_k, tag_list in cat2tag_dict.items():
        for i, tag in enumerate(tag_list):
            tag2idx[cat_k][tag] = i
    tag2idx = OrderedDict(tag2idx)
    return tag2idx
